from __future__ import annotations

import asyncio
import logging

import redis.asyncio as redis

from outline_sage_api.clients.es_client import ElasticsearchStore
from outline_sage_api.clients.outline_client import OutlineClient
from outline_sage_api.clients.qdrant_client import QdrantStore
from outline_sage_api.clients.tei_client import TEIEmbeddingClient
from outline_sage_api.config import get_settings
from outline_sage_api.db import create_engine, create_session_factory
from outline_sage_api.sync.debounce import Debouncer
from outline_sage_api.sync.expiry_listener import run_expiry_listener
from outline_sage_api.sync.worker import SyncWorkerDeps, run_worker_loop

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()

    engine = create_engine(settings.database_url)
    session_factory = create_session_factory(engine)

    # socket_timeout must exceed XREADGROUP's BLOCK duration in run_worker_loop
    redis_client = redis.from_url(settings.redis_url, decode_responses=True, socket_timeout=15)
    debouncer = Debouncer(redis_client, settings.debounce_window_seconds)

    qdrant = QdrantStore(settings.qdrant_url, settings.qdrant_collection, settings.vector_dim)
    await qdrant.ensure_collection()
    es = ElasticsearchStore(settings.elasticsearch_url, settings.elasticsearch_index)
    await es.ensure_index()

    embedding_client = TEIEmbeddingClient(settings.tei_embedding_url)
    outline_client = OutlineClient(settings.outline_api_url, settings.outline_api_token)

    sync_deps = SyncWorkerDeps(
        redis_client=redis_client,
        session_factory=session_factory,
        outline_client=outline_client,
        embedding_client=embedding_client,
        qdrant=qdrant,
        es=es,
        stream_name=settings.sync_stream_name,
        consumer_group=settings.sync_consumer_group,
        consumer_name="worker-1",
    )

    logger.info("Sync Worker started")
    try:
        await asyncio.gather(
            run_expiry_listener(redis_client, debouncer, settings.sync_stream_name),
            run_worker_loop(sync_deps),
        )
    finally:
        await redis_client.close()
        await qdrant.close()
        await es.close()
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
