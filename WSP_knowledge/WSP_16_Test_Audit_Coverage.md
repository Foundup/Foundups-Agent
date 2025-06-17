# WSP 16: Test Audit & Coverage Verification

**Version**: 1.2.0
**Date**: 2025-06-17 (Restored from archive)
**Status**: ACTIVE

## 1. Overview

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
-   **Standard**: **≥90% test coverage** is required for all modules. Higher thresholds (e.g., 95% or 100%) may be mandated for foundational (`C=2`) modules.
-   **Command**: `pytest <module_path>/tests/ --cov=<module_import_path>.src --cov-fail-under=90`
-   **Goal**: Every module must meet or exceed the 90% threshold.

### 3. Acceptance Criteria (Audit PASS)

An audit is considered passed only when all of the following criteria are met:
-   ✅ **FMAS**: Zero `NO_TEST` or `STRUCTURE_ERROR` warnings.
-   ✅ **Pytest Run**: Zero `F`/`E` results and all warnings are addressed.
-   ✅ **Interface Tests**: Zero failures in contract tests.
-   ✅ **Coverage**: Every module meets or exceeds the **90% coverage** standard.

### 4. Production Override Provision

In rare emergencies where the production system is demonstrably functional but test failures are due to infrastructure issues (e.g., CI environment problems) rather than code regressions, this audit may be bypassed.

-   **Criteria**:
    -   Production system is verified as working for core user flows.
    -   Failures are confirmed to be non-functional and infrastructure-related.
    -   The override decision is documented in the `ModLog` (`WSP 11`) with a clear justification and a ticket to fix the underlying test issue.
-   **Usage**: This provision should be used with extreme caution, especially for changes affecting high-LLME modules. 