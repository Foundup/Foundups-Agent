# WSP 78: Database Architecture and Scaling Protocol

## Status
- Status: Active
- Version: 4.0.0
- Last Updated: 2026-02-21

## Purpose
Define canonical data boundaries for FoundUps so SIM, CABR/PoB, and future blockchain settlement remain consistent under scale.

## First-Principles Model
Treat data by function, not by tool:

1. Execution state
- Ephemeral runtime state used for fast simulation/automation loops.
- May be in-memory if fully replayable from events.

2. Operational state
- Mutable relational state used by services and user-facing workflows.
- Must support queryability, constraints, migrations, and backups.

3. Audit trail
- Append-only event history for replay, observability, and forensic analysis.
- Must be durable, ordered, and dedupe-safe.

4. Settlement state
- Final economic commitments anchored to blockchain.
- Off-chain systems are provisional until anchored.

## Canonical Ordering of Truth
For economic claims and treasury accounting:

1. On-chain settlement anchors (highest authority)
2. Append-only audit events (replay source)
3. Operational tables/snapshots
4. Derived UI/render caches (lowest authority)

## Required Storage Layers

### Layer A: Runtime/Derived
- In-memory allowed.
- Must be replayable from Layer C events.
- Example: simulator `state_store` render state.

### Layer B: Operational Relational Store
- Default local backend: SQLite.
- Shared multi-writer backend: PostgreSQL.
- Backend must be switchable through configuration, not code forks.
- Current infrastructure entrypoint: `modules/infrastructure/database/src/db_manager.py`.

### Layer C: Audit Event Store
- Append-only JSONL + indexed SQL store are allowed as dual-write pattern.
- Must guarantee monotonic sequence IDs and dedupe keys.
- Current implementations: FAM and DAE event stores.

### Layer D: Blockchain Settlement
- Epoch roots, treasury settlement commitments, and final payouts belong here.
- Off-chain epoch ledgers are pre-settlement evidence, not final settlement.

## Namespace Contract (Operational Layer)
In shared relational stores, table ownership must be explicit:

- `modules_*`: module-specific operational tables
- `agents_*`: agent memory/coordination tables
- `foundups_*`: FoundUp business/domain tables

Unprefixed shared tables are allowed only when documented as cross-domain infrastructure in module architecture docs.

## SQLite Policy
SQLite is approved for local deterministic execution and single-host deployment, with these minimum requirements:

1. `PRAGMA journal_mode=WAL` for long-lived writable DBs.
2. `PRAGMA synchronous=NORMAL` unless stronger durability is explicitly required.
3. `PRAGMA foreign_keys=ON` on every connection (connection-scoped in SQLite).
4. `PRAGMA busy_timeout` configured for concurrent writer resilience.
5. Integrity checks and backup cadence documented.

## PostgreSQL Policy
Promote from SQLite to PostgreSQL when one or more are true:

- Multi-process/multi-host writers contend regularly.
- Write latency under lock contention exceeds SLO.
- File-level backup/restore windows are operationally unsafe.
- Cross-service transactional boundaries require stronger isolation.

When promoted, keep interface compatibility and migrate via schema/migration tooling, not ad hoc SQL forks.

## SIM and CABR/PoB Requirements

1. Event-first economics
- CABR flow routing, payout progression, and operational-profit distribution must emit audit events.
- Derived simulator state must never be treated as accounting truth.

2. Beneficiary correctness
- Agent work can trigger value flow, but 012 proxy beneficiary distribution must be explicit in accounting events.

3. Reproducibility
- Deterministic simulation runs must preserve event ordering and replayability.

4. Bridge to settlement
- Epoch/merkle summaries may exist off-chain, but publication and settlement anchors must be modeled as separate commitments.

## Satellite Store Policy
Satellite DBs are permitted only for one of:

- Third-party library-managed stores (for example vector index internals).
- Large binary/ephemeral workloads that would bloat operational DB.
- Disposable run artifacts (for example simulation run audit directories).

Every satellite store must document:
- Owner component
- Retention policy
- Why it is not in Layer B
- Migration or permanence decision

## Anti-Patterns
- Treating render/UI caches as accounting truth.
- Assuming SQLite pragmas like `foreign_keys` persist across connections.
- Mixing settlement semantics into mutable operational tables without anchoring strategy.
- Silent proliferation of ad hoc SQLite files without ownership and retention.

## Compliance Checklist
- [x] Operational DB backend is configurable and documented.
- [x] Per-connection SQLite safety pragmas are enforced where SQLite is used.
- [x] Event stores enforce dedupe and monotonic ordering.
- [x] SIM/CABR economic flows are event-auditable.
- [x] Settlement/anchoring boundary is explicit in architecture docs.
- [x] Simulator satellite stores are documented under module policy.
