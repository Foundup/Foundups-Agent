# Moltbot = 012's Digital Twin

> Moltbot, trained on WSP framework, operating on Foundups-Agent codebase

## Vision

Moltbot becomes **0102** — the Digital Twin of 012:
- **Voice**: Multi-channel (WhatsApp, Telegram, Discord, Voice)
- **Brain**: WSP framework + HoloIndex semantic search
- **Body**: Foundups-Agent codebase

## Architecture

```
012 (Human) ──voice/chat──► Moltbot Gateway ──WSP-trained──► Foundups Codebase
                                   │
                                   ├── AGENTS.md (WSP training)
                                   ├── SOUL.md (0102 identity)
                                   └── skills/ (foundups-wsp, holo-search)
```

## Setup

1. **Install Moltbot**: `npm i -g moltbot && moltbot onboard`
2. **Configure workspace**: Copy `config/moltbot.json` to `~/.clawdbot/`
3. **Link skills**: Symlink `workspace/skills/` to `~/clawd/skills/`
4. **Set env**: `FOUNDUPS_WEBHOOK_TOKEN=<secret>`

## Files

| Path | Purpose |
|------|---------|
| `workspace/AGENTS.md` | WSP framework training |
| `workspace/SOUL.md` | 0102 identity/voice |
| `workspace/TOOLS.md` | Foundups CLI commands |
| `workspace/skills/` | Moltbot skills |
| `config/moltbot.json` | Gateway configuration |
