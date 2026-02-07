# Tests - FoundUps Agent Market

## Coverage Goals
- Schema validation for core entities.
- Lifecycle state transition correctness.
- Permission gating for verification and payout.
- Distribution gating and idempotent verified-milestone publish behavior.
- Launch orchestration and repo provisioning boundaries.

## Run
```powershell
cd o:\Foundups-Agent
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest modules/foundups/agent_market/tests -q
```
