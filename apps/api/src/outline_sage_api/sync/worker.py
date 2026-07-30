from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone

import redis.asyncio as redis
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from outline_sage_api.chunking import chunk_document
from outline_sage_api.clients.es_client import ElasticsearchStore
from outline_sage_api.clients.outline_client import OutlineClient
from outline_sage_api.clients.qdrant_client import QdrantStore
from outline_sage_api.clients.tei_client import TEIEmbeddingClient
from outline_sage_api.hashing import diff_chunks
from outline_sage_api.models import ChunkRecord, Document

logger = logging.getLogger(__name__)


@dataclass
class SyncWorkerDeps:
    redis_client: redis.Redis
    session_factory: async_sessionmaker[AsyncSession]
    outline_client: OutlineClient
    embedding_client: TEIEmbeddingClient
    qdrant: QdrantStore
    es: ElasticsearchStore
    stream_name: str
    consumer_group: str
    consumer_name: str


@dataclass
class _ExistingChunk:
    id: uuid.UUID
    content_hash: str
    qdrant_point_id: str
    es_doc_id: str


async def ensure_consumer_group(deps: SyncWorkerDeps) -> None:
    try:
        await deps.redis_client.xgroup_create(
            deps.stream_name, deps.consumer_group, id="0", mkstream=True
        )
    except redis.ResponseError as exc:
        if "BUSYGROUP" not in str(exc):
            raise


async def process_one_event(deps: SyncWorkerDeps, entry_id: str, fields: dict) -> None:
    doc_id = fields["doc_id"]
    event_type = fields.get("event_type", "update")

    if event_type in ("delete", "trash"):
        await _handle_delete(deps, doc_id)
    else:
        await _handle_upsert(deps, doc_id)

    await deps.redis_client.xack(deps.stream_name, deps.consumer_group, entry_id)


async def _load_existing_chunks(deps: SyncWorkerDeps, doc_id: str) -> dict[int, _ExistingChunk]:
    async with deps.session_factory() as session:
        result = await session.execute(select(ChunkRecord).where(ChunkRecord.source_id == doc_id))
        return {
            record.chunk_index: _ExistingChunk(
                id=record.id,
                content_hash=record.content_hash,
                qdrant_point_id=record.qdrant_point_id,
                es_doc_id=record.es_doc_id,
            )
            for record in result.scalars().all()
        }


async def _handle_delete(deps: SyncWorkerDeps, doc_id: str) -> None:
    existing = await _load_existing_chunks(deps, doc_id)

    await deps.qdrant.delete_points([c.qdrant_point_id for c in existing.values()])
    for chunk in existing.values():
        await deps.es.delete_chunk(chunk.es_doc_id)

    async with deps.session_factory() as session:
        async with session.begin():
            await session.execute(
                ChunkRecord.__table__.delete().where(ChunkRecord.source_id == doc_id)
            )
            doc = await session.get(Document, doc_id)
            if doc:
                doc.deleted_at = datetime.now(timezone.utc)

    logger.info("document deleted from index doc_id=%s chunks=%d", doc_id, len(existing))


async def _handle_upsert(deps: SyncWorkerDeps, doc_id: str) -> None:
    doc_data = await deps.outline_client.get_document(doc_id)
    if not doc_data:
        logger.warning("document not found in Outline, skip doc_id=%s", doc_id)
        return

    title = doc_data.get("title", "")
    content = doc_data.get("text", "")
    url = doc_data.get("url", "")
    collection_id = doc_data.get("collectionId", "")

    new_chunks = chunk_document(content, document_title=title)
    new_by_index = {c.index: c.content for c in new_chunks}

    existing = await _load_existing_chunks(deps, doc_id)
    old_hashes = {index: chunk.content_hash for index, chunk in existing.items()}
    to_embed, to_delete_indexes = diff_chunks(old_hashes, new_by_index)

    stale_qdrant_ids = [existing[i].qdrant_point_id for i in to_delete_indexes]
    stale_es_ids = [existing[i].es_doc_id for i in to_delete_indexes]

    vectors_by_index: dict[int, list[float]] = {}
    if to_embed:
        texts = [new_by_index[i] for i in to_embed]
        vectors = await deps.embedding_client.embed_batch(texts)
        vectors_by_index = dict(zip(to_embed.keys(), vectors))

    qdrant_points = []
    es_writes: list[tuple[str, dict]] = []
    new_ids: dict[int, tuple[str, str]] = {}
    for index, vector in vectors_by_index.items():
        current = existing.get(index)
        point_id = current.qdrant_point_id if current else str(uuid.uuid4())
        es_id = current.es_doc_id if current else f"{doc_id}:{index}"
        new_ids[index] = (point_id, es_id)
        payload = {
            "source_id": doc_id,
            "title": title,
            "url": url,
            "chunk_index": index,
            "content": new_by_index[index],
        }
        qdrant_points.append({"id": point_id, "vector": vector, "payload": payload})
        es_writes.append((es_id, payload))

    if qdrant_points:
        await deps.qdrant.upsert_chunks(qdrant_points)
    for es_id, payload in es_writes:
        await deps.es.index_chunk(es_id, payload)
    if stale_qdrant_ids:
        await deps.qdrant.delete_points(stale_qdrant_ids)
    for es_id in stale_es_ids:
        await deps.es.delete_chunk(es_id)

    async with deps.session_factory() as session:
        async with session.begin():
            doc = await session.get(Document, doc_id)
            if doc is None:
                doc = Document(source_id=doc_id)
                session.add(doc)
            doc.title = title
            doc.url = url
            doc.collection_id = collection_id
            doc.last_synced_at = datetime.now(timezone.utc)

            for index in to_delete_indexes:
                record = await session.get(ChunkRecord, existing[index].id)
                if record:
                    await session.delete(record)

            for index, content_hash_value in to_embed.items():
                point_id, es_id = new_ids[index]
                current = existing.get(index)
                if current:
                    record = await session.get(ChunkRecord, current.id)
                    record.content_hash = content_hash_value
                else:
                    session.add(
                        ChunkRecord(
                            source_id=doc_id,
                            chunk_index=index,
                            content_hash=content_hash_value,
                            qdrant_point_id=point_id,
                            es_doc_id=es_id,
                        )
                    )

    logger.info(
        "document synced doc_id=%s embedded=%d deleted=%d",
        doc_id,
        len(to_embed),
        len(to_delete_indexes),
    )


async def run_worker_loop(deps: SyncWorkerDeps, *, block_ms: int = 5000) -> None:
    await ensure_consumer_group(deps)
    while True:
        response = await deps.redis_client.xreadgroup(
            deps.consumer_group,
            deps.consumer_name,
            {deps.stream_name: ">"},
            count=10,
            block=block_ms,
        )
        if not response:
            continue
        for _stream, entries in response:
            for entry_id, fields in entries:
                try:
                    await process_one_event(deps, entry_id, fields)
                except Exception:
                    logger.exception("failed to process sync event entry_id=%s", entry_id)
