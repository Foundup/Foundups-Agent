# WSP 62 Refactoring Plan: qwen_orchestrator.py

**Status:** In Progress
**Date:** 2025-12-19
**Violation:** 1851 lines (351 lines over 1500 critical window)
**Target:** < 1200 lines (OK threshold)
**Strategy:** Module Splitting (WSP 62 Section 3.3.2)

## Current Analysis

### File Size Breakdown
- **Total Lines:** 1851
- **Largest Methods:**
  1. `orchestrate_holoindex_request()` - 221 lines
  2. `_run_wsp_documentation_guardian()` - 150 lines
  3. `_get_orchestration_decisions()` - 95 lines
  4. `_format_intent_aware_response()` - 80 lines
  5. `_extract_component_results_from_report()` - 77 lines

### Functional Groups
1. **WSP Documentation Guardian** (~400 lines):
   - `_run_wsp_documentation_guardian()` (150 lines)
   - `_execute_wsp_remediation_pipeline()` (68 lines)
   - `rollback_ascii_changes()` (48 lines)
   - `_build_module_snapshot()` (46 lines)
   - `_sanitize_ascii_content()` (42 lines)

2. **Orchestration Core** (~500 lines):
   - `orchestrate_holoindex_request()` (221 lines)
   - `_extract_component_results_from_report()` (77 lines)
   - `_get_output_filter_for_intent()` (60 lines)
   - `_format_intent_aware_response()` (80 lines)
   - `_build_orchestration_context()` (42 lines)

3. **CodeIndex Integration** (~100 lines):
   - `_should_trigger_codeindex()` (52 lines)
   - `_generate_codeindex_section()` (53 lines)

## Refactoring Strategy

### Phase 1: Extract WSP Documentation Guardian
**File:** `src/wsp_documentation_guardian.py` (~400 lines)

**Extractions:**
- `_run_wsp_documentation_guardian(query)` - Main guardian logic
- `_execute_wsp_remediation_pipeline(stale_docs)` - Fix stale docs
- `rollback_ascii_changes(module_path, snapshot)` - Rollback changes
- `_build_module_snapshot(module_path)` - Snapshot before changes
- `_sanitize_ascii_content(file_path)` - Fix encoding issues

**Dependencies:**
- `self.repo_root` (Path)
- `WSP_DOC_CONFIG` (dict)
- Logger

**New Class:** `WSPDocumentationGuardian`
```python
class WSPDocumentationGuardian:
    def __init__(self, repo_root: Path, logger):
        self.repo_root = repo_root
        self.logger = logger
        self.config = WSP_DOC_CONFIG

    def run_guardian(self, query: str) -> Dict[str, Any]:
        """Main WSP documentation guardian analysis."""
        ...

    def execute_remediation_pipeline(self, stale_docs: List[Dict]) -> Dict[str, Any]:
        """Execute automated remediation for stale documentation."""
        ...

    def rollback_ascii_changes(self, module_path: Path, snapshot: Dict) -> bool:
        """Rollback ASCII sanitization changes if tests fail."""
        ...

    def build_module_snapshot(self, module_path: Path) -> Dict[str, str]:
        """Build snapshot of module files before changes."""
        ...

    def sanitize_ascii_content(self, file_path: Path) -> bool:
        """Remove offensive ASCII art and replace with Unicode."""
        ...
```

**Integration in Orchestrator:**
```python
from .src.wsp_documentation_guardian import WSPDocumentationGuardian

# In __init__:
self.wsp_guardian = WSPDocumentationGuardian(self.repo_root, logger)

# Replace method calls:
# OLD: result = self._run_wsp_documentation_guardian(query)
# NEW: result = self.wsp_guardian.run_guardian(query)
```

**Lines Saved:** ~400
**New Orchestrator Size:** 1851 - 400 = ~1451 lines

### Phase 2: Extract Orchestration Core
**File:** `src/orchestration_engine.py` (~300 lines)

**Extractions:**
- `orchestrate_holoindex_request(query, verbose)` - Main orchestration (221 lines)
- `_extract_component_results_from_report(report)` - Parse component results (77 lines)

**Dependencies:**
- `self.repo_root`
- `self.intent_classifier`
- `self.breadcrumb_tracer`
- `self.output_composer`
- Component engines (health_monitor, architect_mode)

**New Class:** `OrchestrationEngine`
```python
class OrchestrationEngine:
    def __init__(self, repo_root: Path, intent_classifier, breadcrumb_tracer,
                 output_composer, health_monitor, architect_mode, logger):
        self.repo_root = repo_root
        self.intent_classifier = intent_classifier
        self.breadcrumb_tracer = breadcrumb_tracer
        self.output_composer = output_composer
        self.health_monitor = health_monitor
        self.architect_mode = architect_mode
        self.logger = logger

    def orchestrate_request(self, query: str, verbose: bool = False) -> Dict[str, Any]:
        """Main orchestration logic for HoloIndex requests."""
        ...

    def extract_component_results(self, report: Dict) -> List[Dict]:
        """Extract structured results from component reports."""
        ...
```

**Lines Saved:** ~300
**New Orchestrator Size:** 1451 - 300 = ~1151 lines ✅ (under 1200!)

### Phase 3 (Optional): Further Optimization
If needed, extract:
- **CodeIndex Integration** (~100 lines) → `src/codeindex_integration.py`

## Rollback Plan

If refactoring fails:
1. Git revert to current commit
2. Keep extracted modules for reference
3. Document issues in ModLog.md

## Testing Strategy

1. **Unit Tests** (for extracted modules):
   - Test `WSPDocumentationGuardian.run_guardian()` with mock files
   - Test `OrchestrationEngine.orchestrate_request()` with mock components

2. **Integration Tests** (for refactored orchestrator):
   - Run HoloIndex queries with various intents
   - Verify WSP guardian detects stale docs
   - Check orchestration routing works correctly

3. **Regression Tests**:
   - Compare output before/after refactoring
   - Verify all intent types route correctly

## Success Criteria

- [ ] qwen_orchestrator.py < 1200 lines (OK threshold)
- [ ] All extracted modules < 800 lines each
- [ ] Zero functional regressions
- [ ] All integration tests pass
- [ ] ModLog.md updated with refactoring documentation
- [ ] Git commit created with refactored code

## Timeline

- **Phase 1** (WSP Guardian): 30-45 min
- **Phase 2** (Orchestration Engine): 30-45 min
- **Testing**: 15-20 min
- **Documentation**: 10 min
- **Total**: ~100 minutes

## WSP Compliance

- **WSP 62:** Large File Refactoring Enforcement
- **WSP 49:** Module Directory Structure (src/ subdirectory)
- **WSP 3:** Functional Distribution
- **WSP 22:** ModLog Updates
- **WSP 50:** Pre-Action Research (HoloIndex search completed)

---

**Next Step:** Begin Phase 1 extraction (WSP Documentation Guardian)
