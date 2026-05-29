import asyncio
import time

from opentelemetry import trace

from api.app.config import settings
from api.app.schemas import AskResponse, Source, TokenUsage
from api.app.telemetry import tracer


KNOWLEDGE_BASE = [
    Source(
        title="AI Observability Notes",
        chunk_index=0,
        similarity=0.91,
        content=(
            "AI observability tracks request latency, model latency, token usage, "
            "retrieval latency, errors, and response quality."
        ),
    ),
    Source(
        title="RAG Reliability Notes",
        chunk_index=1,
        similarity=0.86,
        content=(
            "Retrieval hit rate and grounded citations help determine whether a "
            "RAG answer is supported by source context."
        ),
    ),
    Source(
        title="OpenTelemetry Trace Guide",
        chunk_index=2,
        similarity=0.82,
        content=(
            "OpenTelemetry spans should separate API handling, retrieval, model "
            "generation, and response quality evaluation."
        ),
    ),
]


async def run_observed_ai_request(question: str) -> AskResponse:
    request_start = time.perf_counter()
    with tracer.start_as_current_span("ai.request") as span:
        span.set_attribute("ai.question.length", len(question))
        span.set_attribute("ai.model.name", settings.model_name)

        sources, retrieval_latency_ms = await _retrieve_context(question)
        answer, model_latency_ms, usage = await _generate_answer(question, sources)
        quality_score = _score_quality(answer=answer, sources=sources)
        request_latency_ms = (time.perf_counter() - request_start) * 1000

        span.set_attribute("ai.request.latency_ms", request_latency_ms)
        span.set_attribute("ai.retrieval.latency_ms", retrieval_latency_ms)
        span.set_attribute("ai.model.latency_ms", model_latency_ms)
        span.set_attribute("ai.tokens.prompt", usage.prompt_tokens)
        span.set_attribute("ai.tokens.completion", usage.completion_tokens)
        span.set_attribute("ai.tokens.total", usage.total_tokens)
        span.set_attribute("ai.retrieval.hit", bool(sources))
        span.set_attribute("ai.quality.score", quality_score)

        return AskResponse(
            answer=answer,
            sources=sources,
            request_latency_ms=round(request_latency_ms, 2),
            retrieval_latency_ms=round(retrieval_latency_ms, 2),
            model_latency_ms=round(model_latency_ms, 2),
            token_usage=usage,
            reliability={
                "retrieval_hit": bool(sources),
                "quality_score": quality_score,
                "source_count": len(sources),
            },
        )


async def _retrieve_context(question: str) -> tuple[list[Source], float]:
    started = time.perf_counter()
    with tracer.start_as_current_span("ai.retrieval") as span:
        await asyncio.sleep(0.035)
        query_terms = {term.lower().strip(".,?!") for term in question.split()}
        scored_sources = []
        for source in KNOWLEDGE_BASE:
            content_terms = set(source.content.lower().split())
            overlap = len(query_terms & content_terms)
            if overlap > 0:
                scored_sources.append(source)

        if not scored_sources:
            scored_sources = KNOWLEDGE_BASE[:1]

        results = scored_sources[: settings.retrieval_top_k]
        latency_ms = (time.perf_counter() - started) * 1000
        span.set_attribute("ai.retrieval.results", len(results))
        span.set_attribute("ai.retrieval.latency_ms", latency_ms)
        return results, latency_ms


async def _generate_answer(
    question: str,
    sources: list[Source],
) -> tuple[str, float, TokenUsage]:
    started = time.perf_counter()
    with tracer.start_as_current_span("ai.model.generate") as span:
        await asyncio.sleep(0.08)
        context = " ".join(source.content for source in sources)
        answer = (
            "An observable AI API should trace each request across retrieval, "
            "model generation, token accounting, errors, and quality checks. "
            f"For this question, the retrieved context says: {context}"
        )
        prompt_tokens = len(question.split()) + sum(len(source.content.split()) for source in sources)
        completion_tokens = len(answer.split())
        usage = TokenUsage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        )
        latency_ms = (time.perf_counter() - started) * 1000
        span.set_attribute("ai.model.latency_ms", latency_ms)
        span.set_attribute("ai.tokens.prompt", usage.prompt_tokens)
        span.set_attribute("ai.tokens.completion", usage.completion_tokens)
        return answer, latency_ms, usage


def _score_quality(answer: str, sources: list[Source]) -> float:
    with tracer.start_as_current_span("ai.quality.evaluate") as span:
        if not sources:
            score = 0.0
        else:
            cited_terms = sum(
                1 for source in sources if any(term in answer for term in source.title.split())
            )
            score = min(1.0, 0.65 + (0.1 * len(sources)) + (0.05 * cited_terms))
        span.set_attribute("ai.quality.score", score)
        return round(score, 2)
