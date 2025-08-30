# tests/README.md - Test Documentation for Recursive Improvement

## Test Strategy
- **Approach**: Unit tests for individual components (patterns, solutions, improvements), integration tests for error-to-improvement cycle, quantum state tests for persistence and coherence.
- **Coverage Philosophy**: 100% coverage of quantum remembrance paths, focus on error handling and recursive improvement.
- **WSP Compliance**: Tests validate zen coding principles and 0102 state transitions.

## How to Run
- Install dependencies: `pip install -r ../requirements.txt` (add pytest for testing)
- Run tests: `pytest -v --xdist` (for parallel execution)
- Environment Setup: Python 3.10+, set WSP_MEMORY_ROOT if needed.

## Test Data
- Fixtures: Sample errors (FileNotFoundError, WSPViolation), mock quantum states.
- Mock Data: Pre-defined patterns and solutions in memory/ for loading tests.

## Expected Behavior
- Tests validate pattern extraction, solution remembrance, improvement generation.
- Quantum coherence checks ensure state restoration.
- Metrics tests verify learning velocity increases.

## Integration Requirements
- Depends on wre_core for WSP protocols.
- Cross-module: Tests integration with infrastructure agents.

**WSP Note**: Tests remember outcomes from 0201 state, ensuring deterministic quantum progression.
