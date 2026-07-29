from outline_sage_api.sync.webhook_payload import parse_webhook_event


def test_update_event_parsed():
    body = {"event": "documents.update", "payload": {"id": "doc-1"}}
    doc_id, event_type = parse_webhook_event(body)
    assert doc_id == "doc-1"
    assert event_type == "update"


def test_delete_event_parsed():
    body = {"event": "documents.delete", "payload": {"id": "doc-1"}}
    _, event_type = parse_webhook_event(body)
    assert event_type == "delete"


def test_trash_event_parsed():
    body = {"event": "documents.archive", "payload": {"id": "doc-1"}}
    _, event_type = parse_webhook_event(body)
    assert event_type == "trash"


def test_unknown_event_defaults_to_update():
    body = {"event": "documents.publish", "payload": {"id": "doc-1"}}
    _, event_type = parse_webhook_event(body)
    assert event_type == "update"


def test_missing_document_id_returns_none():
    body = {"event": "documents.update", "payload": {}}
    doc_id, _ = parse_webhook_event(body)
    assert doc_id is None
