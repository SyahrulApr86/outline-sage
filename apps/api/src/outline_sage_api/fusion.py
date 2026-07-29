"""Reciprocal rank fusion untuk hybrid retrieval (TSD-002 bagian 6)."""
from __future__ import annotations


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    k: int = 60,
) -> list[tuple[str, float]]:
    """Gabungkan beberapa ranked list (list doc_id terurut) jadi satu skor gabungan.

    score(d) = sum(1 / (k + rank_i(d))) untuk tiap list tempat d muncul, rank mulai dari 1.
    Dipilih alih-alih weighted score karena skor dense (cosine) dan BM25 tidak sebanding skalanya.
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, doc_id in enumerate(ranked, start=1):
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)

    return sorted(scores.items(), key=lambda item: item[1], reverse=True)
