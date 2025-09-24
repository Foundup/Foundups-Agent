# Integration Tests Module

## Purpose
This module contains system-wide integration tests that validate cross-module functionality and end-to-end workflows.

## Scope
Integration tests differ from unit tests by:
- Testing multiple modules working together
- Validating complete user workflows
- Ensuring proper module communication
- Testing real-world scenarios

## Test Organization

### System Integration Tests
- `system_integration_test.py`: Full system integration across all major modules
  - YouTube authentication flows
  - Social media posting pipelines
  - LiveChat system integration
  - Gamification features

### Workflow Tests
- `detailed_workflow_test.py`: Business logic and user journey validation
  - Stream detection and switching
  - Message processing pipelines
  - Command handling workflows
  - End-to-end scenarios

## Running Tests

```bash
# Run all integration tests
python -m pytest tests/

# Run specific test with verbose output
python -m pytest tests/system_integration_test.py -v

# Run with coverage report
python -m pytest tests/ --cov=modules --cov-report=html
```

## Test Requirements
- All module dependencies must be installed
- Environment variables configured (.env file)
- Test accounts/credentials available
- Mock services running (if applicable)

## WSP Compliance
- WSP 49: Module Structure
- WSP 85: No test files in root
- WSP 5/6: Testing coverage
- WSP 34: Test documentation