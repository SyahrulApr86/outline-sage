from __future__ import annotations

import logging
import time

import httpx
from jose import jwt
from jose.exceptions import JOSEError

logger = logging.getLogger(__name__)


class KeycloakAuthenticator:
    def __init__(self, issuer: str, audience: str, jwks_cache_seconds: int = 3600) -> None:
        self._issuer = issuer.rstrip("/")
        self._audience = audience
        self._jwks_cache_seconds = jwks_cache_seconds
        self._jwks: dict | None = None
        self._jwks_fetched_at: float = 0.0

    async def _get_jwks(self) -> dict:
        now = time.time()
        if self._jwks is None or now - self._jwks_fetched_at > self._jwks_cache_seconds:
            async with httpx.AsyncClient(timeout=10) as client:
                discovery = await client.get(f"{self._issuer}/.well-known/openid-configuration")
                discovery.raise_for_status()
                jwks_uri = discovery.json()["jwks_uri"]
                jwks_resp = await client.get(jwks_uri)
                jwks_resp.raise_for_status()
                self._jwks = jwks_resp.json()
                self._jwks_fetched_at = now
        return self._jwks

    async def verify(self, token: str) -> dict:
        """Return payload token kalau valid, raise ValueError kalau tidak."""
        jwks = await self._get_jwks()
        try:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require_exp": True},
            )
        except JOSEError as exc:
            logger.warning("token verification failed: %s", exc)
            raise ValueError(f"invalid token: {exc}") from exc
        return payload
