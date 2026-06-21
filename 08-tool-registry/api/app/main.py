from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status

from api.app.config import settings
from api.app.registry import get_tool, init_db, list_tools, upsert_tool
from api.app.schemas import HealthResponse, ToolCreateRequest, ToolDefinition, ToolListResponse


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Tool Registry API",
    description=(
        "Schema registry for LLM function calling. Stores tool definitions, "
        "JSON Schema input contracts, and metadata for the executor service."
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

    return HealthResponse(
        status="ok" if postgres_status == "ok" else "degraded",
        service_name=settings.service_name,
        environment=settings.environment,
        dependencies={"postgres": postgres_status},
    )


@app.get("/tools", response_model=ToolListResponse, tags=["Tools"])
async def get_tools() -> ToolListResponse:
    tools = [ToolDefinition(**tool) for tool in list_tools()]
    return ToolListResponse(tools=tools, count=len(tools))


@app.get("/tools/{name}", response_model=ToolDefinition, tags=["Tools"])
async def get_tool_by_name(name: str) -> ToolDefinition:
    tool = get_tool(name)
    if tool is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tool not found: {name}")
    return ToolDefinition(**tool)


@app.post("/tools", response_model=ToolDefinition, tags=["Tools"], status_code=status.HTTP_201_CREATED)
async def register_tool(request: ToolCreateRequest) -> ToolDefinition:
    tool = upsert_tool(
        name=request.name,
        description=request.description,
        input_schema=request.input_schema,
        auth_scope=request.auth_scope,
        rate_limit_rpm=request.rate_limit_rpm,
    )
    return ToolDefinition(**tool)
