import hashlib
import hmac

from outline_sage_api.signature import verify_signature

SECRET = "test-webhook-secret"


def _sign(body: bytes) -> str:
    return hmac.new(SECRET.encode("utf-8"), msg=body, digestmod=hashlib.sha256).hexdigest()


def test_valid_signature_accepted():
    body = b'{"event": "documents.update"}'
    assert verify_signature(SECRET, body, _sign(body)) is True


def test_valid_signature_with_sha256_prefix_accepted():
    body = b'{"event": "documents.update"}'
    assert verify_signature(SECRET, body, f"sha256={_sign(body)}") is True


def test_invalid_signature_rejected():
    body = b'{"event": "documents.update"}'
    assert verify_signature(SECRET, body, "0" * 64) is False


def test_missing_signature_header_rejected():
    body = b'{"event": "documents.update"}'
    assert verify_signature(SECRET, body, None) is False
    assert verify_signature(SECRET, body, "") is False


def test_tampered_body_rejected():
    body = b'{"event": "documents.update"}'
    tampered_body = b'{"event": "documents.delete"}'
    assert verify_signature(SECRET, tampered_body, _sign(body)) is False
