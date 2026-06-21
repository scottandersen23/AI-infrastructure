import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from api.app.config import settings
from api.app.schemas import MetricEvent, MetricSummary, TokenUsage


def init_metrics_store() -> None:
    db_path = Path(settings.observability_db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with _connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS metric_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                route TEXT NOT NULL,
                status TEXT NOT NULL,
                request_latency_ms REAL NOT NULL,
                retrieval_latency_ms REAL NOT NULL,
                model_latency_ms REAL NOT NULL,
                prompt_tokens INTEGER NOT NULL,
                completion_tokens INTEGER NOT NULL,
                total_tokens INTEGER NOT NULL,
                retrieval_hit INTEGER NOT NULL,
                quality_score REAL NOT NULL,
                error_message TEXT
            );
            """
        )


def record_event(
    *,
    route: str,
    status: str,
    request_latency_ms: float,
    retrieval_latency_ms: float,
    model_latency_ms: float,
    token_usage: TokenUsage,
    retrieval_hit: bool,
    quality_score: float,
    error_message: str | None = None,
) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO metric_events (
                timestamp, route, status, request_latency_ms, retrieval_latency_ms,
                model_latency_ms, prompt_tokens, completion_tokens, total_tokens,
                retrieval_hit, quality_score, error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                datetime.now(UTC).isoformat(),
                route,
                status,
                request_latency_ms,
                retrieval_latency_ms,
                model_latency_ms,
                token_usage.prompt_tokens,
                token_usage.completion_tokens,
                token_usage.total_tokens,
                int(retrieval_hit),
                quality_score,
                error_message,
            ),
        )


def summarize_events() -> MetricSummary:
    with _connect() as connection:
        row = connection.execute(
            """
            SELECT
                count(*) AS total_requests,
                sum(CASE WHEN status != 'ok' THEN 1 ELSE 0 END) AS error_count,
                avg(request_latency_ms) AS avg_request_latency_ms,
                avg(retrieval_latency_ms) AS avg_retrieval_latency_ms,
                avg(model_latency_ms) AS avg_model_latency_ms,
                avg(total_tokens) AS avg_total_tokens,
                avg(retrieval_hit) AS retrieval_hit_rate,
                avg(quality_score) AS avg_quality_score
            FROM metric_events;
            """
        ).fetchone()

    total = int(row["total_requests"] or 0)
    errors = int(row["error_count"] or 0)
    return MetricSummary(
        total_requests=total,
        error_count=errors,
        error_rate=round(errors / total, 4) if total else 0.0,
        avg_request_latency_ms=round(float(row["avg_request_latency_ms"] or 0), 2),
        avg_retrieval_latency_ms=round(float(row["avg_retrieval_latency_ms"] or 0), 2),
        avg_model_latency_ms=round(float(row["avg_model_latency_ms"] or 0), 2),
        avg_total_tokens=round(float(row["avg_total_tokens"] or 0), 2),
        retrieval_hit_rate=round(float(row["retrieval_hit_rate"] or 0), 4),
        avg_quality_score=round(float(row["avg_quality_score"] or 0), 4),
    )


def list_events(limit: int = 50) -> list[MetricEvent]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT * FROM metric_events
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        ).fetchall()
    return [
        MetricEvent(
            **{
                **dict(row),
                "retrieval_hit": bool(row["retrieval_hit"]),
            }
        )
        for row in rows
    ]


@contextmanager
def _connect():
    connection = sqlite3.connect(settings.observability_db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()
