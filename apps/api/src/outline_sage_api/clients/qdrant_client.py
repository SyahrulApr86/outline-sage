"""Wrapper Qdrant untuk dense vector store (TSD-001/TSD-002)."""
from __future__ import annotations

from qdrant_client import AsyncQdrantClient, models


class QdrantStore:
    def __init__(self, url: str, collection: str, vector_dim: int) -> None:
        self._client = AsyncQdrantClient(url=url)
        self._collection = collection
        self._vector_dim = vector_dim

    async def ensure_collection(self) -> None:
        exists = await self._client.collection_exists(self._collection)
        if not exists:
            await self._client.create_collection(
                collection_name=self._collection,
                vectors_config=models.VectorParams(size=self._vector_dim, distance=models.Distance.COSINE),
            )

    async def upsert_chunks(self, points: list[dict]) -> None:
        """points: [{"id": str, "vector": list[float], "payload": dict}]."""
        await self._client.upsert(
            collection_name=self._collection,
            points=[
                models.PointStruct(id=p["id"], vector=p["vector"], payload=p.get("payload", {}))
                for p in points
            ],
        )

    async def delete_points(self, point_ids: list[str]) -> None:
        if not point_ids:
            return
        await self._client.delete(
            collection_name=self._collection,
            points_selector=models.PointIdsList(points=point_ids),
        )

    async def search(self, vector: list[float], top_k: int) -> list[tuple[str, float, dict]]:
        results = await self._client.query_points(
            collection_name=self._collection,
            query=vector,
            limit=top_k,
            with_payload=True,
        )
        return [(str(point.id), point.score, point.payload or {}) for point in results.points]

    async def close(self) -> None:
        await self._client.close()
