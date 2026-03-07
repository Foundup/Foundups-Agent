# Database Module Architecture

System-specific implementation of `WSP_framework/src/WSP_78_Database_Architecture_Scaling_Protocol.md`.

## Scope
This architecture focuses on data boundaries that affect:
- Simulator (`modules/foundups/simulator`)
- CABR/PoB economics flow
- FAM and DAE event observability
- Blockchain settlement readiness

## Current Runtime Topology (Observed 2026-02-21)

### Core SQLite Stores
| Path | Role | Notes |
|---|---|---|
| `data/foundups.db` | Primary operational store | Large multi-module DB; WAL enabled |
| `modules/foundups/agent_market/memory/fam_audit.db` | FAM audit index | JSONL+SQLite dual-write |
| `modules/infrastructure/dae_daemon/memory/dae_audit.db` | DAE audit index | JSONL+SQLite dual-write |
| `modules/foundups/simulator/memory/*/fam_audit.db` | Per-run simulation audit artifacts | Disposable run evidence |

### Important Observations
- Simulator render state is event-derived and in-memory (`event_bus` -> `state_store`).
- CABR routing and operational profit distribution are emitted as events, then rendered from event stream.
- Epoch ledger in simulator is currently in-memory (blockchain-lite evidence, not settlement).
- `data/foundups.db` contains mixed prefixed and unprefixed tables (shared infra tables exist).

## Data Layer Contract

### Layer A: Runtime/Derived
- `modules/foundups/simulator/state_store.py`
- Non-authoritative, replayable from events.

### Layer B: Operational Relational
- Managed through `modules/infrastructure/database/src/db_manager.py`.
- SQLite default locally, PostgreSQL optional for shared deployment.

### Layer C: Audit/Event
- FAM event store and DAE event store:
  - Append-only JSONL
  - SQLite index for query, dedupe, and parity checks

### Layer D: Settlement
- Off-chain in current implementation.
- Target: on-chain anchoring for epoch commitments, payout commitments, and treasury settlement.

## SIM/CABR-Specific Boundary

1. CABR flow math
- Occurs in simulator economics modules.
- Must emit auditable events for every routed amount.

2. Proxy beneficiary semantics
- Agent work is execution.
- 012 proxy receives UPS distributions (beneficial owner lane).
- This distinction belongs in event payloads and accounting, not UI-only state.

3. Treasury accounting
- Operational state tracks balances and flow counters.
- Final settlement is a separate concern and must be anchorable.

## Satellite Stores Policy

Allowed when justified:
- Library-owned vector stores (for example Chroma internals)
- Binary-heavy or disposable simulation artifacts
- Isolated subsystem scratch stores with clear ownership

Every satellite DB must define:
- Owner
- Retention window
- Why not in `data/foundups.db`
- Migration/permanence decision

Current simulator policy reference:
- `modules/foundups/simulator/docs/SATELLITE_STORES.md`

## Known Architecture Gaps

1. SQLite sprawl
- Many SQLite files exist across the repo, including browser profile artifacts and per-run simulator DBs.
- Not all are part of canonical operational accounting.

2. Documentation drift
- Legacy docs described a strict "single SQLite file" model while runtime already includes dual-write audit stores and backend abstraction.

3. Settlement boundary not yet implemented
- Epoch proofs exist off-chain; no production-grade anchor publisher pipeline is enforced yet.

## Immediate Enforcement Rules

1. Operational writes
- Use `DatabaseManager` or a documented persistence adapter boundary.

2. Event observability writes
- Use append-only event stores with dedupe and sequence guarantees.

3. SQLite safety
- Enforce per-connection pragmas (`foreign_keys`, `busy_timeout`).
- Keep WAL for long-lived writable stores.

4. Claims discipline
- Sustainability, payout, and treasury claims must reference event/audit artifacts or settlement anchors, not derived UI state.

## Recommended Next Phase

1. Introduce a settlement-anchor service boundary
- Consume epoch/event commitments
- Publish anchors on target chain
- Persist tx refs back into operational/audit stores

2. Move shared deployments to PostgreSQL
- Keep SQLite for local deterministic runs
- Keep interface contracts unchanged

3. Add CI checks
- SQLite audit report generation
- Drift checks for undocumented new DB files
