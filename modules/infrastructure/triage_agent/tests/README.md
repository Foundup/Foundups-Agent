# TriageAgent Test Suite

## Purpose
Test suite for TriageAgent implementation per WSP 54 (WRE Agent Duties Specification).

## Test Strategy
- **Unit Tests**: Core functionality, feedback parsing, task creation
- **Integration Tests**: WSP 15 ScoringAgent integration, WSP 48 trigger validation
- **Security Tests**: WSP 71 secrets management integration
- **Performance Tests**: Feedback processing throughput, queue management

## Test Coverage
- Feedback source monitoring and parsing
- Task standardization and WSP compliance
- Priority assignment and scoring integration
- Error handling and graceful degradation
- WSP protocol compliance validation

## How to Run
```bash
# Run all tests
pytest modules/infrastructure/triage_agent/tests/ -v

# Run with coverage
pytest modules/infrastructure/triage_agent/tests/ --cov=modules.infrastructure.triage_agent.src --cov-report=term-missing
```

## Test Environment
- **Dependencies**: pytest, pytest-asyncio, pytest-mock
- **Mock Data**: Simulated feedback channels and task queues
- **WSP Integration**: ScoringAgent mock, SecretsManager test environment 