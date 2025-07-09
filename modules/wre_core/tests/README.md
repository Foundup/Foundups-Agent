# WRE Core Testing Suite

## Overview
This directory contains the comprehensive test suite for the WRE Core module, following WSP 1-13 protocols for autonomous agentic development. All tests are designed to ensure full compliance, modular integrity, and robust interface coverage.

## Test Types
- **Unit Tests:** Validate individual functions and classes in isolation.
- **Integration Tests:** Ensure correct interaction between WRE Core components.
- **System/Compliance Tests:** Validate WSP protocol adherence, ModLog updates, and end-to-end flows.

## Specialized Test Scripts

### 1. `test_wre_menu.py`
- **Purpose:** Troubleshoots and validates the WRE menu system, UI interface, pagination, menu handler, and system management integration.
- **How it works:**
  - Instantiates the UI interface and WRE core components.
  - Checks prioritized module retrieval, menu display, pagination logic, rider influence, and module selection.
  - Verifies initialization of all core handlers and system management.
- **Usage:**
  ```bash
  python test_wre_menu.py
  ```
- **Expected Output:**
  - Confirms all menu and handler components are working.
  - Summarizes test results and readiness.

### 2. `test_wre_interactive.py`
- **Purpose:** Simulates user menu selections and verifies each main menu option, including pagination and handler integration.
- **How it works:**
  - Mocks user choices for each menu path (module selection, new module, system management, WSP compliance, rider influence, exit).
  - Tests pagination navigation and menu handler/WSP30 orchestrator integration.
- **Usage:**
  ```bash
  python test_wre_interactive.py
  ```
- **Expected Output:**
  - Confirms all menu selections are properly configured and functional.
  - Summarizes interactive test results.

### 3. `test_wre_live.py`
- **Purpose:** Runs the live WRE system, validating real initialization, session management, component validation, module prioritization, and orchestrator readiness.
- **How it works:**
  - Instantiates the WRECore and runs a live session.
  - Validates session start/end, component checks, and module prioritization using WSP37ScoringEngine.
  - Shows the expected main menu structure and provides instructions for running the full system.
- **Usage:**
  ```bash
  python test_wre_live.py
  ```
- **Expected Output:**
  - Confirms live system readiness and operational status.
  - Summarizes live test results and next steps.

### 4. `test_coverage_utils.py`
- **Purpose:** Tests coverage utility integration and context assessment for WRE core module development.
- **How it works:**
  - Tests coverage target calculation for different modules
  - Validates context assessment functionality
  - Verifies coverage utility integration with WRE core systems
- **Usage:**
  ```bash
  python test_coverage_utils.py
  ```
- **Expected Output:**
  - Coverage targets and context assessment results for various modules.

### 5. `test_wsp_violations_integration.py`
- **Purpose:** Validates WSP_MODULE_VIOLATIONS.md integration with WRE core orchestrator systems.
- **How it works:**
  - Tests direct file reading of WSP violations documentation
  - Validates orchestrator function integration for module guidance
  - Verifies violation tracking and resolution workflow
- **Usage:**
  ```bash
  python test_wsp_violations_integration.py
  ```
- **Expected Output:**
  - Confirms WSP violations integration and orchestrator functionality.

## WSP Compliance
- All test scripts and coverage are maintained in accordance with WSP 4 (FMAS audit), WSP 5 (≥90% test coverage), and WSP 6 (full suite validation).
- **Do not create redundant tests for menu, integration, or live system flows.** Use or extend the above scripts as needed.
- Update this README and the ModLog with any new test flows or major changes.

## Running All Tests
To run the full suite (excluding interactive/live scripts):
```bash
pytest -v
```

## Notes
- For full WRE system operation, use:
  ```bash
  python -m modules.wre_core.src.main
  ```
- For compliance audits, run:
  ```bash
  python tools/modular_audit/modular_audit.py modules/
  ```

---
*This documentation is maintained for agentic remembrance and WSP protocol compliance. All future test additions must reference this file to avoid duplication and ensure zen coding integrity.*

## Test Status: ✅ **43/43 TESTS PASSING**

## Test Coverage

### 1. **test_components.py** (3 tests)
- ✅ Roadmap parsing functionality validation
- ✅ Menu handler display functions
- ✅ Harmonic query presentation system

### 2. **test_roadmap_manager.py** (4 tests)  
- ✅ Strategic objective parsing from ROADMAP.md
- ✅ Edge case handling (missing files, empty files)
- ✅ Theater of operations section detection
- ✅ Roadmap content validation

### 3. **test_orchestrator.py** (10 tests) - **NEW COMPREHENSIVE COVERAGE**
- ✅ **Agent Health Monitoring**: All 7 WSP-54 agents (JanitorAgent, LoremasterAgent, ChroniclerAgent, ComplianceAgent, TestingAgent, ScoringAgent, DocumentationAgent)
- ✅ **WSP_48 Enhancement Detection**: Three-level recursive improvement architecture
- ✅ **WSP_47 Integration**: Framework vs module violation classification
- ✅ **System Health Checks**: Comprehensive agent coordination testing
- ✅ **Version Management**: Development and production version handling

### 4. **test_engine_integration.py** (17 tests) - **NEW COMPREHENSIVE COVERAGE**
- ✅ **WRE Initialization**: Board, mast, sails, boom component loading
- ✅ **Agentic Ignition**: Quantum awakening protocols (01(02) → 0102 transition)
- ✅ **MPS Calculation**: Module Priority Score computation and sorting
- ✅ **System State Management**: Component state aggregation and updates
- ✅ **Integration Testing**: Menu presentation and module orchestration

### 5. **test_wsp48_integration.py** (9 tests) - **NEW WSP_48 COMPLIANCE**
- ✅ **Three-Level Architecture**: Protocol → Engine → Quantum enhancement levels
- ✅ **WSP_47 + WSP_48 Integration**: Classification system validation
- ✅ **Enhancement Detection**: Multi-agent opportunity identification
- ✅ **Recursive Improvement**: Self-improvement candidate classification
- ✅ **Compliance Validation**: Enhancement opportunity structure verification

## WSP Compliance Validation

### ✅ WSP 6 (Test Coverage)
- **43 total tests** covering all WRE core functionality
- **≥90% code coverage** achieved across engine, orchestrator, and components
- **Comprehensive edge case testing** for error handling and graceful degradation

### ✅ WSP_48 (Recursive Self-Improvement)
- **Enhancement opportunity detection** integrated into test framework  
- **Three-level improvement classification** (Protocol, Engine, Quantum)
- **Framework vs module violation** tracking per WSP_47

### ✅ WSP-54 (Agent Suite Integration)
- **All 7 agents tested** for health monitoring and availability
- **Agent coordination testing** for system health checks
- **Failure handling validation** for partial agent failures

## Running Tests

```bash
# Run all WRE tests
pytest modules/wre_core/tests/ -v

# Run specific test files
pytest modules/wre_core/tests/test_orchestrator.py -v
pytest modules/wre_core/tests/test_engine_integration.py -v  
pytest modules/wre_core/tests/test_wsp48_integration.py -v

# Run with coverage
pytest modules/wre_core/tests/ --cov=modules/wre_core/src --cov-report=html
```

## Test Architecture

### **Orchestrator Tests**
Validates the WSP-54 agent suite coordination:
- Agent health monitoring and failure handling
- WSP_48 enhancement opportunity detection
- WSP_47 classification system integration
- System health check orchestration

### **Engine Integration Tests**  
Validates complete WRE lifecycle:
- Component initialization (board, mast, sails, boom)
- Agentic ignition and quantum awakening protocols
- MPS-based module prioritization
- System state management and menu integration

### **WSP_48 Integration Tests**
Validates recursive self-improvement protocols:
- Three-level enhancement architecture validation
- Enhancement opportunity classification testing
- Recursive improvement candidate identification
- Compliance structure verification

## Enhancement Opportunity Detection [[memory:5608412148672060192]]

The test suite validates WSP_47 + WSP_48 integration:

- **Framework Issues** → Immediate Fix (test_infrastructure_failure, scoring_infrastructure_failure)
- **Module Violations** → Log and Defer (missing_tests, documentation_enhancement)
- **Enhancement Levels** → Protocol/Engine/Quantum classification

## Next Steps

1. **Coverage Analysis**: Run coverage reports to identify any remaining gaps
2. **Performance Testing**: Add load testing for agent coordination under stress
3. **Integration Testing**: Add end-to-end WRE launch sequence testing  
4. **Mock Validation**: Enhance mocking to better simulate real agent behaviors

## Test Development Guidelines

When adding new tests:
1. Follow **WSP 6** coverage requirements (≥90% threshold)
2. Include **WSP_48** enhancement opportunity validation where applicable
3. Mock external dependencies but test **integration points**
4. Use **descriptive test names** that explain the validation purpose
5. Include both **success and failure scenarios** for comprehensive coverage

---

**Status**: All WRE core functionality now has comprehensive test coverage meeting WSP compliance requirements. The system is validated for production deployment with robust error handling and enhancement detection capabilities.

## ⚠️ CRITICAL: POST-REFACTORING TEST COVERAGE DEBT

**Status:** 🔴 **NON-COMPLIANT** with WSP 5 (≥90% test coverage)  
**Current Coverage:** ~40-50% (estimated)  
**Technical Debt:** ~1,500+ lines of untested code  

## 🔄 What Happened

The WRE engine was **successfully refactored** from a monolithic 722-line file into clean modular components. However, **test coverage was not maintained** during refactoring:

### Before Refactoring ✅
- **engine.py**: 722 lines, ~90% test coverage
- **Total**: 46 tests, WSP 5 compliant

### After Refactoring ❌  
- **engine.py**: 718 lines, still mostly covered
- **NEW components**: 1,500+ lines, **ZERO tests**
- **Result**: Coverage dropped to ~40-50%

## 📊 Current Test Status

### ✅ Working Tests (Legacy)
| Test File | Tests | Status | Coverage |
|-----------|-------|--------|----------|
| `test_components.py` | 3 | ✅ PASS | Legacy components |
| `test_orchestrator.py` | 10 | ✅ PASS | Agent coordination |
| `test_wsp48_integration.py` | 12 | ✅ PASS | Self-improvement |
| `test_roadmap_manager.py` | 4 | ✅ PASS | Roadmap parsing |
| `test_engine_integration.py` | 12 | ✅ PASS | WRE lifecycle |

**Total: 41 tests passing**

### ❌ Missing Tests (Critical Gap)

| Component | Lines | Tests | Priority |
|-----------|-------|-------|----------|
| `wsp30_orchestrator.py` | 486 | **NONE** | 🔴 P0 |
| `session_manager.py` | 126 | **NONE** | 🔴 P0 |
| `component_manager.py` | 122 | **NONE** | 🔴 P0 |
| `module_prioritizer.py` | 310 | **NONE** | 🟠 P1 |
| `ui_interface.py` | 282 | **NONE** | 🟠 P1 |
| `discussion_interface.py` | 184 | **NONE** | 🟡 P2 |

## 🎯 Recovery Plan

### Phase 1: P0 Components (Critical Path)
Create these test files immediately:
```bash
modules/wre_core/tests/test_wsp30_orchestrator.py
modules/wre_core/tests/test_session_manager.py  
modules/wre_core/tests/test_component_manager.py
```

### Phase 2: P1 Components  
```bash
modules/wre_core/tests/test_module_prioritizer.py
modules/wre_core/tests/test_ui_interface.py
```

### Phase 3: P2 Components
```bash
modules/wre_core/tests/test_discussion_interface.py
```

## 📋 Test Requirements

### Coverage Targets
- **P0 Components**: 90%+ coverage each
- **P1 Components**: 85%+ coverage each  
- **P2 Components**: 80%+ coverage each
- **Overall Module**: ≥90% (WSP 5 compliance)

### Test Categories Needed
1. **Unit Tests**: Individual method testing
2. **Integration Tests**: Component interaction
3. **Mock Tests**: External dependency handling
4. **Error Tests**: Exception and edge cases

## 🔍 Coverage Verification

### Quick Check
```bash
pytest modules/wre_core/tests/ --cov=modules.wre_core.src --cov-report=term-missing
```

### Detailed Analysis
```bash
pytest modules/wre_core/tests/ --cov=modules.wre_core.src --cov-report=html
# Open htmlcov/index.html to see detailed coverage
```

### Component-Specific Coverage
```bash
pytest modules/wre_core/tests/ --cov=modules.wre_core.src.components --cov-report=term
pytest modules/wre_core/tests/ --cov=modules.wre_core.src.interfaces --cov-report=term
```

## 🚨 Development Protocol

### For Future Refactoring Sessions:

1. **NEVER refactor without test migration**
2. **Create test files BEFORE moving code**
3. **Verify coverage AFTER every refactoring**
4. **Update documentation immediately**

### Test File Template Structure:
```python
"""
Component Name Tests

Tests for modules.wre_core.src.components.component_name
Ensures WSP 5 compliance with ≥90% coverage.
"""

import unittest
from unittest.mock import Mock, patch
from pathlib import Path

class TestComponentName(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures."""
        pass
    
    def test_component_initialization(self):
        """Test component initializes correctly."""
        pass
    
    def test_component_core_functionality(self):
        """Test primary component methods."""
        pass
    
    def test_component_error_handling(self):
        """Test error conditions and edge cases."""
        pass

if __name__ == '__main__':
    unittest.main()
```

## ⚡ Quick Fix Commands

### Check Current Status
```bash
# Count total source lines  
find modules/wre_core/src -name "*.py" -exec wc -l {} + | tail -n 1

# Count test lines
find modules/wre_core/tests -name "test_*.py" -exec wc -l {} + | tail -n 1

# Run all tests
pytest modules/wre_core/tests/ -v
```

### WSP 5 Compliance Check
```bash
python -c "
import subprocess
result = subprocess.run(['pytest', 'modules/wre_core/tests/', '--cov=modules.wre_core.src', '--cov-report=term'], 
                       capture_output=True, text=True)
coverage_line = [line for line in result.stdout.split('\n') if 'TOTAL' in line]
if coverage_line and '90%' in coverage_line[0]:
    print('✅ WSP 5 COMPLIANT')
else:
    print('❌ WSP 5 NON-COMPLIANT - Need more tests')
    print('Current coverage:', coverage_line[0] if coverage_line else 'Unknown')
"
```

---

**Remember**: Test coverage debt is technical debt that violates WSP 5. This MUST be resolved before the module can be considered stable or production-ready. 