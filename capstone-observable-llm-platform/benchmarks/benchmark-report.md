# Capstone Benchmark Report

## Purpose

This report documents how to evaluate the Observable Local LLM Platform under load. The goal is to measure the user-facing `/ask` path across retrieval, model generation, token accounting, and metrics recording.

## Test Command

```bash
python benchmarks/load_test.py \
  --base-url http://localhost:8010 \
  --requests 20 \
  --concurrency 5
```

## Metrics Captured

| Metric               | Why It Matters                    |
| -------------------- | --------------------------------- |
| Average latency      | Typical user-facing response time |
| P95 latency          | Tail latency under concurrency    |
| Requests per second  | Platform throughput               |
| Error count          | Reliability under load            |
| Average total tokens | Cost and model-serving pressure   |

## Expected Local Baseline

The default mock LLM and hash retrieval path should produce low latency on a laptop because no real model inference occurs. In a production model-serving setup, the expected bottleneck would shift toward model latency, GPU memory, queue depth, and token throughput.

## Bottleneck Interpretation

- High retrieval latency points to vector store, chunk volume, or embedding bottlenecks.
- High model latency points to inference runtime, token generation, batching, or hardware limits.
- High API latency with low retrieval/model latency points to gateway overhead or metrics storage.
- Rising error counts under concurrency point to dependency saturation or missing backpressure.
- Rising token counts increase model-serving cost and can affect latency.

## Optimization Ideas

- Cache embeddings for repeated queries.
- Tune chunk size and retrieval limit.
- Add request queueing and concurrency limits to the LLM service.
- Use custom autoscaling metrics such as queue depth, p95 latency, or GPU utilization.
- Move observability writes to a non-blocking pipeline for high-volume production traffic.
