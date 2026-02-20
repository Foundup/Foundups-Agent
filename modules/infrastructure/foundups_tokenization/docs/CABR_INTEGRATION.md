# CABR Integration: Treasury Flow Routing

**Canonical meaning**
- CABR = **Consensus-Driven Autonomous Benefit Rate** (also referred to as **Collective Autonomous Benefit Rate**).
- UPS = treasury accounting unit backed by sats/BTC reserve.
- PoB validation = valve gate.
- CABR score = pipe size (flow rate).
- CABR does **not** mint UPS.

## Why this exists

Without CABR + PoB gating:
- low-quality or spam actions can drain treasury flow,
- no defensible allocation basis,
- weak anti-gaming posture.

With CABR + PoB gating:
- only validated work opens the valve,
- higher-benefit work gets larger flow,
- treasury release is bounded by explicit budgets.

## Flow model

```
Treasury UPS --[epoch budget]--[PoB valve]--[CABR pipe size]--> Routed UPS
```

Where:
- `epoch_budget = min(requested_ups, treasury_ups_available * release_rate)`
- if PoB is validated: `routed_ups = epoch_budget * cabr_pipe_size`
- else: `routed_ups = 0`

## Reference implementation

- Router: `modules/foundups/simulator/economics/cabr_flow_router.py`
- Runtime wiring: `modules/foundups/simulator/mesa_model.py`
- Canonical protocol text: `WSP_framework/src/WSP_29_CABR_Engine.md`

## Operational invariants

1. CABR is always clamped to `[0.0, 1.0]`.
2. Release rate is always clamped to `[0.0, 1.0]`.
3. Routed UPS cannot exceed treasury UPS.
4. PoB failure means zero routed UPS.
5. Treasury after routing is non-negative.

## Anti-gaming requirements

- Multi-agent scoring (Gemma/Qwen/vision where applicable) must run before valve open.
- Pattern checks (spam/self-trade/replay) can force valve closed.
- Routing events must be audit-logged with:
  - `pob_validated`
  - `cabr_pipe_size`
  - `requested_ups`
  - `epoch_release_budget_ups`
  - `routed_ups`

## Terminology guardrail

Deprecated CABR meaning for this module:
- "CABR-triggered minting"
- "CABR mint multiplier"

Current meaning:
- "CABR flow routing"
- "CABR pipe size"

Any new simulator or tokenization docs should use the current meaning.
