import hashlib
import time
from pathlib import Path
from typing import Any

import httpx

from api.app.config import settings
from api.app.schemas import Source, TokenUsage


async def retrieve_context(question: str, limit: int) -> tuple[list[Source], float]:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{settings.rag_service_url.rstrip('/')}/search",
                json={"query": question, "limit": limit},
            )
            response.raise_for_status()
            payload = response.json()
            sources = [Source(**item) for item in payload["results"]]
            return sources, _elapsed_ms(start)
    except Exception:
        return _fallback_retrieve(question, limit), _elapsed_ms(start)


async def generate_answer(question: str, prompt: str, sources: list[Source]) -> tuple[str, str, TokenUsage, float]:
    start = time.perf_counter()
    try:
        async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
            response = await client.post(
                f"{settings.llm_service_url.rstrip('/')}/generate",
                json={
                    "question": question,
                    "prompt": prompt,
                    "sources": [source.model_dump() for source in sources],
                },
            )
            response.raise_for_status()
            payload = response.json()
            return (
                payload["answer"],
                payload.get("model_name", settings.default_model),
                TokenUsage(**payload["token_usage"]),
                _elapsed_ms(start),
            )
    except Exception:
        answer = _fallback_answer(question, sources)
        token_usage = TokenUsage(
            prompt_tokens=max(1, len(prompt.split())),
            completion_tokens=max(1, len(answer.split())),
            total_tokens=max(2, len(prompt.split()) + len(answer.split())),
        )
        return answer, settings.default_model, token_usage, _elapsed_ms(start)


def build_prompt(question: str, sources: list[Source]) -> str:
    context = "\n\n".join(
        (
            f"[Source {idx}: {source.title}, chunk {source.chunk_index}, "
            f"similarity {source.similarity}]\n{source.content}"
        )
        for idx, source in enumerate(sources, start=1)
    )
    return (
        "You are an observable, source-grounded AI platform assistant.\n"
        "Answer from the supplied context. If the context is insufficient, say so.\n"
        "Include platform reliability reasoning and cite source chunks when possible.\n\n"
        f"Context:\n{context}\n\nQuestion:\n{question}\n"
    )


def score_quality(sources: list[Source], answer: str) -> float:
    if not sources:
        return 0.0
    citation_bonus = 0.1 if "chunk" in answer.lower() or "source" in answer.lower() else 0.0
    length_score = min(len(answer.split()) / 80, 1.0)
    return round(min(0.65 + citation_bonus + (0.25 * length_score), 1.0), 4)


def _fallback_retrieve(question: str, limit: int) -> list[Source]:
    sample_path = Path(__file__).resolve().parents[2] / "sample-docs" / "platform-overview.md"
    content = sample_path.read_text(encoding="utf-8") if sample_path.exists() else _default_context()
    chunks = [chunk.strip() for chunk in content.split("\n\n") if chunk.strip()]
    query_tokens = set(_tokenize(question))
    scored: list[tuple[float, int, str]] = []
    for index, chunk in enumerate(chunks):
        tokens = set(_tokenize(chunk))
        overlap = len(query_tokens & tokens)
        stable_noise = int(hashlib.sha256(chunk.encode("utf-8")).hexdigest()[:2], 16) / 1000
        score = round(min(0.25 + (overlap / max(len(query_tokens), 1)) + stable_noise, 0.99), 4)
        scored.append((score, index, chunk))
    scored.sort(reverse=True)
    return [
        Source(
            title="Observable Local LLM Platform",
            chunk_index=index,
            similarity=score,
            content=chunk,
        )
        for score, index, chunk in scored[:limit]
        if score >= 0.3
    ]


def _fallback_answer(question: str, sources: list[Source]) -> str:
    if not sources:
        return "The capstone document store does not provide enough information to answer this question."
    lead = sources[0].content.split(".")[0].strip()
    citations = ", ".join(f"{source.title} chunk {source.chunk_index}" for source in sources[:3])
    return (
        "The capstone platform answers through an API gateway that combines retrieval, "
        "LLM generation, async work, and observability. "
        f"For this question, the strongest source says: {lead}. "
        f"Top sources: {citations}."
    )


def _default_context() -> str:
    return (
        "The capstone platform combines API gateway design, RAG retrieval, local LLM "
        "serving, async workers, observability, benchmarking, Docker, and Kubernetes."
    )


def _tokenize(text: str) -> list[str]:
    return [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split() if token.strip()]


def _elapsed_ms(start: float) -> float:
    return round((time.perf_counter() - start) * 1000, 2)
