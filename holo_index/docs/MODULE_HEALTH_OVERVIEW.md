# Module Health Overview

**Status:** [OK] Implemented (2025-09-23)
**Protocols:** WSP 50, WSP 49, WSP 84, WSP 87

## Purpose
- Provide HoloIndex with deterministic checks for module health (size, structure, refactor debt). [OK]
- Surface guidance to 0102 agents before they extend oversized or non-compliant modules. [OK]
- Feed compliance signals into the Qwen advisor rules engine and CLI reminders. [OK]

## Implemented Features

### 1. Size Audit Module (`module_health/size_audit.py`)
- Tracks file line counts and flags modules exceeding WSP 87 guidelines [OK]
- Thresholds: 800 lines (OK), 800-1000 (WARN), >1000 (CRITICAL)
- Hard limit reminder at 1500 lines
- Audits individual files and entire modules
- Returns `FileSizeResult` with risk tier and guidance

### 2. Structure Audit Module (`module_health/structure_audit.py`)
- Detects missing scaffolding per WSP 49 [OK]
- Required artifacts: README.md, INTERFACE.md, ModLog.md, src/, tests/, TestModLog.md
- Generates actionable TODOs for missing files
- Finds module root from any file path
- Returns `StructureResult` with compliance status

### 3. Rules Engine Integration
- Health checks integrated into `qwen_advisor/rules_engine.py` [OK]
- `check_module_size_health()` - Runs size audits on search hits
- `check_module_structure_health()` - Validates module structure
- `_resolve_file_path()` - Maps various path formats to filesystem
- Violations and reminders added to advisor output

### 4. CLI Integration
- Health notices displayed in search results [OK]
- `[HEALTH]` section shows module issues
- Integrated with advisor guidance and TODOs

### 5. Test Coverage
- 14 comprehensive FMAS tests in `tests/test_module_health.py` [OK]
- All tests passing (100% success rate)
- Covers size thresholds, structure validation, and integration

## Example Output
```bash
$ python holo_index.py --search "large module"

[HEALTH] Module Health Notices:
  - [RULER] WSP 87: handler.py - File exceeds guideline (1200 lines, limit 1000)
  - [U+1F4C1] WSP 49: module - Module missing 2 required artifacts: README.md, tests/

[ADVISOR] Qwen Guidance:
  TODOs:
    - Consider refactoring handler.py (1200 lines)
    - Create module/README.md with module overview
    - Create module/tests/ directory for test files
```

## Longer-Term Vision
- Correlate module health with violation history once `WSP_VIOLATIONS` telemetry exists
- Incorporate churn/ownership data to prioritise refactors
- Auto-suggest WSP 88 remediation playbooks when repeated issues surface
- Track health trends over time
- Predictive maintenance recommendations

## Related Assets
- `holo_index/module_health/` - Implementation package [OK]
- `holo_index/qwen_advisor/rules_engine.py` - Integration point [OK]
- `holo_index/tests/test_module_health.py` - FMAS tests [OK]
- `WSP_framework/src/WSP_87_Code_Navigation_Protocol.md` - Size thresholds
- `WSP_framework/src/WSP_49_Module_Directory_Structure.md` - Structure requirements
