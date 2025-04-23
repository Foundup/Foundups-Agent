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

#### [💡] Task: WSP 5 Enhancement: Improve test coverage for stream_resolver module to >= 90%
**Priority**: P1 (High)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Increase test coverage for the `stream_resolver` module from the current 79% to meet the WSP 5 required 90% threshold. This is a critical module identified in the fmas_discrepancy_summary.md as requiring immediate action.

**Requirements**:
- Analyze current coverage gaps in the `stream_resolver` module
- Add additional test cases targeting uncovered code paths
- Ensure all key methods and edge cases are appropriately tested
- Verify final coverage exceeds 90% using pytest-cov
- Document any complex test scenarios for future reference

**Related Context**: 
- Current coverage is at 79%, which is 11% below the required 90% threshold
- Stream resolver is a critical component for video stream initialization
- Part of CLEAN4 validation identified in fmas_discrepancy_summary.md

#### [💡] Task: WSP 5 Enhancement: Improve test coverage for livechat module to >= 90%
**Priority**: P1 (High)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Increase test coverage for the `livechat` module from the current 35% to meet the WSP 5 required 90% threshold. This module was identified in the fmas_discrepancy_summary.md as requiring immediate action due to its significant coverage gap.

**Requirements**:
- Analyze current coverage gaps in the `livechat` module
- Add comprehensive test suite targeting all major functionality
- Focus on testing async methods and error handling paths
- Verify final coverage exceeds 90% using pytest-cov
- Document any complex test scenarios for future maintenance

**Related Context**: 
- Current coverage is at 35%, which is 55% below the required 90% threshold
- Livechat is a core user interaction component
- May be affected by the async code coverage reporting issue
- Part of CLEAN4 validation identified in fmas_discrepancy_summary.md

#### [💡] Task: WSP 3 Enhancement: Implement and verify FMAS Mode 2 (baseline comparison) functionality
**Priority**: P1 (High)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Implement the missing FMAS Mode 2 functionality to enable proper baseline comparison between different Clean States. This functionality is critical for WSP 2/3 compliance and was identified as a secondary blocker in the fmas_discrepancy_summary.md.

**Requirements**:
- Extend the `modular_audit.py` tool to fully support the `--baseline` flag
- Implement baseline directory traversal and comparison logic
- Add detection and reporting of MISSING, MODIFIED, EXTRA, and FOUND_IN_FLAT file statuses
- Create tests to validate the comparison functionality
- Update documentation to reflect the implementation
- Verify compatibility with existing clean state snapshots

**Related Context**: 
- Critical for proper WSP 2/3 compliance verification
- Currently being worked around using manual WSP 7 procedures
- Documented in foundups_global_rules.md as a known gap
- Part of CLEAN4 validation identified in fmas_discrepancy_summary.md 