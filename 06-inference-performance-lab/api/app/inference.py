import asyncio
import time

from api.app.config import settings
from api.app.schemas import GenerateRequest, GenerateResponse


_semaphore = asyncio.Semaphore(settings.max_concurrent_requests)


async def generate(request: GenerateRequest) -> GenerateResponse:
    started = time.perf_counter()
    queue_started = time.perf_counter()

    async with _semaphore:
        queue_wait_ms = (time.perf_counter() - queue_started) * 1000
        prompt_tokens = _estimate_tokens(request.prompt)
        prompt_eval_ms = prompt_tokens * settings.prompt_token_latency_ms
        generation_ms = request.max_tokens * settings.base_token_latency_ms

        await asyncio.sleep((prompt_eval_ms + generation_ms) / 1000)

        total_latency_ms = (time.perf_counter() - started) * 1000
        tokens_per_second = request.max_tokens / max(generation_ms / 1000, 0.001)
        estimated_vram_mb = _estimate_vram(prompt_tokens + request.max_tokens)

        return GenerateResponse(
            model=settings.model_name,
            response=(
                "Mock inference response generated for performance testing. "
                "Use this endpoint to study latency, throughput, queuing, and concurrency."
            ),
            prompt_tokens=prompt_tokens,
            completion_tokens=request.max_tokens,
            total_tokens=prompt_tokens + request.max_tokens,
            queue_wait_ms=round(queue_wait_ms, 2),
            prompt_eval_ms=round(prompt_eval_ms, 2),
            generation_ms=round(generation_ms, 2),
            total_latency_ms=round(total_latency_ms, 2),
            tokens_per_second=round(tokens_per_second, 2),
            estimated_vram_mb=round(estimated_vram_mb, 2),
        )


def _estimate_tokens(text: str) -> int:
    return max(1, int(len(text.split()) * 1.3))


def _estimate_vram(total_tokens: int) -> float:
    return min(
        settings.simulated_vram_mb,
        512 + (total_tokens * settings.kv_cache_mb_per_token),
    )
