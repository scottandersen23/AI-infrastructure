from contextlib import asynccontextmanager
from uuid import UUID

from fastapi import FastAPI, HTTPException, status

from api.app.agent import run_agent
from api.app.config import settings
from api.app.database import get_run, init_db
from api.app.project08_client import check_url, list_tools
from api.app.schemas import AgentRunRequest, AgentRunResponse, HealthResponse, SavedAgentRun


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Single-Agent ReAct Runtime",
    description=(
        "Bounded agent runtime that fetches tool schemas from Project 08, "
        "invokes tools through the executor, and persists thought/action/observation steps."
    ),
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    postgres_status = "ok"
    try:
        init_db()
    except Exception:
        postgres_status = "error"

    registry_status = await check_url(settings.registry_url)
    executor_status = await check_url(settings.executor_url)

    return HealthResponse(
        status=(
            "ok"
            if postgres_status == "ok" and registry_status == "ok" and executor_status == "ok"
            else "degraded"
        ),
        service_name=settings.service_name,
        environment=settings.environment,
        dependencies={
            "postgres": postgres_status,
            "registry": registry_status,
            "executor": executor_status,
        },
    )


@app.get("/tools", tags=["Tools"])
async def tools():
    return {"tools": await list_tools()}


@app.post("/agent/run", response_model=AgentRunResponse, tags=["Agent"])
async def agent_run(request: AgentRunRequest) -> AgentRunResponse:
    return await run_agent(request)


@app.get("/agent/runs/{run_id}", response_model=SavedAgentRun, tags=["Agent"])
async def get_agent_run(run_id: UUID) -> SavedAgentRun:
    run = get_run(run_id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent run not found")
    return SavedAgentRun(**run)
