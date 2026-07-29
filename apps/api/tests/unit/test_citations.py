from outline_sage_api.citations import extract_citations

CHUNK_MAP = {
    1: {"chunk_id": "c1", "title": "Dokumen A"},
    2: {"chunk_id": "c2", "title": "Dokumen B"},
}


def test_valid_citation_labels_extracted_in_order():
    answer = "Fakta pertama [chunk-1]. Fakta kedua [chunk-2]."
    result = extract_citations(answer, CHUNK_MAP)

    assert result == [CHUNK_MAP[1], CHUNK_MAP[2]]


def test_unknown_citation_label_ignored():
    answer = "Fakta halusinasi [chunk-99]. Fakta valid [chunk-1]."
    result = extract_citations(answer, CHUNK_MAP)

    assert result == [CHUNK_MAP[1]]


def test_duplicate_citation_label_counted_once():
    answer = "[chunk-1] disebut lagi di sini [chunk-1]."
    result = extract_citations(answer, CHUNK_MAP)

    assert result == [CHUNK_MAP[1]]


def test_no_citation_label_returns_empty_list():
    answer = "Jawaban tanpa rujukan sama sekali."
    result = extract_citations(answer, CHUNK_MAP)

    assert result == []
