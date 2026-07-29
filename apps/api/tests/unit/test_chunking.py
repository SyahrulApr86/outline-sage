from outline_sage_api.chunking import chunk_document


def test_empty_content_returns_no_chunks():
    assert chunk_document("", document_title="Doc") == []
    assert chunk_document("   \n  ", document_title="Doc") == []


def test_document_without_heading_produces_single_chunk_with_title_prefix():
    chunks = chunk_document("Isi dokumen singkat tanpa heading.", document_title="Kebijakan Cuti")

    assert len(chunks) == 1
    assert "Dokumen: Kebijakan Cuti" in chunks[0].content
    assert "Isi dokumen singkat tanpa heading." in chunks[0].content
    assert chunks[0].heading is None


def test_section_prefix_includes_nearest_heading():
    content = "# Pendahuluan\nIsi pendahuluan singkat.\n\n## Detail\nIsi detail singkat."
    chunks = chunk_document(content, document_title="Panduan")

    headings = {c.heading for c in chunks}
    assert "Pendahuluan" in headings
    assert "Detail" in headings
    detail_chunk = next(c for c in chunks if c.heading == "Detail")
    assert "Bagian: Detail" in detail_chunk.content


def test_section_exceeding_chunk_size_is_split_further():
    long_paragraph = "kalimat panjang berulang. " * 100  # jauh melebihi 1024 karakter
    content = f"# Bagian Panjang\n{long_paragraph}"

    chunks = chunk_document(content, document_title="Doc", chunk_size=200, chunk_overlap=20)

    assert len(chunks) > 1
    for c in chunks:
        assert c.heading == "Bagian Panjang"


def test_multiple_sections_preserve_order_by_index():
    content = "# A\nisi a\n\n# B\nisi b\n\n# C\nisi c"
    chunks = chunk_document(content, document_title="Doc")

    assert [c.index for c in chunks] == list(range(len(chunks)))
    assert [c.heading for c in chunks] == ["A", "B", "C"]
