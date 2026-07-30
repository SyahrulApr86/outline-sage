"""One-off: enqueue every existing Outline document for sync.

The sync pipeline only reacts to webhooks (future edits), so documents that
existed before the webhook was registered are never indexed on their own.
Run this once after deploy to bootstrap the index, then webhooks take over.
"""
from __future__ import annotations

import asyncio
import logging

import redis.asyncio as redis

from outline_sage_api.clients.outline_client import OutlineClient
from outline_sage_api.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s - %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    settings = get_settings()
    outline_client = OutlineClient(settings.outline_api_url, settings.outline_api_token)
    redis_client = redis.from_url(settings.redis_url, decode_responses=True)

    doc_ids = await outline_client.list_all_document_ids()
    logger.info("found %d documents", len(doc_ids))

    for doc_id in doc_ids:
        await redis_client.xadd(settings.sync_stream_name, {"doc_id": doc_id, "event_type": "update"})

    logger.info("enqueued %d documents to %s", len(doc_ids), settings.sync_stream_name)
    await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
