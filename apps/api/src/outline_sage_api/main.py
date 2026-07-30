from __future__ import annotations

import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI

from outline_sage_api.api.chat import chat_router
from outline_sage_api.api.webhook import webhook_router
from outline_sage_api.auth import KeycloakAuthenticator
from outline_sage_api.clients.es_client import ElasticsearchStore
from outline_sage_api.clients.llm_client import LLMClient
from outline_sage_api.clients.qdrant_client import QdrantStore
from outline_sage_api.clients.tei_client import TEIEmbeddingClient, TEIRerankerClient
from outline_sage_api.config import get_settings
from outline_sage_api.db import create_engine, create_session_factory, init_db
from outline_sage_api.retrieval import HybridRetriever
from outline_sage_api.sync.debounce import Debouncer

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)
    await init_db(engine)
    app.state.engine = engine
    app.state.session_factory = session_factory

    redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis_client = redis_client
    app.state.debouncer = Debouncer(redis_client, settings.debounce_window_seconds)

    qdrant = QdrantStore(settings.qdrant_url, settings.qdrant_collection, settings.vector_dim)
    await qdrant.ensure_collection()
    es = ElasticsearchStore(settings.elasticsearch_url, settings.elasticsearch_index)
    await es.ensure_index()

    embedding_client = TEIEmbeddingClient(settings.tei_embedding_url)
    reranker_client = TEIRerankerClient(settings.tei_reranker_url)
    llm_client = LLMClient(settings.vllm_base_url, settings.chat_model_name)

    app.state.retriever = HybridRetriever(
        qdrant,
        es,
        embedding_client,
        reranker_client,
        top_k=settings.retrieval_top_k,
        rerank_top_k=settings.rerank_top_k,
        rrf_k=settings.rrf_k,
    )
    app.state.llm_client = llm_client
    app.state.authenticator = KeycloakAuthenticator(settings.keycloak_issuer, settings.keycloak_audience)

    logger.info("outline-sage API Service started")
    yield

    await redis_client.close()
    await qdrant.close()
    await es.close()
    await engine.dispose()


app = FastAPI(title="outline-sage API", lifespan=lifespan)
app.include_router(webhook_router)
app.include_router(chat_router)


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}
