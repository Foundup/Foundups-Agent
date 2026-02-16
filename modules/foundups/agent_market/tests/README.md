# Tests - FoundUps Agent Market

## Coverage Goals
- Schema validation for core entities.
- Lifecycle state transition correctness.
- Permission gating for verification and payout.
- Distribution gating and idempotent verified-milestone publish behavior.
- Launch orchestration and repo provisioning boundaries.
- Persistence migration/versioning and backend selection boundaries.
- F_0 investor subscription caps and MVP bid/resolve treasury injection rules.

## Run
```powershell
cd o:\Foundups-Agent
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
python -m pytest modules/foundups/agent_market/tests -q
```

## Tranche 2 Focused Run
```powershell
cd o:\Foundups-Agent
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest `
  modules/foundups/agent_market/tests/test_persistence.py `
  modules/foundups/agent_market/tests/test_sqlite_adapter.py `
  modules/foundups/agent_market/tests/test_migrations.py `
  modules/foundups/agent_market/tests/test_repository_factory.py -q
```
