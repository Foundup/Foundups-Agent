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

WSP 78: Distributed Module Database Protocol

Provides unified database access for the entire FoundUps system.
"""

from .db_manager import DatabaseManager
from .module_db import ModuleDB
from .agent_db import AgentDB
from .database import Database
from pathlib import Path
from typing import Any, Dict, Sequence

__all__ = [
    'DatabaseManager',
    'ModuleDB',
    'AgentDB',
    'Database',
    'audit_sqlite_file',
    'run_sqlite_audit',
]


def audit_sqlite_file(path: Path, options: Any = None) -> Dict[str, Any]:
    from .sqlite_audit import audit_sqlite_file as _audit_sqlite_file

    return _audit_sqlite_file(path=path, options=options)


def run_sqlite_audit(targets: Sequence[Path | str] | None = None, options: Any = None) -> Dict[str, Any]:
    from .sqlite_audit import run_sqlite_audit as _run_sqlite_audit

    return _run_sqlite_audit(targets=targets, options=options)
