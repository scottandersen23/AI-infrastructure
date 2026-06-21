# 08. Tool Registry and Execution Layer

Structured tool registry and executor for Phase 2 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Make tools first-class platform infrastructure so LLMs can invoke structured, observable, auditable functions instead of generating free-form text only.

## Stack

| Layer            | Technology                                  |
| ---------------- | ------------------------------------------- |
| Registry API     | FastAPI + Uvicorn                           |
| Executor service | FastAPI + Uvicorn                           |
| Database         | PostgreSQL 16                               |
| Tool schemas     | JSON Schema                                 |
| Tracing          | OpenTelemetry (console exporter by default) |
| Orchestration    | Docker Compose                              |

## Project Structure

```text
08-tool-registry/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # Registry CRUD + tool listing for LLM binding
│       ├── config.py            # Environment settings
│       ├── database.py          # Postgres connection and schema init
│       ├── schemas.py           # Pydantic API models
│       └── registry.py          # Tool registration and lookup
├── executor/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py              # Tool invocation endpoint
│       ├── config.py            # Environment settings
│       ├── schemas.py           # Invoke request/response models
│       └── handlers/            # Built-in tool implementations
│           ├── __init__.py
│           ├── search_docs.py   # Wraps RAG retrieval (stub)
│           ├── get_metrics.py   # Wraps observability metrics (stub)
│           └── get_job_status.py# Wraps async job lookup (stub)
├── tools/
│   └── README.md                # Built-in tool catalog and schema notes
├── sql/
│   └── init.sql                 # Registry tables and audit log
├── docs/
│   └── architecture.md          # Tool lifecycle and service boundaries
├── diagrams/
│   └── architecture.md          # Component and sequence diagrams
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2)
- Optional: Phase 1 capstone or RAG service running for live `search_docs` integration
- Optional: `curl` for testing endpoints

## Quick Start

### 1. Start the stack

From this directory:

```bash
cd 08-tool-registry
docker compose up --build
```

Wait until all services report healthy. Services:

- Registry API: `http://localhost:8008`
- Executor service: `http://localhost:8009`

### 2. Verify health

```bash
curl -s http://localhost:8008/health | python3 -m json.tool
curl -s http://localhost:8009/health | python3 -m json.tool
```

### 3. List registered tools (for LLM binding)

```bash
curl -s http://localhost:8008/tools | python3 -m json.tool
```

### 4. Invoke a tool

```bash
curl -s -X POST http://localhost:8009/invoke \
  -H "Content-Type: application/json" \
  -d '{"tool_name":"search_docs","arguments":{"query":"AI platform reliability","limit":3}}' \
  | python3 -m json.tool
```

## Endpoints

### Registry API (`:8008`)

| Endpoint            | Purpose                                     |
| ------------------- | ------------------------------------------- |
| `GET /health`       | Validate registry and Postgres connectivity |
| `GET /tools`        | List tools with JSON Schema for LLM binding |
| `GET /tools/{name}` | Get a single tool definition                |
| `POST /tools`       | Register or update a tool schema            |
| `GET /docs`         | OpenAPI / Swagger UI                        |

### Executor Service (`:8009`)

| Endpoint       | Purpose                                          |
| -------------- | ------------------------------------------------ |
| `GET /health`  | Validate executor and downstream configuration   |
| `POST /invoke` | Validate arguments and execute a registered tool |
| `GET /docs`    | OpenAPI / Swagger UI                             |

## Built-in Tools (Initial)

| Tool             | Purpose                      | Status |
| ---------------- | ---------------------------- | ------ |
| `search_docs`    | RAG document retrieval       | Stub   |
| `get_metrics`    | Platform reliability metrics | Stub   |
| `get_job_status` | Async job status lookup      | Stub   |

See [tools/README.md](./tools/README.md) for schema definitions and integration notes.

## Architecture

```text
LLM (function calling)
  -> Registry API (list / validate schemas)
  -> Executor service (invoke handler)
      -> Built-in tool handler
      -> [optional] Phase 1 service (RAG, metrics, jobs)
  -> Structured result + audit log entry
  -> OpenTelemetry span (tool.name, latency, success)
```

Detailed diagrams: [diagrams/architecture.md](./diagrams/architecture.md)

## Local Development (without Docker)

```bash
cd 08-tool-registry
python3 -m venv .venv
source .venv/bin/activate
pip install -r api/requirements.txt

# Terminal 1 — registry
DATABASE_URL=postgresql://tools:tools@localhost:5434/tools \
  uvicorn api.app.main:app --reload --port 8008

# Terminal 2 — executor
REGISTRY_URL=http://localhost:8008 \
  uvicorn executor.app.main:app --reload --port 8009
```

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed. Key settings:

| Variable          | Default                                        | Description                   |
| ----------------- | ---------------------------------------------- | ----------------------------- |
| `DATABASE_URL`    | `postgresql://tools:tools@postgres:5432/tools` | Registry Postgres connection  |
| `REGISTRY_URL`    | `http://registry:8008`                         | Executor → registry base URL  |
| `RAG_SERVICE_URL` | `http://host.docker.internal:8012`             | Optional RAG integration      |
| `METRICS_URL`     | `http://host.docker.internal:8013`             | Optional metrics integration  |
| `OTEL_EXPORTER`   | `console`                                      | OpenTelemetry exporter target |

## Deliverables Checklist

- [ ] Tool schema registry with Postgres persistence
- [ ] Executor service with argument validation
- [ ] Three built-in tools (stub → live integration)
- [ ] OpenTelemetry spans on tool invocation
- [ ] Audit log for tool calls
- [ ] Architecture documentation
- [ ] Docker Compose local development stack
- [ ] Technical writeup and benchmark notes

## What This Demonstrates

- Tools as first-class platform infrastructure
- JSON Schema registration and LLM function-calling compatibility
- Separation of registry (schema) and executor (runtime) concerns
- Foundation for Projects 09–14 (ReAct, DAG, multi-agent, data tools)

## Next Project

Project 09 (Single-Agent ReAct Loop) will consume this tool layer to run bounded plan → act → observe loops over registered tools.
