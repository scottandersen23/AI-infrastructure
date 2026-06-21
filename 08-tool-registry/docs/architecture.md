# Tool Registry Architecture

## Service Boundaries

| Service  | Port | Responsibility                                      |
| -------- | ---- | --------------------------------------------------- |
| Registry | 8008 | Tool schema CRUD, LLM binding, Postgres persistence |
| Executor | 8009 | Argument validation, handler dispatch, audit        |
| Postgres | 5434 | Tool definitions and invocation audit log           |

## Tool Lifecycle

```text
1. Register   — POST /tools with name, description, JSON Schema
2. Bind       — GET /tools returns schemas for LLM function calling
3. Select     — LLM chooses tool + arguments at inference time
4. Validate   — Executor validates args against registry schema
5. Execute    — Handler runs (stub or Phase 1 service integration)
6. Audit      — Invocation recorded in tool_invocations table
7. Observe    — OpenTelemetry span emitted (tool.name, latency, success)
```

## Design Decisions

**Registry vs executor split.** Schemas and runtime are separate services so schema changes do not require redeploying handlers, and handlers can scale independently.

**Postgres over in-memory registry.** Tool definitions and audit logs persist across restarts and support versioning, auth scopes, and rate limits.

**Stub-first handlers.** Built-in tools return structured stub data until Phase 1 services (RAG, metrics, jobs) are wired via environment URLs.

## Phase 2 Integration Points

| Downstream project  | Uses Project 08 for                       |
| ------------------- | ----------------------------------------- |
| 09 ReAct loop       | Tool binding and `/invoke` in agent steps |
| 10 DAG orchestrator | DAG nodes of type `tool_call`             |
| 11 Multi-agent      | Per-agent tool allowlists from registry   |
| 12 Data tools       | New tools registered via POST /tools      |
| 13 Observability    | Spans and audit log for tool reliability  |
| 14 Capstone         | Unified tool layer under supervisor agent |
