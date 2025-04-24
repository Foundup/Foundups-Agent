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
**Status**: ✅ Complete  
**Assignee**: @0102 / @DevTeam  
**Description**: Increase test coverage for the `stream_resolver` module from the current 79% to meet the WSP 5 required 90% threshold. This is a critical module identified in the fmas_discrepancy_summary.md as requiring immediate action.

**Requirements**:
- Analyze current coverage gaps in the `stream_resolver` module
- Add additional test cases targeting uncovered code paths
- Ensure all key methods and edge cases are appropriately tested
- Verify final coverage exceeds 90% using pytest-cov
- Document any complex test scenarios for future reference

**Related Context**: 
- Current coverage is now at 93%, which exceeds the required 90% threshold
- The remaining uncovered lines are primarily in:
  - File integrity guard logic (lines 16-19)
  - Specific quota error handling edge cases (lines 177-179, 195-196) 
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

#### [⚒️] Task: Fix Tests for FMAS Mode 2 (Baseline Comparison)
**Priority**: P1 (High)  
**Status**: 🔄 In Progress  
**Assignee**: @0102 / @DevTeam  
**Description**: Fix the test suite for the existing FMAS Mode 2 implementation in `tools/modular_audit/modular_audit.py`. Validation has confirmed that the `--baseline` flag and file comparison functionality is implemented, but 14 out of 25 tests are failing. These test failures must be addressed before considering the Mode 2 implementation complete.

**Requirements**:
- Fix test failures in `tools/modular_audit/tests/test_modular_audit.py` and `tools/modular_audit/tests/test_fmas_mode2.py`
- Align tests with the existing implementation (do not modify the implementation)
- Ensure all tests pass before moving on to further WSP 3 requirements
- Document any discrepancies found between test expectations and actual implementation

**Related Context**: 
- Manual validation confirms the baseline comparison functionality works as expected
- Test failures include TypeErrors, ValueErrors, and AssertionErrors
- See WSP 3 validation report for detailed findings
- Related to findings in foundups_global_rules.md 

#### [⚒️] Task: WSP 3 Enhancement: Implement and verify FMAS Mode 2 (baseline comparison) functionality
**Priority**: P1 (High)  
**Status**: 🔄 In Progress  
**Assignee**: @0102 / @DevTeam  
**Description**: Verify and extend the existing FMAS Mode 2 functionality to enable proper baseline comparison between different Clean States. Manual validation has confirmed that basic Mode 2 functionality is implemented, but the test suite is failing. This functionality is critical for WSP 2/3 compliance and was identified as a secondary blocker in the fmas_discrepancy_summary.md.

**Requirements**:
- The `modular_audit.py` tool supports the `--baseline` flag
- Verify baseline directory traversal and comparison logic
- Enhance detection and reporting of MISSING, MODIFIED, EXTRA, and FOUND_IN_FLAT file statuses
  - **CRITICAL GAP**: The MODIFIED file detection functionality is completely missing. Validation (Part 4) confirmed the code contains a TODO comment: "For modified files, we'd need to compare file contents"
  - Must implement file content comparison (e.g., hash comparison) to detect files that exist in both locations but have different content
  - Must implement WSP 3.5 compliant logging: "[module] MODIFIED: Content differs from baseline. (File path: ...)"
  - **CRITICAL GAP**: The FOUND_IN_FLAT file detection functionality is completely missing. Validation (Part 5) confirmed the code does not scan for files directly in the baseline's modules/ directory.
  - Must implement logic to detect when a file in the target's structured module was previously in the flat modules directory structure
  - Must implement WSP 3.5 compliant logging: "[module] FOUND_IN_FLAT: Found only in baseline flat modules/, needs proper placement. (File path: ...)"
- Fix tests to validate the comparison functionality
- Update documentation to reflect the implementation
- Verify compatibility with existing clean state snapshots

**Related Context**: 
- Critical for proper WSP 2/3 compliance verification
- Manual validation confirms basic functionality exists but tests are failing (14/25 failures)
- Currently being worked around using manual WSP 7 procedures
- Documented in foundups_global_rules.md as a known gap
- Part of CLEAN4 validation identified in fmas_discrepancy_summary.md

#### [💡] Task: WSP Framework Enhancement: Integrate Cursor AI Interaction Pattern
**Priority**: P2 (Medium)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Formally integrate the Cursor AI interaction patterns and guidelines into the WSP Framework to standardize AI-assisted development workflows. This will improve consistency and efficiency in AI-assisted development tasks.

**Requirements**:
- Document standard AI prompting patterns for development tasks
- Define interaction expectations between developers and AI assistants
- Create guidelines for reviewing AI-generated code
- Establish quality gates for AI-assisted contributions
- Update relevant WSP documents to reference these guidelines
- Create templates for common AI-assisted development scenarios

**Related Context**: 
- Supports consistent utilization of AI development tools
- Addresses observed variations in interaction patterns
- Improves onboarding efficiency for new team members
- Aligns with WSP 5 (Test Coverage) and WSP 8 (Development Milestone) requirements 