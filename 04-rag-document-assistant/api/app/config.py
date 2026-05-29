from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql://rag:rag@localhost:5433/rag"
    embedding_provider: str = "hash"
    embedding_dimension: int = 384
    ollama_base_url: str = "http://localhost:11434"
    ollama_embedding_model: str = "nomic-embed-text"
    llm_api_url: str | None = None
    chunk_size: int = 900
    chunk_overlap: int = 150
    retrieval_limit: int = 5
    similarity_threshold: float = 0.15

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
