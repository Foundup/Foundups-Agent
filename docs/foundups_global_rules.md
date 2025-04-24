# FoundUps APS Project Insights

This document tracks critical insights, architectural decisions, and known gaps discovered during the Active Project System (APS) process.

## Known Gaps & Issues

### FMAS Mode 2 Implementation Missing

**Date Identified:** [Current Date]  
**Status:** Pending Implementation  
**Impact:** High - Blocks proper WSP 2/3 compliance  
**Discovery Context:** During attempt to validate refactored modules against baseline for Clean4.1  

**Description:**  
A critical discrepancy exists between the documentation and implementation of the FoundUps Modular Audit System (FMAS):
- WSP 3 documents FMAS Mode 2 (baseline comparison) as a core feature
- The current implementation in `tools/modular_audit/modular_audit.py` only supports Mode 1 functionality
- This prevents proper baseline comparison and regression detection required by WSP 3 and WSP 2

**Mitigation Strategy:**  
Temporarily using WSP 7 (Snapshot Regression Comparison) manual procedures with `git diff` and `diff -r` until proper FMAS Mode 2 is implemented.

**Action Required:**  
Implement FMAS Mode 2 functionality as specified in WSP 3.

## WSP Compliance Rules

### Test Directory Structure

**Date Implemented:** [Current Date]  
**Status:** Enforced  
**WSP Reference:** WSP Architecture Standards  

**Description:**  
The following rules apply to test directory structure and test file placement:

- **Module Tests Location:** All module-specific tests MUST reside within their respective module directory at `modules/<module_name>/tests/`.
- **Legacy Tests Directory:** The top-level `tests/` directory has been renamed to `tests_archived/` and is NOT for active module tests. This directory contains only historical artifacts and should not be used for new tests.
- **Test File Naming:** Test files should follow the naming convention `test_<component_name>.py`.

**Rationale:**  
This structure ensures tests are co-located with the modules they test, improving discoverability, maintainability, and adherence to the WSP framework's modular architecture principles.

**Action Required:**  
Ensure all new tests are placed in the appropriate module test directory. Do not add new tests to the `tests_archived/` directory. 