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

#### [✅] Task: Implement FMAS Mode 2 (Baseline Comparison)
**Priority**: P1 (High)  
**Status**: ✅ Complete  
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
- Implementation complete and verified as WSP 3.5-compliant

#### [✅] Task: WSP 5 Enhancement: Improve test coverage for stream_resolver module to >= 90%
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

#### [🔄] Task: WSP 5 Enhancement: Improve test coverage for livechat module to >= 90%
**Priority**: P1 (High)  
**Status**: 🔄 In Progress  
**Assignee**: @0102 / @DevTeam  
**Description**: Write a new, comprehensive test suite from scratch for the current modules/livechat/src/livechat.py source code to achieve >= 90% coverage (WSP 5). Place tests in the newly created modular files (e.g., test_livechat_initialization.py, etc.). The previous test suite was discarded due to excessive size and errors.

**Requirements**:
- Create new, focused unit tests for all LiveChatListener methods
- Implement tests for all significant code paths in the livechat module
- Focus on testing async methods and error handling paths
- Verify final coverage exceeds 90% using pytest-cov
- Document test coverage strategy in the tests/README.md file

**Related Context**: 
- After comparison of clean3 vs. clean4 versions, decided to keep clean4 source code
- Previous monolithic test file (test_livechat.py) had unresolvable syntax issues
- Current modular test files provide a clean structure for new tests
- All consolidation/writing phases (3a-3k) completed for the new modular test files, with 178 passing tests
- Final reported coverage baseline is 36%, though actual functional coverage is likely higher
- Known issues with pytest-cov accurately reporting coverage for async code in this module
- Next steps involve further test additions targeting remaining logic gaps to reach the 90% goal, potentially alongside investigation of the coverage tool issue
- Livechat is a core user interaction component requiring comprehensive testing
- Part of CLEAN4 validation identified in fmas_discrepancy_summary.md

#### [✅] Task: Delete problematic legacy test files for livechat module
**Priority**: P1 (High)  
**Status**: ✅ Complete  
**Assignee**: @0102 / @DevTeam  
**Description**: Delete the problematic legacy test files (test_livechat.py and related support files) to prepare for a clean slate with new modular tests. This reflects the decision to adopt Option B: keeping the clean4 source code while building a new test suite.

**Requirements**:
- Delete test_livechat.py (large monolithic file with syntax errors)
- Remove temporary helper scripts used in previous fix attempts
- Keep the newly created modular test files (test_livechat_*.py)
- Preserve essential configuration files (__init__.py, README.md)
- Document the files removed in the commit message

**Related Context**: 
- The massive test_livechat.py file had numerous syntax errors and indentation issues
- Previous attempts to fix or break up the file were unsuccessful
- New, clean modular test files have been created as a better foundation
- This approach aligns with WSP compliance and maintainability goals
- Part of the Option B strategy decided after comparing clean3 vs. clean4 code

#### [✅] Task: Fix Tests for FMAS Mode 2 (Baseline Comparison)
**Priority**: P1 (High)  
**Status**: ✅ Complete  
**Assignee**: @0102 / @DevTeam  
**Description**: Fix the test suite for the existing FMAS Mode 2 implementation in `tools/modular_audit/modular_audit.py`. Validation has confirmed that the `--baseline` flag and file comparison functionality is implemented, but 14 out of 25 tests were failing. These test failures have been addressed.

**Requirements**:
- Fix test failures in `tools/modular_audit/tests/test_modular_audit.py` and `tools/modular_audit/tests/test_fmas_mode2.py`
- Align tests with the existing implementation (do not modify the implementation)
- Ensure all tests pass before moving on to further WSP 3 requirements
- Document any discrepancies found between test expectations and actual implementation

**Related Context**: 
- Manual validation confirms the baseline comparison functionality works as expected
- All tests now pass, confirming proper implementation
- See WSP 3 validation report for detailed findings
- Related to findings in foundups_global_rules.md 

#### [✅] Task: WSP 3 Enhancement: Implement and verify FMAS Mode 2 (baseline comparison) functionality
**Priority**: P1 (High)  
**Status**: ✅ Complete  
**Assignee**: @0102 / @DevTeam  
**Description**: Verify and extend the existing FMAS Mode 2 functionality to enable proper baseline comparison between different Clean States. Manual validation has confirmed that Mode 2 functionality is fully implemented and tested.

**Requirements**:
- The `modular_audit.py` tool supports the `--baseline` flag
- Verify baseline directory traversal and comparison logic
- Enhance detection and reporting of MISSING, MODIFIED, EXTRA, and FOUND_IN_FLAT file statuses
  - Verification has confirmed that the core logic for all detection types is present and working
  - All associated test suite failures have been fixed
  - Proper WSP 3.5 compliant logging for all detection types is implemented
- Fix tests to validate the comparison functionality
- Update documentation to reflect the implementation
- Verify compatibility with existing clean state snapshots

**Related Context**: 
- Critical for proper WSP 2/3 compliance verification
- Validation confirms full functionality exists and all tests are passing
- Now being used for WSP 7 procedures instead of manual workarounds
- Updated in foundups_global_rules.md to reflect completion
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

#### [💡] Task: Relocate test_quota_manager.py
**Priority**: P3 (Low)  
**Status**: 📝 Planned  
**Assignee**: @0102 / @DevTeam  
**Description**: Move the test file `test_quota_manager.py` from its current location in `modules/livechat/tests/` to a more appropriate location, likely within a `utils/tests/` or `utils/oauth_manager/tests/` directory structure, as it tests components from `utils/oauth_manager` rather than `modules/livechat`.

**Requirements**:
- Determine the correct target directory for utility tests (create if necessary).
- Move the `test_quota_manager.py` file.
- Update any necessary `__init__.py` files.
- Ensure the tests still run correctly from the new location (adjust imports if needed).
- Remove the file entry from `modules/livechat/tests/README.md`.

**Related Context**: 
- File identified as misplaced during livechat test refactoring.
- Improves test structure modularity and maintainability.
- Tests should be logically co-located with the code they test.
- Current location violates modularity principles and could lead to confusion. 