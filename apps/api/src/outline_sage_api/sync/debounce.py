from __future__ import annotations

import redis.asyncio as redis

DEBOUNCE_KEY_PREFIX = "debounce:pending:"
DEBOUNCE_META_PREFIX = "debounce:meta:"


class Debouncer:
    def __init__(self, redis_client: redis.Redis, window_seconds: int) -> None:
        self._redis = redis_client
        self._window = window_seconds

    async def register_event(self, doc_id: str, event_type: str) -> None:
        """Refresh window debounce untuk doc_id dan simpan tipe event terbaru."""
        await self._redis.hset(f"{DEBOUNCE_META_PREFIX}{doc_id}", mapping={"event_type": event_type})
        await self._redis.set(f"{DEBOUNCE_KEY_PREFIX}{doc_id}", "1", ex=self._window)

    async def read_meta(self, doc_id: str) -> dict[str, str]:
        return await self._redis.hgetall(f"{DEBOUNCE_META_PREFIX}{doc_id}")

    async def clear_meta(self, doc_id: str) -> None:
        await self._redis.delete(f"{DEBOUNCE_META_PREFIX}{doc_id}")

    @staticmethod
    def doc_id_from_expired_key(key: str) -> str | None:
        if not key.startswith(DEBOUNCE_KEY_PREFIX):
            return None
        return key[len(DEBOUNCE_KEY_PREFIX) :]
