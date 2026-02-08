# ROADMAP - FoundUps Agent Market

## Versioning and Progression
- PoC: `0.0.x`
- Prototype: `0.1.x - 0.9.x`
- MVP: `1.0.x+`

## PoC (COMPLETE - 2026-02-07)
### Goal
Ship contract-complete, testable infrastructure for tokenized Foundup launch and agent task pipeline.

### Deliverables
- [x] Complete interface contracts for registry, token, agent join, task/proof/verify/payout, treasury/governance, CABR hooks, observability.
- [x] In-memory implementation with deterministic state transitions.
- [x] Test suite for schema validation, lifecycle transitions, and permission gates.
- [x] Holo retrieval discoverability updates.

### Exit Criteria
- [x] Tests pass in CI/local.
- [x] Contracts are stable enough for OpenClaw/WRE integration.

## Prototype (Current)
### Goal
Integrate real persistence and one chain adapter while keeping chain-agnostic interface.

### Tranche 1: Observability Backbone (COMPLETE - 2026-02-08)
**Deliverables:**
- [x] `fam_event_v1` schema with deterministic IDs, sequence IDs, dedupe keys
- [x] `FAMEventStore`: JSONL append-only sink + SQLite audit index
- [x] `FAMDaemon`: Heartbeat loop, health/status API, event listeners
- [x] Replay-safe writes with idempotent dedupe enforcement
- [x] Parity verification for JSONL/SQLite sync
- [x] Test suite: 26 tests covering schema, ordering, dedupe, parity, health, thread safety

**Files Added:**
- `src/fam_daemon.py` (737 LOC)
- `tests/test_fam_daemon.py` (comprehensive coverage)

### Tranche 2: Persistence Layer (Planned)
- SQLite/Postgres repository layer for Foundups, Tasks, Proofs
- Migration scripts and schema versioning
- Query optimization and indexing

### Tranche 3: Chain Adapter (Planned)
- One concrete token adapter (Hedera or EVM)
- Chain-agnostic interface preservation
- Test doubles for CI

### Tranche 4: Role Refinement (Planned)
- Role model for verifiers/governance actors
- Permission matrix enforcement
- Audit trail per actor

### Exit Criteria
- End-to-end pipeline works with persistent storage and adapter test doubles.

## MVP (Requires Paying Users)
### Goal
Production deployment with governance, treasury safety controls, and operational observability.

**CRITICAL**: MVP status requires at least one paying user completing a full launch-to-payout cycle. Until then, this remains Prototype regardless of feature completeness.

### Planned Work
- FAM DAEmon: Vitals pump for 012/Overseer observability (WSP 91).
- Integration with breadcrumb_telemetry.db and DaemonMonitorMixin.
- Multisig/DAO adapter integration.
- Idempotent payout orchestration with retry/compensation.
- Operational dashboards and incident runbooks.
- Explicit launch gateway docs and user onboarding path.

### Exit Criteria
- [ ] At least ONE paying user with completed launch-to-payout cycle
- [ ] Production SLO/SLA with audited controls
- [ ] Real user launch workflow validated end-to-end
- [ ] Revenue generated through platform
