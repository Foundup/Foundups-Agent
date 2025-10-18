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

# Main CLI interface
from .cli import main

# Version info
__version__ = "1.0.0"
__author__ = "0102 DAE System"

# Expose key functions for programmatic use
try:
    from .cli import HoloIndex, QwenAdvisor
    __all__ = ['main', 'HoloIndex', 'QwenAdvisor']
except ImportError:
    # Graceful fallback if dependencies not available
    __all__ = ['main']