"""Fake implementation external service untuk integration test tanpa GPU/model sungguhan."""
from __future__ import annotations


class FakeQdrantStore:
    def __init__(self) -> None:
        self.points: dict[str, dict] = {}

    async def ensure_collection(self) -> None:
        pass

    async def upsert_chunks(self, points: list[dict]) -> None:
        for p in points:
            self.points[p["id"]] = {"vector": p["vector"], "payload": p["payload"]}

    async def delete_points(self, point_ids: list[str]) -> None:
        for pid in point_ids:
            self.points.pop(pid, None)

    async def search(self, vector: list[float], top_k: int) -> list[tuple[str, float, dict]]:
        items = list(self.points.items())[:top_k]
        return [(pid, 1.0, data["payload"]) for pid, data in items]

    async def close(self) -> None:
        pass


class FakeElasticsearchStore:
    def __init__(self) -> None:
        self.docs: dict[str, dict] = {}

    async def ensure_index(self) -> None:
        pass

    async def index_chunk(self, doc_id: str, body: dict) -> None:
        self.docs[doc_id] = body

    async def delete_chunk(self, doc_id: str) -> None:
        self.docs.pop(doc_id, None)

    async def search(self, query: str, top_k: int) -> list[tuple[str, float, dict]]:
        items = list(self.docs.items())[:top_k]
        return [(doc_id, 1.0, body) for doc_id, body in items]

    async def close(self) -> None:
        pass


class FailingStore:
    """Simulasi backend down (dipakai untuk test degradasi hybrid retrieval)."""

    async def search(self, *args, **kwargs):
        raise ConnectionError("backend unavailable")


class FakeOutlineClient:
    def __init__(self, documents: dict[str, dict]) -> None:
        self._documents = documents

    async def export_document(self, document_id: str) -> dict | None:
        return self._documents.get(document_id)


class FakeEmbeddingClient:
    def __init__(self) -> None:
        self.call_count = 0

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        return [[float(len(t) % 97)] * 4 for t in texts]


class FakeRerankerClient:
    async def rerank(self, query: str, documents: list[str]) -> list[dict]:
        return [{"index": i, "score": 1.0 - (i * 0.01)} for i in range(len(documents))]
