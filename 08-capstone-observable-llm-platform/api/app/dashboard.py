from api.app.schemas import MetricEvent, MetricSummary


def render_dashboard(summary: MetricSummary, events: list[MetricEvent]) -> str:
    rows = "\n".join(
        (
            "<tr>"
            f"<td>{event.timestamp}</td>"
            f"<td>{event.route}</td>"
            f"<td>{event.status}</td>"
            f"<td>{event.request_latency_ms}</td>"
            f"<td>{event.total_tokens}</td>"
            f"<td>{event.retrieval_hit}</td>"
            f"<td>{event.quality_score}</td>"
            "</tr>"
        )
        for event in events
    )
    return f"""
    <!doctype html>
    <html>
      <head>
        <title>Capstone AI Observability Dashboard</title>
        <style>
          body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }}
          .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; }}
          .card {{ border: 1px solid #d5d8dc; border-radius: 12px; padding: 1rem; }}
          .value {{ font-size: 1.8rem; font-weight: 700; }}
          table {{ border-collapse: collapse; width: 100%; margin-top: 2rem; }}
          th, td {{ border-bottom: 1px solid #e5e7e9; padding: 0.6rem; text-align: left; }}
        </style>
      </head>
      <body>
        <h1>Capstone AI Observability Dashboard</h1>
        <p>Local dashboard for latency, token usage, retrieval quality, and request health.</p>
        <section class="grid">
          <div class="card"><div>Total Requests</div><div class="value">{summary.total_requests}</div></div>
          <div class="card"><div>Error Rate</div><div class="value">{summary.error_rate}</div></div>
          <div class="card"><div>Avg Latency (ms)</div><div class="value">{summary.avg_request_latency_ms}</div></div>
          <div class="card"><div>Avg Tokens</div><div class="value">{summary.avg_total_tokens}</div></div>
          <div class="card"><div>Retrieval Hit Rate</div><div class="value">{summary.retrieval_hit_rate}</div></div>
          <div class="card"><div>Avg Quality</div><div class="value">{summary.avg_quality_score}</div></div>
          <div class="card"><div>Retrieval Latency</div><div class="value">{summary.avg_retrieval_latency_ms}</div></div>
          <div class="card"><div>Model Latency</div><div class="value">{summary.avg_model_latency_ms}</div></div>
        </section>
        <table>
          <thead>
            <tr>
              <th>Timestamp</th><th>Route</th><th>Status</th><th>Latency</th>
              <th>Tokens</th><th>Retrieval Hit</th><th>Quality</th>
            </tr>
          </thead>
          <tbody>{rows}</tbody>
        </table>
      </body>
    </html>
    """
