"""Integration test endpoint webhook HTTP: FSD-001 AC-2, AC-6."""
from __future__ import annotations

import hashlib
import hmac
import json

import httpx
import pytest
from fastapi import FastAPI

from outline_sage_api.api.webhook import webhook_router
from outline_sage_api.sync.debounce import Debouncer

SECRET = "test-secret"


def _make_app(redis_client) -> FastAPI:
    app = FastAPI()
    app.include_router(webhook_router)
    app.state.settings = type("Settings", (), {"outline_webhook_secret": SECRET})()
    app.state.debouncer = Debouncer(redis_client, window_seconds=2)
    return app


def _sign(body: bytes) -> str:
    return hmac.new(SECRET.encode(), msg=body, digestmod=hashlib.sha256).hexdigest()


@pytest.mark.asyncio
async def test_webhook_with_valid_signature_registers_debounce(redis_client):
    app = _make_app(redis_client)
    body = json.dumps({"event": "documents.update", "payload": {"id": "doc-5"}}).encode()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/internal/webhooks/outline", content=body, headers={"X-Outline-Signature": _sign(body)}
        )

    assert resp.status_code == 202
    assert await redis_client.exists("debounce:pending:doc-5") == 1


@pytest.mark.asyncio
async def test_webhook_with_invalid_signature_rejected(redis_client):
    app = _make_app(redis_client)
    body = json.dumps({"event": "documents.update", "payload": {"id": "doc-6"}}).encode()

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/internal/webhooks/outline", content=body, headers={"X-Outline-Signature": "0" * 64}
        )

    assert resp.status_code == 401
    assert await redis_client.exists("debounce:pending:doc-6") == 0


@pytest.mark.asyncio
async def test_multiple_rapid_webhooks_refresh_same_debounce_key(redis_client):
    app = _make_app(redis_client)
    body = json.dumps({"event": "documents.update", "payload": {"id": "doc-7"}}).encode()
    signature = _sign(body)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(3):
            resp = await client.post(
                "/internal/webhooks/outline", content=body, headers={"X-Outline-Signature": signature}
            )
            assert resp.status_code == 202

    ttl = await redis_client.ttl("debounce:pending:doc-7")
    assert 0 < ttl <= 2
