from __future__ import annotations

import re
from dataclasses import dataclass

DEFAULT_CHUNK_SIZE = 1024
DEFAULT_CHUNK_OVERLAP = 100
DEFAULT_SEPARATORS: tuple[str, ...] = ("\n\n", "\n", " ", "")

_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)


@dataclass
class Chunk:
    content: str
    heading: str | None
    index: int


def _split_by_heading(text: str) -> list[tuple[str | None, str]]:
    """Pisahkan teks jadi list (heading_terdekat, isi_section)."""
    matches = list(_HEADING_RE.finditer(text))
    if not matches:
        return [(None, text)]

    sections: list[tuple[str | None, str]] = []
    if matches[0].start() > 0:
        sections.append((None, text[: matches[0].start()]))

    for i, match in enumerate(matches):
        heading = match.group(2).strip()
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        sections.append((heading, text[start:end]))

    return sections


def _recursive_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    separators: tuple[str, ...],
) -> list[str]:
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    if not separators:
        step = max(chunk_size - chunk_overlap, 1)
        return [text[i : i + chunk_size] for i in range(0, len(text), step)]

    sep, *rest = separators
    pieces = list(text) if sep == "" else text.split(sep)

    chunks: list[str] = []
    current = ""
    for piece in pieces:
        candidate = current + (sep if current else "") + piece
        if len(candidate) <= chunk_size:
            current = candidate
            continue

        if current:
            chunks.append(current)
        if len(piece) > chunk_size:
            chunks.extend(_recursive_split(piece, chunk_size, chunk_overlap, tuple(rest)))
            current = ""
        else:
            current = piece

    if current:
        chunks.append(current)

    if chunk_overlap > 0 and len(chunks) > 1:
        overlapped = [chunks[0]]
        for prev, curr in zip(chunks, chunks[1:]):
            tail = prev[-chunk_overlap:]
            overlapped.append((tail + curr)[: chunk_size + chunk_overlap])
        return overlapped

    return chunks


def chunk_document(
    content: str,
    *,
    document_title: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
    separators: tuple[str, ...] = DEFAULT_SEPARATORS,
) -> list[Chunk]:
    """Split per heading Markdown dulu, section yang masih kebesaran dipecah lagi per karakter."""
    if not content or not content.strip():
        return []

    sections = _split_by_heading(content)
    chunks: list[Chunk] = []
    index = 0
    for heading, section_text in sections:
        pieces = _recursive_split(section_text, chunk_size, chunk_overlap, separators)
        for piece in pieces:
            prefix_parts = [f"Dokumen: {document_title}"]
            if heading:
                prefix_parts.append(f"Bagian: {heading}")
            prefixed = "\n\n".join(prefix_parts) + "\n\n" + piece.strip()
            chunks.append(Chunk(content=prefixed, heading=heading, index=index))
            index += 1

    return chunks
