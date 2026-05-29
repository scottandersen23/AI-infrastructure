# Load Test Results

Phase 6 deliverable for recording concurrent inference load tests.

## How To Run

Start the mock inference API:

```bash
cd 06-inference-performance-lab
uvicorn api.app.main:app --reload --port 8004
```

Run a load test:

```bash
python scripts/load_test.py \
  --api-url http://localhost:8004 \
  --concurrency 4 \
  --requests 16 \
  --max-tokens 128
```

The script writes JSON and CSV files to `results/`, which is ignored by git.

## Baseline Test Matrix

| Scenario       | Concurrency | Requests | Max Tokens | Purpose                          |
| -------------- | ----------: | -------: | ---------: | -------------------------------- |
| Baseline       |           1 |        8 |        128 | Single-user latency              |
| Moderate load  |           4 |       16 |        128 | Match default server concurrency |
| Queue pressure |           8 |       32 |        128 | Observe queue wait growth        |
| Long output    |           4 |       16 |        512 | Test generation-bound workload   |
| Prompt-heavy   |           4 |       16 |         64 | Test prompt evaluation cost      |

## Metrics Captured

| Metric          | Meaning                                      |
| --------------- | -------------------------------------------- |
| Client latency  | End-to-end HTTP latency from the load tester |
| Server latency  | Server-side request latency                  |
| Queue wait      | Time waiting for an inference slot           |
| Prompt eval     | Simulated prompt processing time             |
| Generation time | Simulated token generation time              |
| Tokens/sec      | Completion throughput per request            |
| Estimated VRAM  | Approximate KV cache pressure                |

## Sample Summary Shape

```json
{
  "requests": 16,
  "elapsed_seconds": 10.2,
  "requests_per_second": 1.57,
  "generated_tokens_per_second": 200.78,
  "avg_latency_ms": 2530.4,
  "p50_latency_ms": 2310.2,
  "p95_latency_ms": 4610.9,
  "max_latency_ms": 4702.1,
  "avg_queue_wait_ms": 580.4,
  "max_queue_wait_ms": 2300.7,
  "concurrency": 4,
  "max_tokens": 128
}
```

## Interpretation

- If p95 latency increases but generation time is stable, queuing is likely the bottleneck.
- If generation time dominates, output length, model size, or hardware acceleration is the bottleneck.
- If prompt evaluation dominates, context length or prefill efficiency is the bottleneck.
- If estimated VRAM approaches the hardware limit, reduce context length, batch size, or model size.
