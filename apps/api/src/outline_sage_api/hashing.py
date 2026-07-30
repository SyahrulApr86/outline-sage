from __future__ import annotations

import hashlib


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def diff_chunks(
    old_hashes: dict[int, str],
    new_chunks: dict[int, str],
) -> tuple[dict[int, str], list[int]]:
    """Return (to_embed: {index: hash} baru/berubah, to_delete: index yang hilang di versi baru)."""
    to_embed: dict[int, str] = {}
    for index, content in new_chunks.items():
        new_hash = content_hash(content)
        if old_hashes.get(index) != new_hash:
            to_embed[index] = new_hash

    to_delete = [index for index in old_hashes if index not in new_chunks]

    return to_embed, to_delete
