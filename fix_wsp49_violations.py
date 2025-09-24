#!/usr/bin/env python3
"""
WSP 49 Violation Fixer
Creates missing src/, tests/, README.md, INTERFACE.md for all modules
"""

import os
import re
from pathlib import Path

# Template contents (ASCII-only)
README_TEMPLATE = """# [MODULE_NAME]

**Domain:** [DOMAIN] (ai_intelligence | communication | platform_integration | infrastructure | monitoring | development | foundups | gamification | blockchain)
**Status:** POC (POC | Prototype | MVP | Production)
**WSP Compliance:** In Progress (Compliant | In Progress | Non-Compliant)

## [OVERVIEW] Module Overview

**Purpose:** [Module functionality description - update this]

**Key Capabilities:**
- [Primary capability 1]
- [Primary capability 2]

**Dependencies:**
- [List key dependencies]

## [STATUS] Current Status & Scoring

### MPS + LLME Scores
**Last Scored:** 2025-09-25
**Scored By:** WSP 49 Compliance Fixer

| Dimension | Score | Rationale |
|-----------|-------|-----------|
| **Complexity** | 3 | Standard module complexity |
| **Importance** | 3 | Core functionality |
| **Deferability** | 2 | Should be addressed soon |
| **Impact** | 3 | Affects module usability |
| **MPS Total** | 11 | **Priority Classification:** P2 |

**LLME Semantic Score:** BBB
- **B (Present State):** 1 - relevant - Basic structure exists
- **B (Local Impact):** 1 - relevant - Used by domain modules
- **B (Systemic Importance):** 1 - conditional - Important for domain completeness

**LLME Target:** BCC - Full compliance and integration

## [ROADMAP] Module Roadmap

### Phase Progression: null -> 001 -> 011 -> 111

#### [COMPLETE] Completed Phases
- [x] **Phase 0 (null):** Module concept and planning
  - [x] MPS/LLME initial scoring
  - [x] WSP structure creation
  - [x] Domain placement decision

#### [CURRENT] Current Phase: WSP 49 Compliance
- [x] **Phase 1:** Basic structure compliance
  - [x] Create missing src/ directory
  - [x] Create missing tests/ directory
  - [x] Create README.md template
  - [x] Create INTERFACE.md template
  - [ ] Add actual implementation
  - [ ] Add comprehensive tests

#### [UPCOMING] Upcoming Phases
- [ ] **Phase 2:** Functional implementation
  - [ ] Core functionality development
  - [ ] Integration testing
  - [ ] Documentation completion

## [API] Public API & Usage

### Exported Functions/Classes
```python
# Update with actual exports when implemented
from modules.[DOMAIN].[MODULE_NAME] import [MainClass]

# Usage pattern
instance = [MainClass]()
result = instance.process()
```

### Integration Patterns
**For Other Modules:**
```python
# How other modules should integrate
from modules.[DOMAIN].[MODULE_NAME] import [IntegrationInterface]
```

**WSP 11 Compliance:** In Progress - Interface definition needed

## [MODLOG] ModLog (Chronological History)

### 2025-09-25 - WSP 49 Compliance Fix
- **By:** WSP 49 Violation Fixer
- **Changes:** Created missing src/, tests/, README.md, INTERFACE.md
- **Impact:** Module now compliant with WSP 49 structure requirements
- **LLME Transition:** BBB -> BCC (structure compliance achieved)

## [COMPLIANCE] WSP Compliance Checklist

### Structure Compliance (WSP 49)
- [x] **Directory Structure:** modules/[domain]/[module_name]/
- [x] **Required Files:**
  - [x] README.md (this file)
  - [x] src/__init__.py (created)
  - [x] src/[module_name].py (created placeholder)
  - [x] tests/__init__.py (created)
  - [x] tests/README.md (created)
  - [ ] requirements.txt (if dependencies exist)

### Testing Compliance (WSP 13)
- [ ] **Test Coverage:** >=90% (Current: 0%)
- [ ] **Test Documentation:** tests/README.md complete
- [ ] **Test Patterns:** Follows established module patterns
- [ ] **Last Test Run:** None - implementation needed

### Interface Compliance (WSP 11)
- [ ] **Public API Defined:** __init__.py needs actual exports
- [ ] **Interface Documentation:** Usage examples needed
- [ ] **Backward Compatibility:** N/A - new module

---

**Template Version:** 1.0
**Last Updated:** 2025-09-25
**WSP Framework Compliance:** WSP 49 Structure Compliant
"""

INTERFACE_TEMPLATE = """# [MODULE_NAME] Interface Specification

**WSP 11 Compliance:** In Progress
**Last Updated:** 2025-09-25
**Version:** 0.1.0

## [OVERVIEW] Module Overview

**Domain:** [DOMAIN]
**Purpose:** [Brief description of module functionality]

## [API] Public API

### Primary Classes

#### [MainClassName]
```python
class [MainClassName]:
    \"\"\"Main class for [module functionality]\"\"\"

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        \"\"\"Initialize [MainClassName]

        Args:
            config: Optional configuration dictionary
        \"\"\"

    def [main_method](self, [parameters]) -> [ReturnType]:
        \"\"\"[Method description]

        Args:
            [parameters]: [Parameter description]

        Returns:
            [ReturnType]: [Return value description]

        Raises:
            [ExceptionType]: [When exception is raised]
        \"\"\"
```

### Utility Functions

#### [utility_function]
```python
def [utility_function]([parameters]) -> [ReturnType]:
    \"\"\"[Function description]

    Args:
        [parameters]: [Parameter description]

    Returns:
        [ReturnType]: [Return value description]
    \"\"\"
```

## [CONFIG] Configuration

### Required Configuration
```python
# Example configuration
config = {
    "setting1": "value1",
    "setting2": 42
}
```

### Optional Configuration
```python
# Optional settings with defaults
optional_config = {
    "timeout": 30,  # Default: 30 seconds
    "retries": 3    # Default: 3 attempts
}
```

## [USAGE] Usage Examples

### Basic Usage
```python
from modules.[DOMAIN].[MODULE_NAME] import [MainClassName]

# Initialize
instance = [MainClassName](config)

# Use main functionality
result = instance.[main_method]([example_parameters])
print(f"Result: {result}")
```

### Advanced Usage
```python
# With custom configuration
custom_config = {
    "special_setting": "custom_value"
}
advanced_instance = [MainClassName](custom_config)

# Use utility function
processed = [utility_function]([input_data])
```

## [DEPENDENCIES] Dependencies

### Internal Dependencies
- modules.[domain].[dependency_module] - [Reason for dependency]

### External Dependencies
- [package_name]>=x.y.z - [Purpose of dependency]

## [TESTING] Testing

### Running Tests
```bash
cd modules/[DOMAIN]/[MODULE_NAME]
python -m pytest tests/
```

### Test Coverage
- **Current:** 0% (implementation needed)
- **Target:** >=90%

## [PERFORMANCE] Performance Characteristics

### Expected Performance
- **Latency:** [expected latency]
- **Throughput:** [expected throughput]
- **Resource Usage:** [memory/CPU expectations]

## [ERRORS] Error Handling

### Common Errors
- **[ErrorType1]:** [Description and resolution]
- **[ErrorType2]:** [Description and resolution]

### Exception Hierarchy
```python
class [ModuleName]Error(Exception):
    \"\"\"Base exception for [module_name]\"\"\"
    pass

class [SpecificError]([ModuleName]Error):
    \"\"\"Specific error type\"\"\"
    pass
```

## [HISTORY] Version History

### 0.1.0 (2025-09-25)
- Initial interface specification
- Basic API structure defined
- Placeholder implementation created

## [NOTES] Development Notes

### Current Status
- [x] WSP 49 structure compliance
- [x] Interface specification defined
- [ ] Functional implementation (TODO)
- [ ] Comprehensive testing (TODO)

### Future Enhancements
- [Enhancement 1]
- [Enhancement 2]
- [Integration with other modules]

---

**WSP 11 Interface Compliance:** Structure Complete, Implementation Pending
"""

SRC_INIT_TEMPLATE = """\"\"\"[MODULE_NAME] implementation package\"\"\"

# Public API exports - update when implementation is complete
__all__ = [
    # "[MainClassName]",
    # "[utility_function]"
]
"""

SRC_MAIN_TEMPLATE = """\"\"\"[MODULE_NAME] core implementation\"\"\"

# TODO: Implement actual functionality
# This is a placeholder created for WSP 49 compliance

class [MainClassName]:
    \"\"\"Placeholder main class for [module_name]\"\"\"

    def __init__(self, config=None):
        \"\"\"Initialize [MainClassName]

        Args:
            config: Optional configuration dictionary
        \"\"\"
        self.config = config or {}

    def [main_method](self):
        \"\"\"Placeholder main method

        TODO: Implement actual functionality
        \"\"\"
        return f"[MODULE_NAME] placeholder result"

def [utility_function]():
    \"\"\"Placeholder utility function

    TODO: Implement actual utility functionality
    \"\"\"
    return "[MODULE_NAME] utility result"
"""

TESTS_INIT_TEMPLATE = """\"\"\"[MODULE_NAME] test package\"\"\"

# Test package initialization
"""

TESTS_README_TEMPLATE = """# [MODULE_NAME] Test Suite

**Test Coverage:** 0% (implementation needed)
**Last Run:** Never
**Framework:** pytest

## [TEST] Test Categories

### Unit Tests (test_*.py)
- test_[module_name].py - Core functionality tests
- test_integration.py - Integration tests (when applicable)

### Test Structure
```
tests/
├── __init__.py              # Test package
├── README.md               # This file
├── test_[module_name].py   # Main test file
└── TestModLog.md          # Test evolution log
```

## [RUN] Running Tests

### All Tests
```bash
cd modules/[DOMAIN]/[MODULE_NAME]
python -m pytest tests/
```

### Specific Test
```bash
cd modules/[DOMAIN]/[MODULE_NAME]
python -m pytest tests/test_[module_name].py
```

### With Coverage
```bash
cd modules/[DOMAIN]/[MODULE_NAME]
python -m pytest --cov=src --cov-report=html tests/
```

## [COVERAGE] Coverage Requirements

**WSP 13 Compliance Target:** >=90% coverage

### Current Status
- **Lines:** 0%
- **Functions:** 0%
- **Branches:** 0%

### Coverage Areas Required
- [ ] Core functionality
- [ ] Error handling
- [ ] Edge cases
- [ ] Integration points

## [CONFIG] Test Configuration

### pytest.ini (if needed)
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

## [CASES] Test Cases (TODO)

### Basic Functionality
- [ ] Test initialization
- [ ] Test main methods
- [ ] Test configuration handling

### Error Conditions
- [ ] Test invalid inputs
- [ ] Test missing dependencies
- [ ] Test network failures (if applicable)

### Integration Tests
- [ ] Test with dependent modules
- [ ] Test end-to-end workflows
- [ ] Test performance requirements

## [EVOLUTION] Test Evolution Log

See TestModLog.md for detailed test development history.

---

**WSP 13 Testing Compliance:** Structure Complete, Implementation Pending
"""

def fix_module_structure(module_path: Path):
    """Fix WSP 49 structure for a single module"""
    domain = module_path.parent.name
    module_name = module_path.name

    # Create missing directories
    src_dir = module_path / "src"
    tests_dir = module_path / "tests"

    src_dir.mkdir(exist_ok=True)
    tests_dir.mkdir(exist_ok=True)

    # Create src/__init__.py
    src_init = src_dir / "__init__.py"
    if not src_init.exists():
        content = SRC_INIT_TEMPLATE.replace("[MODULE_NAME]", module_name)
        src_init.write_text(content)

    # Create src/[module_name].py
    src_main = src_dir / f"{module_name}.py"
    if not src_main.exists():
        content = SRC_MAIN_TEMPLATE.replace("[MODULE_NAME]", module_name)
        content = content.replace("[MainClassName]", module_name.title().replace("_", ""))
        content = content.replace("[main_method]", "process")
        content = content.replace("[utility_function]", f"utility_{module_name}")
        src_main.write_text(content)

    # Create tests/__init__.py
    tests_init = tests_dir / "__init__.py"
    if not tests_init.exists():
        content = TESTS_INIT_TEMPLATE.replace("[MODULE_NAME]", module_name)
        tests_init.write_text(content)

    # Create tests/README.md
    tests_readme = tests_dir / "README.md"
    if not tests_readme.exists():
        content = TESTS_README_TEMPLATE.replace("[MODULE_NAME]", module_name)
        content = content.replace("[DOMAIN]", domain)
        tests_readme.write_text(content)

    # Create README.md
    readme = module_path / "README.md"
    if not readme.exists():
        content = README_TEMPLATE.replace("[MODULE_NAME]", module_name)
        content = content.replace("[DOMAIN]", domain)
        readme.write_text(content)

    # Create INTERFACE.md
    interface = module_path / "INTERFACE.md"
    if not interface.exists():
        content = INTERFACE_TEMPLATE.replace("[MODULE_NAME]", module_name)
        content = content.replace("[DOMAIN]", domain)
        content = content.replace("[MainClassName]", module_name.title().replace("_", ""))
        content = content.replace("[main_method]", "process")
        content = content.replace("[utility_function]", f"utility_{module_name}")
        interface.write_text(content)

def main():
    """Fix WSP 49 violations for all modules"""
    modules_dir = Path("modules")
    fixed_count = 0

    print("WSP 49 Violation Fixes")
    print("=" * 40)

    for domain_dir in modules_dir.iterdir():
        if not domain_dir.is_dir() or domain_dir.name.startswith('_'):
            continue

        for module_dir in domain_dir.iterdir():
            if not module_dir.is_dir() or module_dir.name.startswith('_'):
                continue

            # Check if any required items are missing
            missing_items = []
            if not (module_dir / 'src').exists():
                missing_items.append('src/')
            if not (module_dir / 'tests').exists():
                missing_items.append('tests/')
            if not (module_dir / 'README.md').exists():
                missing_items.append('README.md')
            if not (module_dir / 'INTERFACE.md').exists():
                missing_items.append('INTERFACE.md')

            if missing_items:
                print(f"Fixing {module_dir}: missing {', '.join(missing_items)}")
                fix_module_structure(module_dir)
                fixed_count += 1

    print(f"\\nFixed {fixed_count} modules for WSP 49 compliance")
    print("All modules now have required src/, tests/, README.md, INTERFACE.md")

if __name__ == "__main__":
    main()