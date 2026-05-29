# Before/After Optimization Notes

Phase 6 deliverable for documenting performance changes and measured impact.

## Optimization Log Template

| Experiment                 | Before          | Change                               | After           | Result                                           |
| -------------------------- | --------------- | ------------------------------------ | --------------- | ------------------------------------------------ |
| Lower max output tokens    | p95 TBD         | Reduce `max_tokens` from 512 to 128  | p95 TBD         | Expected lower decode latency                    |
| Reduce retrieved context   | Prompt eval TBD | Lower retrieved chunks from 5 to 3   | Prompt eval TBD | Expected lower prefill latency                   |
| Increase concurrency slots | Queue wait TBD  | Raise server concurrency from 4 to 8 | Queue wait TBD  | Helps only if hardware has headroom              |
| Quantize model             | VRAM TBD        | Move FP16 to Q4/Q5                   | VRAM TBD        | Expected lower memory, possible quality tradeoff |
| Enable batching            | Throughput TBD  | Batch compatible requests            | Throughput TBD  | Expected higher tokens/sec                       |

## Optimization Patterns

### Reduce Output Length

Before:

- High generation time
- Linear latency growth with `max_tokens`

Change:

- Lower default max tokens
- Add answer-length guidance in prompts
- Stream partial responses for better perceived latency

Expected after:

- Lower p95 latency
- Lower total tokens
- Similar first-token latency

### Reduce Prompt Length

Before:

- Prompt evaluation dominates
- RAG prompts include too many chunks

Change:

- Lower retrieved chunk count
- Use smaller chunks
- Add reranking or context compression

Expected after:

- Lower prefill latency
- Lower KV cache memory
- Possible quality impact if relevant context is removed

### Tune Concurrency

Before:

- Queue wait increases under load

Change:

- Increase worker/model replicas
- Increase concurrency only when hardware has available memory and compute
- Add admission control when saturated

Expected after:

- Higher throughput
- Lower queue wait until the next bottleneck appears

### Quantize Model

Before:

- VRAM pressure limits concurrency

Change:

- Use Q4/Q5/AWQ/GPTQ depending on runtime

Expected after:

- Lower memory footprint
- Potentially higher throughput
- Possible quality regression, which must be evaluated

## Reporting Standard

Each optimization should include:

- Workload description
- Runtime and model
- Hardware notes
- Concurrency
- Prompt/output length
- p50 and p95 latency
- Generated tokens/sec
- Error rate
- Quality or response review notes
