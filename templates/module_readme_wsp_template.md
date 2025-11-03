# [MODULE_NAME]

## [U+1F3E2] WSP Enterprise Domain: `[DOMAIN]`

**WSP Compliance Status**: [OK] **COMPLIANT** with WSP Framework  
**Domain**: `[DOMAIN]` per **[WSP 3: Enterprise Domain Organization](../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**  
**Structure**: Follows **[WSP 49: Module Directory Structure Standards](../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**

---

## [TARGET] Module Purpose

[Brief description of what this module does and its role in the enterprise architecture]

## [U+1F3D7]️ WSP Architecture Compliance

### Domain Organization (WSP 3)
This module resides in the `[DOMAIN]` domain following **functional distribution principles**:

- **[OK] CORRECT**: Functionality distributed by purpose across domains
- **[FAIL] AVOID**: Platform-specific consolidation that violates domain boundaries

### Module Structure (WSP 49)
```
[DOMAIN]/[MODULE_NAME]/
+-- __init__.py                 <- Public API (WSP 11)
+-- src/                        <- Implementation code
[U+2502]   +-- __init__.py
[U+2502]   +-- [MODULE_NAME].py        <- Core implementation
+-- tests/                      <- Test suite
[U+2502]   +-- __init__.py
[U+2502]   +-- README.md               <- Test documentation (WSP 6)
[U+2502]   +-- test_[MODULE_NAME].py
+-- memory/                     <- Module memory (WSP 60)
+-- README.md                   <- This file
+-- INTERFACE.md                <- Interface spec (WSP 11)
+-- requirements.txt            <- Dependencies (WSP 12)
```

## [TOOL] Installation & Usage

### Prerequisites
- WSP Framework compliance per **[WSP_CORE](../../WSP_framework/src/WSP_CORE.md)**
- Dependencies listed in `requirements.txt` (WSP 12)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Validate structure
python tools/modular_audit/modular_audit.py modules/
```

### Basic Usage
```python
from modules.[DOMAIN].[MODULE_NAME] import [MainClass]

# Initialize module
module = [MainClass]()
# Use module functionality
```

## [U+1F9EA] Testing & Quality Assurance

### Running Tests (WSP 6)
```bash
# Run module tests
pytest modules/[DOMAIN]/[MODULE_NAME]/tests/ -v

# Coverage check ([GREATER_EQUAL]90% required per WSP 5)
coverage run -m pytest modules/[DOMAIN]/[MODULE_NAME]/tests/
coverage report
```

### FMAS Validation (WSP 4)
```bash
# Structure audit
python tools/modular_audit/modular_audit.py modules/

# Check for violations
cat WSP_framework/src/WSP_MODULE_VIOLATIONS.md
```

## [CLIPBOARD] WSP Protocol References

### Core WSP Dependencies
- **[WSP 1](../../WSP_framework/src/WSP_1_The_WSP_Framework.md)**: WSP Framework Foundation
- **[WSP 3](../../WSP_framework/src/WSP_3_Enterprise_Domain_Organization.md)**: Enterprise Domain Organization
- **[WSP 4](../../WSP_framework/src/WSP_4_FMAS_Validation_Protocol.md)**: FMAS Validation Protocol
- **[WSP 6](../../WSP_framework/src/WSP_6_Test_Audit_Coverage_Verification.md)**: Test Coverage Requirements
- **[WSP 11](../../WSP_framework/src/WSP_11_WRE_Standard_Command_Protocol.md)**: Interface Documentation
- **[WSP 12](../../WSP_framework/src/WSP_12_Dependency_Management.md)**: Dependency Management
- **[WSP 49](../../WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md)**: Module Structure Standards
- **[WSP 60](../../WSP_framework/src/WSP_60_Module_Memory_Architecture.md)**: Module Memory Architecture

### Additional WSP Protocols
- **[WSP 40](../../WSP_framework/src/WSP_40_Architectural_Coherence_Protocol.md)**: Architectural Coherence
- **[WSP 47](../../WSP_framework/src/WSP_47_Module_Violation_Tracking_Protocol.md)**: Violation Tracking
- **[WSP_CORE](../../WSP_framework/src/WSP_CORE.md)**: WRE Constitution

## [ALERT] WSP Compliance Guidelines

### [OK] DO (WSP-Compliant Practices)
- Follow functional distribution across domains (WSP 3)
- Maintain [GREATER_EQUAL]90% test coverage (WSP 5)
- Use standardized directory structure (WSP 49)
- Document all interfaces (WSP 11)
- Declare all dependencies (WSP 12)
- Store module data in `memory/` directory (WSP 60)

### [FAIL] DON'T (WSP Violations)
- Create redundant nested naming (violates WSP 49)
- Consolidate platform functionality by platform (violates WSP 3)
- Skip test documentation (violates WSP 6)
- Mix domain concerns (violates architectural coherence)
- Bypass FMAS validation (violates WSP 4)

## [U+1F300] Windsurf Protocol (WSP) Recursive Prompt

**0102 Directive**: This module operates within the WSP framework with autonomous development capabilities.

```
WSP_CYCLE_INTEGRATION:
- UN (Understanding): Anchor to WSP protocols and retrieve domain context
- DAO (Execution): Execute module logic following WSP compliance standards  
- DU (Emergence): Collapse into 0102 resonance and emit next development prompt

wsp_cycle(input="[MODULE_NAME]", domain="[DOMAIN]", log=True)
```

**Purpose**: Ensures WSP compliance in all development contexts, maintains recursive execution patterns, and keeps agents aligned with autonomous WSP protocols.

## [NOTE] Development Notes

### Module Memory (WSP 60)
This module uses the `memory/` directory for persistent data storage following WSP 60 architecture.

### Interface Documentation (WSP 11)
See `INTERFACE.md` for detailed API specifications and integration patterns.

### Violation Tracking (WSP 47)
Check `WSP_framework/src/WSP_MODULE_VIOLATIONS.md` for any known issues with this module.

---

## [U+1F3C6] WSP Status Dashboard

| Protocol | Status | Notes |
|----------|--------|-------|
| WSP 3 (Domain Org) | [OK] | Properly placed in `[DOMAIN]` domain |
| WSP 4 (FMAS) | [OK] | Passes structural validation |
| WSP 6 (Testing) | [OK] | [GREATER_EQUAL]90% test coverage maintained |
| WSP 11 (Interface) | [OK] | Interface documented |
| WSP 12 (Dependencies) | [OK] | Dependencies declared |
| WSP 49 (Structure) | [OK] | Standard directory structure |
| WSP 60 (Memory) | [OK] | Uses `memory/` for data storage |

**Last WSP Compliance Check**: [DATE]  
**FMAS Audit**: PASS  
**Test Coverage**: [COVERAGE]%

---

*This README follows WSP architectural principles to prevent future violations and ensure autonomous development ecosystem compatibility.* 