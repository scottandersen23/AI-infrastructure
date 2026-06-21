# Observability Dashboard

The capstone exposes a local HTML dashboard from the API gateway at:

```text
http://localhost:8010/dashboard
```

The dashboard summarizes:

- Total requests
- Error rate
- Average request latency
- Average retrieval latency
- Average model latency
- Average total tokens
- Retrieval hit rate
- Average quality score
- Recent request-level events

## Screenshot Workflow

After starting the platform and sending sample `/ask` traffic, open the dashboard and capture screenshots into:

```text
docs/screenshots/
```

Recommended screenshots:

- `dashboard-summary.png`
- `metrics-events.png`
- `ask-response-with-sources.png`

These screenshots complete the capstone observability artifact by showing how the system reports latency, token usage, retrieval quality, and request health.
