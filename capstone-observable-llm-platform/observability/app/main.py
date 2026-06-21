from fastapi import FastAPI
from fastapi.responses import HTMLResponse


app = FastAPI(
    title="Capstone Observability Service",
    description="Dashboard boundary for capstone platform metrics.",
    version="1.0.0",
)


@app.get("/health", tags=["Health"])
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "capstone-observability"}


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"])
async def dashboard() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Capstone Observability</title>
        <style>
          body { font-family: system-ui, sans-serif; margin: 2rem; color: #17202a; }
          .card { border: 1px solid #d5d8dc; border-radius: 12px; padding: 1rem; margin: 1rem 0; }
        </style>
      </head>
      <body>
        <h1>Capstone Observability Service</h1>
        <p>The API gateway exposes live request metrics at <code>/metrics/summary</code> and <code>/dashboard</code>.</p>
        <div class="card">
          <h2>Tracked Signals</h2>
          <p>Request latency, retrieval latency, model latency, token usage, retrieval hit rate, quality score, and errors.</p>
        </div>
      </body>
    </html>
    """
