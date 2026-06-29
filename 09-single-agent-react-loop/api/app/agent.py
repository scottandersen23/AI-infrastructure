import re
import time
import uuid
from typing import Any

from api.app import database
from api.app.config import settings
from api.app.project08_client import invoke_tool, list_tools
from api.app.schemas import AgentRunRequest, AgentRunResponse, AgentStep, ToolDefinition


def _question_mentions(question: str, terms: tuple[str, ...]) -> bool:
    normalized = question.lower()
    return any(term in normalized for term in terms)


def _extract_job_id(question: str) -> str | None:
    match = re.search(
        r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}",
        question,
    )
    return match.group(0) if match else None


def _select_next_action(
    question: str,
    tools: list[ToolDefinition],
    used_tools: set[str],
) -> tuple[str | None, dict[str, Any], str]:
    available = {tool.name for tool in tools}

    if (
        _question_mentions(question, ("doc", "docs", "search", "source", "rag"))
        and "search_docs" in available
        and "search_docs" not in used_tools
    ):
        return (
            "search_docs",
            {"query": question, "limit": 3},
            "Search the document index for source-grounded context.",
        )

    if (
        _question_mentions(question, ("metric", "metrics", "latency", "reliability", "error rate"))
        and "get_metrics" in available
        and "get_metrics" not in used_tools
    ):
        return (
            "get_metrics",
            {},
            "Fetch platform metrics to ground the reliability answer.",
        )

    job_id = _extract_job_id(question)
    if job_id and "get_job_status" in available and "get_job_status" not in used_tools:
        return (
            "get_job_status",
            {"job_id": job_id},
            "Look up the referenced async job status.",
        )

    return None, {}, "No remaining tool action is required for this request."


def _synthesize_answer(question: str, steps: list[AgentStep]) -> str:
    successful_observations = [
        step for step in steps if step.action is not None and step.success and step.observation
    ]

    if not successful_observations:
        return (
            "No tool call was required or completed successfully. "
            f"Question handled by the scaffolded agent loop: {question}"
        )

    summary_lines = [
        f"Agent completed {len(successful_observations)} tool-backed step(s) for: {question}"
    ]
    for step in successful_observations:
        summary_lines.append(f"- {step.action}: {step.observation}")

    return "\n".join(summary_lines)


async def run_agent(request: AgentRunRequest) -> AgentRunResponse:
    run_id = uuid.uuid4()
    max_steps = request.max_steps or settings.max_steps
    timeout_seconds = settings.timeout_ms / 1000
    start = time.perf_counter()
    steps: list[AgentStep] = []
    used_tools: set[str] = set()

    database.create_run(run_id, request.question, max_steps)

    try:
        tools = await list_tools()
        for step_index in range(1, max_steps + 1):
            if time.perf_counter() - start > timeout_seconds:
                step = AgentStep(
                    step_index=step_index,
                    thought="Timeout budget reached before selecting another action.",
                    success=False,
                    error="timeout_budget_reached",
                )
                steps.append(step)
                database.insert_step(run_id, step)
                break

            action, action_input, thought = _select_next_action(
                request.question,
                tools,
                used_tools,
            )

            if action is None:
                step = AgentStep(step_index=step_index, thought=thought)
                steps.append(step)
                database.insert_step(run_id, step)
                break

            invoke_start = time.perf_counter()
            try:
                observation = await invoke_tool(action, action_input)
                latency_ms = round((time.perf_counter() - invoke_start) * 1000, 2)
                step = AgentStep(
                    step_index=step_index,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    observation=observation,
                    success=observation.get("success", False),
                    latency_ms=latency_ms,
                    error=observation.get("error"),
                )
            except Exception as exc:
                latency_ms = round((time.perf_counter() - invoke_start) * 1000, 2)
                step = AgentStep(
                    step_index=step_index,
                    thought=thought,
                    action=action,
                    action_input=action_input,
                    success=False,
                    latency_ms=latency_ms,
                    error=str(exc),
                )

            used_tools.add(action)
            steps.append(step)
            database.insert_step(run_id, step)

        final_answer = _synthesize_answer(request.question, steps)
        status = "completed" if all(step.success for step in steps) else "completed_with_errors"
        database.complete_run(run_id, status, final_answer, len(steps))

        return AgentRunResponse(
            run_id=run_id,
            status=status,
            question=request.question,
            final_answer=final_answer,
            steps_taken=len(steps),
            max_steps=max_steps,
            steps=steps,
        )
    except Exception as exc:
        database.fail_run(run_id, str(exc), len(steps))
        raise
