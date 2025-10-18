# -*- coding: utf-8 -*-
from __future__ import annotations

import sys
import io



import os
from dataclasses import dataclass
from pathlib import Path


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
class QwenAdvisorConfig:
    """Runtime configuration for the HoloIndex↔Qwen advisor layer.

    Defaults read from environment so deployments can override paths without
    editing source (WSP 87 navigation compliance).
    """

    model_path: Path = Path(os.getenv("HOLO_QWEN_MODEL", "E:/HoloIndex/models/qwen-coder-1.5b.gguf"))
    telemetry_path: Path = Path(os.getenv("HOLO_QWEN_TELEMETRY", "E:/HoloIndex/indexes/holo_usage.json"))
    max_tokens: int = int(os.getenv("HOLO_QWEN_MAX_TOKENS", "512"))
    temperature: float = float(os.getenv("HOLO_QWEN_TEMPERATURE", "0.2"))
    cache_enabled: bool = os.getenv("HOLO_QWEN_CACHE", "1") != "0"

    @classmethod
    def from_env(cls, **overrides: object) -> "QwenAdvisorConfig":
        """Build config from environment variables plus explicit overrides."""

        config = cls()
        for key, value in overrides.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config
