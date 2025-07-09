# WSP Shared Tools Testing Suite

## Overview
This directory contains test scripts for shared utility functions that are used across multiple modules in the WSP framework. These tests ensure proper functionality of cross-cutting concerns and shared infrastructure.

## WSP Compliance
- **WSP 1**: Proper placement in tools/shared/tests/ directory for shared functionality testing
- **WSP 5**: Test coverage validation for shared utilities  
- **WSP 13**: Test management procedures for shared components
- **WSP 22**: Traceable narrative documentation

## Test Files

### `test_pagination.py`
- **Purpose:** Tests pagination system functionality with module scoring and prioritization
- **Scope:** Tests pagination logic for module lists using WSP37ScoringEngine
- **How it works:**
  - Initializes WSP37ScoringEngine for module scoring and sorting
  - Tests pagination calculation and display logic
  - Validates priority module filtering (P0, P1, etc.)
  - Tests placeholder module handling
- **Usage:**
  ```bash
  # From project root
  python tools/shared/tests/test_pagination.py
  ```
- **Expected Output:**
  - Module pagination results with priority scoring
  - P0 (critical) module identification
  - Page navigation structure validation

## Related Components
These tests validate shared functionality used by:
- **WRE Core**: Module prioritization and menu pagination
- **Scoring Engine**: WSP37 module priority calculation
- **System Management**: Module listing and organization

## Running Shared Tests

```bash
# Run all shared utility tests
python -m pytest tools/shared/tests/ -v

# Run specific test
python tools/shared/tests/test_pagination.py

# Run with coverage for shared utilities
python -m pytest tools/shared/tests/ --cov=tools/shared --cov-report=html
```

## Test Development Guidelines

When adding tests for shared utilities:

1. **Scope Validation**: Ensure the test truly covers shared functionality used across modules
2. **WSP Compliance**: Follow WSP 1, 5, 13, 22 protocols for test organization
3. **Cross-Module Impact**: Test how changes affect multiple consuming modules
4. **Documentation**: Update this README when adding new test files
5. **ModLog Updates**: Document changes in tools/shared/ ModLog following WSP 22

## Directory Structure

```
tools/shared/tests/
├── README.md              ← This file
├── test_pagination.py     ← Pagination system testing
└── [future_test_files]    ← Additional shared utility tests
```

## Integration Points

- **Module Scoring Engine**: WSP37ScoringEngine functionality validation
- **MPS Calculator**: Module Priority Score computation testing  
- **WSP Compliance Engine**: Shared compliance checking utilities
- **ModLog Integration**: Shared documentation utilities

---

*This testing suite ensures shared utilities maintain quality and compatibility across the autonomous WSP development ecosystem.*  
*WSP Compliance: WSP 1 (Structure), WSP 5 (Coverage), WSP 13 (Test Management), WSP 22 (Documentation)* 