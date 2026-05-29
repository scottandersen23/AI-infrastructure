import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Analyze a load test JSON result file.")
    parser.add_argument("path", help="Path to a load-test JSON file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    summary = data["summary"]
    rows = data["results"]

    avg_generation = sum(row["generation_ms"] for row in rows) / len(rows)
    avg_prompt_eval = sum(row["prompt_eval_ms"] for row in rows) / len(rows)
    avg_queue = sum(row["queue_wait_ms"] for row in rows) / len(rows)
    bottleneck = max(
        [
            ("generation", avg_generation),
            ("prompt_eval", avg_prompt_eval),
            ("queue_wait", avg_queue),
        ],
        key=lambda item: item[1],
    )

    print("Load Test Analysis")
    print("==================")
    print(f"Requests: {summary['requests']}")
    print(f"Concurrency: {summary['concurrency']}")
    print(f"p95 latency: {summary['p95_latency_ms']} ms")
    print(f"Generated tokens/sec: {summary['generated_tokens_per_second']}")
    print(f"Likely bottleneck: {bottleneck[0]} ({bottleneck[1]:.2f} ms avg)")


if __name__ == "__main__":
    main()
