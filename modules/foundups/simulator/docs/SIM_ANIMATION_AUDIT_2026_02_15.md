# Simulator + Animation Audit (2026-02-15)

## Inputs Loaded
- Simulator entrypoint: `modules/foundups/simulator/run.py`
- Core runtime: `modules/foundups/simulator/mesa_model.py`
- State/event boundary: `modules/foundups/simulator/state_store.py`, `modules/foundups/simulator/event_bus.py`
- Animation/web path: `public/js/foundup-cube.js`
- SSE bridge: `modules/foundups/simulator/sse_server.py`
- Config: `modules/foundups/simulator/config.py`

## Current Architecture Snapshot
- `FoundUpsModel.step()` orchestrates behavior + economics + events.
- `FAMBridge` emits canonical events into `FAMDaemon`.
- `EventBus` normalizes to `SimEvent`, `StateStore` derives renderable state.
- Terminal/cube renderers read mutable `SimulatorState`.
- Web animation subscribes to SSE stream and maps event payloads into visuals.

## Call Graph (high-level)
`run.py -> FoundUpsModel.step -> FAMBridge + economics modules -> FAMDaemon.emit`
`FAMDaemon -> EventBus -> StateStore -> render/* OR sse_server -> public/js/foundup-cube.js`

## WSP Risk Findings
1. **Mixed concerns in `FoundUpsModel`** (Risk: High)
   - Tick orchestration includes behavior, economics, and telemetry formatting.
2. **No versioned parameter registry previously** (Risk: High)
   - Config existed as dataclass only; no schema/bounds/scenario pack.
3. **Animation contract not explicitly versioned** (Risk: Medium)
   - SSE payloads relied on implicit event conventions.
4. **Deterministic harness incomplete** (Risk: Medium)
   - Standard run path exists, but scenario/Monte Carlo manifests were missing.

## Refactor Priority Queue
1. Parameter schema + scenario registry (done in this tranche).
2. Immutable frame adapter boundary (done in this tranche).
3. Scenario runner with reproducible manifests (done in this tranche).
4. Extract pure `step(state, params, rng, events)` core (pending).
5. Full module split (`economics_core`, `behavior_*`, `dao_escalation`) with swappable interfaces (pending).

## Addendum - Determinism Hardening (2026-02-15)
- Scenario runner now isolates each run from global singleton state:
  - dedicated FAM daemon store per run label.
  - FiRating singleton reset per run.
- `frame_digest_sha256` now hashes a stable projection (state/pools/metrics) with float normalization.
- SSE timestamps now use timezone-aware UTC (`datetime.now(UTC)`), removing deprecation noise in Python 3.12+.
- Tick scheduling now has a pure core (`step_core.compute_step_decision`) that returns deterministic periodic action flags.
- Immutable state contracts added (`state_contracts.py`) and pure step path established (`step_pure.step`).
