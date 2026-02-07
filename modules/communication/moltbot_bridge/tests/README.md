# Tests - OpenClaw Bridge

## Coverage Goals
- Intent classification and routing behavior.
- WSP preflight + permission gates.
- End-to-end `process()` safety fallbacks.
- Cisco skill scanner guard behavior.
- Skill boundary policy enforcement (workspace skills vs internal `skillz`).
- SOURCE tier permission enforcement (AgentPermissionManager).
- Webhook rate limiting (token bucket per sender/channel).
- COMMAND graceful degradation (WRE unavailable fallback).

## Run
```powershell
cd o:\Foundups-Agent
.\modules\communication\moltbot_bridge\tests\run_tests.ps1
```

CI gate behavior:
- Runs security tests first and fails fast if any fail:
  - `test_skill_boundary_policy.py`
  - `test_skill_safety_guard.py`
  - `test_hardening_tranche.py`
- Use `-SkipSecurityGate` only for local diagnostics (never for CI/prod).

Optional custom args:
```powershell
.\modules\communication\moltbot_bridge\tests\run_tests.ps1 -PytestArgs @("-q", "-k", "skill_safety")
```
