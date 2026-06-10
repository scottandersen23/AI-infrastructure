I built a Local LLM Serving Lab as part of my AI infrastructure learning path.

The goal: move beyond “I can run a model locally” and start treating local inference like infrastructure.

This project wraps local model runtimes behind a FastAPI service and includes:
- A local LLM API wrapper
- Ollama integration plus a mock runtime for smoke tests
- Non-streaming and streaming generation endpoints
- Model comparison notes for Ollama, llama.cpp, TGI, and vLLM concepts
- Benchmark tooling for latency and tokens/sec
- A latency and throughput report template

The biggest takeaway: model serving is not just about generating text. It is about API design, streaming UX, runtime tradeoffs, token throughput, quantization, context windows, and repeatable measurement.

This lab creates a foundation for the next layers: RAG, observability, performance testing, and Kubernetes deployment.

#LLM #AIInfrastructure #FastAPI #Ollama #ModelServing #LocalAI #MachineLearning #BackendEngineering
