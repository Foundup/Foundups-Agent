# OpenClaw Bridge = 012's Digital Twin

> **OpenClaw** (formerly Moltbot/Clawdbot), trained on WSP framework, operating on Foundups-Agent codebase

## Version Note

| Date | Name | Package |
|------|------|---------|
| Jan 30, 2026 | **OpenClaw** (current) | `openclaw` |
| Jan 27, 2026 | Moltbot | `moltbot` |
| Pre-2026 | Clawdbot | `clawdbot` |

## Vision

OpenClaw becomes **0102** — the Digital Twin of 012:
- **Voice**: Multi-channel (WhatsApp, Telegram, Discord, Voice)
- **Brain**: WSP framework + HoloIndex semantic search
- **Body**: Foundups-Agent codebase

## Architecture

```
012 (Human) ──voice/chat──► OpenClaw Gateway ──WSP-trained──► Foundups Codebase
                                   │
                                   ├── AGENTS.md (WSP training)
                                   ├── SOUL.md (0102 identity)
                                   └── skills/ (foundups-wsp, holo-search)
```

## Setup

> ⚠️ **Important**: See [docs/INSTALL_OPENCLAW.md](docs/INSTALL_OPENCLAW.md) for full guide

1. **Install Node.js in WSL**: Required first! (not Windows Node)
2. **Install OpenClaw**: `npm i -g openclaw && openclaw onboard`
3. **Configure workspace**: Point to this module's `workspace/` directory
4. **Set env**: `DISCORD_BOT_TOKEN`, `FOUNDUPS_WEBHOOK_TOKEN`

## Files

| Path | Purpose |
|------|---------|
| `workspace/AGENTS.md` | WSP framework training |
| `workspace/SOUL.md` | 0102 identity/voice |
| `workspace/TOOLS.md` | Foundups CLI commands |
| `workspace/skills/` | OpenClaw skills |
| `config/moltbot.json` | Legacy sample config (OpenClaw uses `~/.openclaw/openclaw.json`) |

## Skill Safety Gate (Cisco Skill Scanner)

OpenClaw DAE now runs a cached safety preflight on local skills before mutating routes
(`command`, `system`, `schedule`, `social`, `automation`, `foundup`).

- Scanner package: `cisco-ai-skill-scanner`
- CLI: `skill-scanner`
- Skills path scanned: `modules/communication/moltbot_bridge/workspace/skills`
- Report path: `modules/communication/moltbot_bridge/reports/openclaw_skill_scan_report.json`

Environment toggles:
- `OPENCLAW_SKILL_SCAN_REQUIRED=1` (default): fail closed if scanner missing
- `OPENCLAW_SKILL_SCAN_ENFORCED=1` (default): block risky scans above threshold
- `OPENCLAW_SKILL_SCAN_MAX_SEVERITY=medium` (default)
- `OPENCLAW_SKILL_SCAN_TTL_SEC=900` (default cache window)

## Skill Boundary Policy

OpenClaw workspace skills and internal `skillz` are intentionally separated.

- Policy: `docs/SKILL_BOUNDARY_POLICY.md`
- OpenClaw workspace skills: `workspace/skills/**/SKILL.md` (operator workflow layer)
- Internal execution skillz: `modules/**/skillz/**/SKILLz.md` (trusted module layer)

## Security Hardening

### SOURCE Tier Permission Check
SOURCE tier operations (code edits) require explicit permission via AgentPermissionManager.
Fail-closed: blocked if manager unavailable or check fails. Permission denied events emitted with 60s dedupe.

### Webhook Rate Limiting
Token bucket rate limiting per sender and channel (defense-in-depth):
- `OPENCLAW_RATE_LIMITING_ENABLED=1` (default)
- `OPENCLAW_RATE_SENDER_PER_SEC=2.0` / `OPENCLAW_RATE_SENDER_BURST=10.0`
- `OPENCLAW_RATE_CHANNEL_PER_SEC=5.0` / `OPENCLAW_RATE_CHANNEL_BURST=20.0`

Returns HTTP 429 with `X-Retry-After` when exceeded.

### COMMAND Graceful Degradation
When WRE is unavailable, COMMAND intents return deterministic advisory fallback with:
- Advisory Mode header
- Command recognition
- Three actionable options (CLI, retry, query mode)
