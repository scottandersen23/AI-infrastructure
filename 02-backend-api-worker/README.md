# 02. Backend API + Async Worker System

Production-style backend service with async job processing — Phase 2 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Build a reliable, containerized backend that separates synchronous API requests from long-running background work using a queue-based worker pattern.

## Stack

| Layer         | Technology                         |
| ------------- | ---------------------------------- |
| API           | FastAPI + Uvicorn                  |
| Worker        | Python (Redis consumer loop)       |
| Queue         | Redis                              |
| Database      | PostgreSQL                         |
| Orchestration | Docker Compose                     |
| API docs      | OpenAPI / Swagger (auto-generated) |
| Logging       | structlog (JSON)                   |

---

## Project Structure

```text
02-backend-api-worker/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # FastAPI routes
│       ├── schemas.py       # Pydantic models
│       ├── validation.py    # Job payload validation
│       └── queue.py         # Redis enqueue helper
├── worker/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py          # Queue consumer loop
│       └── tasks.py         # Job handlers
├── shared/
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   └── logging_config.py
├── docs/
│   └── API.md               # REST API reference
├── diagrams/
│   └── architecture.md      # System architecture diagram
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2)
- Optional: `curl` for testing endpoints

---

## Quick Start

### 1. Start the stack

From this directory:

```bash
cd 02-backend-api-worker
docker compose up --build
```

Wait until all services report healthy. The API will be available at **http://localhost:8000**.

### 2. Verify health

```bash
curl -s http://localhost:8000/health | python3 -m json.tool
```

Expected:

```json
{
  "status": "ok",
  "postgres": "ok",
  "redis": "ok"
}
```

### 3. Submit a background job

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"word_count","payload":{"text":"hello async world"}}' \
  | python3 -m json.tool
```

### 4. Poll job status

Copy the `id` from the response:

```bash
curl -s http://localhost:8000/jobs/<JOB_ID> | python3 -m json.tool
```

When `status` is `completed`, the `result` field contains the output.

### 5. Open interactive API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

---

## Job Types

| Type           | Purpose                    | Example payload                     |
| -------------- | -------------------------- | ----------------------------------- |
| `word_count`   | Count words and characters | `{"text": "hello world"}`           |
| `reverse_text` | Reverse a string           | `{"text": "infrastructure"}`        |
| `slow_task`    | Simulate long-running work | `{"seconds": 5, "message": "test"}` |

---

## How It Works

1. Client sends `POST /jobs` with a job type and payload.
2. API validates input and writes a job record to PostgreSQL (`pending`).
3. API pushes the job ID to the Redis queue and updates status to `queued`.
4. Worker blocks on `BRPOP`, picks up the job ID, and sets status to `running`.
5. Worker executes the task handler and writes `result` or `error` to PostgreSQL.
6. Client polls `GET /jobs/{id}` until status is `completed` or `failed`.

See [diagrams/architecture.md](./diagrams/architecture.md) for sequence and component diagrams.

---

## Services

| Service    | Port | Description              |
| ---------- | ---: | ------------------------ |
| `api`      | 8000 | FastAPI REST service     |
| `worker`   |    — | Background job processor |
| `postgres` | 5432 | Job persistence          |
| `redis`    | 6379 | Job queue                |

---

## Environment Variables

Copy `.env.example` to `.env` for local (non-Docker) development:

| Variable       | Default                                    | Description           |
| -------------- | ------------------------------------------ | --------------------- |
| `DATABASE_URL` | `postgresql://app:app@localhost:5432/jobs` | PostgreSQL connection |
| `REDIS_URL`    | `redis://localhost:6379/0`                 | Redis connection      |
| `QUEUE_NAME`   | `job_queue`                                | Redis list name       |
| `LOG_LEVEL`    | `INFO`                                     | Log verbosity         |

Docker Compose overrides these for container networking automatically.

---

## Useful Commands

```bash
# Start in background
docker compose up -d --build

# View logs (all services)
docker compose logs -f

# View API logs only
docker compose logs -f api

# View worker logs only
docker compose logs -f worker

# Stop and remove containers
docker compose down

# Stop and remove containers + database volume
docker compose down -v
```

---

## Deliverables

| Deliverable                    | Location                                               |
| ------------------------------ | ------------------------------------------------------ |
| Dockerized backend application | `api/`, `docker-compose.yml`                           |
| Queue-based worker system      | `worker/`, Redis queue in `shared/config.py`           |
| API documentation              | [docs/API.md](./docs/API.md), `/docs`, `/redoc`        |
| Architecture diagram           | [diagrams/architecture.md](./diagrams/architecture.md) |
| Local setup README             | This file                                              |

---

## Features Implemented

- REST API endpoints (`POST /jobs`, `GET /jobs/{id}`, `GET /jobs`)
- Request validation (Pydantic per job type)
- Background job submission via Redis queue
- Async task processing in dedicated worker
- Job status tracking in PostgreSQL
- Error handling (validation, enqueue failures, task failures)
- Docker Compose local development environment
- Health checks for all services
- Structured JSON logging

---

## Troubleshooting

| Issue                        | Fix                                                                     |
| ---------------------------- | ----------------------------------------------------------------------- |
| API returns 503 on `/health` | Wait for Postgres/Redis health checks; run `docker compose ps`          |
| Job stuck in `queued`        | Check worker logs: `docker compose logs worker`                         |
| Port 8000 already in use     | Stop conflicting service or change port mapping in `docker-compose.yml` |
| Database schema issues       | Reset volumes: `docker compose down -v && docker compose up --build`    |

---

## Next Steps

This project lays the foundation for later phases:

- **Phase 3** — replace task handlers with LLM inference jobs
- **Phase 4** — add OpenTelemetry traces across API and worker
- **Phase 5** — benchmark worker throughput under load
- **Phase 7** — deploy API + worker to Kubernetes

---

## Related Phase 1 Notes

- [Distributed Systems Notes](../01-systems-foundations/distributed-systems-notes.md)
- [Networking Request Lifecycle](../01-systems-foundations/diagrams/networking-request-lifecycle.md)
- [DDIA Architecture Breakdowns](../01-systems-foundations/ddia-architecture-breakdowns.md)
