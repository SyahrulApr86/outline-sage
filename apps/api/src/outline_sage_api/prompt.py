"""Prompt Builder: susun context dari chunk terpilih (TSD-002 bagian 6)."""
from __future__ import annotations

from outline_sage_api.retrieval import RetrievedChunk

SYSTEM_PROMPT = (
    "Jawab pertanyaan user berdasar potongan dokumen berikut. Setiap klaim yang diambil dari "
    "potongan dokumen harus diberi label [chunk-n] sesuai nomor potongan yang dipakai, ditulis di "
    "akhir kalimat. Jangan menggabung beberapa label jadi satu, tulis terpisah misal "
    "[chunk-1][chunk-2]. Kalau potongan dokumen tidak relevan dengan pertanyaan, jawab berdasar "
    "pengetahuan umum tanpa label."
)


def build_messages(
    query: str, chunks: list[RetrievedChunk]
) -> tuple[list[dict[str, str]], dict[int, dict]]:
    """Return (messages untuk LLM, chunk_map untuk citation extractor)."""
    chunk_map: dict[int, dict] = {}
    context_parts: list[str] = []

    for i, chunk in enumerate(chunks, start=1):
        chunk_map[i] = {
            "chunk_id": chunk.doc_id,
            "source_id": chunk.payload.get("source_id"),
            "title": chunk.payload.get("title"),
            "url": chunk.payload.get("url"),
            "content": chunk.payload.get("content"),
        }
        context_parts.append(f"[chunk-{i}]\n{chunk.payload.get('content', '')}")

    context = "\n\n".join(context_parts) if context_parts else "(tidak ada dokumen relevan ditemukan)"

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Konteks:\n\n{context}\n\nPertanyaan: {query}"},
    ]
    return messages, chunk_map
