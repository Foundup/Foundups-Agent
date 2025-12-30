# -*- coding: utf-8 -*-
import sys
import io

"""
HoloIndex - Semantic Code Discovery and WSP Compliance Assistant

A sophisticated semantic search system that prevents vibecoding by finding existing code
and provides real-time WSP compliance guidance.

Key Components:
- CLI interface for semantic search
- QwenAdvisor for intelligent code understanding
- WSP violation detection and prevention
- Vector database for instant code discovery
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
import sys
import io

if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

# Version info
__version__ = "1.0.0"
__author__ = "0102 DAE System"

def main(argv=None):
    """
    Lazy CLI entrypoint.

    Avoid importing `holo_index.cli` at package import time so `python -m holo_index.cli`
    doesn't emit RuntimeWarnings and consumers can import `holo_index` cheaply.
    """
    from .cli import main as _main
    return _main(argv)


def __getattr__(name: str):
    if name in {"HoloIndex", "QwenAdvisor"}:
        from .cli import HoloIndex, QwenAdvisor
        return {"HoloIndex": HoloIndex, "QwenAdvisor": QwenAdvisor}[name]
    raise AttributeError(f"module 'holo_index' has no attribute {name!r}")


__all__ = ["main", "HoloIndex", "QwenAdvisor"]
