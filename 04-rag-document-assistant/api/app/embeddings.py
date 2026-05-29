import hashlib
import math
from abc import ABC, abstractmethod

import httpx

from api.app.config import settings


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        """Return an embedding vector for a text input."""


class HashEmbeddingProvider(EmbeddingProvider):
    """Deterministic local embedding provider for repeatable smoke tests."""

    def __init__(self, dimension: int) -> None:
        self.dimension = dimension

    async def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        tokens = [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split()]
        for token in tokens:
            if not token:
                continue
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign
        return _normalize(vector)


class OllamaEmbeddingProvider(EmbeddingProvider):
    def __init__(self, base_url: str, model: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, text: str) -> list[float]:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            response.raise_for_status()
            embedding = response.json()["embedding"]
        if len(embedding) != settings.embedding_dimension:
            raise ValueError(
                "Ollama embedding dimension does not match EMBEDDING_DIMENSION: "
                f"{len(embedding)} != {settings.embedding_dimension}"
            )
        return embedding


def get_embedding_provider() -> EmbeddingProvider:
    if settings.embedding_provider.lower() == "ollama":
        return OllamaEmbeddingProvider(
            base_url=settings.ollama_base_url,
            model=settings.ollama_embedding_model,
        )
    return HashEmbeddingProvider(dimension=settings.embedding_dimension)


def to_vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{value:.8f}" for value in values) + "]"


def _normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
