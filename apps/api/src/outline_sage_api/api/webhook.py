from __future__ import annotations

import logging

from fastapi import APIRouter, Request, Response

from outline_sage_api.signature import verify_signature
from outline_sage_api.sync.debounce import Debouncer
from outline_sage_api.sync.webhook_payload import parse_webhook_event

logger = logging.getLogger(__name__)

webhook_router = APIRouter()


@webhook_router.post("/internal/webhooks/outline")
async def receive_outline_webhook(request: Request) -> Response:
    raw_body = await request.body()
    signature = request.headers.get("X-Outline-Signature") or request.headers.get("Signature")

    settings = request.app.state.settings
    if not verify_signature(settings.outline_webhook_secret, raw_body, signature):
        return Response(status_code=401)

    body = await request.json()
    doc_id, event_type = parse_webhook_event(body)
    if not doc_id:
        # Event tanpa ID dokumen (misal event collection-level) tidak diproses, bukan error.
        return Response(status_code=202)

    debouncer: Debouncer = request.app.state.debouncer
    await debouncer.register_event(doc_id, event_type)

    return Response(status_code=202)
