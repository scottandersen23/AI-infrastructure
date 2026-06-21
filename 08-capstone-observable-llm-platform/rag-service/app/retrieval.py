import hashlib
from pathlib import Path

from app.schemas import Source


def load_chunks() -> list[Source]:
    sample_dir = Path(__file__).resolve().parents[2] / "sample-docs"
    chunks: list[Source] = []
    for path in sorted(sample_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        for index, chunk in enumerate(part for part in content.split("\n\n") if part.strip()):
            chunks.append(
                Source(
                    title=path.stem.replace("-", " ").title(),
                    chunk_index=index,
                    similarity=0.0,
                    content=chunk.strip(),
                )
            )
    return chunks


def search(query: str, limit: int) -> list[Source]:
    query_tokens = set(_tokenize(query))
    scored: list[Source] = []
    for chunk in load_chunks():
        chunk_tokens = set(_tokenize(chunk.content))
        overlap = len(query_tokens & chunk_tokens)
        stable_noise = int(hashlib.sha256(chunk.content.encode("utf-8")).hexdigest()[:2], 16) / 1000
        similarity = round(min(0.25 + (overlap / max(len(query_tokens), 1)) + stable_noise, 0.99), 4)
        if similarity >= 0.3:
            scored.append(chunk.model_copy(update={"similarity": similarity}))
    scored.sort(key=lambda source: source.similarity, reverse=True)
    return scored[:limit]


def _tokenize(text: str) -> list[str]:
    return [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split() if token.strip()]
