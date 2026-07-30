from __future__ import annotations

import logging

import redis.asyncio as redis

from outline_sage_api.sync.debounce import Debouncer

logger = logging.getLogger(__name__)


async def run_expiry_listener(
    redis_client: redis.Redis,
    debouncer: Debouncer,
    stream_name: str,
) -> None:
    pubsub = redis_client.pubsub()
    await pubsub.psubscribe("__keyevent@0__:expired")

    async for message in pubsub.listen():
        if message["type"] != "pmessage":
            continue

        key = message["data"]
        doc_id = Debouncer.doc_id_from_expired_key(key)
        if not doc_id:
            continue

        meta = await debouncer.read_meta(doc_id)
        event_type = meta.get("event_type", "update")

        await redis_client.xadd(stream_name, {"doc_id": doc_id, "event_type": event_type})
        await debouncer.clear_meta(doc_id)
        logger.info("sync event queued doc_id=%s event_type=%s", doc_id, event_type)
