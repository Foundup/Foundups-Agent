# -*- coding: utf-8 -*-
import sys
import io


"""HoloIndex Core Components - WSP 49 Compliant Module Structure"""

from .intelligent_subroutine_engine import IntelligentSubroutineEngine
from .module_scoring_subroutine import ModuleScoringSubroutine
from .holo_index import HoloIndex
from .search_cache import SearchCache, get_search_cache

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

__all__ = ['IntelligentSubroutineEngine', 'ModuleScoringSubroutine', 'HoloIndex']

