import argparse
import csv
import json
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import httpx


DEFAULT_PROMPTS = [
    "Explain why quantization matters for local LLM serving.",
    "Summarize the tradeoffs between CPU and GPU inference.",
    "Write a concise checklist for benchmarking a local language model.",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark the local LLM API wrapper.")
    parser.add_argument("--api-url", default="http://localhost:8001")
    parser.add_argument("--models", nargs="+", default=["llama3.2:3b"])
    parser.add_argument("--requests", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=128)
    parser.add_argument("--temperature", type=float, default=0.2)
    parser.add_argument("--out-dir", default="benchmark-runs")
    return parser.parse_args()


def run_request(
    client: httpx.Client,
    api_url: str,
    model: str,
    prompt: str,
    max_tokens: int,
    temperature: float,
) -> dict[str, Any]:
    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    started = time.perf_counter()
    response = client.post(f"{api_url.rstrip('/')}/generate", json=payload)
    elapsed_ms = (time.perf_counter() - started) * 1000
    response.raise_for_status()
    data = response.json()
    return {
        "model": model,
        "prompt": prompt,
        "latency_ms": round(elapsed_ms, 2),
        "reported_latency_ms": data.get("latency_ms"),
        "tokens_per_second": data.get("tokens_per_second"),
        "completion_tokens": data.get("usage", {}).get("completion_tokens"),
        "response_chars": len(data.get("response", "")),
    }


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    for model in sorted({row["model"] for row in rows}):
        model_rows = [row for row in rows if row["model"] == model]
        latencies = [row["latency_ms"] for row in model_rows]
        throughput = [
            row["tokens_per_second"]
            for row in model_rows
            if row["tokens_per_second"] is not None
        ]
        summaries.append(
            {
                "model": model,
                "requests": len(model_rows),
                "avg_latency_ms": round(statistics.mean(latencies), 2),
                "p50_latency_ms": round(statistics.median(latencies), 2),
                "max_latency_ms": round(max(latencies), 2),
                "avg_tokens_per_second": (
                    round(statistics.mean(throughput), 2) if throughput else None
                ),
            }
        )
    return summaries


def write_outputs(out_dir: Path, rows: list[dict[str, Any]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    summary = summarize(rows)

    json_path = out_dir / f"benchmark-{timestamp}.json"
    csv_path = out_dir / f"benchmark-{timestamp}.csv"

    json_path.write_text(
        json.dumps({"results": rows, "summary": summary}, indent=2),
        encoding="utf-8",
    )

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {json_path}")
    print(f"Wrote {csv_path}")
    print(json.dumps(summary, indent=2))


def main() -> None:
    args = parse_args()
    rows: list[dict[str, Any]] = []

    with httpx.Client(timeout=180) as client:
        for model in args.models:
            for index in range(args.requests):
                prompt = DEFAULT_PROMPTS[index % len(DEFAULT_PROMPTS)]
                print(f"Benchmarking model={model} request={index + 1}/{args.requests}")
                rows.append(
                    run_request(
                        client=client,
                        api_url=args.api_url,
                        model=model,
                        prompt=prompt,
                        max_tokens=args.max_tokens,
                        temperature=args.temperature,
                    )
                )

    write_outputs(Path(args.out_dir), rows)


if __name__ == "__main__":
    main()
