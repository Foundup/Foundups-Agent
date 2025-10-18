# -*- coding: utf-8 -*-
import sys
import io


"""
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

WRE Master Orchestrator - THE One Orchestrator
Per WSP 46, WSP 65, WSP 82
"""

from .src.wre_master_orchestrator import (
    WREMasterOrchestrator,
    OrchestratorPlugin,
    Pattern,
    PatternMemory,
    WSPValidator,
    # Example plugins
    SocialMediaPlugin,
    MLEStarPlugin,
    BlockPlugin,
)

__all__ = [
    'WREMasterOrchestrator',
    'OrchestratorPlugin',
    'Pattern',
    'PatternMemory',
    'WSPValidator',
    'SocialMediaPlugin',
    'MLEStarPlugin',
    'BlockPlugin',
]

__version__ = '1.1.1'  # POC per WSP 8 LLME scoring