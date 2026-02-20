# WSP Alignment: Cube SSE + Earnings UX

**Date**: 2026-02-12
**Status**: Implementation Complete
**WSP References**: WSP 50 (Pre-Action Verification), WSP 22 (ModLog), WSP 11 (API Stability)

## Summary

This document captures the alignment between the FoundUps cube animation frontend and the simulator event backend via Server-Sent Events (SSE).

## Architecture Overview

```
┌─────────────────┐     SSE Stream      ┌─────────────────────┐
│  foundup-cube.js │ ◄─────────────────  │  sse_server.py      │
│  (Frontend)      │   /api/sim-events   │  (FastAPI/Cloud Run)│
└─────────────────┘                      └─────────────────────┘
                                                  │
                                                  ▼
                                         ┌─────────────────────┐
                                         │  FAMDaemon          │
                                         │  (Event SSoT)       │
                                         └─────────────────────┘
```

## Event Flow

### SSE Server → Frontend

Events streamed via `GET /api/sim-events`:

| Event Type | Cube Behavior | Ticker Message |
|------------|---------------|----------------|
| `foundup_created` | `loop_started` | "new foundup #N starting..." |
| `task_state_changed` | `agent_spawned`, `block_filled`, `phase_changed` | Varies by status |
| `fi_trade_executed` | `sim_dex_trade` + $ pulse | "DEX: N F_i traded" |
| `investor_funding_received` | `sim_investor_funding` + $ pulse burst | "investor seed: X BTC" |
| `mvp_subscription_accrued` | `sim_mvp_subscription` | "subscription accrued: +N UPS" |
| `mvp_bid_submitted` | `sim_mvp_bid` + $ pulse | "MVP bid submitted: N UPS" |
| `mvp_offering_resolved` | `sim_mvp_resolved` + $ pulse burst | "MVP offering resolved: +N UPS treasury" |
| `milestone_published` | `dao_launched` | "Foundup_i MVP is Live!" |
| `payout_triggered` | $ pulse | (via block_filled) |

### Event Format

SSE server sends named events:
```
event: sim_event
id: <sequence_id>
retry: 3000
data: {"event_type": "...", "payload": {...}, "timestamp": "..."}
```

Frontend handles both:
- New format: `{event_type, payload, sequence_id}`
- Legacy format: `{type, data}` (backward compatible)

## Token Icon Standard

**MANDATORY**: Use `$` ASCII character for all token/earning indicators.

| Context | Character | Notes |
|---------|-----------|-------|
| Worker agent icon | `$` | Worker role indicator |
| Gold tokens | `$` | Floating earnings |
| Earning pulses | `$` | Economic event indicators |
| Ticker messages | `UPS` | Token denomination |
| Investor icon | `₿` | Bitcoin (investors only) |

**DO NOT USE**: 💰 🪙 💵 💲 or other emoji for token representation.

## Earning Pulse System

Random pulsing `$` indicators spawn around cube during economic events:

| Event | Pulse Count | Color |
|-------|-------------|-------|
| `payout_triggered` | 2-3 | Cyan `#00e5d0` |
| `fi_trade_executed` | 1-2 | Gold `#ffd700` |
| `investor_funding_received` | 3-5 (burst) | Gold `#ffd700` |
| `mvp_offering_resolved` | 4-6 (burst) | Pink `#ff4ea0` |
| `mvp_bid_submitted` | 1 | Purple `#7c5cfc` |
| Random (BUILDING phase) | 1 | Gold (0.8% chance/frame) |

Pulse characteristics:
- Lifetime: ~1.3s fade
- Scale: 0.6-1.0x with pulsing effect
- Drift: Slight upward + random direction
- Glow: 8px shadow blur

## Reconnection Strategy

Exponential backoff with jitter:

```javascript
reconnectDelay = min(30000, baseDelay * 1.5^attempts + random(0, 1000))
```

- Base delay: 2000ms
- Max delay: 30000ms
- Max attempts: 5
- Sequence deduplication on reconnect via `lastSequenceId`

## Files Modified

| File | Changes |
|------|---------|
| `modules/foundups/simulator/sse_server.py` | **NEW** - FastAPI SSE server |
| `public/js/foundup-cube.js` | Hardened event bridge, earning pulses |

## Deployment Notes

SSE server designed for Cloud Run deployment (like chat endpoint):

```bash
# Local development
cd modules/foundups/simulator
python sse_server.py --port 8080 --simulate

# Production
# Deploy to Cloud Run, update simBridge.endpoint in frontend
```

Environment variables:
- `PORT`: Server port (default: 8080)

## Testing

1. **SSE Server health**: `curl http://localhost:8080/api/health`
2. **SSE stream**: `curl -N http://localhost:8080/api/sim-events`
3. **Frontend**: Set `FLAGS.USE_SIM_EVENTS = true` in foundup-cube.js

## WSP Compliance

- **WSP 50**: Pre-action verification - checked existing patterns before implementation
- **WSP 22**: ModLog documentation - this file + module logs updated
- **WSP 11**: API stability - event format backward compatible with legacy

---

*0102 Pattern Memory: SSE + earning pulses for cube animation*
