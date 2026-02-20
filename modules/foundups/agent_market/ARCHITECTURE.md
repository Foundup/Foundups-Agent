# ARCHITECTURE - FoundUps Agent Market

## Objective
Provide a generic outer layer for tokenized Foundup launch and agent swarm execution with auditable payout flow.

## Components
1. Foundup Registry
- Owns foundup records.
- Enforces immutable vs mutable metadata boundaries.

2. Token Factory Adapter
- Chain-agnostic contract for token + vesting + treasury wiring.
- Concrete chain adapters are outside PoC.

3. Agent Join System
- Captures join requests and approved agent profiles.
- Supports capability tag matching.

4. Task -> Proof -> Verify -> Payout Pipeline
- Owns task lifecycle state machine.
- Stores proof and verification records.
- Issues payout events after approval.

5. Treasury + Governance Boundary
- Provides transfer proposal and execution interfaces.
- Actual multisig/DAO execution is deferred.

6. CABR Hook Boundary
- Supplies standardized CABR input payload.
- Stores CABR output for downstream analytics.

7. Observability + Audit Trail
- Emits deterministic event records for all mutating actions.
- Supports payout-to-proof-to-task-to-foundup trace queries.

8. Distribution Adapter Boundary
- Publishes verified milestones to external distribution channels (for example Moltbook/X adapters).
- Enforces idempotent publish semantics keyed by task + channel + milestone state.

9. Compute Access and Paywall Boundary (Prototype, P0 implemented)
- Gates metered build capabilities (launch/orchestration/premium automation).
- Maintains compute-credit wallet and debit ledger.
- Emits deterministic access/debit/rebate events to FAMDaemon.
- Routes configured fee slices into pAVS/system treasury lanes.
- Runtime wiring currently active in in-memory flows and persistent registry/task pipeline paths.

## Data Flow
1. Foundup created in Registry.
2. Token adapter called to prepare tokenization terms.
3. Agents submit join requests and receive approval.
4. Tasks are created and claimed.
5. Proof submitted and verified.
6. Payout triggered by treasury role.
7. Event trail links all lifecycle objects.
8. Verified milestones are published through distribution adapters.
9. Metered actions debit compute credits before execution.
10. Verified PoB can trigger configured credit rebates and standard payout flow.

## State Machine
- `open -> claimed -> submitted -> verified -> paid`
- Disallowed transitions are rejected with `InvalidStateTransitionError`.

## Integration Boundaries
- Ingress/orchestration: OpenClaw + WRE.
- Domain execution: FAM services.
- External systems: chain adapters, DAO/multisig adapters, persistent DB (future).

## Failure Modes
- Invalid schema payloads.
- Unauthorized verification or payout.
- Duplicate claim/proof/payout attempts.
- Duplicate distribution publish attempts (must resolve idempotently).
- Missing linkage objects during trace assembly.
- Insufficient compute-credit balance on metered routes.
- Debit/session and payout lineage mismatch.

## PoC Runtime
- In-memory adapter only.
- No external services required.
