# 09. Single-Agent ReAct Loop

Bounded agent runtime for Phase 2 of the [AI Infrastructure Learning Lab](../README.md).

## Goal

Replace single-shot RAG responses with an agent runtime that can plan, call registered tools, observe results, and synthesize a final answer under explicit iteration and timeout budgets.

## Stack

| Layer         | Technology                               |
| ------------- | ---------------------------------------- |
| Agent API     | FastAPI + Uvicorn                        |
| State store   | PostgreSQL 16                            |
| Tool registry | Project 08 registry API                  |
| Tool executor | Project 08 executor service              |
| Agent loop    | Deterministic ReAct scaffold (LLM-ready) |
| Orchestration | Docker Compose                           |

## Project Structure

```text
09-single-agent-react-loop/
├── api/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── __init__.py
│       ├── main.py              # FastAPI routes
│       ├── config.py            # Environment settings
│       ├── schemas.py           # Pydantic request/response models
│       ├── database.py          # Postgres connection and run persistence
│       ├── project08_client.py  # Registry and executor HTTP clients
│       └── agent.py             # Bounded ReAct-style runtime
├── sql/
│   └── init.sql                 # agent_runs and agent_steps tables
├── docs/
│   └── architecture.md          # Agent lifecycle and design notes
├── diagrams/
│   └── architecture.md          # Component and sequence diagrams
├── evals/
│   └── scripted-questions.md    # Initial evaluation prompts
├── docker-compose.yml
├── .env.example
└── README.md
```

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or Docker Engine + Compose v2)
- Project 08 running locally:
  - Registry API: `http://localhost:8008`
  - Executor service: `http://localhost:8009`
- Optional: Phase 1 capstone services running so Project 08 tools call live RAG, metrics, and jobs endpoints
- Optional: `curl` for testing endpoints

## Quick Start

### 1. Start Project 08

From the Project 08 directory:

```bash
cd ../08-tool-registry
docker compose up --build
```

### 2. Start Project 09

From this directory:

```bash
cd ../09-single-agent-react-loop
docker compose up --build
```

The agent API runs at `http://localhost:8014`.

### 3. Verify Health

```bash
curl -s http://localhost:8014/health | python3 -m json.tool
```

### 4. Run an Agent Request

```bash
curl -s -X POST http://localhost:8014/agent/run \
  -H "Content-Type: application/json" \
  -d '{"question":"Search the docs and summarize AI platform reliability metrics.","max_steps":3}' \
  | python3 -m json.tool
```

### 5. Inspect a Saved Run

```bash
curl -s http://localhost:8014/agent/runs/{run_id} | python3 -m json.tool
```

## Endpoints

| Endpoint               | Purpose                                      |
| ---------------------- | -------------------------------------------- |
| `GET /health`          | Validate agent runtime and dependencies      |
| `POST /agent/run`      | Run a bounded ReAct-style agent workflow     |
| `GET /agent/runs/{id}` | Retrieve an agent run and persisted steps    |
| `GET /tools`           | Proxy Project 08 registered tool definitions |
| `GET /docs`            | OpenAPI / Swagger UI                         |

## Agent Loop

This scaffold uses deterministic planning rules so the infrastructure is easy to inspect before introducing model-driven planning.

```text
User question
  -> load available tools from Project 08
  -> select next tool based on question + prior observations
  -> invoke tool through Project 08 executor
  -> persist thought/action/observation step
  -> stop on max_steps, no next action, or timeout
  -> synthesize final answer from observations
```

## Initial Tool Routing

| Signal in question                 | Tool             |
| ---------------------------------- | ---------------- |
| `doc`, `search`, `source`, `rag`   | `search_docs`    |
| `metric`, `latency`, `reliability` | `get_metrics`    |
| `job`, `status`                    | `get_job_status` |

The runtime avoids invoking the same tool twice in a run unless future logic explicitly allows retries.

## Environment Variables

Copy `.env.example` to `.env` and adjust as needed.

| Variable       | Default                                        | Description                 |
| -------------- | ---------------------------------------------- | --------------------------- |
| `DATABASE_URL` | `postgresql://agent:agent@postgres:5432/agent` | Agent run Postgres database |
| `REGISTRY_URL` | `http://host.docker.internal:8008`             | Project 08 registry API     |
| `EXECUTOR_URL` | `http://host.docker.internal:8009`             | Project 08 executor service |
| `MAX_STEPS`    | `4`                                            | Default maximum agent steps |
| `TIMEOUT_MS`   | `30000`                                        | Default run timeout budget  |
| `LOG_LEVEL`    | `INFO`                                         | Runtime logging level       |

## Deliverables Checklist

- [x] Agent runtime API scaffold
- [x] Project 08 registry and executor integration
- [x] Postgres persistence for agent runs and steps
- [x] Docker Compose local development stack
- [ ] Model-driven planner adapter
- [ ] Idempotent retry policy for transient tool failures
- [ ] Benchmark comparison: single-shot RAG vs ReAct loop
- [ ] Agent run replay documentation
- [ ] Technical writeup and LinkedIn summary

## What This Demonstrates

- Bounded agent execution with explicit budgets
- Separation of agent planning from tool execution
- Persisted thought/action/observation traces
- A bridge from tool calling (Project 08) to DAG orchestration (Project 10)

## Next Project

Project 10 (DAG Workflow Orchestrator) will generalize this single-agent loop into dependency-aware workflows with fan-out, fan-in, checkpointing, and replay.
