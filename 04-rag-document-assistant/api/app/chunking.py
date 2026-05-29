from dataclasses import dataclass


@dataclass(frozen=True)
class TextChunk:
    index: int
    content: str
    token_estimate: int


def chunk_text(text: str, chunk_size: int, chunk_overlap: int) -> list[TextChunk]:
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    paragraphs = [paragraph.strip() for paragraph in text.split("\n\n") if paragraph.strip()]
    chunks: list[TextChunk] = []
    current = ""

    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.extend(_split_large_text(current, chunk_size, chunk_overlap, len(chunks)))
        current = paragraph

    if current:
        chunks.extend(_split_large_text(current, chunk_size, chunk_overlap, len(chunks)))

    return chunks


def _split_large_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    start_index: int,
) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    start = 0
    index = start_index

    while start < len(text):
        end = min(start + chunk_size, len(text))
        content = text[start:end].strip()
        if content:
            chunks.append(
                TextChunk(
                    index=index,
                    content=content,
                    token_estimate=max(1, len(content.split())),
                )
            )
            index += 1
        if end == len(text):
            break
        start = max(0, end - chunk_overlap)

    return chunks
