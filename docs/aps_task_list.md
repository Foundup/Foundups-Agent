# APS Task List

This document tracks prioritized development tasks for the FoundUps Agent. Tasks are categorized by priority and status.

## Priority Legend
- **P0**: Critical - Blocking project progress
- **P1**: High - Important for next milestone
- **P2**: Medium - Should be addressed soon
- **P3**: Low - Nice to have, can be deferred

## Task Status
- **🔄 In Progress** - Work has started
- **⏸️ Blocked** - Dependent on another task
- **📝 Planned** - Defined but not started
- **✅ Complete** - Finished and verified

## Active Tasks

### System Tools & Infrastructure

#### [💡] Task: Implement FMAS Mode 2 (Baseline Comparison)
**Priority**: P1 (High)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Extend `tools/modular_audit/modular_audit.py` to support the `--baseline` flag and perform file comparison (MISSING, MODIFIED, EXTRA, FOUND_IN_FLAT) as specified in WSP 3. Blocked WSP 2/3 compliance until complete.

**Requirements**:
- Add `--baseline` command-line parameter
- Implement file system traversal of baseline directory
- Add content comparison logic between current and baseline files
- Detect and report MISSING, MODIFIED, EXTRA, and FOUND_IN_FLAT conditions
- Update test suite to validate new functionality
- Update documentation to match implementation

**Related Context**: 
- See WSP 3 for detailed requirements
- Related to findings in foundups_global_rules.md 

#### [💡] Task: Diagnose and Fix Coverage Reporting for livechat.py
**Priority**: P1 (High - Blocking WSP 5 Validation)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Investigate why pytest-cov is not reporting coverage accurately for methods like `_handle_auth_error` in `modules/livechat/src/livechat.py`, despite targeted tests passing. Explore potential causes (async interaction, mocking, tool config) and implement a fix to ensure reliable coverage measurement.

**Requirements**:
- Isolate the root cause of coverage measurement failures
- Verify whether the issue is with async code, mocking approaches, or tool configuration
- Implement a fix or workaround to enable accurate coverage measurement
- Document the solution for future reference
- Validate coverage meets the 90% WSP 5 threshold once accurate measurement is in place

**Related Context**: 
- Current coverage stuck at ~42%; lines 41-58 consistently show as uncovered despite targeted tests
- Issue is blocking WSP 5 compliance validation
- May indicate a systemic issue with coverage reporting for async code 