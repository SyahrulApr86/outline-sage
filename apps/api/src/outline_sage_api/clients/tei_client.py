from __future__ import annotations

import httpx


class TEIEmbeddingClient:
    def __init__(self, base_url: str, timeout: float = 30.0, max_batch_size: int = 32) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._max_batch_size = max_batch_size

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        results: list[list[float]] = []
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            for i in range(0, len(texts), self._max_batch_size):
                chunk = texts[i : i + self._max_batch_size]
                resp = await client.post(f"{self._base_url}/embed", json={"inputs": chunk})
                resp.raise_for_status()
                results.extend(resp.json())
        return results


class TEIRerankerClient:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    async def rerank(self, query: str, documents: list[str]) -> list[dict]:
        if not documents:
            return []
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(
                f"{self._base_url}/rerank",
                json={"query": query, "texts": documents},
            )
            resp.raise_for_status()
            return resp.json()
