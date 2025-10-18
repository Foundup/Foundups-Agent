# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io



import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

@dataclass
class AdvisorCache:
    """In-memory cache for advisor responses (WSP 17 pattern reuse).

    A simple dictionary keyed by a stable hash so the first iteration can
    reuse responses while we design a persistent store.
    """

    enabled: bool = True
    store: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    def make_key(self, query: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        payload = {
            "query": query,
            "metadata": metadata or {},
        }
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True).encode("utf-8")).hexdigest()
        return digest

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if not self.enabled:
            return None
        return self.store.get(key)

    def set(self, key: str, value: Dict[str, Any]) -> None:
        if not self.enabled:
            return
        self.store[key] = value


class FileBackedAdvisorCache(AdvisorCache):
    """Optional JSONL cache on disk (future enhancement)."""

    def __init__(self, path: Path, enabled: bool = True) -> None:
        super().__init__(enabled=enabled)
        self.path = path

    # Persistence hooks will be implemented when advisor logic lands.
