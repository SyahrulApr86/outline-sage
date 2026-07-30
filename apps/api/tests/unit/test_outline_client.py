import respx
from httpx import Response

from outline_sage_api.clients.outline_client import OutlineClient

BASE_URL = "https://outline.example.com"


@respx.mock
async def test_list_all_document_ids_paginates_and_dedupes_across_collections():
    respx.post(f"{BASE_URL}/api/collections.list").mock(
        return_value=Response(200, json={"data": [{"id": "col-1"}, {"id": "col-2"}]})
    )

    def documents_list_side_effect(request):
        body = request.content
        import json

        payload = json.loads(body)
        if payload["collectionId"] == "col-1" and payload["offset"] == 0:
            return Response(200, json={"data": [{"id": f"doc-{i}"} for i in range(100)]})
        if payload["collectionId"] == "col-1" and payload["offset"] == 100:
            return Response(200, json={"data": [{"id": "doc-100"}]})
        if payload["collectionId"] == "col-2" and payload["offset"] == 0:
            return Response(200, json={"data": [{"id": "doc-100"}, {"id": "doc-shared"}]})
        return Response(200, json={"data": []})

    respx.post(f"{BASE_URL}/api/documents.list").mock(side_effect=documents_list_side_effect)

    client = OutlineClient(BASE_URL, "token")
    doc_ids = await client.list_all_document_ids()

    assert len(doc_ids) == 102  # doc-0..doc-100 (101) + doc-shared, doc-100 deduped
    assert "doc-shared" in doc_ids
    assert doc_ids.count("doc-100") == 1


@respx.mock
async def test_list_all_document_ids_returns_empty_when_no_collections():
    respx.post(f"{BASE_URL}/api/collections.list").mock(return_value=Response(200, json={"data": []}))

    client = OutlineClient(BASE_URL, "token")
    doc_ids = await client.list_all_document_ids()

    assert doc_ids == []


@respx.mock
async def test_list_all_document_ids_stops_on_error_response():
    respx.post(f"{BASE_URL}/api/collections.list").mock(
        return_value=Response(200, json={"data": [{"id": "col-1"}]})
    )
    respx.post(f"{BASE_URL}/api/documents.list").mock(return_value=Response(500, json={}))

    client = OutlineClient(BASE_URL, "token")
    doc_ids = await client.list_all_document_ids()

    assert doc_ids == []
