# Observable Local LLM Platform Architecture

The capstone platform turns the first seven learning lab phases into one integrated system. The API gateway is the user-facing boundary. It retrieves document context, calls the LLM service, submits async jobs, records reliability metrics, and exposes dashboard endpoints.

## Service Responsibilities

| Service       | Responsibility                                                             |
| ------------- | -------------------------------------------------------------------------- |
| API Gateway   | Request validation, RAG orchestration, LLM calls, jobs, metrics, dashboard |
| RAG Service   | Document chunk loading and deterministic retrieval                         |
| LLM Service   | Mock model serving boundary with token accounting                          |
| Worker        | Redis-backed async job execution                                           |
| Postgres      | Durable state and pgvector-ready storage                                   |
| Redis         | Queue coordination                                                         |
| Observability | Dashboard boundary and reliability documentation                           |

## Key Design Decisions

- Keep API, retrieval, model serving, worker, and observability boundaries separate.
- Provide local fallbacks so the gateway can run without Docker during development.
- Return source chunks, retrieval scores, token usage, latency, and quality fields from `/ask`.
- Use Docker Compose for full local integration and Kubernetes manifests for production-style deployment shape.
- Treat benchmark and dashboard artifacts as first-class deliverables, not afterthoughts.
