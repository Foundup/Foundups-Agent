# Moltbot Bridge Interface

## Public API

### WebhookReceiver

```python
from modules.communication.moltbot_bridge.src.webhook_receiver import app

# FastAPI app exposing:
# POST /webhook/moltbot - Receives messages from Moltbot Gateway
# GET /health - Health check endpoint
```

### Message Format (Inbound from Moltbot)

```python
class MoltbotMessage(BaseModel):
    message: str                    # User's message text
    sessionKey: str                 # Session identifier
    channel: str                    # Source channel (whatsapp, telegram, etc.)
    sender: str                     # Sender identifier
    metadata: dict = {}             # Additional context
```

### Response Format (Outbound to Moltbot)

```python
class FoundupsResponse(BaseModel):
    text: str                       # Response text
    deliver: bool = True            # Whether Moltbot should deliver response
    channel: str | None = None      # Override delivery channel
    to: str | None = None           # Override recipient
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `FOUNDUPS_WEBHOOK_TOKEN` | Yes | Shared secret with Moltbot |
| `MOLTBOT_GATEWAY_URL` | No | Moltbot gateway (default: ws://127.0.0.1:18789) |

## WSP Compliance

- **WSP 49**: Standard module structure
- **WSP 73**: Digital Twin architecture integration
- **WSP 77**: Agent coordination (routes to AI Overseer)
