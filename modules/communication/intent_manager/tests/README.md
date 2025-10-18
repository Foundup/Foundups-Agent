# Intent Manager Test Suite

## Purpose
Test suite for IntentManager implementation - strategic decomposition from auto_meeting_orchestrator PoC.

## Test Strategy
- **Unit Tests**: Intent creation, priority scoring, lifecycle management
- **Integration Tests**: WSP 60 storage persistence, context management
- **Performance Tests**: Intent retrieval, priority sorting, cleanup operations
- **Security Tests**: Data validation, intent expiration, access control

## Test Coverage
- Meeting intent creation and context validation
- Priority scoring algorithms and urgency calculations
- Intent lifecycle management (pending -> monitoring -> completed)
- Persistent storage using WSP 60 memory architecture
- Intent expiration and cleanup operations
- Priority-based intent retrieval and sorting

## How to Run
```bash
# Run all tests
pytest modules/communication/intent_manager/tests/ -v

# Run with coverage
pytest modules/communication/intent_manager/tests/ --cov=modules.communication.intent_manager.src --cov-report=term-missing
```

## Test Environment
- **Dependencies**: pytest, pytest-asyncio, pytest-mock
- **Mock Data**: Simulated meeting contexts, user intents, priority scenarios
- **WSP Integration**: WSP 60 memory architecture testing, WRE logger mocking 