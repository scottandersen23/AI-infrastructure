import json
from contextlib import contextmanager
from typing import Any, Generator
from uuid import UUID

import psycopg

from api.app.config import settings
from api.app.schemas import AgentStep


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    with psycopg.connect(settings.database_url) as conn:
        yield conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute("SELECT 1")


def create_run(run_id: UUID, question: str, max_steps: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agent_runs (id, question, status, max_steps)
            VALUES (%s, %s, %s, %s)
            """,
            (run_id, question, "running", max_steps),
        )
        conn.commit()


def insert_step(run_id: UUID, step: AgentStep) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO agent_steps (
                run_id,
                step_index,
                thought,
                action,
                action_input,
                observation,
                success,
                latency_ms,
                error_message
            )
            VALUES (%s, %s, %s, %s, %s::jsonb, %s::jsonb, %s, %s, %s)
            """,
            (
                run_id,
                step.step_index,
                step.thought,
                step.action,
                json.dumps(step.action_input) if step.action_input is not None else None,
                json.dumps(step.observation) if step.observation is not None else None,
                step.success,
                step.latency_ms,
                step.error,
            ),
        )
        conn.commit()


def complete_run(run_id: UUID, status: str, final_answer: str, steps_taken: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE agent_runs
            SET status = %s,
                final_answer = %s,
                steps_taken = %s,
                completed_at = NOW()
            WHERE id = %s
            """,
            (status, final_answer, steps_taken, run_id),
        )
        conn.commit()


def fail_run(run_id: UUID, error_message: str, steps_taken: int) -> None:
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE agent_runs
            SET status = 'error',
                error_message = %s,
                steps_taken = %s,
                completed_at = NOW()
            WHERE id = %s
            """,
            (error_message, steps_taken, run_id),
        )
        conn.commit()


def get_run(run_id: UUID) -> dict[str, Any] | None:
    with get_connection() as conn:
        run = conn.execute(
            """
            SELECT id, question, status, final_answer, max_steps, steps_taken, error_message
            FROM agent_runs
            WHERE id = %s
            """,
            (run_id,),
        ).fetchone()
        if run is None:
            return None

        step_rows = conn.execute(
            """
            SELECT step_index, thought, action, action_input, observation, success, latency_ms, error_message
            FROM agent_steps
            WHERE run_id = %s
            ORDER BY step_index
            """,
            (run_id,),
        ).fetchall()

    return {
        "run_id": run[0],
        "question": run[1],
        "status": run[2],
        "final_answer": run[3],
        "max_steps": run[4],
        "steps_taken": run[5],
        "error_message": run[6],
        "steps": [
            {
                "step_index": row[0],
                "thought": row[1],
                "action": row[2],
                "action_input": row[3],
                "observation": row[4],
                "success": row[5],
                "latency_ms": row[6],
                "error": row[7],
            }
            for row in step_rows
        ],
    }
