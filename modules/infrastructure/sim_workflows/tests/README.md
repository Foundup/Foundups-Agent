# tests — sim_workflows (WSP 34)

## Test Strategy
- Unit tests for:
  - HTTP client happy-path and error-path via httpx mocking
  - Socket.io bridge event wiring via socketio test server or monkeypatch
  - Webhook signature verification edge cases

## How to Run
```bash
pytest modules/infrastructure/sim_workflows/tests -q
```

## Test Data
- Synthetic JSON payloads for `flow-status`, `flow-log`, `flow-error`
- HMAC fixtures for positive/negative signature checks

## Expected Behavior
- Client raises on non-2xx
- Bridge forwards events to registered handlers
- Signature verification is timing-safe and rejects malformed inputs

## Integration Requirements
- None at unit level; Sim service not required for unit tests
