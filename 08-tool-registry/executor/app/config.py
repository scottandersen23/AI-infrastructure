from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "tool-executor"
    environment: str = "local"
    registry_url: str = "http://localhost:8008"
    database_url: str = "postgresql://tools:tools@localhost:5434/tools"
    rag_service_url: str = "http://localhost:8012"
    metrics_url: str = "http://localhost:8010"
    jobs_api_url: str = "http://localhost:8010"
    otel_exporter: str = "console"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
