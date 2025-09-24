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
