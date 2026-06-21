from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "tool-registry-api"
    environment: str = "local"
    database_url: str = "postgresql://tools:tools@localhost:5434/tools"
    otel_exporter: str = "console"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
