"""
Commenting Control Plane (012 -> Comment DAE)
============================================

Provides a small, file-backed "broadcast config" that 012 can update and
commenting DAEs can consume.

WSP alignment:
- WSP 60: Module memory (config stored under module memory)
- WSP 49: Module structure (src + memory)
- WSP 22: Change tracking (ModLog updated when behavior changes)
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional


MODULE_ROOT = Path(__file__).resolve().parents[1]  # modules/communication/video_comments
DEFAULT_PATH = MODULE_ROOT / "memory" / "commenting_broadcast.json"


@dataclass
class CommentingBroadcast:
    """
    Minimal broadcast config for 012 to influence comment replies.

    Fields are intentionally small and stable (avoid schema churn).
    """

    enabled: bool = False
    promo_handles: List[str] = field(default_factory=list)  # e.g. ["@MyNewChannel"]
    promo_message: str = ""  # optional free-form message, injected as context
    updated_at_unix: float = 0.0
    updated_by: str = "012"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _normalize_handle(handle: str) -> str:
    h = (handle or "").strip()
    if not h:
        return ""
    return h if h.startswith("@") else f"@{h}"


def load_broadcast(path: Path = DEFAULT_PATH) -> CommentingBroadcast:
    if not path.exists():
        return CommentingBroadcast()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return CommentingBroadcast()
        enabled = bool(raw.get("enabled", False))
        promo_handles = [
            _normalize_handle(x)
            for x in (raw.get("promo_handles") or [])
            if isinstance(x, str) and _normalize_handle(x)
        ]
        promo_message = str(raw.get("promo_message") or "")
        updated_at_unix = float(raw.get("updated_at_unix") or 0.0)
        updated_by = str(raw.get("updated_by") or "012")
        return CommentingBroadcast(
            enabled=enabled,
            promo_handles=promo_handles,
            promo_message=promo_message,
            updated_at_unix=updated_at_unix,
            updated_by=updated_by,
        )
    except Exception:
        return CommentingBroadcast()


def save_broadcast(broadcast: CommentingBroadcast, path: Path = DEFAULT_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    # Stamp update time on save
    broadcast.updated_at_unix = time.time()
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(broadcast.to_dict(), indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    tmp.replace(path)
    return path


def set_promo(
    *,
    enabled: Optional[bool] = None,
    promo_handles: Optional[List[str]] = None,
    promo_message: Optional[str] = None,
    updated_by: str = "012",
    path: Path = DEFAULT_PATH,
) -> CommentingBroadcast:
    current = load_broadcast(path)
    if enabled is not None:
        current.enabled = bool(enabled)
    if promo_handles is not None:
        current.promo_handles = [
            _normalize_handle(x)
            for x in promo_handles
            if isinstance(x, str) and _normalize_handle(x)
        ]
    if promo_message is not None:
        current.promo_message = str(promo_message)
    current.updated_by = updated_by or "012"
    save_broadcast(current, path)
    return current


def clear_promo(path: Path = DEFAULT_PATH) -> CommentingBroadcast:
    current = load_broadcast(path)
    current.enabled = False
    current.promo_handles = []
    current.promo_message = ""
    save_broadcast(current, path)
    return current

