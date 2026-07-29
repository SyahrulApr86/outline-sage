"""Parsing payload webhook Outline (TSD-001 Open Questions #1: asumsi format belum diverifikasi)."""
from __future__ import annotations

_DELETE_EVENTS = {"documents.delete", "documents.permanent_delete"}
_TRASH_EVENTS = {"documents.archive", "documents.trash"}


def parse_webhook_event(body: dict) -> tuple[str | None, str]:
    """Return (doc_id, event_type). event_type salah satu dari: update, delete, trash.

    Asumsi: payload berbentuk {"event": "documents.update", "payload": {"id": "..."}},
    isi dokumen tidak disertakan (harus di-fetch terpisah lewat Outline API).
    """
    event_name = body.get("event", "")
    payload = body.get("payload", {}) or {}
    doc_id = payload.get("id") or payload.get("documentId")

    if event_name in _DELETE_EVENTS:
        event_type = "delete"
    elif event_name in _TRASH_EVENTS:
        event_type = "trash"
    else:
        event_type = "update"

    return doc_id, event_type
