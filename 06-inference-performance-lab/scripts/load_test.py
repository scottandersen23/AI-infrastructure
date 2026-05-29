import argparse
import asyncio
import csv
import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx


PROMPTS = [
    "Explain how batching improves model-serving throughput.",
    "Compare latency and throughput for local LLM inference.",
    "Describe how KV cache memory affects concurrent requests.",
    "Summarize why quantization can improve inference speed.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a concurrent inference load test.")
    parser.add_argument("--api-url", default="http://localhost:8004")
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument("--requests", type=int, default=16)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--out-dir", default="results")
    return parser.parse_args()


async def send_request(
    client: httpx.AsyncClient,
    api_url: str,
    index: int,
    max_tokens: int,
) -> dict[str, Any]:
    payload = {
        "prompt": PROMPTS[index % len(PROMPTS)],
        "max_tokens": max_tokens,
        "temperature": 0.2,
    }
    started = time.perf_counter()
    response = await client.post(f"{api_url.rstrip('/')}/generate", json=payload)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    data = response.json()
    return {
        "request_id": index,
        "client_latency_ms": round(elapsed_ms, 2),
        "server_latency_ms": data["total_latency_ms"],
        "queue_wait_ms": data["queue_wait_ms"],
        "prompt_eval_ms": data["prompt_eval_ms"],
        "generation_ms": data["generation_ms"],
        "total_tokens": data["total_tokens"],
        "completion_tokens": data["completion_tokens"],
        "tokens_per_second": data["tokens_per_second"],
        "estimated_vram_mb": data["estimated_vram_mb"],
    }


async def run_load_test(args: argparse.Namespace) -> list[dict[str, Any]]:
    semaphore = asyncio.Semaphore(args.concurrency)
    async with httpx.AsyncClient(timeout=300) as client:
        async def bounded(index: int) -> dict[str, Any]:
            async with semaphore:
                return await send_request(
                    client=client,
                    api_url=args.api_url,
                    index=index,
                    max_tokens=args.max_tokens,
                )

        return await asyncio.gather(*(bounded(index) for index in range(args.requests)))


def summarize(rows: list[dict[str, Any]], elapsed_seconds: float) -> dict[str, Any]:
    latencies = [row["client_latency_ms"] for row in rows]
    queue_wait = [row["queue_wait_ms"] for row in rows]
    tokens = sum(row["completion_tokens"] for row in rows)
    return {
        "requests": len(rows),
        "elapsed_seconds": round(elapsed_seconds, 2),
        "requests_per_second": round(len(rows) / elapsed_seconds, 2),
        "generated_tokens_per_second": round(tokens / elapsed_seconds, 2),
        "avg_latency_ms": round(statistics.mean(latencies), 2),
        "p50_latency_ms": round(statistics.median(latencies), 2),
        "p95_latency_ms": round(_percentile(latencies, 0.95), 2),
        "max_latency_ms": round(max(latencies), 2),
        "avg_queue_wait_ms": round(statistics.mean(queue_wait), 2),
        "max_queue_wait_ms": round(max(queue_wait), 2),
    }


def write_outputs(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    out_dir: Path,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    json_path = out_dir / f"load-test-{timestamp}.json"
    csv_path = out_dir / f"load-test-{timestamp}.csv"
    json_path.write_text(json.dumps({"summary": summary, "results": rows}, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(json.dumps(summary, indent=2))


def _percentile(values: list[float], percentile: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(round((len(ordered) - 1) * percentile)))
    return ordered[index]


async def main() -> None:
    args = parse_args()
    started = time.perf_counter()
    rows = await run_load_test(args)
    elapsed_seconds = time.perf_counter() - started
    summary = summarize(rows, elapsed_seconds)
    summary["concurrency"] = args.concurrency
    summary["max_tokens"] = args.max_tokens
    write_outputs(rows, summary, Path(args.out_dir))


if __name__ == "__main__":
    asyncio.run(main())
