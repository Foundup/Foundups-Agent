# ROADMAP - FoundUps Simulator

## Phase Status
- PoC: complete
- Prototype: in progress
- MVP: pending paying-user validation path

## Mission
Provide deterministic market + lifecycle simulation that mirrors FoundUps runtime
contracts and supports operator decisions (CABR/PoB, liquidity, allocation policy).

## Prototype Tranches

### Tranche S1 - Deterministic Core (Complete)
- State contracts (`state_contracts.py`)
- Pure-step path (`step_pure.py`)
- Step extraction and shadow parity checks
- Scenario runner with deterministic manifests

### Tranche S2 - Event Plane + Visualization (In Progress)
- SSE stream integration and event normalization
- Frame schema for animation adapter
- Cube visualization and lifecycle ticker integration
- Remaining:
  - tighten member-only gate behavior at API/SSE boundary
  - formalize DEX orderbook snapshot stream

### Tranche S3 - DEX and Market Dynamics (In Progress)
- Existing orderbook kernel (`economics/fi_orderbook.py`)
- Existing market events (`fi_trade_executed`)
- Remaining:
  - add canonical DEX contract events (`order_placed`, `order_cancelled`, `order_matched`, `price_tick`)
  - stress-pack scenarios for liquidity shocks and spread widening
  - role-aware behavior simulation (`observer_012`, `agent_trader`)

### Tranche S4 - Control Panel Read Models (Planned)
- Read-model emitters for:
  - portfolio summary,
  - FoundUp health (CABR, traction, active agents),
  - DEX tape and depth windows.
- Keep panel read-only defaults.

### Tranche S5 - Policy Tuning and Operations (Planned)
- Monte Carlo sweeps for policy sensitivity.
- Optimizer feedback loops into parameter scenarios.
- Operator runbook-grade metrics packs.

## WSP 15 Priority Queue

### P0
1. Canonical DEX event contract parity with `agent_market`.
2. SSE/API member gate hardening.
3. Concatenated integration tests with `moltbot_bridge` and `agent_market`.

### P1
1. Read-model outputs for control panel.
2. DEX stress scenarios and reporting pack.

### P2
1. Auto-tuning guidance from scenario outputs.
2. Expanded behavior models for advanced agent strategy lanes.

## Validation Command
```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest modules/foundups/simulator/tests -q
```

