# INTERFACE - FoundUps Simulator

## Module Contract
FoundUps Simulator provides real-time event streaming via Server-Sent Events (SSE) for the cube visualization frontend, bridging FAMDaemon observability data to the web UI.

## CABR Canonical Intent
- CABR = Consensus-Driven Autonomous Benefit Rate (also referred to as Collective Autonomous Benefit Rate).
- WHY: CABR exists to power Proof of Benefit (PoB).
- HOW: Collective 0102 consensus determines CABR (consensus-driven process).
- RESULT: PoB drives protocol allocation/distribution; ROI is a downstream financial readout.

## Core Schemas

### SSE Event Envelope
```python
SSEEventEnvelope(
    event_id: str,           # Unique event identifier (from FAMDaemon or simulated)
    sequence_id: int,        # Monotonically increasing, gap-free for reconnect dedup
    event_type: str,         # One of STREAMABLE_EVENT_TYPES
    actor_id: str,           # Agent or system actor
    foundup_id: str | None,  # FoundUp context
    task_id: str | None,     # Task context (when applicable)
    payload: dict,           # Event-specific data
    timestamp: str,          # ISO8601 UTC timestamp
)
```

### STREAMABLE_EVENT_TYPES
```python
STREAMABLE_EVENT_TYPES = {
    "foundup_created",           # New FoundUp launched
    "task_state_changed",        # Task status transition
    "fi_trade_executed",         # DEX trade completed
    "order_placed",              # DEX order accepted
    "order_cancelled",           # DEX order cancelled
    "order_matched",             # DEX order matched/executed
    "price_tick",                # DEX ticker update
    "orderbook_snapshot",        # DEX depth snapshot
    "portfolio_updated",         # Wallet/portfolio update
    "investor_funding_received", # BTC investment received
    "mvp_subscription_accrued",  # Monthly UP$ accrued
    "subscription_allocation_refreshed",  # 012 subscription cycle refresh
    "subscription_cycle_reset",  # Monthly subscription reset
    "mvp_bid_submitted",         # Investor bid placed
    "mvp_offering_resolved",     # MVP offering completed
    "ups_allocation_executed",   # 0102 allocation batch execution
    "ups_allocation_result",     # Per-foundup allocation outcome
    "milestone_published",       # Distribution post published
    "proof_submitted",           # Work proof submitted
    "verification_recorded",     # Proof verified
    "payout_triggered",          # Token payout executed
    "demurrage_cycle_completed", # Decay redistribution summary
    "pavs_treasury_updated",     # pAVS/network balance update
    "treasury_separation_snapshot",  # System vs FoundUp treasury view
    "fi_rating_updated",         # F_i rating color gradient
    "cabr_score_updated",        # CABR 3V consensus score
}
```

### Event Payloads by Type
```python
# foundup_created
{"name": str, "token_symbol": str}

# task_state_changed
{"new_status": str, "task_id": str}
# Note: Uses 'new_status' key (not 'new_state') per frontend expectation

# fi_trade_executed
{"quantity": int, "price": float, "ups_total": float, "side": str}

# order_placed
{"order_id": str, "side": "buy" | "sell", "owner_id": str, "price": float, "quantity": float, "status": str}

# order_cancelled
{"order_id": str, "owner_id": str, "reason": str | null}

# order_matched
{"trade_id": str, "buyer_id": str, "seller_id": str, "price": float, "quantity": float, "ups_total": float}

# price_tick
{"last_price": float, "best_bid": float | null, "best_ask": float | null, "spread": float | null, "mid_price": float | null}

# orderbook_snapshot
{"best_bid": float | null, "best_ask": float | null, "spread": float | null, "mid_price": float | null, "bids": list, "asks": list}

# portfolio_updated
{"owner_id": str, "ups_balance": float, "fi_positions": dict}

# investor_funding_received
{"btc_amount": float, "source_foundup_id": str}

# mvp_subscription_accrued
{"added_ups": int}

# subscription_allocation_refreshed
{"human_id": str, "tier": str, "allocation_ups": float, "remaining_allocation_ups": float, "wallet_ups": float}

# subscription_cycle_reset
{"human_id": str, "tier": str, "cycles_per_month": int}

# mvp_bid_submitted
{"bid_ups": int}

# mvp_offering_resolved
{"total_injection_ups": int}

# ups_allocation_executed
{"human_id": str, "strategy": str, "ups_requested": float, "ups_executed": float, "fi_received": float, "success_count": int, "pending_count": int, "remaining_allocation_ups": float}

# ups_allocation_result
{"human_id": str, "path": str, "ups_allocated": float, "fi_received": float, "fee_paid": float, "order_id": str | null}

# proof_submitted
{"proof_type": str}

# payout_triggered
{"amount": int}

# demurrage_cycle_completed
{"wallets_affected": int, "total_decay_ups": float, "network_pool_delta_ups": float, "pavs_treasury_delta_ups": float}

# pavs_treasury_updated
{"pavs_treasury_balance_ups": float, "network_pool_balance_ups": float, "treasury_health": float}

# treasury_separation_snapshot
{"pavs_treasury_ups": float, "network_pool_ups": float, "fund_pool_ups": float, "foundup_ups_treasury": {str: float}}

# fi_rating_updated
{"rating": {"velocity": float, "traction": float, "health": float, "potential": float, "composite": float}, "border_color": str, "tier_name": str}

# cabr_score_updated
{"env_score": float, "soc_score": float, "part_score": float, "total": float, "threshold": float, "threshold_met": bool, "confidence": float}
```

## Service Contracts

### FrameSchema (animation adapter)

`modules/foundups/simulator/frame_schema.py` defines immutable snapshot contracts consumed by animation clients.

Top-level envelope:
```python
{
  "frame_schema_version": "1.0.0",
  "tick": int,
  "elapsed_seconds": float,
  "foundups": [...],
  "actors": [...],
  "pools": {...},
  "metrics": {...},
  "recent_events": [str]
}
```

Invariant:
- Animation consumers read frame fields only.
- Animation layer does not mutate simulator state or run economic logic.

### Pure-step shadow parity telemetry

`FoundUpsModel` supports an opt-in shadow parity gate (off by default) that runs
immutable `step_pure.step()` alongside runtime tick execution.

Config fields (`SimulatorConfig`):
- `pure_step_shadow_enabled: bool`
- `pure_step_shadow_log_interval: int`
- `pure_step_shadow_max_actor_drift: float`
- `pure_step_shadow_max_pool_drift: float`
- `pure_step_shadow_max_fi_drift: float`

Stats fields (`FoundUpsModel.get_stats()`):
- `pure_step_shadow_checks`
- `pure_step_shadow_failures`
- `pure_step_shadow_last_tick`
- `pure_step_shadow_last_ok`

Parity drift signal:
- Emits daemon event `pure_step_shadow_drift` when configured thresholds are exceeded.

### SSE Server Endpoints

#### GET /api/sim-events
Server-Sent Events stream for simulator/FAMDaemon events.

**Request:**
- Method: `GET`
- Headers: `Accept: text/event-stream`
- Member gate headers (when enabled):
  - `x-invite-key: <secret>` (or query `invite_key=...`)
  - `x-member-role: observer_012|member|agent_trader|admin` (or query `role=...`)

**Response:**
- Content-Type: `text/event-stream`
- Cache-Control: `no-cache`
- Connection: `keep-alive`
- X-Accel-Buffering: `no` (nginx SSE compatibility)

**Event Format:**
```
event: sim_event
id: <sequence_id>
retry: 3000
data: {"event_id": "...", "event_type": "...", "payload": {...}, ...}

```

**Special Events:**
- `event: connected` - Sent on connection with mode and heartbeat interval
- `event: heartbeat` - Sent every 15 seconds for connection keepalive
- `event: error` - Sent on internal server error

#### GET /api/health
Health check endpoint for Cloud Run readiness probes.

**Response:**
```json
{
    "status": "healthy",
    "mode": "simulated" | "live" | "live+simulator",
    "fam_connected": bool,
    "queue_size": int,
    "dropped_events": int,
    "timestamp": "ISO8601"
}
```

#### GET /
Root endpoint with API info.

**Response:**
```json
{
    "service": "FoundUps SSE Server",
    "version": "1.0.0",
    "endpoints": {
        "/api/sim-events": "SSE stream of simulator events",
        "/api/health": "Health check"
    }
}
```

### FAMEventSource
```python
FAMEventSource()
```

**Runtime API:**
- `connect() -> bool`: Connect to FAMDaemon singleton
- `disconnect() -> None`: Disconnect and cleanup
- `get_event(timeout: float = 1.0) -> dict | None`: Get next queued event
- `is_connected -> bool`: Connection status property

**Invariants:**
- Queue bounded to 1000 events (backpressure safety)
- Non-streamable event types filtered at source
- Graceful event drop on queue full (no exception, logged warning)
- Sequence IDs assigned atomically on queue entry

### SimulatedEventSource
```python
SimulatedEventSource()
```

**Runtime API:**
- `generate_event() -> dict | None`: Generate random simulated event

**Invariants:**
- Events generated at 0.5-2.0 second intervals
- Weighted distribution favoring task_state_changed (40%)
- Sequence IDs monotonically increasing
- Uses 'new_status' key for task_state_changed (frontend compatibility)

### BackgroundSimulator
```python
BackgroundSimulator(num_founders=3, num_users=10, tick_rate=2.0)
```

**Runtime API:**
- `start() -> bool`: Start Mesa simulator in background thread
- `stop() -> None`: Stop simulator gracefully (2s join timeout)
- `is_running -> bool`: Running status property

**Architecture:**
- Runs Mesa `FoundUpsModel` in a daemon thread
- Shares FAMDaemon singleton with SSE server (same process)
- Events flow: Mesa Model → FAMDaemon.emit() → FAMEventSource queue → SSE stream

**Invariants:**
- Background thread is daemon (dies with main process)
- Error in simulation loop sleeps 1s to prevent tight loop
- Graceful shutdown via `_running` flag + thread join

## Sequence ID Semantics

1. **Monotonic Ordering**: Sequence IDs are strictly increasing (no gaps)
2. **Reconnect Deduplication**: Client tracks `lastSequenceId` to skip already-processed events
3. **Heartbeat Exception**: Heartbeat events use `sequence_id: 0` (not counted)
4. **Source Isolation**: FAMEventSource and SimulatedEventSource maintain separate counters

## Heartbeat Protocol

- **Interval**: 15 seconds (`SSE_HEARTBEAT_INTERVAL`)
- **Purpose**: Keep connection alive through proxies/load balancers
- **Payload**: `{"timestamp": "ISO8601", "mode": "simulated"|"live"}`
- **Client Retry**: 3000ms (`SSE_RECONNECT_RETRY`)

## CORS Configuration

Allowed origins:
- `https://foundups.com` (production)
- `https://foundupscom.web.app` (Firebase preview)
- `https://foundupscom.firebaseapp.com` (Firebase hosting)
- `http://localhost:5000` (local dev)
- `http://127.0.0.1:5000` (local dev)

Allowed methods: `GET` only
Credentials: Allowed

## Backpressure Safety

**Queue Bounds:**
- `asyncio.Queue(maxsize=1000)` prevents unbounded memory growth
- On queue full: event dropped, warning logged
- Dropped event counter available via `_dropped_event_count` (observability)

**Client Reconnect:**
- Exponential backoff with jitter: `min(30000, base * 1.5^attempts + random(0, 1000))`
- Base delay: 2000ms
- Max delay: 30000ms
- Max attempts: 5

## Deployment

**Environment Variables:**
- `PORT`: Server port (default: 8080)
- `FAM_MEMBER_GATE_ENABLED`: `1` to enforce invite-only access on `/api/sim-events`
- `FAM_MEMBER_INVITE_KEY`: Shared invite key for member-gated endpoints
- `FAM_MEMBER_GATE_ALLOW_LOCAL_BYPASS`: `1` allows localhost bypass for dev
- `FAM_MEMBER_GATE_PROTECT_HEALTH`: `1` also gates `/api/health`
- `FAM_MEMBER_ALLOWED_ROLES`: Comma-separated role allowlist

**Modes:**
| Mode | Command | Description |
|------|---------|-------------|
| Simulated | `--simulate` | Random fake events (demo/fallback) |
| Live | (default) | Connects to existing FAMDaemon |
| Live+Simulator | `--run-simulator` | Mesa model in-process, real events |

**Local Development:**
```bash
# Simulated events (no dependencies)
python -m modules.foundups.simulator.sse_server --simulate

# Live simulator → SSE → Web Animation
python -m modules.foundups.simulator.sse_server --run-simulator -v

# Custom simulator config
python -m modules.foundups.simulator.sse_server -r --founders 5 --users 20 --speed 4.0
```

**Web Animation Integration:**
```
http://localhost:5000?sim=1        # Firebase local dev with SSE
public/index.html?sim=1           # Direct file with SSE
public/index.html?sse_url=<url>   # Custom SSE endpoint
```

**Cloud Run Configuration:**
- Designed for Cloud Run deployment (like chat endpoint)
- Long-lived connections supported
- X-Accel-Buffering disabled for nginx compatibility
- Deploy: `./deploy-sse.sh`

**Production:**
```bash
python sse_server.py --run-simulator --port $PORT
```

## Frontend Integration

**Event Bridge Configuration:**
```javascript
const simBridge = {
    endpoint: '/api/sim-events',  // Cloud Run URL in production
    reconnectDelay: 2000,
    maxReconnectAttempts: 5,
    lastSequenceId: 0,  // Track for dedup on reconnect
};
```

**Event Handling:**
```javascript
// Handles both new format and legacy format
function handleSimulatorEvent(simEvent) {
    const eventType = simEvent.event_type || simEvent.type;
    const eventData = simEvent.payload || simEvent.data || {};
    // ...
}
```

## WSP References

- **WSP 50**: Pre-action verification (event deduplication)
- **WSP 22**: ModLog documentation
- **WSP 11**: API stability (backward-compatible event format)
- **WSP 72**: Module independence (SSE server standalone)
