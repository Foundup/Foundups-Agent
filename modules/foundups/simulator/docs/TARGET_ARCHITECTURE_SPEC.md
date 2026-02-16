# Target Architecture Spec (Incremental WSP Refactor)

## Scope
Refactor simulator into module boundaries that are swappable, testable, and deterministic while preserving current behavior.

## Module Map (Target)
- `economics_core`: UPS/F_i treasury math, demurrage, exit routing
- `adoption_curve`: growth/stage progression functions
- `token_emission`: 21M cap + release policy
- `reward_allocator`: 80/20 and 60/16/4 pool splits
- `behavior_humans`: stake/churn/subscription behavior
- `behavior_agents`: productivity/work execution
- `sentinel_enforcement`: anomaly/penalty hooks
- `dao_escalation`: FoundUp -> DAO transitions
- `reporting_docs`: manifests, metrics, scenario outputs
- `animation_adapter`: immutable frame translation only

## Contracts
### State Contracts
- `SystemState`
- `FoundUpState[]`
- `ActorState[]`
- `PoolState`
- `MetricsState`

### Step Contract
`next_state = step(current_state, params, rng, events)`

### Frame Contract
- `frame_schema.py` defines immutable render snapshots.
- Animation consumers depend only on `FRAME_SCHEMA_VERSION` + fields.

## Determinism Requirements
- All randomness seeded through config/scenario params.
- No time-based RNG in sim core.
- Each run writes:
  - manifest (`*_manifest.json`)
  - metrics (`*_metrics.json`)
  - optional frame stream (`*_frames.jsonl`)

## Current Tranche Delivered
1. Parameter schema + defaults + scenario overrides.
2. Scenario runner with manifest/metrics and optional Monte Carlo.
3. Immutable animation frame adapter.
4. Runtime telemetry for allocation + pAVS separation.

## Pending Tranches
1. Move orchestration logic from `FoundUpsModel` into pure step modules.
2. Replace mutable state internals with immutable state transitions.
3. Complete module carve-out per target map with interface-only dependencies.

## WSP 15 Ordering (Current)

Scored with MPS = Complexity + Importance + Deferability + Impact.

| Work Item | C | I | D | Im | MPS | Priority | Status |
|---|---:|---:|---:|---:|---:|---|---|
| Step orchestration extraction seam (`step_pipeline.py`) | 3 | 5 | 5 | 5 | 18 | P0 | Done |
| Pure-step state transition core (`next_state = step(...)`) | 5 | 5 | 5 | 5 | 20 | P0 | In Progress (state contracts + pure step + shadow parity gate) |
| Behavior/economics module carve-out behind interfaces | 4 | 5 | 4 | 4 | 17 | P0 | Next |
| Sensitivity analysis runner + scenario packs | 3 | 4 | 4 | 4 | 15 | P1 | Next |
| Additional animation contract hardening (frame compatibility checks) | 2 | 3 | 3 | 3 | 11 | P2 | Backlog |

Decision: execute P0 items first, then P1. No P2 work until pure-step path is landed.
