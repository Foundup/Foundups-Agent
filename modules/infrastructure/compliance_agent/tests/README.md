# Compliance Agent Tests

## Overview
Test suite for the `compliance_agent` infrastructure agent module.

## Test Files
| Test File | Purpose | Coverage Area |
|-----------|---------|---------------|
| `test_compliance_agent.py` | Core agent functionality | Main agent operations |

## Running Tests

### Individual Tests
```bash
# Run all tests for this module
pytest modules/infrastructure/compliance_agent/tests/ -v

# Run specific test file
pytest modules/infrastructure/compliance_agent/tests/test_compliance_agent.py -v
```

### Coverage Analysis
```bash
# Generate coverage report
pytest modules/infrastructure/compliance_agent/tests/ --cov=modules.infrastructure.compliance_agent.src --cov-report=term-missing
```

## WSP Compliance
- **WSP 4 (FMAS)**: Tests validate agent structure compliance
- **WSP 5 (Coverage)**: Maintains ≥90% test coverage requirement
- **WSP 6 (Test Audit)**: Comprehensive test validation for agent operations
- **WSP 54 (Agent Duties)**: Tests verify agent specification compliance

## Test Categories
1. **Initialization Tests**: Agent startup and configuration
2. **Operation Tests**: Core agent functionality 
3. **Integration Tests**: WRE orchestrator compatibility
4. **Error Handling**: Exception and failure scenarios

## Notes
- All tests follow WSP compliance patterns
- Agent tests verify WRE orchestrator integration
- Coverage requirements enforced per WSP 5
