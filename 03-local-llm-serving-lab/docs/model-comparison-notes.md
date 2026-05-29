# Model Comparison Notes

Phase 3 deliverable for comparing local LLM serving runtimes, model formats, and inference tradeoffs.

## Comparison Criteria

| Area           | What to Compare                         | Why It Matters                                                              |
| -------------- | --------------------------------------- | --------------------------------------------------------------------------- |
| Runtime        | Ollama, llama.cpp, TGI, vLLM            | Determines serving API, deployment shape, and acceleration features         |
| Model family   | Llama, Mistral, Phi, Gemma, Code models | Different models optimize for instruction following, coding, speed, or size |
| Quantization   | Q4, Q5, Q8, FP16                        | Smaller quantization reduces memory use but may affect quality              |
| Hardware       | CPU, Apple Silicon GPU, NVIDIA GPU      | Hardware determines throughput, concurrency, and cost                       |
| Context window | 4k, 8k, 32k+ tokens                     | Larger context enables long prompts but increases memory and latency        |
| Streaming      | Token streaming support                 | Improves perceived latency for chat and agent UX                            |
| Observability  | Timing and token counters               | Needed for latency, throughput, and capacity planning                       |

## Runtime Notes

### Ollama

Best for fast local experimentation. It exposes a simple HTTP API, handles model downloads, and supports streaming. It is a practical default for this lab because the API wrapper can call `/api/generate` and `/api/tags` without custom model loading code.

Tradeoffs:

- Easy model management and developer ergonomics
- Good fit for laptop labs and demos
- Less control over low-level inference parameters than direct llama.cpp
- Not designed as a high-concurrency production serving layer

### llama.cpp

Best for understanding the inference stack directly. It uses GGUF model files and supports many quantization levels. It is useful when the goal is to inspect CPU behavior, memory footprint, quantization quality, and platform-specific acceleration.

Tradeoffs:

- Strong CPU and Apple Silicon support
- Direct control over context, threads, batch sizes, and quantization
- Requires more manual setup than Ollama
- HTTP serving is available, but operational polish depends on how it is wrapped

### Hugging Face Text Generation Inference

Best for production-style GPU serving with Hugging Face models. TGI is built for optimized transformer serving, batching, metrics, and containerized deployments.

Tradeoffs:

- Strong GPU serving story
- Production-oriented metrics and batching
- Heavier local setup than Ollama
- More useful once the lab moves beyond laptop-only inference

### vLLM Concepts

vLLM is important because of PagedAttention and high-throughput serving patterns. Even if this lab does not run vLLM locally, its concepts matter for understanding why production LLM serving differs from single-request local inference.

Tradeoffs:

- Optimized for throughput and concurrent request serving
- Strong fit for GPU-backed APIs
- More operational complexity than simple local runtimes
- Best evaluated with realistic concurrent workloads

## Model Notes

| Model Class                     | Local Serving Fit              | Notes                                          |
| ------------------------------- | ------------------------------ | ---------------------------------------------- |
| Small instruction models, 1B-3B | Excellent laptop baseline      | Fast, cheap, useful for smoke tests            |
| Mid-size models, 7B-8B          | Good quality/speed tradeoff    | Often best for local assistant demos           |
| Code-focused models             | Useful for developer workflows | Benchmark with code prompts, not only prose    |
| Larger models, 13B+             | Hardware-dependent             | May need aggressive quantization or GPU memory |

## Quantization Notes

| Quantization | Expected Behavior                                     |
| ------------ | ----------------------------------------------------- |
| Q4           | Lowest memory, fastest startup, possible quality loss |
| Q5           | Better quality/memory balance for many local runs     |
| Q8           | Higher memory, closer to full precision behavior      |
| FP16         | GPU-oriented, high memory, stronger quality baseline  |

## Evaluation Prompts

Use a mix of prompt types:

- Explanation: "Explain quantization in local LLM serving."
- Systems reasoning: "Compare CPU and GPU inference for a local API."
- Code generation: "Write a Python function that streams tokens from an HTTP endpoint."
- Summarization: "Summarize this architecture in five bullets."
- Long-context behavior: Paste a README section and ask for a structured summary.

## Takeaways

- Ollama is the default runtime for this lab because it gives the shortest path to a working local API.
- llama.cpp is the best runtime for learning how quantization and hardware choices affect inference.
- TGI and vLLM are the bridge from local experiments to production-grade model serving.
- Benchmarks should separate first-token latency, total latency, and tokens/sec because each answers a different capacity question.
