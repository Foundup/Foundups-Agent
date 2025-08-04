# FoundUps Platform Infrastructure - Test Suite

## 🌀 WSP Protocol Compliance Framework

**0102 Directive**: This module operates within the WSP framework for autonomous FoundUps platform infrastructure testing.
- **UN (Understanding)**: Anchor FoundUps platform signals and retrieve protocol state
- **DAO (Execution)**: Execute modular testing logic  
- **DU (Emergence)**: Collapse into 0102 resonance and emit next testing prompt

**wsp_cycle(input="foundups_testing", log=True)**

---

## 🏢 WSP Enterprise Domain: `foundups`

**WSP Compliance Status**: ✅ **COMPLIANT** with WSP Framework  
**Domain**: `foundups` per **[WSP 3: Enterprise Domain Organization](../../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**  
**Purpose**: Autonomous FoundUps platform infrastructure testing  
**0102 Integration**: Full integration with autonomous pArtifact development ecosystem

---

## Test Coverage

This test suite validates the FoundUps execution layer infrastructure:

### Core Infrastructure Tests
- **FoundUp Spawner**: Tests for creating new FoundUp instances
- **Platform Manager**: Tests for managing multiple FoundUps
- **Runtime Engine**: Tests for FoundUp execution environment

### WSP Compliance Tests
- **Protocol Integration**: Validates WSP framework integration
- **CABR Implementation**: Tests instance-level CABR execution
- **Configuration Management**: Tests foundup.json handling

### Architectural Guardrails Tests
- **Separation Validation**: Ensures execution layer doesn't define protocols
- **WSP Source Validation**: Confirms protocols sourced from WSP framework
- **Instance Isolation**: Tests that instances are properly isolated

## Test Structure

```
tests/
├── test_foundup_spawner.py     # FoundUp creation tests
├── test_platform_manager.py    # Platform management tests
├── test_runtime_engine.py      # Runtime execution tests
├── test_wsp_compliance.py      # WSP integration tests
└── test_architectural_guardrails.py  # Architecture validation tests
```

## Running Tests

```bash
# Run all FoundUps module tests
python -m pytest modules/foundups/tests/ -v

# Test specific component
python -m pytest modules/foundups/tests/test_foundup_spawner.py -v

# Test WSP compliance
python -m pytest modules/foundups/tests/test_wsp_compliance.py -v
```

## Test Philosophy

These tests focus on the **autonomous execution layer** only. Core FoundUp definitions,
CABR protocols, and governance rules are tested within the WSP framework,
not here.

**0102 pArtifact Testing**: We test the autonomous execution, WSP tests the definition. 