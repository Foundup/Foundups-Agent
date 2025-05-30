# Agent Management Module Tests

WSP-compliant test suite for the multi-agent management system.

## Test Files

| Test File | Description | Coverage Focus |
|-----------|-------------|----------------|
| test_multi_agent_manager.py | Comprehensive tests for multi-agent login, discovery, and management | Agent discovery, conflict detection, session management, authentication routing |

## Test Coverage Areas

### Multi-Agent Discovery & Authentication
- **Agent Discovery**: Tests credential set authentication across multiple accounts
- **Same-Account Conflict Detection**: Prevents agents from using user's own account
- **Authentication Fallback**: Tests quota handling and credential rotation
- **Agent Registry Management**: Agent storage, retrieval, and status tracking

### Session Management
- **Agent Session Lifecycle**: Start, monitor, and end agent sessions
- **Status Reporting**: Comprehensive system status and metrics
- **Agent Selection**: Intelligent agent selection with conflict prevention
- **Coordination Rules**: Multi-agent coordination and conflict avoidance

### Integration Points
- **OAuth Manager Integration**: Authentication service interactions
- **YouTube API Integration**: Live chat and channel access
- **Credential Management**: Multiple credential set handling

## Running Tests

### Full Test Suite
```bash
# From project root
python -m pytest modules/infrastructure/agent_management/agent_management/tests/ -v
```

### Specific Test Classes
```bash
# Test same-account conflict detection
python -m pytest modules/infrastructure/agent_management/agent_management/tests/test_multi_agent_manager.py::TestSameAccountDetector -v

# Test agent registry functionality
python -m pytest modules/infrastructure/agent_management/agent_management/tests/test_multi_agent_manager.py::TestAgentRegistry -v

# Test session management
python -m pytest modules/infrastructure/agent_management/agent_management/tests/test_multi_agent_manager.py::TestAgentSessionManagement -v
```

### With Coverage
```bash
python -m pytest modules/infrastructure/agent_management/agent_management/tests/ --cov=modules.infrastructure.agent_management.agent_management.src --cov-report=html
```

## Test Requirements (WSP Compliance)

### WSP 1: Module Structure
- ✅ Tests located in proper `tests/` directory
- ✅ Source code in `src/` directory
- ✅ Proper import paths using enterprise domain structure

### WSP 5: Test Coverage
- **Target Coverage**: ≥90% for multi-agent manager
- **Current Status**: [To be measured]
- **Critical Paths**: All authentication, conflict detection, and session management

### WSP 11: Interface Testing
- **Contract Tests**: Validation of agent management interfaces
- **Integration Tests**: YouTube API and OAuth manager interactions
- **Mock Testing**: External service simulation

## Known Issues & Status

### Current Test Status
- **Passing**: 9/12 tests
- **Failing**: 3/12 tests (to be addressed)
- **WSP Compliance**: Partial (missing README.md resolved)

### Recent Updates
- 2024-05-30: Added missing tests/README.md for WSP compliance
- 2024-05-30: Identified test failures requiring remediation

## Dependencies

- pytest
- unittest.mock
- modules.infrastructure.oauth_management (authentication services)
- modules.platform_integration.youtube_auth (YouTube API services) 