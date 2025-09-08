import pytest
from modules.wre_core.recursive_improvement.src.learning import RecursiveLearningEngine, process_error
from modules.wre_core.recursive_improvement.src.core import Improvement

@pytest.mark.asyncio
async def test_process_error():
    engine = RecursiveLearningEngine()
    error = ValueError("Test WSP violation")
    improvement = await process_error(error)
    assert isinstance(improvement, Improvement)
    assert improvement.pattern_id is not None
    assert improvement.solution_id is not None

# TODO: Add more tests for quantum state, metrics, etc.
