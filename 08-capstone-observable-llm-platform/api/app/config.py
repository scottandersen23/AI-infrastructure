from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "capstone-api-gateway"
    environment: str = "local"
    llm_service_url: str = "http://localhost:8011"
    rag_service_url: str = "http://localhost:8012"
    observability_db_path: str = "data/capstone_metrics.db"
    redis_url: str = "redis://localhost:6379/0"
    request_timeout_seconds: int = 120
    default_model: str = "capstone-mock-llm"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
