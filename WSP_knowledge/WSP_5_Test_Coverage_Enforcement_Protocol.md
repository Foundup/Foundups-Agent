# WSP 5: Test Coverage Enforcement Protocol

**Version**: 1.1.0
**Date**: 2025-06-18
**Status**: ACTIVE
**Source**: `docs/archive/FoundUps_WSP_Framework.md`

## 1. Overview

This protocol ensures that all modules meet a minimum standard of test coverage to guarantee reliability and maintainability. It defines the specific coverage target and the methods for its enforcement.

## 2. Coverage Target

-   **Global Target**: A mandatory **90%** test coverage target is enforced across all modules.
-   **Rationale**: This high standard ensures that not only the "happy path" is tested, but also edge cases, error handling, and alternative branches, which is critical for agentic systems.
-   **Override**: While possible via a project-specific `.foundups_project_rules` file (see **WSP 9**), any reduction below 90% is considered a major exception and must be explicitly justified and approved.

## 3. Enforcement and Measurement

-   **Agent**: The `TestingAgent` is responsible for coverage analysis.
-   **Tool**: The `pytest-cov` plugin is the standard tool for measuring coverage.
-   **Command**: The audit is performed using a command similar to:
    ```bash
    pytest --cov=modules.<domain>.<module>.src --cov-report=term-missing
    ```
-   **Process**: This check is an integral part of the **Comprehensive Test Audit (WSP 6)**. During the audit, if all tests pass, the coverage is calculated. If it is below the 90% target, the audit fails, and the module is considered non-compliant.

## 4. Strategy for Improving Coverage

1.  **Gap Analysis**: Developers should first run the coverage report locally and focus on the "Missing" lines, which indicate untested code paths.
2.  **Prioritization**: Efforts should be focused on covering critical logic, complex conditional branches, and error handling routines first.
3.  **Validation**: After adding new tests, the coverage command should be re-run to confirm the target has been met or exceeded. 