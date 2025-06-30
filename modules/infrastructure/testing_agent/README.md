# WSP-54: TestingAgent Module

This module contains the `TestingAgent`, responsible for automating the project's testing and code coverage validation.

## Core Mandate

To automate the project's testing and code coverage validation.

## Trigger

Dispatched on-demand by the WRE or as part of a pre-commit hook (future).

## Duties

1.  **Execute `pytest`:** Run the test suite for a specified module or the entire project.
2.  **Calculate Coverage:** Execute `pytest --cov` to get the test coverage percentage.
3.  **Validate Threshold:** Compare coverage against the required threshold (e.g., 90%).

## Output

A test report object containing the pass/fail status and the coverage percentage. 