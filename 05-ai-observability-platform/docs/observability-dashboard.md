# Observability Dashboard

Phase 5 deliverable for visualizing AI system performance.

## Local Dashboard

The API includes a lightweight local dashboard:

```text
http://localhost:8003/dashboard
```

It summarizes:

- Total requests
- Error rate
- Average request latency
- Average retrieval latency
- Average model latency
- Average token usage
- Retrieval hit rate
- Average quality score
- Recent request events

## Dashboard Spec

The file [`dashboards/ai-observability-dashboard.json`](../dashboards/ai-observability-dashboard.json) describes the panels to reproduce in Grafana, Phoenix notebooks, or another observability tool.

## Metrics Endpoint

Use the API directly for dashboard data:

```bash
curl -s http://localhost:8003/metrics/summary | python3 -m json.tool
curl -s http://localhost:8003/metrics/events | python3 -m json.tool
```

## Panel Rationale

| Panel              | Why It Matters                         |
| ------------------ | -------------------------------------- |
| Request latency    | User-facing performance                |
| Retrieval latency  | Vector store or retrieval bottlenecks  |
| Model latency      | LLM runtime bottlenecks                |
| Token usage        | Cost and context pressure              |
| Error rate         | Reliability baseline                   |
| Retrieval hit rate | RAG grounding signal                   |
| Quality score      | Response usefulness and source support |

## Next Iteration

For production, replace the SQLite-backed local metrics with Prometheus metrics, OTLP metrics, or warehouse-backed analytics. Keep the same dimensions: route, status, model, retrieval hit, token counts, and latency phases.
