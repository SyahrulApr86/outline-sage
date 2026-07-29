"""Wrapper Elasticsearch untuk sparse/BM25 index (TSD-001/TSD-002)."""
from __future__ import annotations

from elasticsearch import AsyncElasticsearch, NotFoundError


class ElasticsearchStore:
    def __init__(self, url: str, index: str) -> None:
        self._client = AsyncElasticsearch(url)
        self._index = index

    async def ensure_index(self) -> None:
        exists = await self._client.indices.exists(index=self._index)
        if not exists:
            await self._client.indices.create(index=self._index)

    async def index_chunk(self, doc_id: str, body: dict) -> None:
        await self._client.index(index=self._index, id=doc_id, document=body)

    async def delete_chunk(self, doc_id: str) -> None:
        try:
            await self._client.delete(index=self._index, id=doc_id)
        except NotFoundError:
            pass

    async def search(self, query: str, top_k: int) -> list[tuple[str, float]]:
        resp = await self._client.search(
            index=self._index,
            query={"match": {"content": query}},
            size=top_k,
        )
        return [(hit["_id"], hit["_score"]) for hit in resp["hits"]["hits"]]

    async def close(self) -> None:
        await self._client.close()
