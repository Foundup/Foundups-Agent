# FoundUps Agent Market (FAM)

## Purpose
FoundUps Agent Market (FAM) is the outer layer for launching tokenized FoundUps and coordinating agent swarms through a task to proof to verification to payout pipeline.

This module is intentionally generic and chain-agnostic in PoC.

## Scope in This PoC
- Foundup registry with immutable vs mutable metadata rules.
- Token factory adapter interface (no chain lock-in).
- Agent join requests and capability tagging.
- Task lifecycle: `open -> claimed -> submitted -> verified -> paid`.
- Treasury and governance boundaries as interfaces.
- CABR integration hooks as interfaces.
- Event audit trail linking payout to proof to task to foundup.
- Verified milestone distribution contract with idempotent publish semantics.
- In-memory adapter for deterministic tests.

## Out of Scope in This PoC
- Production blockchain writes.
- Production DAO/multisig execution.
- UI implementation.
- External DB dependencies.

## Directory Layout
- `src/models.py`: core schemas and validation.
- `src/interfaces.py`: service contracts and adapter boundaries.
- `src/in_memory.py`: PoC in-memory implementation.
- `src/exceptions.py`: domain errors.
- `tests/`: schema, lifecycle, and permission tests.
- `memory/`: module memory artifacts.

## Quick Start
```powershell
cd o:\Foundups-Agent
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest modules/foundups/agent_market/tests -q
```

## OpenClaw Execution Arm Alignment
OpenClaw remains the execution ingress for intent routing. FAM provides explicit contracts that OpenClaw/WRE can call for launch and execution flows.
