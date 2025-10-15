# WSP 6: Test Audit & Coverage Verification
- **Status:** Active
- **Purpose:** To define the comprehensive, multi-step audit for ensuring a module's quality, compliance, and integration-readiness.
- **Trigger:** Before committing code to a protected branch; as a final quality gate before integration.
- **Input:** The `modules/` directory or a specific module path.
- **Output:** A final pass/fail audit result based on structure, tests, and coverage.
- **Responsible Agent(s):** TestingAgent, ComplianceAgent

This WSP defines the comprehensive audit of active modules to ensure quality, compliance, and integration-readiness. The primary goals are to:
-   Serve as a final quality gate before integration.
-   Verify compliance with all structural and documentation-related WSPs.
-   Ensure test coverage meets the project standard.
-   Validate that modules correctly implement their defined interfaces (contract testing).

The rigor of this audit should be scaled based on a module's LLME score, with foundational modules (`C=2`) receiving the most stringent review.

## 2. Procedure

### A. Preparation
1.  Create a dedicated audit branch (e.g., `test/audit-YYYYMMDD`) from the latest `main`.
2.  Ensure all dependencies are installed and the environment is clean.

### B. Step 1: Structural & Test File Audit (WSP 4)
-   **Action**: Run the FoundUps Modular Audit System (FMAS) to check for structural integrity and test file existence.
-   **Command**: `python tools/modular_audit/modular_audit.py ./modules`
-   **Goal**: Remediate all `STRUCTURE_ERROR` and `NO_TEST` warnings. Every source file must have a corresponding test file.

### C. Step 2: Test Suite Execution Sweep
-   **Action**: Run the entire test suite, paying close attention to failures, errors, and warnings.
-   **Command**: `pytest -ra modules/`
-   **Goal**: A clean run with zero `F` (Failures), `E` (Errors), or unaddressed `W` (Warnings). Skips (`s`) and expected failures (`x`/`X`) should be reviewed to ensure they are still valid.

### D. Step 3: Interface Contract Testing (WSP 12)
-   **Action**: For each module with a defined interface, run its specific contract tests. This verifies that the module adheres to its public-facing promises.
-   **Goal**: Zero contract test failures. This is especially critical for modules with high local impact (`B=2`) or systemic importance (`C=2`).

### E. Step 4: Per-Module Coverage Verification
-   **Action**: Loop through each module and verify its test coverage meets the project standard.
-   **Standard**: **[U+2265]90% test coverage** is required for all modules. Higher thresholds (e.g., 95% or 100%) may be mandated for foundational (`C=2`) modules.
-   **Command**: `pytest <module_path>/tests/ --cov=<module_import_path>.src --cov-fail-under=90`
-   **Goal**: Every module must meet or exceed the 90% threshold.

### F. Step 5: Behavioral Synchronization Verification
-   **Purpose**: Validates that test expectations remain synchronized with actual module behavior changes.
-   **Trigger**: When tests fail due to changing behavior rather than regressions.

#### F.1. Test-Code Behavioral Drift Detection
-   **Check**: Identifies test failures caused by intentional behavior changes vs. actual bugs.
-   **Command**: `pytest modules/ --tb=short | grep "AssertionError.*Expected.*but got"`
-   **Analysis**: Review each assertion failure to determine if it represents:
    - **Regression**: Unintended behavior change requiring code fix
    - **Evolution**: Intended behavior improvement requiring test update

#### F.2. Behavioral Change Impact Assessment
When behavioral drift is detected:
1. **Root Cause Analysis**: Determine if behavior change was intentional
2. **Impact Classification**: Assess scope of behavioral change:
   - **ISOLATED**: Single test case, minimal scope
   - **MODULAR**: Multiple tests within one module  
   - **SYSTEMIC**: Cross-module test impacts
3. **Synchronization Decision**: Choose appropriate response:
   - **Revert Code**: If change was unintentional regression
   - **Update Tests**: If change represents intentional improvement
   - **Design Review**: If change has systemic implications

#### F.3. Test Expectation Update Protocol
For intentional behavioral improvements:
1. **Validation**: Confirm new behavior is desired and documented
2. **Test Update**: Modify test expectations to match new behavior
3. **Documentation**: Update module documentation to reflect behavior changes
4. **Integration Check**: Verify changes don't break dependent modules

#### F.4. Dynamic Response Testing Protocol
For modules with randomized/dynamic response generation:
1. **Deterministic Control**: Use mocking or seeding to ensure consistent test responses
2. **Pattern Testing**: Test response patterns/structure rather than exact content
3. **Behavioral Assertions**: Focus on response type, format, and semantic categories
4. **Range Validation**: Verify responses fall within acceptable parameter bounds

**Example Dynamic Test Pattern**:
```python
# Instead of exact response matching:
assert response == "Exact expected text"

# Use pattern/structure matching:
assert isinstance(response, str) and len(response) > 0
assert "[U+270A][U+270B][U+1F590][U+FE0F]" in response  # Contains expected emoji sequence
assert response.startswith(("Nice", "That's", "I see"))  # Pattern matching
```

## 3. Acceptance Criteria (Audit PASS)

An audit is considered passed only when all of the following criteria are met:
-   [U+2705] **FMAS**: Zero `NO_TEST` or `STRUCTURE_ERROR` warnings.
-   [U+2705] **Pytest Run**: Zero `F`/`E` results and all warnings are addressed.
-   [U+2705] **Interface Tests**: Zero failures in contract tests.
-   [U+2705] **Coverage**: Every module meets or exceeds the **90% coverage** standard.
-   [U+2705] **Behavioral Sync**: All test expectations synchronized with current module behavior.

## 4. Production Override Provision

In rare emergencies where the production system is demonstrably functional but test failures are due to infrastructure issues (e.g., CI environment problems) rather than code regressions, this audit may be bypassed.

-   **Criteria**:
    -   Production system is verified as working for core user flows.
    -   Failures are confirmed to be non-functional and infrastructure-related.
    -   The override decision is documented in the `ModLog` (`WSP 11`) with a clear justification and a ticket to fix the underlying test issue.
-   **Usage**: This provision should be used with extreme caution, especially for changes affecting high-LLME modules.
