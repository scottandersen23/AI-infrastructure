# Phoenix Integration

Phase 5 deliverable for sending OpenTelemetry traces to Arize Phoenix.

## Local Flow

```text
FastAPI app
  -> OpenTelemetry spans
  -> OTLP gRPC exporter
  -> Phoenix collector on :4317
  -> Phoenix UI on :6006
```

## Run With Docker Compose

```bash
cd 05-ai-observability-platform
docker compose up --build
```

Open Phoenix:

```text
http://localhost:6006
```

Send a request:

```bash
curl -s -X POST http://localhost:8003/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How should I monitor a RAG API?"}' \
  | python3 -m json.tool
```

Expected trace spans:

- `POST /ask`
- `ai.request`
- `ai.retrieval`
- `ai.model.generate`
- `ai.quality.evaluate`

## Environment Variables

| Variable        | Local Value            | Purpose                                  |
| --------------- | ---------------------- | ---------------------------------------- |
| `OTEL_EXPORTER` | `otlp`                 | Enables OTLP trace export                |
| `OTLP_ENDPOINT` | `http://phoenix:4317`  | Sends spans to Phoenix in Docker Compose |
| `SERVICE_NAME`  | `ai-observability-api` | Service identity in traces               |
| `ENVIRONMENT`   | `local`                | Deployment environment attribute         |

## Console Fallback

For a no-container smoke test, use the console exporter:

```bash
OTEL_EXPORTER=console uvicorn api.app.main:app --reload --port 8003
```

Spans will print to stdout instead of being sent to Phoenix.
