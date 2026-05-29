import asyncio
import json
import time
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

import httpx

from api.app.config import (
    DEFAULT_MODEL,
    LLM_RUNTIME,
    OLLAMA_BASE_URL,
    REQUEST_TIMEOUT_SECONDS,
)
from api.app.schemas import GenerateRequest, GenerateResponse, ModelInfo, TokenUsage


class LocalLLMClient(ABC):
    runtime: str

    @abstractmethod
    async def health(self) -> str:
        """Return backend health status."""

    @abstractmethod
    async def list_models(self) -> list[ModelInfo]:
        """Return locally available models."""

    @abstractmethod
    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        """Run a non-streaming generation request."""

    @abstractmethod
    async def stream_generate(self, request: GenerateRequest) -> AsyncIterator[str]:
        """Yield generated text chunks."""


class OllamaClient(LocalLLMClient):
    runtime = "ollama"

    def __init__(self, base_url: str = OLLAMA_BASE_URL) -> None:
        self.base_url = base_url.rstrip("/")

    async def health(self) -> str:
        async with httpx.AsyncClient(timeout=5) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
        return "ok"

    async def list_models(self) -> list[ModelInfo]:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            data = response.json()

        models: list[ModelInfo] = []
        for model in data.get("models", []):
            details = model.get("details") or {}
            models.append(
                ModelInfo(
                    name=model.get("name", "unknown"),
                    runtime=self.runtime,
                    size=model.get("size"),
                    modified_at=model.get("modified_at"),
                    quantization=details.get("quantization_level"),
                )
            )
        return models

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        model = request.model or DEFAULT_MODEL
        payload = self._build_payload(request, model, stream=False)
        started = time.perf_counter()

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.post(f"{self.base_url}/api/generate", json=payload)
            response.raise_for_status()
            data = response.json()

        latency_ms = (time.perf_counter() - started) * 1000
        completion_tokens = data.get("eval_count")
        prompt_tokens = data.get("prompt_eval_count")
        tokens_per_second = self._tokens_per_second(
            completion_tokens=completion_tokens,
            eval_duration_ns=data.get("eval_duration"),
            fallback_latency_ms=latency_ms,
        )

        return GenerateResponse(
            model=model,
            runtime=self.runtime,
            response=data.get("response", ""),
            latency_ms=round(latency_ms, 2),
            tokens_per_second=tokens_per_second,
            usage=TokenUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=self._total_tokens(prompt_tokens, completion_tokens),
            ),
        )

    async def stream_generate(self, request: GenerateRequest) -> AsyncIterator[str]:
        model = request.model or DEFAULT_MODEL
        payload = self._build_payload(request, model, stream=True)

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json=payload,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line:
                        continue
                    event = json.loads(line)
                    chunk = event.get("response")
                    if chunk:
                        yield chunk

    @staticmethod
    def _build_payload(
        request: GenerateRequest,
        model: str,
        stream: bool,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "prompt": request.prompt,
            "stream": stream,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            },
        }
        if request.system:
            payload["system"] = request.system
        return payload

    @staticmethod
    def _tokens_per_second(
        completion_tokens: int | None,
        eval_duration_ns: int | None,
        fallback_latency_ms: float,
    ) -> float | None:
        if not completion_tokens:
            return None
        if eval_duration_ns:
            return round(completion_tokens / (eval_duration_ns / 1_000_000_000), 2)
        return round(completion_tokens / (fallback_latency_ms / 1000), 2)

    @staticmethod
    def _total_tokens(
        prompt_tokens: int | None,
        completion_tokens: int | None,
    ) -> int | None:
        if prompt_tokens is None and completion_tokens is None:
            return None
        return (prompt_tokens or 0) + (completion_tokens or 0)


class MockLLMClient(LocalLLMClient):
    runtime = "mock"

    async def health(self) -> str:
        return "ok"

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                name="mock-local-model",
                runtime=self.runtime,
                quantization="none",
            )
        ]

    async def generate(self, request: GenerateRequest) -> GenerateResponse:
        started = time.perf_counter()
        await asyncio.sleep(0.05)
        text = (
            "Mock local LLM response: "
            f"{request.prompt[:120]}"
            "\n\nThis runtime is for API and benchmark smoke tests."
        )
        completion_tokens = max(1, len(text.split()))
        latency_ms = (time.perf_counter() - started) * 1000
        return GenerateResponse(
            model=request.model or "mock-local-model",
            runtime=self.runtime,
            response=text,
            latency_ms=round(latency_ms, 2),
            tokens_per_second=round(completion_tokens / (latency_ms / 1000), 2),
            usage=TokenUsage(
                prompt_tokens=len(request.prompt.split()),
                completion_tokens=completion_tokens,
                total_tokens=len(request.prompt.split()) + completion_tokens,
            ),
        )

    async def stream_generate(self, request: GenerateRequest) -> AsyncIterator[str]:
        text = (
            "Mock streaming response for local LLM serving. "
            f"Prompt preview: {request.prompt[:80]}"
        )
        for token in text.split():
            await asyncio.sleep(0.02)
            yield f"{token} "


def get_llm_client() -> LocalLLMClient:
    if LLM_RUNTIME.lower() == "mock":
        return MockLLMClient()
    return OllamaClient()
