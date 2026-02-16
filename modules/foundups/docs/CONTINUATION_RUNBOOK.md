# Continuation Runbook (0102)

## Purpose
Fast, deterministic session resume for FoundUps workstreams.

## 1) Read Order (5-10 minutes)
1. `modules/foundups/ROADMAP.md`
2. `modules/foundups/docs/OCCAM_LAYERED_EXECUTION_PLAN.md`
3. Module roadmaps:
   - `modules/foundups/agent_market/ROADMAP.md`
   - `modules/foundups/simulator/ROADMAP.md`
   - `modules/foundups/agent/ROADMAP.md`
4. Latest module ModLogs touched in last tranche.

## 2) Validate Current State
Run:
```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest `
  modules/communication/moltbot_bridge/tests `
  modules/foundups/agent_market/tests `
  modules/foundups/simulator/tests -q
```

Expected baseline currently:
- `321 passed` (plus repo-level pytest warnings).

## 3) Pick Next Work by WSP 15
Select the highest-impact unblocked P0 item from:
- access gating,
- DEX contracts,
- symbol registry,
- integration tests.

If no P0 remains, move to P1 control-panel read models.

## 4) Change Protocol
For each code tranche:
1. implement code + tests
2. run concatenated suite
3. update docs:
   - module `ModLog.md`
   - module `tests/TestModLog.md`
   - impacted `INTERFACE.md` and `ROADMAP.md`
4. re-index Holo if retrieval targets changed

## 5) Done Criteria for Handoff
- No failing tests in concatenated lane.
- No undocumented interface changes.
- Clear next action list in WSP 15 order.

## 6) Known Remaining Work (Current)
- Member/invite fail-closed gating for SSE/API write surfaces.
- DEX symbol registry + reservation policy.
- Unified DEX event contract across market + simulator.
- Control-panel read models (portfolio, CABR, traction, active agents).

