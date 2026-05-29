import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from datetime import UTC, datetime
from typing import Any

from api.app.config import settings
from api.app.schemas import MetricEvent, MetricSummary


@contextmanager
def get_connection():
    connection = sqlite3.connect(settings.metrics_db_path)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_metrics_store() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ai_request_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                route TEXT NOT NULL,
                status TEXT NOT NULL,
                model_name TEXT NOT NULL,
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


def record_metric(event: dict[str, Any]) -> None:
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO ai_request_metrics (
                timestamp,
                route,
                status,
                model_name,
                request_latency_ms,
                retrieval_latency_ms,
                model_latency_ms,
                prompt_tokens,
                completion_tokens,
                total_tokens,
                retrieval_hit,
                quality_score,
                error_message
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (
                datetime.now(UTC).isoformat(),
                event["route"],
                event["status"],
                event["model_name"],
                event["request_latency_ms"],
                event["retrieval_latency_ms"],
                event["model_latency_ms"],
                event["prompt_tokens"],
                event["completion_tokens"],
                event["total_tokens"],
                1 if event["retrieval_hit"] else 0,
                event["quality_score"],
                event.get("error_message"),
            ),
        )


def list_recent_events(limit: int = 25) -> list[MetricEvent]:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM ai_request_metrics
            ORDER BY id DESC
            LIMIT ?;
            """,
            (limit,),
        ).fetchall()

    return [_row_to_event(row) for row in rows]


def get_summary() -> MetricSummary:
    with get_connection() as connection:
        rows = connection.execute("SELECT * FROM ai_request_metrics;").fetchall()

    if not rows:
        return MetricSummary(
            total_requests=0,
            error_count=0,
            error_rate=0.0,
            avg_request_latency_ms=0.0,
            avg_retrieval_latency_ms=0.0,
            avg_model_latency_ms=0.0,
            avg_total_tokens=0.0,
            retrieval_hit_rate=0.0,
            avg_quality_score=0.0,
        )

    total = len(rows)
    errors = sum(1 for row in rows if row["status"] != "ok")
    return MetricSummary(
        total_requests=total,
        error_count=errors,
        error_rate=round(errors / total, 4),
        avg_request_latency_ms=_avg(row["request_latency_ms"] for row in rows),
        avg_retrieval_latency_ms=_avg(row["retrieval_latency_ms"] for row in rows),
        avg_model_latency_ms=_avg(row["model_latency_ms"] for row in rows),
        avg_total_tokens=_avg(row["total_tokens"] for row in rows),
        retrieval_hit_rate=round(sum(row["retrieval_hit"] for row in rows) / total, 4),
        avg_quality_score=_avg(row["quality_score"] for row in rows),
    )


def _avg(values: Iterable[float]) -> float:
    values_list = list(values)
    if not values_list:
        return 0.0
    return round(sum(values_list) / len(values_list), 2)


def _row_to_event(row: sqlite3.Row) -> MetricEvent:
    return MetricEvent(
        id=row["id"],
        timestamp=datetime.fromisoformat(row["timestamp"]),
        route=row["route"],
        status=row["status"],
        model_name=row["model_name"],
        request_latency_ms=row["request_latency_ms"],
        retrieval_latency_ms=row["retrieval_latency_ms"],
        model_latency_ms=row["model_latency_ms"],
        prompt_tokens=row["prompt_tokens"],
        completion_tokens=row["completion_tokens"],
        total_tokens=row["total_tokens"],
        retrieval_hit=bool(row["retrieval_hit"]),
        quality_score=row["quality_score"],
        error_message=row["error_message"],
    )
