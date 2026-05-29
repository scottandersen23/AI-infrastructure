from api.app.metrics_store import get_summary, list_recent_events


def render_dashboard() -> str:
    summary = get_summary()
    events = list_recent_events(limit=10)
    rows = "\n".join(
        f"""
        <tr>
          <td>{event.timestamp.strftime('%H:%M:%S')}</td>
          <td>{event.status}</td>
          <td>{event.request_latency_ms:.2f}</td>
          <td>{event.retrieval_latency_ms:.2f}</td>
          <td>{event.model_latency_ms:.2f}</td>
          <td>{event.total_tokens}</td>
          <td>{event.quality_score:.2f}</td>
        </tr>
        """
        for event in events
    )
    return f"""
    <!doctype html>
    <html>
      <head>
        <title>AI Observability Dashboard</title>
        <style>
          body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
          .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
          .card {{ border: 1px solid #d5d8dc; border-radius: 12px; padding: 1rem; }}
          .value {{ font-size: 2rem; font-weight: 700; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 1rem; }}
          th, td {{ border-bottom: 1px solid #e5e7e9; padding: 0.6rem; text-align: left; }}
        </style>
      </head>
      <body>
        <h1>AI Observability Dashboard</h1>
        <p>Local dashboard for request latency, model latency, retrieval latency, token usage, errors, retrieval hit rate, and quality score.</p>
        <section class="grid">
          <div class="card"><div>Total Requests</div><div class="value">{summary.total_requests}</div></div>
          <div class="card"><div>Error Rate</div><div class="value">{summary.error_rate:.2%}</div></div>
          <div class="card"><div>Avg Latency</div><div class="value">{summary.avg_request_latency_ms:.0f} ms</div></div>
          <div class="card"><div>Retrieval Hit Rate</div><div class="value">{summary.retrieval_hit_rate:.2%}</div></div>
          <div class="card"><div>Avg Retrieval</div><div class="value">{summary.avg_retrieval_latency_ms:.0f} ms</div></div>
          <div class="card"><div>Avg Model</div><div class="value">{summary.avg_model_latency_ms:.0f} ms</div></div>
          <div class="card"><div>Avg Tokens</div><div class="value">{summary.avg_total_tokens:.0f}</div></div>
          <div class="card"><div>Avg Quality</div><div class="value">{summary.avg_quality_score:.2f}</div></div>
        </section>
        <h2>Recent Events</h2>
        <table>
          <thead>
            <tr>
              <th>Time</th><th>Status</th><th>Request ms</th><th>Retrieval ms</th><th>Model ms</th><th>Tokens</th><th>Quality</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </body>
    </html>
    """
