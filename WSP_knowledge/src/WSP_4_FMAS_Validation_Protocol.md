# WSP 4: FMAS Validation Protocol
- **Status:** Active
- **Purpose:** To govern the automated validation of module structural compliance, ensuring all modules adhere to framework rules.
- **Trigger:** Before code integration (pre-commit hook or CI pipeline); when a new module is created.
- **Input:** The path to the `modules/` directory.
- **Output:** A compliance report listing any structural violations.
- **Responsible Agent(s):** ComplianceAgent

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

### 2.3. System-Wide Naming Coherence (Related to WSP 19)
-   **Purpose**: Prevents system coherence violations by validating that any naming changes are propagated across ALL system layers.
-   **Trigger**: Before any modification to names, identifiers, or terminology used across multiple files.

#### 2.3.1. Pre-Change Impact Analysis
Before ANY naming change, FMAS must execute:
```bash
# Step 1: Comprehensive Reference Search
grep -r "TARGET_NAME" WSP_framework/ WSP_knowledge/ WSP_agentic/ modules/ tools/ tests/

# Step 2: Configuration Analysis  
find . -name "*.json" -o -name "*.yaml" -o -name "*.toml" | xargs grep "TARGET_NAME"

# Step 3: Import Chain Analysis
grep -r "from.*TARGET_NAME\|import.*TARGET_NAME" modules/ tools/
```

#### 2.3.2. Impact Classification
| Impact Level | Definition | FMAS Action Required |
|--------------|------------|---------------------|
| **ISOLATED** | [U+2264]3 references, single module | Standard validation |
| **MODULAR** | 4-10 references, cross-module | Cross-module validation |
| **SYSTEMIC** | >10 references, cross-domain | Full coherence protocol |
| **CRITICAL** | Core infrastructure, WRE engine | Architecture review + approval |

#### 2.3.3. Naming Coherence Validation
-   **Check**: Verifies that ALL references to changed names have been updated consistently across the system.
-   **Command**: `grep -r "OLD_NAME" . && echo "ERROR: Incomplete naming propagation detected"`
-   **Expected Result**: No output. Any remaining references to old names indicate incomplete propagation.

#### 2.3.4. Post-Change System Validation
After naming changes, FMAS must validate:
```bash
# Import validation - verify all imports resolve
python -c "import modules.target_module; print('NAMING_COHERENCE_SUCCESS')"

# Test validation - ensure no naming-related test failures
pytest modules/ --tb=short -q

# Configuration validation - verify all configs parse correctly
python -c "import json; [json.load(open(f)) for f in ['modules/*/module.json']]"
```

### 2.4. Module Memory Structure Validation (Related to WSP 60)
-   **Check**: Validates that modules using memory storage follow the modular memory architecture.
-   **Validation Points**:
    - Memory directories located at `modules/[domain]/[module]/memory/` (not legacy `memory/`)
    - Memory access patterns comply with module ownership (modules only write to their own memory)
    - Memory cleanup and retention policies are documented in module READMEs
-   **Expected Result**: Memory structure follows WSP 60 modular architecture principles.

### 2.5. File Size Compliance Validation (Related to WSP 62)
-   **Check**: Validates that all files comply with WSP 62 size thresholds and refactoring requirements.
-   **Validation Points**:
    - Python files under 500 lines (or domain-specific threshold)
    - Configuration files under 200 lines
    - Functions under 50 lines, classes under 200 lines
    - Documented exemptions for oversized files
    - Refactoring plans for files approaching thresholds
-   **Command**: `python tools/modular_audit/modular_audit.py modules/ --wsp-62-size-check`
-   **Expected Result**: All files comply with size thresholds or have documented exemptions.

## 3. Failure Condition

-   If any validation check fails, the FMAS will flag the module as non-compliant.
-   **Naming Coherence Failures**: If incomplete naming propagation is detected, FMAS will immediately trigger rollback procedures and prevent system integration.
-   **Size Compliance Failures**: If WSP 62 size violations are detected without documented exemptions, FMAS will block integration and require refactoring.
-   In an automated CI/CD environment or pre-commit hook, a failure of this audit will block the module from being integrated, tested further, or deployed.
-   The audit script's output will specify the exact files or directories in violation.

### 3.1. Naming Coherence Emergency Protocol
When naming coherence violations are detected:
1. **Immediate Halt**: Stop all further system modifications
2. **Impact Assessment**: Generate complete reference map of affected files
3. **Rollback Decision**: Determine if rollback is required or if forward-fix is possible
4. **System Validation**: Re-run full test suite and import validation after any corrections

### 3.2. Size Compliance Emergency Protocol (WSP 62 Integration)
When size violations are detected:
1. **Immediate Assessment**: Categorize violations by severity (>150% threshold = critical)
2. **Exemption Review**: Check for valid documented exemptions
3. **Refactoring Planning**: Generate automated refactoring recommendations
4. **Integration Blocking**: Prevent further development until compliance achieved

### 2.4. Test Framework Fixture Dependency Management (Related to WSP 6)
-   **Purpose**: Validates pytest fixture dependencies and parametrized test configurations to prevent test framework structural failures.
-   **Trigger**: When test files use pytest fixtures, parametrization, or advanced pytest features.

#### 2.4.1. Pytest Fixture Validation
-   **Check**: Verifies that all fixture dependencies are properly declared and available.
-   **Command**: `pytest --collect-only modules/ 2>&1 | grep "fixture.*not found"`
-   **Expected Result**: No output. Any fixture errors indicate missing dependencies.

#### 2.4.2. Parametrized Test Validation
-   **Check**: Ensures parametrized tests have proper fixture setup or data sources.
-   **Command**: `grep -r "@pytest.mark.parametrize\|def test_.*(" modules/*/tests/ | grep -v "def test_.*()"`
-   **Expected Result**: All parametrized tests must have corresponding data sources or fixtures.

#### 2.4.3. Test Framework Structural Integrity
-   **Check**: Validates that test files follow proper pytest conventions and can be collected successfully.
-   **Command**: `pytest --collect-only modules/ --quiet`
-   **Expected Result**: Successful collection of all tests with no collection errors.

#### 2.4.4. Test Framework Emergency Repair Protocol
When pytest fixture dependency failures are detected:
1. **Immediate Analysis**: Identify missing fixture definitions or incorrect test signatures
2. **Fixture Resolution**: Either add missing fixtures or remove parametrization if not needed
3. **Test Framework Validation**: Re-run collection to ensure test discovery succeeds
4. **Integration Testing**: Verify repaired tests can execute successfully

### 3.2. Critical Naming Violations
The following naming changes require **Architecture Review** before FMAS validation:
- Core agent class names (ChroniclerAgent, ComplianceAgent, etc.)
- WRE engine components and interfaces
- Cross-WSP canonical symbols and terminology
- Module import paths and public API names 