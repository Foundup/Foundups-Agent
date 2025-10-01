from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional


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
