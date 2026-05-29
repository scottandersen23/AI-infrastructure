# Latency and Throughput Report

Phase 3 deliverable for explaining how to interpret local LLM serving performance.

## Summary

Local LLM performance depends on model size, quantization, prompt length, output length, runtime, and hardware. A useful benchmark report should avoid a single "fast or slow" judgment and instead separate:

- **End-to-end latency:** How long the full API request takes.
- **First-token latency:** How quickly streaming starts.
- **Throughput:** How many completion tokens the runtime generates per second.
- **Quality:** Whether the output is good enough for the use case.

## Serving Path

```text
Client
  -> FastAPI wrapper
      -> Local runtime (Ollama / llama.cpp / TGI / vLLM)
          -> Model weights + tokenizer
      <- Generated tokens
  <- JSON response or streamed text chunks
```

## What Each Metric Tells You

| Metric              | Good For                 | Caveat                                          |
| ------------------- | ------------------------ | ----------------------------------------------- |
| End-to-end latency  | API user experience      | Includes HTTP and client overhead               |
| First-token latency | Chat and streaming UX    | Not captured by simple non-streaming benchmarks |
| Tokens/sec          | Model throughput         | Usually excludes prompt evaluation              |
| Prompt tokens/sec   | Long-context performance | Runtime support varies                          |
| Memory use          | Capacity planning        | Must be measured outside this API wrapper       |

## Expected Bottlenecks

### Model Size

Larger models usually improve reasoning quality but require more memory and produce fewer tokens per second.

### Quantization

Lower-bit quantization reduces memory pressure and often improves speed, but may reduce output quality or instruction following.

### Context Window

Long prompts increase prompt evaluation time. A model can have high generation throughput and still feel slow if prompt processing dominates.

### Hardware

CPU inference is useful for learning and small models. GPU inference is usually required for higher throughput, larger models, and concurrent workloads.

## Reporting Template

| Question                                           | Answer                                            |
| -------------------------------------------------- | ------------------------------------------------- |
| Which model was fastest?                           | TBD after local benchmark run                     |
| Which model had the best quality/speed balance?    | TBD after comparing outputs                       |
| Did streaming improve perceived latency?           | TBD after streaming tests                         |
| Did quantization noticeably affect output quality? | TBD after Q4/Q5/Q8 comparison                     |
| What is the recommended default model?             | Start with `llama3.2:3b`; update after benchmarks |

## Recommended Test Plan

1. Run the mock runtime to verify the API and benchmark script.
2. Run Ollama with one small baseline model.
3. Add a larger model and compare latency, tokens/sec, and answer quality.
4. Repeat with different `max_tokens` values to see how output length affects total latency.
5. Test `/generate/stream` manually and note perceived first-token latency.

## Initial Recommendation

Use Ollama plus a small instruction model as the default local development path. Move to llama.cpp for deeper quantization experiments and use TGI or vLLM concepts when designing production serving architecture.
