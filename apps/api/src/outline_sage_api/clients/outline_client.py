from __future__ import annotations

import httpx
from httpx_retries import Retry, RetryTransport


def _build_client(timeout: float = 60.0) -> httpx.AsyncClient:
    retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
    transport = RetryTransport(transport=httpx.AsyncHTTPTransport(), retry=retry)
    return httpx.AsyncClient(transport=transport, timeout=timeout)


class OutlineClient:
    def __init__(self, base_url: str, api_token: str) -> None:
        self._base_url = base_url.rstrip("/")
        self._headers = {"Authorization": f"Bearer {api_token}", "Content-Type": "application/json"}

    async def export_document(self, document_id: str) -> dict | None:
        async with _build_client() as client:
            resp = await client.post(
                f"{self._base_url}/api/documents.export",
                json={"id": document_id},
                headers=self._headers,
            )
            if resp.status_code != 200:
                return None
            return resp.json().get("data")

    async def get_document(self, document_id: str) -> dict | None:
        async with _build_client() as client:
            resp = await client.post(
                f"{self._base_url}/api/documents.info",
                json={"id": document_id},
                headers=self._headers,
            )
            if resp.status_code != 200:
                return None
            return resp.json().get("data")

    async def list_collections(self) -> list[dict]:
        async with _build_client() as client:
            resp = await client.post(
                f"{self._base_url}/api/collections.list",
                json={"limit": 100},
                headers=self._headers,
            )
            if resp.status_code != 200:
                return []
            return resp.json().get("data", [])
