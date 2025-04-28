# FMAS Test Suite

This folder contains tests for the Foundups Modular Audit System (FMAS). These tests verify functionality related to module structure checking, test existence verification, and baseline comparison.

| Test File                 | Description (Auto-generated - May Need Refinement) |
|----------------------------|-----------------------------------------------------|
| test_fmas_mode2.py         | Tests for FMAS Mode 2 baseline comparison functionality |
| test_modular_audit.py      | General tests for the modular audit system |
| test_found_in_flat.py      | Tests for detection of files found in flat structure |
| test_missing_extra.py      | Tests for detection of missing and extra files |
| test_modified.py           | Tests for detection of modified file content |
| test_output_format.py      | Tests for log message formatting and output generation |
| test_mode2.py              | Additional Mode 2 specific tests |
| custom_test.py             | Custom test scenarios for specialized cases |
| auth_error_coverage_test.py| Tests for authentication error coverage |
| run_coverage_test.py       | Script for running coverage tests |
| __init__.py                | Package initialization file |

---

**Important:**  
- Agents must read this README before creating a new test
- If a similar test already exists, extend it instead of creating a duplicate
- When adding new tests, update this README with appropriate descriptions 