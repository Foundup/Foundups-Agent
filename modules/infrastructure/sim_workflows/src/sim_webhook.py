from __future__ import annotations

import hashlib
import hmac
from typing import Optional


def verify_signature(secret: str, payload: bytes, signature: str) -> bool:
    """Verify HMAC SHA256 signature for webhook payloads.

    This is a generic helper. Sim-side header naming may vary; caller is
    responsible for extracting the header value and passing it here.
    """
    if not secret or not payload or not signature:
        return False
    try:
        mac = hmac.new(secret.encode("utf-8"), payload, hashlib.sha256)
        expected = mac.hexdigest()
        # Timing-safe compare
        return hmac.compare_digest(expected, signature)
    except Exception:
        return False
