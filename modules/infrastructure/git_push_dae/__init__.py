# -*- coding: utf-8 -*-
import sys
import io


# GitPushDAE - Autonomous Git Push Daemon
# WSP 91 Compliant DAEMON for autonomous development publishing

from .src.git_push_dae import GitPushDAE, PushContext, PushDecision, HealthStatus

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

__all__ = [
    'GitPushDAE',
    'PushContext',
    'PushDecision',
    'HealthStatus'
]

__version__ = '1.0.0'
__author__ = '0102'
__description__ = 'WSP 91 compliant DAEMON for autonomous git push decisions'
