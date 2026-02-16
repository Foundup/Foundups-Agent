# Compute Access Paywall Spec (FAM + pAVS)

## Status
- Phase: Prototype in progress (P0 in-memory and persistence-adapter enforcement merged; registry/task pipeline wiring done; remaining service paths pending)
- Scope: Access and pricing model for building FoundUps with shared agent compute
- WSP References: WSP 11, WSP 15, WSP 22, WSP 26, WSP 29, WSP 50

## Objective
Define a simple, scalable paywall where users pay for coordinated build compute, not for idea submission or passive browsing.

This is the commercial access layer for FoundUps:
- FAM provides venture workflow (launch, tasks, proof, verify, payout)
- pAVS provides treasury lanes and allocation accounting
- CABR gates quality and benefit validity (PoB)

## First-Principles Constraints
1. The scarce resource is coordinated agent compute and verification bandwidth.
2. Ideas should be cheap to start; execution should be metered.
3. Reward distribution must follow validated benefit (PoB), not vanity activity.
4. One accounting unit should drive enforcement (Occam rule).

## Occam Model (Single Meter)
Use one normalized internal meter for all chargeable execution:
- Unit: `compute_credits` (CC)
- Funding rails:
  - plan subscription (monthly CC allotment)
  - UP$ conversion to CC
  - earned CC rebates from verified PoB contribution

No secondary hidden meters in prototype.

## Access Policy (What is Free vs Metered)

### Free (Low-Risk Discovery)
- Browse FoundUps and public dashboards
- Draft idea canvas
- Join waitlist / interest graph

### Metered (Execution Surface)
- Launch FoundUp workspace with active agents
- Run orchestration flows (task decomposition, assignment, verification passes)
- Trigger distribution and promotion automations
- Use premium analytics, scenario runs, and CABR advisory loops

## Proposed Access Tiers
All tier numbers are config-managed and can change without interface changes.

1. `scout` (free)
   - Read/discover only
   - No autonomous orchestration actions
2. `builder` (paid)
   - Single FoundUp active workspace
   - Monthly CC allocation and UP$ top-up
3. `swarm` (paid)
   - Multi-FoundUp orchestration
   - Higher CC cap and priority queueing
4. `sovereign` (paid/team)
   - Team seats, governance controls, advanced observability
   - pAVS treasury controls and incident tooling

## Core Economic Loop (Paywall -> PoB)
1. User funds CC (plan or UP$ conversion).
2. User runs build actions; CC debited per metered action.
3. Completed work enters FAM task->proof->verify->payout pipeline.
4. CABR evaluates benefit quality; PoB confirmed.
5. Rewards distributed:
   - contributor receives F_i rewards per policy
   - optional CC rebate for high-quality contribution windows
   - pAVS and network pools receive configured fees

## ROI Replacement: PoB Yield Signals
For protocol decisions, use PoB yield instead of traditional ROI/CAGR:

- `pob_yield = sum(validated_benefit_units) / sum(compute_credits_spent)`
- `cabr_weighted_yield = sum(cabr_score * benefit_units) / sum(compute_credits_spent)`

Interpretation:
- Higher yield means the system turns paid compute into validated benefit efficiently.
- Financial ROI remains a downstream reporting view, not the protocol control variable.

## FAM Contract Additions (Planned)
Add a `ComputeAccessService` contract with:
- `ensure_access(actor_id, capability, foundup_id) -> AccessDecision`
- `get_wallet(actor_id) -> ComputeWallet`
- `purchase_credits(actor_id, amount, rail) -> LedgerEntry`
- `debit_credits(actor_id, amount, reason, foundup_id) -> LedgerEntry`
- `record_compute_session(actor_id, foundup_id, workload) -> session_id`
- `rebate_credits(actor_id, amount, reason) -> LedgerEntry`

## Event Schema Additions (Planned)
Add to `fam_event_v1`:
- `compute_plan_activated`
- `compute_credits_purchased`
- `compute_credits_debited`
- `compute_session_recorded`
- `compute_credits_rebated`
- `paywall_access_denied`

All events require deterministic IDs, sequence IDs, and dedupe keys.

## WSP 15 Priority Build Order
Scores use MPS = Complexity + Importance + Deferability + Impact.

| Work Item | C | I | D | Im | Score | Priority |
|---|---:|---:|---:|---:|---:|---|
| Access gate + debit ledger enforcement | 3 | 5 | 5 | 5 | 18 | P0 |
| Metering hooks in orchestrator/task pipeline | 3 | 5 | 4 | 4 | 16 | P0 |
| Tier/plan management API + storage | 3 | 4 | 4 | 4 | 15 | P1 |
| UP$ <-> CC conversion policy + limits | 4 | 4 | 3 | 4 | 15 | P1 |
| pAVS fee routing + rebate settlement | 4 | 4 | 3 | 4 | 15 | P1 |
| Simulator scenario pack for PoB yield stress tests | 3 | 4 | 3 | 4 | 14 | P1 |
| Dynamic pricing/queue optimization | 4 | 3 | 2 | 3 | 12 | P2 |

## Implementation Tranches

### Tranche A (P0)
- Add access/debit contracts and persistence tables.
- Enforce gate in launch/orchestration/task-mutating endpoints.
- Emit compute access events through FAMDaemon.

### Tranche B (P1)
- Add plan management and top-up rails.
- Add pAVS routing and rebate policies.
- Add simulator scenario pack for payout and yield testing.

### Tranche C (P2)
- Add adaptive pricing and queue controls from observed utilization.

## Security and Abuse Controls (Minimum)
- Fail-closed on insufficient CC balance.
- Idempotency keys on purchase/debit/rebate operations.
- Per-actor and per-foundup rate limits for metered endpoints.
- Audit trail from debit -> session -> proof -> verification -> payout.
- Separate operator override path with signed audit records.

## Acceptance Criteria
- Every metered action has a deterministic debit or explicit denial event.
- No payout event can exist without traceable workload/proof lineage.
- Same input and seed produce reproducible simulator yield outputs.
- Interface and roadmap docs remain aligned with implementation status.
