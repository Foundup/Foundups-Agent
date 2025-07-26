# Priority Scorer Test Suite

## Purpose
Test suite for PriorityScorer implementation - strategic decomposition from auto_meeting_orchestrator PoC with 000-222 emoji scale gamification.

## Test Strategy
- **Unit Tests**: Priority scoring algorithms, emoji scale generation, urgency calculations
- **Integration Tests**: Multi-factor scoring validation, context weighting systems
- **Performance Tests**: Priority queue sorting, large-scale intent ranking
- **Gamification Tests**: 000-222 emoji scale accuracy, engagement mechanics validation

## Test Coverage
- Multi-factor priority score calculation with all weighting factors
- 000-222 emoji scale generation and visual representation accuracy
- Urgency factor calculations based on context (duration, participants, deadlines)
- Priority queue management and comparative ranking algorithms
- Keyword boost calculations and importance recognition
- Time pressure and priority decay factor validation

## How to Run
```bash
# Run all tests
pytest modules/gamification/priority_scorer/tests/ -v

# Run with coverage
pytest modules/gamification/priority_scorer/tests/ --cov=modules.gamification.priority_scorer.src --cov-report=term-missing
```

## Test Environment
- **Dependencies**: pytest, pytest-mock, datetime manipulation tools
- **Mock Data**: Simulated meeting contexts, priority scenarios, urgency factors
- **Gamification Testing**: 000-222 emoji scale validation, engagement mechanics verification 