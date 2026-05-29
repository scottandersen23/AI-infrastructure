from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "ai-observability-api"
    environment: str = "local"
    otel_exporter: str = "console"
    otlp_endpoint: str = "http://localhost:4317"
    metrics_db_path: str = "observability_metrics.db"
    model_name: str = "mock-local-llm"
    retrieval_top_k: int = 3

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
