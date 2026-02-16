# Simulator Tests ModLog

## Test Modification Log (WSP 22 Compliance)

### 2026-02-16 - Cross-module concatenated validation (identity-anchor hardened)
**Command**:
`$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; .venv\\Scripts\\python.exe -m pytest modules/communication/moltbot_bridge/tests modules/foundups/agent_market/tests modules/foundups/simulator/tests -q`
**Status**: 335/335 PASSED
**Coverage**:
- Confirms SSE member gate + DEX stream contract integration remains stable
  under full OpenClaw/FAM/Simulator lane.
- Confirms OpenClaw conversation identity anchor hardening resolves prior
  end-to-end nondeterministic assertions.

---

### 2026-02-16 - SSE member gate + DEX stream contract coverage
**Command**:
`$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests/test_sse_server.py modules/foundups/agent_market/tests/test_e2e_integration.py modules/foundups/agent_market/tests/test_persistence.py modules/foundups/agent_market/tests/test_task_lifecycle.py -q`
**Status**: 55/55 PASSED
**Coverage** (added/validated):
- `test_sse_server.py`
  - Member gate authorization paths (disabled, missing key, valid key+role,
    insufficient role, localhost bypass, misconfigured gate fail-closed).
  - Endpoint gating checks for `/api/sim-events` and `/api/health`.
  - DEX stream contract events present in `STREAMABLE_EVENT_TYPES`.
- `test_e2e_integration.py`
  - FAM adapter auto-symbol generation when token omitted.
  - Collision-safe symbol resolution across repeated launches.
- `test_persistence.py`, `test_task_lifecycle.py`
  - Case-insensitive token symbol uniqueness in SQLite and in-memory registries.

---

### 2026-02-15 - Pure-Step Shadow Parity Tests
**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests -q`
**Status**: 82/82 PASSED
**Coverage** (added):
- `test_step_shadow_parity.py`
  - `test_shadow_parity_records_check_metrics`
  - `test_shadow_parity_failure_counter_increments_on_drift`
- Confirms shadow parity telemetry is active only when enabled and fail counters increment on drift.

---

### 2026-02-15 - Determinism + UTC Timestamp Hardening
**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests -q`
**Status**: 80/80 PASSED
**Coverage**:
- `test_scenario_runner_determinism.py` now validates deterministic digest with:
  - isolated per-run FAM daemon storage,
  - FiRating singleton reset per run,
  - stable/normalized frame digest projection.
- `test_sse_server.py` updated to timezone-aware datetime usage (`datetime.now(UTC)`).
- Demurrage warning dedupe hardening validated in full suite regression run.
- `test_step_pipeline_extraction.py` verifies `FoundUpsModel.step()` delegates to `step_pipeline.run_step()`.
- `test_step_core.py` validates pure tick scheduler logic (`compute_step_decision`) for boot tick and periodic action flags.
- `test_state_contracts.py` validates immutable state contract bridge from runtime state.
- `test_step_pure.py` validates side-effect-free `step()` evolution over immutable contracts.

**Notes**:
- Remaining warnings are project-level pytest config options (`asyncio_*`) with plugin autoload disabled, not simulator regressions.

---

### 2026-02-15 - AI Parameter Optimizer Tests (OpenClaw + GPT)
**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests/test_ai_parameter_optimizer.py -v`
**Status**: 21/21 PASSED
**Coverage** (added):
- `TestParameterBounds` (2 tests) - Parameter bounds validation, config matching
- `TestMockAIGateway` (2 tests) - Mock gateway response format, JSON parsing
- `TestAIParameterOptimizer` (7 tests) - Core optimizer: init, config conversion, GPT parsing, bounds clamping
- `TestOptimizationObjectives` (3 tests) - Objective definitions, scoring functions
- `TestOptimizerConfig` (2 tests) - Default/custom config validation
- `TestOptimizationSummary` (2 tests) - Summary generation, history tracking
- `TestIntegrationWithSimulator` (3 tests) - Prompt building, improvement calculation

**Notes**:
- Uses MockAIGateway for offline testing without API keys
- Integrates with PAVSAuditor for compliance scoring
- 4 optimization objectives: STAKER_DISTRIBUTION, ECOSYSTEM_GROWTH, TOKEN_VELOCITY, BALANCED

---

### 2026-02-15 - Refactor Foundations Test Additions
**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests -q`
**Status**: Added tests pass in full suite
**Coverage** (added):
- `test_parameter_registry.py` - schema/default/scenario load + config conversion.
- `test_animation_adapter.py` - immutable frame contract output.
- `test_scenario_runner_determinism.py` - same seed + scenario -> same frame digest.

---

### 2026-02-15 - 012 Allocation + pAVS Treasury Runtime Wiring
**Command**: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .venv\\Scripts\\python.exe -m pytest modules/foundups/simulator/tests -q`
**Status**: 48/48 PASSED
**Coverage** (added):
- `test_012_allocation_updates_state_and_emits_events` - Validates live allocation path updates state + emits batch/result telemetry.
- `test_demurrage_emits_treasury_separation_events` - Validates demurrage emits pAVS/network/fund separation events.

**Regression fixes validated**:
- Demurrage threshold attribute mismatch (`pavs_treasury_*`) no longer raises runtime errors.
- Allocation scoring uses available FiRatingEngine API (composite score) instead of missing `get_rating()`.

---

### 2026-02-12 - SSE Server Observability Test Added
**Command**: `python -c "..." # Direct test runner (Windows)`
**Status**: 12/12 PASSED
**Coverage** (added):
- `test_fam_event_source_observability_properties` - Dropped event count and queue size monitoring

**Notes**:
- Added test for `dropped_event_count` and `queue_size` properties
- Health endpoint now exposes queue metrics for monitoring

---

### 2026-02-12 - SSE Server Unit Tests Added
**Command**: `pytest modules/foundups/simulator/tests/test_sse_server.py -v`
**Status**: 11/11 PASSED
**Coverage**:
- `test_format_sse_event_structure` - SSE event format validation
- `test_format_sse_event_json_escaping` - JSON special character handling
- `test_simulated_event_source_sequence_monotonic` - Sequence ID monotonicity
- `test_simulated_event_source_event_types` - Event type filtering
- `test_simulated_event_source_task_state_uses_new_status` - new_status vs new_state
- `test_simulated_event_source_required_fields` - Required field validation
- `test_fam_event_source_queue_bounded` - Queue maxsize=1000 verification
- `test_fam_event_source_filters_non_streamable_events` - Event filtering
- `test_fam_event_source_accepts_streamable_events` - Streamable event acceptance
- `test_fam_event_source_queue_full_handling` - Graceful overflow handling
- `test_streamable_event_types_includes_economic_events` - Economic events for earning pulses

**Notes**:
- Minor deprecation warnings for `datetime.utcnow()` (Python 3.12+)
- All tests run without FAMDaemon dependency (unit tests on class internals)

---

### Existing Test Files
- `test_ai_parameter_optimizer.py` - AI-driven parameter optimization (OpenClaw + GPT)
- `test_alignment_and_tokenomics.py` - Token economics validation
- `test_allocation_and_treasury_runtime.py` - 012 allocation + pAVS treasury telemetry wiring
- `test_f0_mvp_offering_flow.py` - F_0 MVP offering
- `test_fam_lifecycle_flow.py` - FAM event lifecycle
- `test_investor_liability_engine.py` - Investor underwriting
- `test_investor_share_contract.py` - Share contract logic
- `test_lifecycle_stage_and_market.py` - Lifecycle stages
- `test_underwriting_scenarios.py` - Underwriting scenarios
