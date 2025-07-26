# Priority Scorer Test Suite

## Purpose
Test suite for PriorityScorer implementation using established WSP framework (WSP 15/37/8) instead of custom scoring system.

## Test Strategy
- **Unit Tests**: WSP 15 MPS 4-question scoring methodology validation
- **Integration Tests**: WSP 37 cube color mapping and WSP 8 LLME triplet integration
- **Framework Tests**: Compliance with established WSP protocols (no custom scoring)
- **Regression Tests**: Ensure WSP framework consistency and proper score ranges

## Test Coverage
- **WSP 15 MPS Scoring**: 4-question methodology (Complexity, Importance, Deferability, Impact)
- **WSP 37 Cube Colors**: Proper mapping from MPS scores to cube color visualization
- **WSP 8 LLME Integration**: Semantic triplet rating system integration and validation
- **Priority Classification**: P0-P4 priority levels based on total MPS scores (4-20 range)
- **Score Validation**: Proper 1-5 range validation for each MPS dimension
- **Context Estimation**: Automated scoring hints from context keywords and metadata

## WSP Framework Compliance Tests
- **WSP 15 Methodology**: Verify 4-question scoring produces 4-20 total range
- **WSP 37 Color Mapping**: Validate cube color assignments match WSP specifications
- **WSP 8 Triplet Format**: Ensure LLME triplets follow A≤B≤C progression rules
- **Framework Integration**: Test integration with existing WSP protocols
- **No Custom Scoring**: Verify no custom scoring systems bypass established WSP framework

## How to Run
```bash
# Run all tests
pytest modules/gamification/priority_scorer/tests/ -v

# Run with coverage
pytest modules/gamification/priority_scorer/tests/ --cov=modules.gamification.priority_scorer.src --cov-report=term-missing

# Run WSP framework compliance tests
pytest modules/gamification/priority_scorer/tests/test_wsp_compliance.py -v
```

## Test Environment
- **Dependencies**: pytest, pytest-mock, datetime manipulation tools
- **Mock Data**: Simulated meeting contexts, WSP scoring scenarios, LLME triplets
- **WSP Framework Testing**: Validation of established protocols (WSP 15/37/8)
- **Compliance Verification**: Ensure no custom scoring bypasses WSP framework 