"""
ReOrder AI — Shared FastAPI dependencies.
Rate limiting, API key auth, request identification.
"""

import hashlib
import hmac
import secrets
import logging
from typing import Optional

from fastapi import Depends, HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from starlette.status import HTTP_403_FORBIDDEN, HTTP_429_TOO_MANY_REQUESTS

from src.core.config import get_settings

logger = logging.getLogger(__name__)


# ── Rate Limiting ─────────────────────────────────────────────
# Key function for slowapi: use client IP (respects X-Forwarded-For behind a proxy)

def get_client_ip(request: Request) -> str:
    """Extract client IP for rate limiting. Handles reverse proxies."""
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# ── API Key Auth ──────────────────────────────────────────────
# Protects write/mutation endpoints (sync, pipeline, forecast run).
# The key is set via API_SECRET_KEY in .env.
# If not set, auth is disabled (dev mode).

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def require_api_key(
    request: Request,
    api_key: Optional[str] = Security(_api_key_header),
) -> str:
    """
    FastAPI dependency that enforces API key auth on protected endpoints.

    - If API_SECRET_KEY is not set in .env → auth is skipped (dev mode).
    - If set → the request must include a matching X-API-Key header.

    Returns the validated key (or "dev" if auth is disabled).
    """
    settings = get_settings()
    server_key = settings.api_secret_key

    # Dev mode: no key configured → allow all
    if not server_key:
        return "dev"

    if not api_key:
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Missing X-API-Key header",
        )

    # Constant-time comparison to prevent timing attacks
    if not hmac.compare_digest(api_key, server_key):
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="Invalid API key",
        )

    return api_key
