"""Integration test sync worker: FSD-001 AC-1, AC-3, AC-4, AC-5, AC-6."""
from __future__ import annotations

import asyncio

import pytest

from outline_sage_api.sync.debounce import Debouncer
from outline_sage_api.sync.worker import SyncWorkerDeps, ensure_consumer_group, process_one_event
from tests.integration.fakes import FakeElasticsearchStore, FakeEmbeddingClient, FakeOutlineClient, FakeQdrantStore

STREAM = "test:sync:events"
GROUP = "test-group"


async def _read_one(redis_client, consumer_name: str = "worker-1"):
    response = await redis_client.xreadgroup(GROUP, consumer_name, {STREAM: ">"}, count=1, block=2000)
    [(_stream, entries)] = response
    [(entry_id, fields)] = entries
    return entry_id, fields


@pytest.mark.asyncio
async def test_webhook_update_event_syncs_to_both_stores(redis_client, session_factory):
    outline_client = FakeOutlineClient(
        {"doc-1": {"title": "Panduan", "text": "# Judul\nIsi dokumen singkat.", "url": "http://x/doc-1", "collectionId": "col-1"}}
    )
    qdrant = FakeQdrantStore()
    es = FakeElasticsearchStore()
    deps = SyncWorkerDeps(
        redis_client=redis_client,
        session_factory=session_factory,
        outline_client=outline_client,
        embedding_client=FakeEmbeddingClient(),
        qdrant=qdrant,
        es=es,
        stream_name=STREAM,
        consumer_group=GROUP,
        consumer_name="worker-1",
    )
    await ensure_consumer_group(deps)

    await redis_client.xadd(STREAM, {"doc_id": "doc-1", "event_type": "update"})
    entry_id, fields = await _read_one(redis_client)
    await process_one_event(deps, entry_id, fields)

    assert len(qdrant.points) == 1
    assert len(es.docs) == 1


@pytest.mark.asyncio
async def test_delete_event_removes_entries_from_both_stores(redis_client, session_factory):
    outline_client = FakeOutlineClient(
        {"doc-2": {"title": "Doc", "text": "# A\nisi a", "url": "http://x/doc-2", "collectionId": "col-1"}}
    )
    qdrant = FakeQdrantStore()
    es = FakeElasticsearchStore()
    deps = SyncWorkerDeps(
        redis_client=redis_client,
        session_factory=session_factory,
        outline_client=outline_client,
        embedding_client=FakeEmbeddingClient(),
        qdrant=qdrant,
        es=es,
        stream_name=STREAM,
        consumer_group=GROUP,
        consumer_name="worker-1",
    )
    await ensure_consumer_group(deps)

    await redis_client.xadd(STREAM, {"doc_id": "doc-2", "event_type": "update"})
    entry_id, fields = await _read_one(redis_client)
    await process_one_event(deps, entry_id, fields)
    assert len(qdrant.points) == 1

    await redis_client.xadd(STREAM, {"doc_id": "doc-2", "event_type": "delete"})
    entry_id, fields = await _read_one(redis_client)
    await process_one_event(deps, entry_id, fields)

    assert len(qdrant.points) == 0
    assert len(es.docs) == 0


@pytest.mark.asyncio
async def test_unchanged_document_is_not_reembedded(redis_client, session_factory):
    outline_client = FakeOutlineClient(
        {"doc-3": {"title": "Doc", "text": "# A\nisi tetap sama", "url": "http://x/doc-3", "collectionId": "col-1"}}
    )
    qdrant = FakeQdrantStore()
    es = FakeElasticsearchStore()
    embedding_client = FakeEmbeddingClient()
    deps = SyncWorkerDeps(
        redis_client=redis_client,
        session_factory=session_factory,
        outline_client=outline_client,
        embedding_client=embedding_client,
        qdrant=qdrant,
        es=es,
        stream_name=STREAM,
        consumer_group=GROUP,
        consumer_name="worker-1",
    )
    await ensure_consumer_group(deps)

    await redis_client.xadd(STREAM, {"doc_id": "doc-3", "event_type": "update"})
    entry_id, fields = await _read_one(redis_client)
    await process_one_event(deps, entry_id, fields)
    assert embedding_client.call_count == 1

    # sync kedua kali, konten tidak berubah sama sekali
    await redis_client.xadd(STREAM, {"doc_id": "doc-3", "event_type": "update"})
    entry_id, fields = await _read_one(redis_client)
    await process_one_event(deps, entry_id, fields)

    assert embedding_client.call_count == 1  # tidak ada panggilan embed tambahan


@pytest.mark.asyncio
async def test_debounce_collapses_rapid_webhooks_for_same_document(redis_client):
    debouncer = Debouncer(redis_client, window_seconds=1)

    await debouncer.register_event("doc-4", "update")
    await asyncio.sleep(0.3)
    await debouncer.register_event("doc-4", "update")  # refresh TTL, mensimulasikan autosave beruntun

    meta = await debouncer.read_meta("doc-4")
    assert meta["event_type"] == "update"

    exists_before_expiry = await redis_client.exists("debounce:pending:doc-4")
    assert exists_before_expiry == 1

    await asyncio.sleep(1.2)
    exists_after_expiry = await redis_client.exists("debounce:pending:doc-4")
    assert exists_after_expiry == 0
