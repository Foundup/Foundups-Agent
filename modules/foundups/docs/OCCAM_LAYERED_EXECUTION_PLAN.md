# Occam Layered Execution Plan (FoundUps)

## Goal
Provide a stable, low-ambiguity blueprint so any 0102 can resume work without
reconstructing architecture intent.

## Design Rule
Prefer the smallest architecture that preserves:
- auditability,
- deterministic behavior,
- role-safe access control,
- clear module boundaries.

## System Topology
- Ingress/control plane: `modules/communication/moltbot_bridge/`
- Execution/ledger core: `modules/foundups/agent_market/`
- Market/simulation plane: `modules/foundups/simulator/`
- Member/operator surface: `public/`
- Oversight/security plane: `modules/ai_intelligence/ai_overseer/`

## Layer Contracts

### L0 Access + Event Reliability
Must provide:
- invite/member gating at endpoint layer,
- event ordering + dedupe guarantees,
- health/heartbeat and replay-safe persistence.

Primary contracts:
- `fam_event_v1` envelope
- SSE envelope (`event_id`, `sequence_id`, `event_type`, `payload`, `timestamp`)

### L1 FoundUp Execution
Must provide:
- launch, tasks, proofs, verification, payout,
- CABR/PoB gating before distribution/payout-sensitive actions,
- persistent repository behavior equivalent to in-memory behavior.

Primary contracts:
- `FoundupRegistryService`
- `TaskPipelineService`
- `CABRHookService`
- `ObservabilityService`

### L2 Agent-Only DEX
Must provide:
- symbol reservation/uniqueness,
- order place/cancel/match flow,
- settlement and ledger updates,
- role policy (`observer_012` read-only, `agent_trader` mutating).

Primary contracts (to lock):
- `order_placed`
- `order_cancelled`
- `order_matched`
- `price_tick`
- `portfolio_updated`

### L3 Simulation and Forecast
Must provide:
- deterministic scenario runs by seed,
- stress pack outputs for policy decisions,
- bridge parity with production event contract.

Primary outputs:
- run manifest,
- metrics report,
- frame snapshots.

### L4 Control Panel
Must provide:
- portfolio view,
- FoundUp health table (CABR, traction, active agents, stage),
- live DEX tape,
- event feed.

Read-only first; role-based mutation second.

### L5 MVP Operations
Must provide:
- paying-user evidence for MVP,
- runbooks and incident workflow,
- production SLO/SLA evidence.

## Non-Negotiable Invariants
1. Event schema changes require interface doc + tests in same tranche.
2. No hidden write path outside role checks.
3. No UI-only access enforcement.
4. No phase promotion without concatenated suite pass.

## Handoff Packet (every tranche)
- What changed (paths + rationale)
- What is blocked (single source of blockers)
- Validation command + result
- Next ordered actions (WSP 15 P0/P1/P2)

## Blocker Register Format
Use one line per blocker:
`[SEVERITY] [LAYER] [OWNER] [SYMPTOM] [NEXT_ACTION]`

Example:
`[P0] [L2] [agent_market] Symbol collisions under concurrent launch -> add atomic reservation + unique index`

