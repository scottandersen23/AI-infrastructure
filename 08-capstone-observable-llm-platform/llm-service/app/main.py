import os

from fastapi import FastAPI

from app.schemas import GenerateRequest, GenerateResponse, HealthResponse, TokenUsage


RUNTIME = os.getenv("LLM_RUNTIME", "mock")
MODEL_NAME = os.getenv("DEFAULT_MODEL", "capstone-mock-llm")

app = FastAPI(
    title="Capstone LLM Service",
    description="Mock/Ollama-compatible LLM boundary for the capstone platform.",
    version="1.0.0",
)


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health() -> HealthResponse:
    return HealthResponse(status="ok", runtime=RUNTIME, model_name=MODEL_NAME)


@app.post("/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate(request: GenerateRequest) -> GenerateResponse:
    answer = _generate_mock_answer(request)
    prompt_tokens = len(request.prompt.split())
    completion_tokens = len(answer.split())
    return GenerateResponse(
        answer=answer,
        model_name=MODEL_NAME,
        token_usage=TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )


def _generate_mock_answer(request: GenerateRequest) -> str:
    if not request.sources:
        return "The supplied context does not contain enough information to answer the question."

    first_source = request.sources[0]
    source_title = first_source.get("title", "source")
    chunk_index = first_source.get("chunk_index", 0)
    content = first_source.get("content", "")
    lead = content.split(".")[0].strip()
    return (
        "The observable local LLM platform combines an API gateway, retrieval, model serving, "
        "async jobs, and telemetry so AI behavior can be operated like a platform. "
        f"Relevant context from {source_title} chunk {chunk_index} says: {lead}. "
        "The important architectural pattern is separating platform responsibilities while "
        "returning latency, token, retrieval, and quality signals with each response."
    )
