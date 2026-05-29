import httpx

from api.app.config import settings
from api.app.embeddings import get_embedding_provider
from api.app.prompts import build_rag_prompt
from api.app.schemas import AskResponse, RetrievedChunk
from api.app.vector_store import search_chunks


async def retrieve(query: str, limit: int, similarity_threshold: float) -> list[RetrievedChunk]:
    provider = get_embedding_provider()
    query_embedding = await provider.embed(query)
    return search_chunks(
        query_embedding=query_embedding,
        limit=limit,
        similarity_threshold=similarity_threshold,
    )


async def answer_question(
    question: str,
    limit: int,
    similarity_threshold: float,
    include_context: bool,
) -> AskResponse:
    chunks = await retrieve(
        query=question,
        limit=limit,
        similarity_threshold=similarity_threshold,
    )
    prompt = build_rag_prompt(question, chunks)
    answer = await _generate_answer(prompt, chunks)
    return AskResponse(
        question=question,
        answer=answer,
        sources=chunks,
        prompt=prompt if include_context else None,
    )


async def _generate_answer(prompt: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "The indexed documents do not provide enough information to answer this question."

    if settings.llm_api_url:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(
                f"{settings.llm_api_url.rstrip('/')}/generate",
                json={
                    "prompt": prompt,
                    "temperature": 0.2,
                    "max_tokens": 400,
                },
            )
            response.raise_for_status()
            return response.json()["response"]

    citations = ", ".join(
        f"{chunk.title} chunk {chunk.chunk_index}" for chunk in chunks[:3]
    )
    return (
        "Retrieved relevant context from the document store. "
        "Set LLM_API_URL to the Phase 3 local LLM API to generate a synthesized answer. "
        f"Top sources: {citations}."
    )
