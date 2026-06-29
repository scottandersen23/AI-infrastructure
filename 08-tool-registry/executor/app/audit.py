import json
from contextlib import contextmanager
from typing import Any, Generator

import psycopg

from executor.app.config import settings


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def record_invocation(
    *,
    tool_name: str,
    arguments: dict[str, Any],
    success: bool,
    latency_ms: float,
    result: dict[str, Any] | None = None,
    error_message: str | None = None,
) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tool_invocations (
                tool_name,
                arguments,
                success,
                result,
                error_message,
                latency_ms
            )
            VALUES (%s, %s::jsonb, %s, %s::jsonb, %s, %s)
            """,
            (
                tool_name,
                json.dumps(arguments),
                success,
                json.dumps(result) if result is not None else None,
                error_message,
                latency_ms,
            ),
        )
        conn.commit()
