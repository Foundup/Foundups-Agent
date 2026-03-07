# SQLite Audit: SIM + CABR + Blockchain Boundary

Date: 2026-02-21  
Scope: Current SQLite usage and target architecture alignment for simulator economics and settlement readiness.

## Executive Findings

1. Data boundaries are conceptually correct but operationally fragmented.
- Simulator render state is event-derived and in-memory (good).
- FAM/DAE use dual-write audit stores (good for replay/forensics).
- Settlement is not yet on-chain (expected, but boundary must stay explicit).

2. SQLite safety was inconsistent before this hardening pass.
- `foreign_keys` was not guaranteed on every runtime connection in the shared DB manager.
- Event stores were not consistently configured for concurrent-writer pragmas.

3. Documentation drift existed.
- Some docs still described a pure single-file model while runtime had multiple canonical persistence lanes (operational DB + audit stores + satellite stores).

## Evidence Snapshot (Observed)

Inspected files:
- `data/foundups.db`
- `modules/infrastructure/database/data/foundups.db`
- `modules/infrastructure/database/data/agent_db.sqlite`
- `modules/foundups/agent_market/memory/fam_audit.db`
- `modules/infrastructure/dae_daemon/memory/dae_audit.db`
- `modules/foundups/simulator/memory/fam_audit.db`

Observed examples:
- `data/foundups.db`: large operational store, WAL enabled, integrity `ok`.
- FAM/DAE audit DBs: integrity `ok`, compact schemas, event-count driven growth.
- Multiple simulator run artifact DBs under `modules/foundups/simulator/memory/*`.

## First-Principles Data Model

1. Runtime/derived state
- Fast, replayable, non-authoritative.

2. Operational relational state
- Mutable, queryable, constrained.
- Default local backend may be SQLite; shared deployment should support PostgreSQL.

3. Audit/event state
- Append-only with sequence and dedupe guarantees.

4. Settlement state
- Final commitments belong on-chain.
- Off-chain ledgers are provisional evidence.

## SIM + CABR Implications

1. CABR routing and proxy-beneficiary distributions must remain event-auditable.
2. `state_store`/UI projections must never be treated as accounting truth.
3. Epoch/merkle off-chain structures should feed an explicit anchoring pipeline.

## Gaps Closed in This Pass

Code hardening applied:
- `modules/infrastructure/database/src/db_manager.py`
  - per-connection `PRAGMA foreign_keys=ON`
  - per-connection `PRAGMA busy_timeout=5000`
- `modules/foundups/agent_market/src/fam_daemon.py`
  - configured SQLite connection helper
  - WAL + NORMAL init pragmas
  - per-connection foreign keys + busy timeout
- `modules/infrastructure/dae_daemon/src/event_store.py`
  - same hardening as FAM event store
- `modules/infrastructure/database/src/sqlite_audit.py`
  - repeatable audit utility with JSON output

## Target Architecture (Recommended)

Layer A: Runtime
- In-memory simulation and render caches.

Layer B: Operational DB
- SQLite local, PostgreSQL shared.
- Interface-compatible persistence boundary.

Layer C: Audit DB + JSONL
- Deterministic replay and parity checks.

Layer D: Blockchain settlement
- Anchor epoch commitments and treasury settlement artifacts.

## Decision Rule

If a value claim affects payout, treasury health, or sustainability claims:
- It must be verifiable from Layer C events and/or Layer D settlement anchors.
- Layer A-only state is insufficient.

## Repeatable Audit Command

```bash
python -m modules.infrastructure.database.src.sqlite_audit \
  --output modules/infrastructure/database/memory/sqlite_audit_report.json
```

