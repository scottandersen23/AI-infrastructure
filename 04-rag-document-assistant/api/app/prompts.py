from api.app.schemas import RetrievedChunk


RAG_SYSTEM_PROMPT = """You are a source-grounded document assistant.
Answer only from the supplied context.
If the context does not contain the answer, say that the documents do not provide enough information.
Always cite source titles and chunk numbers when possible."""


def build_rag_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    context = "\n\n".join(
        (
            f"[Source {index}: {chunk.title}, chunk {chunk.chunk_index}, "
            f"similarity {chunk.similarity}]\n{chunk.content}"
        )
        for index, chunk in enumerate(chunks, start=1)
    )
    return f"""{RAG_SYSTEM_PROMPT}

Context:
{context}

Question:
{question}

Answer with concise reasoning and source citations.
"""
