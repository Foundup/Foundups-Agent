# OpenClaw Skill Boundary Policy

## Purpose

Define hard separation between:
- Internal FoundUps `skillz` (trusted execution capabilities).
- OpenClaw workspace skills (operator-facing prompt/workflow surface).

This prevents prompt-surface drift from becoming an execution backdoor.

## Canonical Terms

- `skillz`: Module-local capabilities under `modules/**/skillz/` using `SKILLz.md`.
- OpenClaw workspace skills: Operator-facing skills under
  `modules/communication/moltbot_bridge/workspace/skills/**/SKILL.md`.

## Non-Negotiable Boundary Rules

1. OpenClaw workspace skills are orchestration/prompt artifacts only.
2. Execution logic must live in module code or internal `skillz` executors, never under `workspace/skills`.
3. Mutating OpenClaw routes (`command`, `system`, `schedule`, `social`, `automation`, `foundup`) must pass skill safety scan.
4. Scanner policy defaults are fail-closed:
   - `OPENCLAW_SKILL_SCAN_REQUIRED=1`
   - `OPENCLAW_SKILL_SCAN_ENFORCED=1`
5. OpenClaw workspace skills are never a dependency source for internal module execution.
6. Security failures must emit `openclaw_security_alert` via AI Overseer with dedupe.

## Allowed Data Flow

OpenClaw workspace skill -> OpenClaw DAE intent/router -> WRE/module execution -> result

## Prohibited Data Flow

OpenClaw workspace skill -> direct Python execution path in core modules

## Operational Safety Requirements

- Run scanner via `modules/communication/moltbot_bridge/src/skill_safety_guard.py`.
- Keep alerting enabled:
  - `OPENCLAW_SECURITY_PREFLIGHT=1`
  - `OPENCLAW_SECURITY_PREFLIGHT_ENFORCED=1`
  - `OPENCLAW_SECURITY_MONITOR_ENABLED=1`
- Use dedupe window for repeated failures:
  - `OPENCLAW_SECURITY_ALERT_DEDUPE_SEC` (default `900`)

## Troubleshooting Signals (AI Overseer)

Required fields for `openclaw_security_alert` events:
- `event`
- `severity`
- `source`
- `dedupe_key`
- `checked_at`
- `required`
- `enforced`
- `max_severity`
- `exit_code`
- `message`
- `report_path`
- `skills_dir`

These signals must be visible in daemon logs and routed to alert channels.
