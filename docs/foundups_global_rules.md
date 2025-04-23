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