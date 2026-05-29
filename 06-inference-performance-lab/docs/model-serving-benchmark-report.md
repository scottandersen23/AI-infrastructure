# Model-Serving Benchmark Report

Phase 6 deliverable for comparing model-serving behavior under different workload shapes.

## Benchmark Dimensions

| Dimension     | Why It Matters                                                     |
| ------------- | ------------------------------------------------------------------ |
| Concurrency   | Reveals queuing and saturation behavior                            |
| Output length | Drives decode latency and throughput                               |
| Prompt length | Drives prefill latency and KV cache memory                         |
| Quantization  | Changes memory use, speed, and quality                             |
| Runtime       | Ollama, llama.cpp, vLLM, and TGI make different batching tradeoffs |
| Hardware      | CPU, Apple Silicon, and NVIDIA GPUs have different bottlenecks     |

## Runtime Comparison Notes

| Runtime   | Best Use                                       | Benchmark Focus                               |
| --------- | ---------------------------------------------- | --------------------------------------------- |
| Ollama    | Local development and simple model management  | Single-user latency and streaming UX          |
| llama.cpp | Quantization and CPU/Apple Silicon experiments | Threads, batch size, GGUF quantization        |
| vLLM      | High-throughput GPU serving                    | Concurrent requests, paged KV cache, batching |
| TGI       | Production Hugging Face serving                | GPU utilization, batching, metrics            |

## Benchmark Procedure

1. Start the target model server.
2. Run the same prompt set across multiple concurrency levels.
3. Record p50, p95, requests/sec, generated tokens/sec, and error rate.
4. Repeat with short and long output lengths.
5. Repeat with at least two quantization levels or model sizes.
6. Compare throughput and p95 latency, not just average latency.

## Results Template

| Runtime   | Model                | Quantization    | Concurrency | p50 Latency | p95 Latency | Tokens/sec | Notes                      |
| --------- | -------------------- | --------------- | ----------: | ----------: | ----------: | ---------: | -------------------------- |
| Mock API  | mock-inference-model | N/A             |           4 |         TBD |         TBD |        TBD | Use for script validation  |
| Ollama    | llama3.2:3b          | Runtime default |           4 |         TBD |         TBD |        TBD | Phase 3 wrapper target     |
| llama.cpp | GGUF local model     | Q5              |           4 |         TBD |         TBD |        TBD | Quantization experiment    |
| vLLM      | GPU model            | FP16/AWQ        |          16 |         TBD |         TBD |        TBD | Production serving concept |

## Key Questions

- At what concurrency does queue wait become visible?
- Does longer output length scale latency linearly?
- Does prompt length increase prefill time enough to hurt UX?
- Does quantization improve throughput without unacceptable quality loss?
- Is throughput limited by API overhead, model runtime, memory, or hardware?
