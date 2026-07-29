"""Integration test hybrid retrieval: FSD-002 AC-1, AC-2, AC-5, AC-6."""
from __future__ import annotations

import pytest

from outline_sage_api.retrieval import HybridRetriever
from tests.integration.fakes import FailingStore, FakeElasticsearchStore, FakeEmbeddingClient, FakeQdrantStore, FakeRerankerClient


async def _seed(qdrant: FakeQdrantStore, es: FakeElasticsearchStore) -> None:
    await qdrant.upsert_chunks(
        [
            {"id": "p1", "vector": [1.0], "payload": {"source_id": "d1", "title": "A", "url": "u1", "content": "isi p1"}},
            {"id": "p2", "vector": [1.0], "payload": {"source_id": "d2", "title": "B", "url": "u2", "content": "isi p2"}},
        ]
    )
    await es.index_chunk("p2", {"source_id": "d2", "title": "B", "url": "u2", "content": "isi p2"})
    await es.index_chunk("p3", {"source_id": "d3", "title": "C", "url": "u3", "content": "isi p3"})


@pytest.mark.asyncio
async def test_hybrid_retrieval_fuses_dense_and_sparse_results():
    qdrant = FakeQdrantStore()
    es = FakeElasticsearchStore()
    await _seed(qdrant, es)

    retriever = HybridRetriever(qdrant, es, FakeEmbeddingClient(), FakeRerankerClient(), top_k=10, rerank_top_k=10)
    results = await retriever.retrieve("query apapun")

    result_ids = {r.doc_id for r in results}
    assert result_ids == {"p1", "p2", "p3"}


@pytest.mark.asyncio
async def test_qdrant_down_degrades_to_sparse_only():
    es = FakeElasticsearchStore()
    await es.index_chunk("p3", {"source_id": "d3", "title": "C", "url": "u3", "content": "isi p3"})

    retriever = HybridRetriever(FailingStore(), es, FakeEmbeddingClient(), FakeRerankerClient(), top_k=10, rerank_top_k=10)
    results = await retriever.retrieve("query apapun")

    assert [r.doc_id for r in results] == ["p3"]


@pytest.mark.asyncio
async def test_elasticsearch_down_degrades_to_dense_only():
    qdrant = FakeQdrantStore()
    await qdrant.upsert_chunks(
        [{"id": "p1", "vector": [1.0], "payload": {"source_id": "d1", "title": "A", "url": "u1", "content": "isi p1"}}]
    )

    retriever = HybridRetriever(qdrant, FailingStore(), FakeEmbeddingClient(), FakeRerankerClient(), top_k=10, rerank_top_k=10)
    results = await retriever.retrieve("query apapun")

    assert [r.doc_id for r in results] == ["p1"]


@pytest.mark.asyncio
async def test_both_backends_down_returns_empty_without_raising():
    retriever = HybridRetriever(FailingStore(), FailingStore(), FakeEmbeddingClient(), FakeRerankerClient())
    results = await retriever.retrieve("query apapun")

    assert results == []
