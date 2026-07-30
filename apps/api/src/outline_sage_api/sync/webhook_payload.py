from __future__ import annotations

_DELETE_EVENTS = {"documents.delete", "documents.permanent_delete"}
_TRASH_EVENTS = {"documents.archive", "documents.trash"}


def parse_webhook_event(body: dict) -> tuple[str | None, str]:
    # asumsi: payload berisi {"event": ..., "payload": {"id": ...}}, isi dokumen di-fetch terpisah

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
