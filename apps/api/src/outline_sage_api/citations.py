from __future__ import annotations

import re
from typing import Any

_CITATION_RE = re.compile(r"\[chunk-(\d+)\]")


def extract_citations(answer_text: str, chunk_map: dict[int, dict[str, Any]]) -> list[dict[str, Any]]:
    # label yang tidak ada di chunk_map (halusinasi LLM) diabaikan, bukan ditampilkan

    seen: set[int] = set()
    citations: list[dict[str, Any]] = []
    for match in _CITATION_RE.finditer(answer_text):
        n = int(match.group(1))
        if n in seen or n not in chunk_map:
            continue
        seen.add(n)
        citations.append(chunk_map[n])
    return citations
