# API Documentation

REST API for submitting background jobs, tracking status, and checking service health.

**Base URL (local):** `http://localhost:8000`

**Interactive docs:**

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- OpenAPI JSON: [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

## Authentication

No authentication in this learning-lab version. Production deployments should add API keys, JWT, or mTLS before exposing the service.

---

## Endpoints

### Health Check

```http
GET /health
```

Verifies PostgreSQL and Redis connectivity.

**200 OK**

```json
{
  "status": "ok",
  "postgres": "ok",
  "redis": "ok"
}
```

**503 Service Unavailable** — one or more dependencies are unreachable.

---

### Create Job

```http
POST /jobs
Content-Type: application/json
```

Submit a background job. The API validates the payload, persists a job record, and enqueues the job ID to Redis.

**202 Accepted**

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "type": "word_count",
  "status": "queued",
  "payload": { "text": "hello async world" },
  "result": null,
  "error": null,
  "created_at": "2026-05-24T12:00:00Z",
  "updated_at": "2026-05-24T12:00:00Z",
  "started_at": null,
  "completed_at": null
}
```

**422 Unprocessable Entity** — invalid job type or payload.

**503 Service Unavailable** — job record created but Redis enqueue failed.

#### Job Types

| Type           | Payload fields                         | Worker output                   |
| -------------- | -------------------------------------- | ------------------------------- |
| `word_count`   | `text` (string, 1–100000 chars)        | `word_count`, `character_count` |
| `reverse_text` | `text` (string, 1–100000 chars)        | `original`, `reversed`          |
| `slow_task`    | `seconds` (1–30), `message` (optional) | `message`, `slept_seconds`      |

#### Example Requests

**Word count**

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"word_count","payload":{"text":"hello async world"}}'
```

**Reverse text**

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"reverse_text","payload":{"text":"infrastructure"}}'
```

**Slow task (simulates long-running work)**

```bash
curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"slow_task","payload":{"seconds":5,"message":"embedding simulation"}}'
```

---

### Get Job Status

```http
GET /jobs/{job_id}
```

Poll job status until `completed` or `failed`.

**200 OK**

```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "type": "word_count",
  "status": "completed",
  "payload": { "text": "hello async world" },
  "result": { "word_count": 3, "character_count": 17 },
  "error": null,
  "created_at": "2026-05-24T12:00:00Z",
  "updated_at": "2026-05-24T12:00:05Z",
  "started_at": "2026-05-24T12:00:01Z",
  "completed_at": "2026-05-24T12:00:05Z"
}
```

**404 Not Found** — job ID does not exist.

#### Job Status Lifecycle

```text
pending -> queued -> running -> completed
                            \-> failed
```

| Status      | Meaning                            |
| ----------- | ---------------------------------- |
| `pending`   | Record created, not yet enqueued   |
| `queued`    | Waiting in Redis for a worker      |
| `running`   | Worker is processing the job       |
| `completed` | Result available in `result`       |
| `failed`    | Error message available in `error` |

---

### List Recent Jobs

```http
GET /jobs?limit=20
```

Returns the most recent jobs (default limit: 20, max: 100).

**200 OK** — array of job objects (same schema as `GET /jobs/{job_id}`).

---

## Error Response Format

FastAPI returns validation errors in this shape:

```json
{
  "detail": "Invalid payload for job type 'word_count': ..."
}
```

---

## Typical Client Flow

```bash
# 1. Submit job
JOB=$(curl -s -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"type":"word_count","payload":{"text":"one two three four"}}')

JOB_ID=$(echo "$JOB" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")

# 2. Poll until complete
curl -s "http://localhost:8000/jobs/$JOB_ID"
```

For production clients, use exponential backoff instead of tight polling loops.

---

## Related Documentation

- [Project README](../README.md) — local setup and architecture overview
- [Architecture Diagram](../diagrams/architecture.md) — system component diagram
