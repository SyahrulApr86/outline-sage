from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SAGE_", env_file=".env", extra="ignore")

    outline_api_url: str = ""
    outline_api_token: str = ""
    outline_webhook_secret: str = "changeme"

    database_url: str = "postgresql+asyncpg://sage:sage@localhost:5432/sage"

    redis_url: str = "redis://localhost:6380/0"
    sync_stream_name: str = "sage:sync:events"
    sync_consumer_group: str = "sage-sync-workers"
    debounce_window_seconds: int = 2

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "sage_chunks"
    vector_dim: int = 1024

    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "sage_chunks"

    tei_embedding_url: str = "http://localhost:8081"
    tei_reranker_url: str = "http://localhost:8082"
    embedding_model_name: str = "BAAI/bge-m3"
    reranker_model_name: str = "BAAI/bge-reranker-v2-m3"

    vllm_base_url: str = "http://localhost:8000/v1"
    chat_model_name: str = "Qwen/Qwen3-14B"

    retrieval_top_k: int = 20
    rerank_top_k: int = 6
    rrf_k: int = 60

    keycloak_issuer: str = ""
    keycloak_audience: str = ""

    chunk_size: int = 1024
    chunk_overlap: int = 100


def get_settings() -> Settings:
    return Settings()
