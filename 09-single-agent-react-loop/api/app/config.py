from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "single-agent-react-api"
    environment: str = "local"
    database_url: str = "postgresql://agent:agent@localhost:5435/agent"
    registry_url: str = "http://localhost:8008"
    executor_url: str = "http://localhost:8009"
    max_steps: int = 4
    timeout_ms: int = 30_000
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
