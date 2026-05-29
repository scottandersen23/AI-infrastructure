# Bottleneck Analysis

Phase 6 deliverable for diagnosing where inference requests spend time.

## Request Timing Breakdown

```text
Client
  -> HTTP request
  -> API routing
  -> queue wait for inference slot
  -> prompt evaluation / prefill
  -> token generation / decode
  -> response serialization
  -> client receives answer
```

## Common Bottlenecks

| Bottleneck      | Signal                                         | Likely Cause                   | Fix                                                   |
| --------------- | ---------------------------------------------- | ------------------------------ | ----------------------------------------------------- |
| Queue wait      | `queue_wait_ms` rises with concurrency         | Server saturated               | Increase replicas, lower max tokens, add batching     |
| Prompt prefill  | `prompt_eval_ms` dominates                     | Long context windows           | Reduce retrieved chunks, compress context             |
| Decode speed    | `generation_ms` dominates                      | Model/hardware bound           | Smaller model, quantization, GPU acceleration         |
| Memory pressure | VRAM estimate approaches limit                 | KV cache growth                | Lower context, lower concurrency, use paged attention |
| API overhead    | Client latency much higher than server latency | Network or framework overhead  | Profile API path, reuse clients, reduce middleware    |
| Error rate      | Failures under load                            | Timeout or resource exhaustion | Backpressure, retries, queue limits                   |

## Diagnostic Method

1. Run baseline with concurrency 1.
2. Increase concurrency until p95 latency rises sharply.
3. Compare queue wait vs generation time.
4. Increase `max_tokens` to isolate decode cost.
5. Increase prompt length to isolate prefill cost.
6. Compare results across model sizes or quantization levels.

## How To Read Results

### Queue-Bound

Symptoms:

- p95 latency rises faster than p50.
- `queue_wait_ms` grows as concurrency increases.
- Per-request tokens/sec remains stable.

Interpretation: the model server has reached its concurrency limit.

### Decode-Bound

Symptoms:

- `generation_ms` dominates total latency.
- Longer `max_tokens` increases latency roughly linearly.
- Queue wait may be low at small concurrency.

Interpretation: the runtime is limited by token generation speed.

### Prefill-Bound

Symptoms:

- Long prompts create high latency even with short outputs.
- Retrieval-heavy prompts are slower than direct prompts.

Interpretation: context length, tokenization, and attention prefill are dominating.

### Memory-Bound

Symptoms:

- Concurrency causes instability or errors.
- Larger context windows fail first.
- GPU utilization may be low while memory is full.

Interpretation: KV cache or model weights exceed practical memory capacity.

## Profiling Tools

| Tool                     | Use                                |
| ------------------------ | ---------------------------------- |
| Python `cProfile`        | API-side CPU profiling             |
| `py-spy`                 | Low-overhead Python flame graphs   |
| Runtime metrics          | Model latency and token throughput |
| NVIDIA tools             | GPU utilization, memory, kernels   |
| OpenTelemetry            | Cross-service request timing       |
| k6/Locust/custom scripts | Load and concurrency pressure      |
