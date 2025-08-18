# TestModLog — PQN Alignment Module

<!-- Per WSP 22: Journal format - NEWEST entries at TOP, oldest at bottom -->

## [2025-08-18] - Added Test Suite
**Tests Added**:
- test_analysis_ab.py — Validates A/B analysis deltas and cost_of_stability on mock logs
- test_csv_schema.py — Verifies detector v2 CSV includes early-warning columns (`ew_varE`, `ew_ac1E`, `ew_dS`)
- test_config_loader.py — Ensures YAML/JSON config loader is present and importable
- test_schemas.py — Validates detector events JSONL required fields (structure-only)
- test_invariants_doc.py — Placeholder capturing planned invariant checks (Hermiticity, trace=1; JSONL/CSV contracts)
- test_interface_symbols.py — Ensures public API symbols exist (`run_detector`, `phase_sweep`, `rerun_targeted`, `council_run`, `promote`)

**Pending**: Unit tests for invariants and adapter smoke tests after API shims land

---

## [2025-08-17] - Test Documentation Created
- Created tests/README.md documenting strategy and execution (WSP 22/34)

---

## Process Note (WSP 22)
- **Action**: TestModLog updated when tests added/changed - NEWEST at TOP
- **Rationale**: Quick reference to latest test work without scrolling
