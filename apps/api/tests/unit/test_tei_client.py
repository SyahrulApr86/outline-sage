import respx
from httpx import Response

from outline_sage_api.clients.tei_client import TEIEmbeddingClient

BASE_URL = "https://tei-embed.example.com"


@respx.mock
async def test_embed_batch_splits_requests_above_max_batch_size():
    call_sizes: list[int] = []

    def side_effect(request):
        import json

        payload = json.loads(request.content)
        inputs = payload["inputs"]
        call_sizes.append(len(inputs))
        return Response(200, json=[[float(len(t))] for t in inputs])

    respx.post(f"{BASE_URL}/embed").mock(side_effect=side_effect)

    client = TEIEmbeddingClient(BASE_URL, max_batch_size=32)
    texts = [f"chunk {i}" for i in range(75)]
    vectors = await client.embed_batch(texts)

    assert len(vectors) == 75
    assert call_sizes == [32, 32, 11]


@respx.mock
async def test_embed_batch_single_request_when_within_limit():
    respx.post(f"{BASE_URL}/embed").mock(return_value=Response(200, json=[[1.0], [2.0]]))

    client = TEIEmbeddingClient(BASE_URL, max_batch_size=32)
    vectors = await client.embed_batch(["a", "b"])

    assert vectors == [[1.0], [2.0]]


async def test_embed_batch_empty_input_returns_empty_without_request():
    client = TEIEmbeddingClient(BASE_URL)
    assert await client.embed_batch([]) == []
