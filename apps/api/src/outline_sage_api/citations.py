"""Ekstraksi citation dari jawaban LLM (TSD-002 bagian 6, Citation Extractor)."""
from __future__ import annotations

import re
from typing import Any

_CITATION_RE = re.compile(r"\[chunk-(\d+)\]")


def extract_citations(answer_text: str, chunk_map: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    """Ekstrak label [chunk-n] yang benar-benar dikirim di context (chunk_map).

    Label yang tidak dikenal (halusinasi LLM menyebut chunk yang tidak ada di context)
    diabaikan, tidak ditampilkan sebagai rujukan (FR-09, PRD-001).
    """
    seen: set[int] = set()
    citations: list[dict[str, Any]] = []
    for match in _CITATION_RE.finditer(answer_text):
        n = int(match.group(1))
        if n in seen or n not in chunk_map:
            continue
        seen.add(n)
        citations.append(chunk_map[n])
    return citations
