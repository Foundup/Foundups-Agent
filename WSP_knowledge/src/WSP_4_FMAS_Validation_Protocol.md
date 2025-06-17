# WSP 4: FMAS Validation Protocol

**Version**: 1.1.0
**Date**: 2025-06-18
**Status**: ACTIVE
**Source**: `docs/archive/FoundUps_WSP_Framework.md`

## 1. Overview

This protocol governs the automated validation of test file existence and structure, as well as overall module structural compliance. It is a key component of the **FMAS (Framework and Module Auditing System)**, ensuring that all development artifacts adhere to the foundational rules of the framework before they are integrated.

## 2. Validation Process

The **`ComplianceAgent`** is responsible for executing the FMAS audit using the `tools/modular_audit/modular_audit.py` script. The audit performs the following checks relevant to this protocol:

### 2.1. Module Structure Compliance (Related to WSP 1)
-   **Check**: Verifies that all Python files reside exclusively within `src/` or `tests/` subdirectories, with the exception of the module's top-level `__init__.py`.
-   **Command**: `find modules/ -name "*.py" ! -path "*/src/*" ! -path "*/tests/*" ! -name "__init__.py"`
-   **Expected Result**: No output. Any file listed is a violation.

### 2.2. Test Documentation Existence (Related to WSP 7)
-   **Check**: Ensures every `tests/` directory contains a `README.md` file for documenting test patterns and strategies.
-   **Command**: `find modules/ -path "*/tests" ! -exec test -f {}/README.md \; -print`
-   **Expected Result**: No output. Any directory listed is a violation.

## 3. Failure Condition

-   If any validation check fails, the FMAS will flag the module as non-compliant.
-   In an automated CI/CD environment or pre-commit hook, a failure of this audit will block the module from being integrated, tested further, or deployed.
-   The audit script's output will specify the exact files or directories in violation. 