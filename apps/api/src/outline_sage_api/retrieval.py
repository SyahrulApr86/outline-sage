from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from outline_sage_api.clients.es_client import ElasticsearchStore
from outline_sage_api.clients.qdrant_client import QdrantStore
from outline_sage_api.clients.tei_client import TEIEmbeddingClient, TEIRerankerClient
from outline_sage_api.fusion import reciprocal_rank_fusion

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    doc_id: str
    payload: dict


class HybridRetriever:
    def __init__(
        self,
        qdrant: QdrantStore,
        es: ElasticsearchStore,
        embedding_client: TEIEmbeddingClient,
        reranker_client: TEIRerankerClient,
        top_k: int = 20,
        rerank_top_k: int = 6,
        rrf_k: int = 60,
    ) -> None:
        self._qdrant = qdrant
        self._es = es
        self._embedding_client = embedding_client
        self._reranker_client = reranker_client
        self._top_k = top_k
        self._rerank_top_k = rerank_top_k
        self._rrf_k = rrf_k

    async def _safe_dense_search(self, vector: list[float]) -> list[tuple[str, float, dict]]:
        try:
            return await self._qdrant.search(vector, self._top_k)
        except Exception:
            logger.exception("dense search (Qdrant) failed, degrading to sparse-only")
            return []

    async def _safe_sparse_search(self, query: str) -> list[tuple[str, float, dict]]:
        try:
            return await self._es.search(query, self._top_k)
        except Exception:
            logger.exception("sparse search (Elasticsearch) failed, degrading to dense-only")
            return []

    async def retrieve(self, query: str) -> list[RetrievedChunk]:
        query_vector = (await self._embedding_client.embed_batch([query]))[0]

        dense_results, sparse_results = await asyncio.gather(
            self._safe_dense_search(query_vector),
            self._safe_sparse_search(query),
        )

        payload_by_id: dict[str, dict] = {}
        for doc_id, _score, payload in [*dense_results, *sparse_results]:
            payload_by_id.setdefault(doc_id, payload)

        dense_ids = [doc_id for doc_id, _, _ in dense_results]
        sparse_ids = [doc_id for doc_id, _, _ in sparse_results]

        if not dense_ids and not sparse_ids:
            return []

        fused = reciprocal_rank_fusion([dense_ids, sparse_ids], k=self._rrf_k)
        candidate_ids = [doc_id for doc_id, _ in fused][: self._top_k]

        if not candidate_ids:
            return []

        candidates = [RetrievedChunk(doc_id=cid, payload=payload_by_id[cid]) for cid in candidate_ids]
        return await self._rerank(query, candidates)

    async def _rerank(self, query: str, candidates: list[RetrievedChunk]) -> list[RetrievedChunk]:
        try:
            texts = [c.payload.get("content", "") for c in candidates]
            scored = await self._reranker_client.rerank(query, texts)
            ordered = sorted(scored, key=lambda item: item["score"], reverse=True)
            return [candidates[item["index"]] for item in ordered[: self._rerank_top_k]]
        except Exception:
            logger.exception("reranker failed, fallback to fusion order")
            return candidates[: self._rerank_top_k]
