# Presence Aggregator Test Suite

## Purpose
Test suite for PresenceAggregator implementation - strategic decomposition from auto_meeting_orchestrator PoC.

## Test Strategy
- **Unit Tests**: Core aggregation logic, status normalization, confidence scoring
- **Integration Tests**: Platform adapter integration, WRE secrets manager
- **Performance Tests**: Multi-platform aggregation latency, subscription handling
- **Security Tests**: WSP 71 secrets management integration

## Test Coverage
- Multi-platform presence collection and aggregation
- Status normalization across different platform formats
- Confidence scoring algorithms and platform weighting
- Real-time subscription and notification system
- Error handling and graceful degradation

## How to Run
```bash
# Run all tests
pytest modules/platform_integration/presence_aggregator/tests/ -v

# Run with coverage
pytest modules/platform_integration/presence_aggregator/tests/ --cov=modules.platform_integration.presence_aggregator.src --cov-report=term-missing
```

## Test Environment
- **Dependencies**: pytest, pytest-asyncio, pytest-mock
- **Mock APIs**: Simulated Discord, WhatsApp, Zoom presence APIs
- **WSP Integration**: SecretsManager test environment, WRE logger mocking 