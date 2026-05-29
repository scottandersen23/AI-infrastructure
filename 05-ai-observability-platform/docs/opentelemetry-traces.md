# OpenTelemetry Traces

Phase 5 deliverable for documenting trace instrumentation.

## Span Map

| Span                  | Purpose                | Key Attributes                                  |
| --------------------- | ---------------------- | ----------------------------------------------- |
| `POST /ask`           | FastAPI request span   | HTTP method, route, status                      |
| `ai.request`          | AI workflow root span  | Question length, model, aggregate metrics       |
| `ai.retrieval`        | Retrieval work         | Result count, retrieval latency                 |
| `ai.model.generate`   | Model generation work  | Model latency, prompt tokens, completion tokens |
| `ai.quality.evaluate` | Response quality check | Quality score                                   |

## Export Modes

### Console

```bash
OTEL_EXPORTER=console uvicorn api.app.main:app --reload --port 8003
```

Best for local smoke tests and inspecting raw span structure.

### OTLP / Phoenix

```bash
OTEL_EXPORTER=otlp OTLP_ENDPOINT=http://localhost:4317 uvicorn api.app.main:app --reload --port 8003
```

Best for trace waterfall views and multi-span analysis.

## Trace Attributes

The API sets AI-specific attributes:

- `ai.question.length`
- `ai.model.name`
- `ai.request.latency_ms`
- `ai.retrieval.latency_ms`
- `ai.model.latency_ms`
- `ai.tokens.prompt`
- `ai.tokens.completion`
- `ai.tokens.total`
- `ai.retrieval.hit`
- `ai.quality.score`

## Debugging Playbook

| Symptom          | Trace Clue                                              |
| ---------------- | ------------------------------------------------------- |
| Slow response    | Compare `ai.retrieval` and `ai.model.generate` duration |
| High token usage | Inspect `ai.tokens.prompt` and retrieved source count   |
| Poor grounding   | Check `ai.retrieval.hit` and `ai.quality.score`         |
| Model errors     | Look for error status and exception events on spans     |
