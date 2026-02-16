# OpenClaw Bridge Interface

## Public API

### WebhookReceiver

```python
from modules.communication.moltbot_bridge.src.webhook_receiver import app

# FastAPI app exposing:
# POST /webhook/openclaw - Receives messages from OpenClaw Gateway
# POST /webhook/moltbot - Legacy endpoint (compat)
# GET /health - Health check endpoint
```

### Message Format (Inbound from OpenClaw)

```python
class MoltbotMessage(BaseModel):
    message: str                    # User's message text
    sessionKey: str                 # Session identifier
    channel: str                    # Source channel (whatsapp, telegram, etc.)
    sender: str                     # Sender identifier
    metadata: dict = {}             # Additional context

# OpenClawMessage is an alias of MoltbotMessage (preferred naming)
```

### Response Format (Outbound to OpenClaw)

```python
class FoundupsResponse(BaseModel):
    text: str                       # Response text
    deliver: bool = True            # Whether OpenClaw should deliver response
    channel: str | None = None      # Override delivery channel
    to: str | None = None           # Override recipient
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FOUNDUPS_WEBHOOK_TOKEN` | Yes | Shared secret with OpenClaw |
| `OPENCLAW_GATEWAY_URL` | No | OpenClaw gateway (default: ws://127.0.0.1:18789) |
| `MOLTBOT_GATEWAY_URL` | No | Legacy name (fallback) |

## Auth Headers

- `Authorization: Bearer <token>`
- `x-openclaw-token: <token>` (preferred)
- `x-moltbot-token: <token>` (legacy)

### OpenClaw DAE (Frontal Lobe)

```python
from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE

dae = OpenClawDAE(repo_root=Path("O:/Foundups-Agent"))

# Full autonomy loop:
# Ingress -> Intent -> Preflight -> Plan -> Permission -> Execute -> Validate -> Remember
response = await dae.process(
    message="What is the WRE orchestrator?",
    sender="user123",
    channel="telegram",
    session_key="session-id",
    metadata={},
)
```

### Intent Categories

| Category | Route | Permission | Description |
|----------|-------|------------|-------------|
| QUERY | holo_index | ADVISORY | Read-only search/lookup |
| COMMAND | wre_orchestrator | DOCS_TESTS+ | Execute tasks via WRE |
| MONITOR | ai_overseer | ADVISORY | System status/health |
| SCHEDULE | youtube_shorts_scheduler | METRICS | Time-bound scheduling |
| SOCIAL | communication | METRICS | Engagement (comment/post) |
| SYSTEM | infrastructure | SOURCE | System admin (commander only) |
| AUTOMATION | auto_moderator_bridge | METRICS | YouTube automation routing |
| FOUNDUP | fam_adapter | METRICS | FoundUp launch and FAM workflows |
| CONVERSATION | digital_twin | ADVISORY | Casual dialogue |

### FOUNDUP Route Contract (FAM Adapter)

- Launch command examples:
  - `launch foundup <name> with token <SYMBOL>`
  - `create foundup <name> token <SYMBOL>`
- Token symbol resolution:
  - If token is omitted, parser auto-generates from FoundUp name.
  - If token is `AUTO` (or legacy `FUP` seed), adapter auto-generates and resolves collisions.
  - Collision resolution is deterministic (`BASE`, `BASE2`, `BASE3`, ...), then handed to Agent Market.

### Autonomy Tiers (Graduated)

| Tier | Who | Can Do |
|------|-----|--------|
| ADVISORY | Anyone | Read-only: search, status, chat |
| METRICS | Commander | + Write metrics/logs |
| DOCS_TESTS | Commander | + Edit tests and docs |
| SOURCE | Commander (explicit) | + Edit source code |

### WSP 73 Partner-Principal-Associate

- **Partner**: OpenClaw bridge receives intent, owns dialogue
- **Principal**: OpenClaw DAE decomposes tasks, selects domain DAEs
- **Associates**: Domain DAEs execute (communication, platform, dev, content)

### Security

- Non-commanders: ADVISORY only (no mutations)
- COMMAND/SYSTEM intents blocked for non-commanders (WSP 50)
- Cisco skill scanner preflight runs before mutating/skill-driven routes:
  `command`, `system`, `schedule`, `social`, `automation`, `foundup`
- Secret patterns (AIza*, sk-*, oauth_token*) redacted from output
- All decisions logged to WRE pattern memory (WSP 22)
- Skill boundary policy (workspace skills vs internal `skillz`) is codified in:
  `modules/communication/moltbot_bridge/docs/SKILL_BOUNDARY_POLICY.md`
- MONITOR responses include OpenClaw skill safety gate state:
  - status, required/enforced, last check timestamp, and gate message.

### Skill Safety Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_SKILL_SCAN_REQUIRED` | No | `1` fail-closed if scanner missing (default) |
| `OPENCLAW_SKILL_SCAN_ENFORCED` | No | `1` block risky scans above threshold (default) |
| `OPENCLAW_SKILL_SCAN_MAX_SEVERITY` | No | Scanner threshold (default `medium`) |
| `OPENCLAW_SKILL_SCAN_TTL_SEC` | No | Cached scan TTL in seconds (default `900`) |

### Rate Limiting (Webhook)

Token bucket rate limiting per sender and channel (WSP 95 defense-in-depth):

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENCLAW_RATE_LIMITING_ENABLED` | No | `0` to disable rate limiting (default `1`) |
| `OPENCLAW_RATE_SENDER_PER_SEC` | No | Tokens/sec per sender (default `2.0`) |
| `OPENCLAW_RATE_SENDER_BURST` | No | Burst capacity per sender (default `10.0`) |
| `OPENCLAW_RATE_CHANNEL_PER_SEC` | No | Tokens/sec per channel (default `5.0`) |
| `OPENCLAW_RATE_CHANNEL_BURST` | No | Burst capacity per channel (default `20.0`) |

When limits exceeded, webhook returns HTTP 429 with `X-Retry-After` header.

```python
from modules.communication.moltbot_bridge.src.webhook_receiver import WebhookRateLimiter

limiter = WebhookRateLimiter()
allowed, bucket_type = limiter.check_allowed(sender="user123", channel="telegram")
# Returns (True, None) if allowed, or (False, "sender"|"channel") if blocked
```

### SOURCE Tier Permission Check

SOURCE tier operations require explicit permission via AgentPermissionManager (fail-closed):

```python
from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE

dae = OpenClawDAE()
granted, reason = dae._check_source_permission(intent)
# granted=False, reason="permission manager unavailable" if manager missing
# granted=False, reason=<agent_permission_manager reason> if denied
# granted=True, reason="granted" if allowed
```

Permission denied events emitted with 60s dedupe window (WSP 71 forensics).

### COMMAND Graceful Degradation

When WRE is unavailable, COMMAND intents return deterministic advisory fallback:

```python
# Returns advisory with:
# - "Advisory Mode" header
# - Command recognition
# - Three actionable options (CLI, retry, query mode)
# - Optional error detail
```

## WSP Compliance

- **WSP 46**: WRE Protocol (execution cortex)
- **WSP 49**: Standard module structure
- **WSP 50**: Pre-Action Verification (preflight gate)
- **WSP 73**: Digital Twin architecture integration
- **WSP 77**: Agent coordination (4-phase execution)
- **WSP 91**: Observability (structured logging)
- **WSP 96**: Skill execution (micro chain-of-thought)
