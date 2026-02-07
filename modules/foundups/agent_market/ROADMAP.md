# ROADMAP - FoundUps Agent Market

## Versioning and Progression
- PoC: `0.0.x`
- Prototype: `0.1.x - 0.9.x`
- MVP: `1.0.x+`

## PoC (Current)
### Goal
Ship contract-complete, testable infrastructure for tokenized Foundup launch and agent task pipeline.

### Deliverables
- Complete interface contracts for registry, token, agent join, task/proof/verify/payout, treasury/governance, CABR hooks, observability.
- In-memory implementation with deterministic state transitions.
- Test suite for schema validation, lifecycle transitions, and permission gates.
- Holo retrieval discoverability updates.

### Exit Criteria
- Tests pass in CI/local.
- Contracts are stable enough for OpenClaw/WRE integration.

## Prototype
### Goal
Integrate real persistence and one chain adapter while keeping chain-agnostic interface.

### Planned Work
- Add SQLite/Postgres repository layer.
- Add one concrete token adapter (still behind `TokenFactoryAdapter`).
- Add role model refinement for verifiers/governance actors.
- Add replayable event store and reconciliation routines.

### Exit Criteria
- End-to-end pipeline works with persistent storage and adapter test doubles.

## MVP
### Goal
Production deployment with governance, treasury safety controls, and operational observability.

### Planned Work
- Multisig/DAO adapter integration.
- Idempotent payout orchestration with retry/compensation.
- Operational dashboards and incident runbooks.
- Explicit launch gateway docs and user onboarding path.

### Exit Criteria
- Production SLO/SLA, audited controls, real user launch workflow.
