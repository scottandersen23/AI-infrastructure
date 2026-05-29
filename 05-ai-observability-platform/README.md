# 05. AI Observability Platform

Instrumented AI API for Phase 5 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Instrument an AI application so model behavior, latency, failures, token usage, retrieval behavior, and response quality can be traced and monitored.

## Stack

| Layer            | Technology                               |
| ---------------- | ---------------------------------------- |
| API              | FastAPI + Uvicorn                        |
| Tracing          | OpenTelemetry                            |
| Trace viewer     | Arize Phoenix via OTLP                   |
| Local metrics    | SQLite                                   |
| Dashboard        | Built-in HTML dashboard + dashboard spec |
| Reliability docs | Markdown report                          |

## Project Structure

```text
05-ai-observability-platform/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # FastAPI routes
│       ├── ai_pipeline.py       # Instrumented AI workflow
│       ├── telemetry.py         # OpenTelemetry setup
│       ├── metrics_store.py     # Local reliability metrics
│       ├── dashboard.py         # HTML dashboard renderer
│       ├── schemas.py           # API models
│       └── config.py            # Environment settings
├── dashboards/
│   └── ai-observability-dashboard.json
├── docs/
│   ├── ai-reliability-report.md
│   ├── observability-dashboard.md
│   ├── opentelemetry-traces.md
│   └── phoenix-integration.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## Quick Start

### 1. Run with console traces

```bash
cd 05-ai-observability-platform
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt
OTEL_EXPORTER=console uvicorn api.app.main:app --reload --port 8003
```

### 2. Send an instrumented request

```bash
curl -s -X POST http://localhost:8003/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How should I monitor a RAG API?"}' \
  | python3 -m json.tool
```

### 3. View metrics

```bash
curl -s http://localhost:8003/metrics/summary | python3 -m json.tool
curl -s http://localhost:8003/metrics/events | python3 -m json.tool
```

Open the dashboard:

```text
http://localhost:8003/dashboard
```

## Phoenix Trace Viewer

Run the API and Phoenix together:

```bash
docker compose up --build
```

Open Phoenix:

```text
http://localhost:6006
```

The API exports traces to Phoenix using OTLP at `http://phoenix:4317`.

## API Endpoints

| Endpoint               | Purpose                                        |
| ---------------------- | ---------------------------------------------- |
| `GET /health`          | Check API, exporter, and metrics configuration |
| `POST /ask`            | Run the instrumented AI workflow               |
| `GET /metrics/summary` | Aggregate reliability metrics                  |
| `GET /metrics/events`  | Recent request-level metric events             |
| `GET /dashboard`       | Local observability dashboard                  |
| `GET /docs`            | Swagger UI                                     |

## Metrics Captured

| Metric             | Description                                    |
| ------------------ | ---------------------------------------------- |
| Request latency    | Total `/ask` time                              |
| Retrieval latency  | Time spent fetching context                    |
| Model latency      | Time spent generating answer text              |
| Token usage        | Prompt, completion, and total tokens           |
| Error rate         | Failed requests over total requests            |
| Retrieval hit rate | Requests with at least one source              |
| Quality score      | Simple heuristic for grounded response quality |

## Deliverables

| Deliverable             | Location                                                                                                                                                                           |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Instrumented AI API     | `api/app/main.py`, `api/app/ai_pipeline.py`                                                                                                                                        |
| OpenTelemetry traces    | `api/app/telemetry.py`, [docs/opentelemetry-traces.md](./docs/opentelemetry-traces.md)                                                                                             |
| Phoenix integration     | [docs/phoenix-integration.md](./docs/phoenix-integration.md), `docker-compose.yml`                                                                                                 |
| Observability dashboard | `GET /dashboard`, [docs/observability-dashboard.md](./docs/observability-dashboard.md), [dashboards/ai-observability-dashboard.json](./dashboards/ai-observability-dashboard.json) |
| AI reliability report   | [docs/ai-reliability-report.md](./docs/ai-reliability-report.md)                                                                                                                   |

## Related Projects

- [Phase 3 Local LLM Serving Lab](../03-local-llm-serving-lab/README.md)
- [Phase 4 RAG Document Assistant](../04-rag-document-assistant/README.md)
