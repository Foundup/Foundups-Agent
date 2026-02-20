# dae_daemon Tests

## Test Organization

Tests follow the 8-layer architecture — each layer tested independently before integration.

| Test | Layer | What it covers |
|------|-------|----------------|
| `test_schemas.py` | 0 | Enum values, dataclass serialization round-trips, deterministic IDs |
| Integration tests | 0-7 | Run via manual scripts (pytest has eth_typing conflict on Windows) |

## Running Tests

```bash
# Formal pytest (if eth_typing issue is resolved)
python -m pytest modules/infrastructure/dae_daemon/tests/ -v

# Manual execution (Windows-safe)
cd O:/Foundups-Agent
python -c "
import sys; sys.path.insert(0, '.')
from modules.infrastructure.dae_daemon.tests.test_schemas import *
# Run test classes manually
"
```

## Coverage Target

- Layer 0 (schemas): 100% — all enums, all dataclass fields, round-trips
- Layer 1 (event_store): Write, query, dedupe, parity, persistence
- Layer 2 (registry): Register, heartbeat, toggle, stale detection
- Layer 3 (killswitch): Severity thresholds, PID mock, report generation, popup alert
- Layer 4 (daemon): Singleton, lifecycle, event forwarding
- Layer 5 (adapter): Registration, heartbeat, event reporting, graceful no-ops
- Layer 6 (FAM integration): FAM standalone + reports to central daemon
- Layer 7 (dashboard): Renders, enable/disable toggles

## Notes

- SQLite holds file locks on Windows — use `gc.collect()` before temp dir cleanup
- Tests mock `ctypes.windll.user32.MessageBoxW` to avoid actual popup dialogs
