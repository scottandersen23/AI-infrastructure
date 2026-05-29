from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_name: str = "mock-inference-model"
    base_token_latency_ms: float = 18.0
    prompt_token_latency_ms: float = 1.5
    max_concurrent_requests: int = 4
    simulated_vram_mb: int = 4096
    kv_cache_mb_per_token: float = 0.02

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
