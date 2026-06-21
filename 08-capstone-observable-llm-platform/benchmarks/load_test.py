import argparse
import asyncio
import json
import statistics
import time
from pathlib import Path

import httpx


async def run_load_test(base_url: str, requests: int, concurrency: int) -> dict:
    semaphore = asyncio.Semaphore(concurrency)
    latencies: list[float] = []
    token_counts: list[int] = []
    errors = 0

    async def one_request(index: int) -> None:
        nonlocal errors
        async with semaphore:
            start = time.perf_counter()
            try:
                async with httpx.AsyncClient(timeout=30) as client:
                    response = await client.post(
                        f"{base_url.rstrip('/')}/ask",
                        json={"question": f"How reliable is the capstone platform? request {index}"},
                    )
                    response.raise_for_status()
                    payload = response.json()
                    token_counts.append(payload["token_usage"]["total_tokens"])
            except Exception:
                errors += 1
            finally:
                latencies.append((time.perf_counter() - start) * 1000)

    start = time.perf_counter()
    await asyncio.gather(*(one_request(index) for index in range(requests)))
    elapsed = time.perf_counter() - start
    return {
        "base_url": base_url,
        "requests": requests,
        "concurrency": concurrency,
        "errors": errors,
        "duration_seconds": round(elapsed, 2),
        "requests_per_second": round(requests / elapsed, 2) if elapsed else 0,
        "avg_latency_ms": round(statistics.mean(latencies), 2) if latencies else 0,
        "p95_latency_ms": round(_percentile(latencies, 95), 2) if latencies else 0,
        "avg_total_tokens": round(statistics.mean(token_counts), 2) if token_counts else 0,
    }


def _percentile(values: list[float], percentile: int) -> float:
    sorted_values = sorted(values)
    index = int((percentile / 100) * (len(sorted_values) - 1))
    return sorted_values[index]


def main() -> None:
    parser = argparse.ArgumentParser(description="Load test the capstone /ask endpoint.")
    parser.add_argument("--base-url", default="http://localhost:8010")
    parser.add_argument("--requests", type=int, default=20)
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--output", default="benchmarks/results/latest-load-test.json")
    args = parser.parse_args()

    result = asyncio.run(run_load_test(args.base_url, args.requests, args.concurrency))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
