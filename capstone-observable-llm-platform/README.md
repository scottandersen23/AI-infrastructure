# Capstone: Observable Local LLM Platform

The capstone combines the prior AI Infrastructure Learning Lab phases into one production-style local platform. It accepts user requests through an API gateway, retrieves document context, calls a local/mock LLM service, processes async jobs, records AI reliability metrics, benchmarks inference behavior, and ships with Docker and Kubernetes deployment assets.

## Architecture

```text
Client
  -> API Gateway
      -> RAG Service
          -> Postgres / pgvector-style retrieval layer
          -> Sample document store
      -> LLM Service
      -> Redis Queue
      -> Worker
      -> Observability Dashboard
```

## Capstone Deliverables

| Deliverable                  | Location                                                            |
| ---------------------------- | ------------------------------------------------------------------- |
| Full source code             | `api/`, `worker/`, `llm-service/`, `rag-service/`, `observability/` |
| Docker Compose setup         | `docker-compose.yml`                                                |
| Kubernetes deployment files  | `kubernetes/manifests/`                                             |
| Architecture diagrams        | `diagrams/capstone-architecture.md`                                 |
| Benchmark report             | `benchmarks/benchmark-report.md`                                    |
| Observability dashboard docs | `docs/observability-dashboard.md`, `docs/screenshots/`              |
| Technical writeup            | `article/observable-local-llm-platform-article.md`                  |
| LinkedIn project summary     | `article/linkedin-summary.md`                                       |
| GitHub documentation         | This README and linked docs                                         |

## Quick Start

### Option 1: Run with Docker Compose

```bash
cd AI-infrastructure/capstone-observable-llm-platform
docker compose up --build
```

Services:

- API Gateway: `http://localhost:8010`
- LLM Service: `http://localhost:8011`
- RAG Service: `http://localhost:8012`
- Observability Dashboard: `http://localhost:8013/dashboard`

### Option 2: Run API Locally

```bash
cd AI-infrastructure/capstone-observable-llm-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
PYTHONPATH=. uvicorn api.app.main:app --reload --port 8010
```

When running only the API gateway, the gateway uses local fallback implementations for RAG, LLM, and observability so the core flow can still be tested.

## Core API Flow

```bash
curl -s http://localhost:8010/health | python3 -m json.tool
```

```bash
curl -s -X POST http://localhost:8010/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I operate a reliable local LLM platform?"}' \
  | python3 -m json.tool
```

```bash
curl -s -X POST http://localhost:8010/jobs \
  -H "Content-Type: application/json" \
  -d '{"task_type":"rag_summary","payload":{"topic":"AI platform reliability"}}' \
  | python3 -m json.tool
```

```bash
curl -s http://localhost:8010/metrics/summary | python3 -m json.tool
```

Open the dashboard:

```text
http://localhost:8010/dashboard
```

## Endpoints

| Endpoint               | Purpose                                         |
| ---------------------- | ----------------------------------------------- |
| `GET /health`          | Validate gateway and dependency configuration   |
| `POST /ask`            | Run source-grounded RAG + LLM answer generation |
| `POST /jobs`           | Submit async AI jobs                            |
| `GET /jobs/{job_id}`   | Check job status                                |
| `GET /metrics/summary` | View aggregate AI reliability metrics           |
| `GET /metrics/events`  | View recent request-level events                |
| `GET /dashboard`       | HTML dashboard for local observability          |
| `GET /docs`            | OpenAPI / Swagger UI                            |

## Kubernetes

Local Kubernetes manifests live in `kubernetes/manifests/` and include namespace, config, secrets example, Postgres, Redis, API, worker, LLM service, RAG service, observability service, ingress, autoscaling, and network policies.

```bash
kubectl apply -f kubernetes/manifests/
kubectl -n capstone-ai-platform get pods,svc,ingress,hpa
```

## What This Demonstrates

- API gateway and service boundaries
- RAG retrieval over local documents
- Local/mock LLM serving
- Async worker orchestration
- AI observability for latency, tokens, retrieval hit rate, and quality score
- Benchmarking and bottleneck analysis
- Dockerized local development
- Kubernetes deployment readiness
- Public technical documentation
