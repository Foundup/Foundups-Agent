# -*- coding: utf-8 -*-
import sys
import io


import pytest
from modules.infrastructure.wre_core.recursive_improvement.src.learning import RecursiveLearningEngine, process_error
from modules.infrastructure.wre_core.recursive_improvement.src.core import Improvement

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

@pytest.mark.asyncio
async def test_process_error():
    engine = RecursiveLearningEngine()
    error = ValueError("Test WSP violation")
    improvement = await process_error(error)
    assert isinstance(improvement, Improvement)
    assert improvement.pattern_id is not None
    assert improvement.solution_id is not None

# TODO: Add more tests for quantum state, metrics, etc.
