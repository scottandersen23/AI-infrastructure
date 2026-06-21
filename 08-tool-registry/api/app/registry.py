import json
from contextlib import contextmanager
from typing import Any, Generator

import psycopg

from api.app.config import settings


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("SELECT 1")


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def list_tools(active_only: bool = True) -> list[dict[str, Any]]:
    query = """
        SELECT name, description, input_schema, version, auth_scope, rate_limit_rpm, is_active
        FROM tools
    """
    if active_only:
        query += " WHERE is_active = TRUE"
    query += " ORDER BY name"

    with get_connection() as conn:
        rows = conn.execute(query).fetchall()

    return [
        {
            "name": row[0],
            "description": row[1],
            "input_schema": row[2] if isinstance(row[2], dict) else json.loads(row[2]),
            "version": row[3],
            "auth_scope": row[4],
            "rate_limit_rpm": row[5],
            "is_active": row[6],
        }
        for row in rows
    ]


def get_tool(name: str) -> dict[str, Any] | None:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT name, description, input_schema, version, auth_scope, rate_limit_rpm, is_active
            FROM tools
            WHERE name = %s AND is_active = TRUE
            """,
            (name,),
        ).fetchone()

    if row is None:
        return None

    return {
        "name": row[0],
        "description": row[1],
        "input_schema": row[2] if isinstance(row[2], dict) else json.loads(row[2]),
        "version": row[3],
        "auth_scope": row[4],
        "rate_limit_rpm": row[5],
        "is_active": row[6],
    }


def upsert_tool(
    name: str,
    description: str,
    input_schema: dict[str, Any],
    auth_scope: str = "public",
    rate_limit_rpm: int = 60,
) -> dict[str, Any]:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO tools (name, description, input_schema, auth_scope, rate_limit_rpm)
            VALUES (%s, %s, %s::jsonb, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                description = EXCLUDED.description,
                input_schema = EXCLUDED.input_schema,
                auth_scope = EXCLUDED.auth_scope,
                rate_limit_rpm = EXCLUDED.rate_limit_rpm,
                version = tools.version + 1,
                updated_at = NOW()
            """,
            (name, description, json.dumps(input_schema), auth_scope, rate_limit_rpm),
        )
        conn.commit()

    tool = get_tool(name)
    if tool is None:
        raise RuntimeError(f"Failed to upsert tool: {name}")
    return tool
