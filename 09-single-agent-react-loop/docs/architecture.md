# Single-Agent ReAct Architecture

## Service Boundaries

| Service      | Port | Responsibility                                      |
| ------------ | ---- | --------------------------------------------------- |
| Agent API    | 8014 | Plan, invoke tools, persist runs, synthesize answer |
| Postgres     | 5435 | Agent run and step history                          |
| Registry API | 8008 | Tool schemas from Project 08                        |
| Executor     | 8009 | Validated tool invocation from Project 08           |

## Agent Lifecycle

```text
1. Start run      — Persist agent_runs row with status=running
2. Bind tools     — Fetch registered tool definitions from Project 08
3. Think          — Select next action from question and observations
4. Act            — Invoke Project 08 executor
5. Observe        — Persist action result as agent_steps row
6. Stop           — Budget exhausted, no action remains, or timeout reached
7. Synthesize     — Produce final answer from observations
```

## Design Decisions

**Deterministic planner first.** The scaffold starts with predictable routing rules so persistence, budgets, tool binding, and response shape are easy to validate before adding a model-driven planner.

**Project 08 remains the tool boundary.** Project 09 does not implement tools directly. It fetches schemas from the registry and invokes tools through the executor, preserving audit logs and validation in one place.

**Postgres for run history.** Agent runs and steps are persisted to prepare for replay, debugging, and later DAG checkpointing in Project 10.

## ReAct Step Shape

Each step records:

- `thought`: why the runtime selected a tool or stopped
- `action`: tool name, if a tool was called
- `action_input`: JSON arguments passed to the tool
- `observation`: structured tool result
- `success`: whether the action succeeded
- `latency_ms`: executor latency

## Future Extension Points

| Extension                | Target file          |
| ------------------------ | -------------------- |
| LLM planner adapter      | `api/app/agent.py`   |
| Retry and backoff policy | `api/app/agent.py`   |
| Token budget accounting  | `api/app/schemas.py` |
| Replay endpoint          | `api/app/main.py`    |
| Trace integration        | `api/app/main.py`    |
