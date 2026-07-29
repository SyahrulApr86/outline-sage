from outline_sage_api.prompt import build_messages
from outline_sage_api.retrieval import RetrievedChunk


def test_build_messages_maps_chunk_labels_in_order():
    chunks = [
        RetrievedChunk(doc_id="p1", payload={"source_id": "d1", "title": "A", "url": "u1", "content": "isi 1"}),
        RetrievedChunk(doc_id="p2", payload={"source_id": "d2", "title": "B", "url": "u2", "content": "isi 2"}),
    ]

    messages, chunk_map = build_messages("apa itu X?", chunks)

    assert chunk_map[1]["chunk_id"] == "p1"
    assert chunk_map[2]["chunk_id"] == "p2"
    assert "[chunk-1]" in messages[1]["content"]
    assert "[chunk-2]" in messages[1]["content"]
    assert "apa itu X?" in messages[1]["content"]


def test_build_messages_with_no_chunks_uses_fallback_context():
    messages, chunk_map = build_messages("pertanyaan umum", [])

    assert chunk_map == {}
    assert "tidak ada dokumen relevan" in messages[1]["content"]
