# Youtube Proxy Tests

## Overview
WSP-compliant tests for the `youtube_proxy` orchestrator, covering cross-domain wiring (auth, stream resolution, chat, AI) and error handling.

## Test Files
| Test File | Purpose | Coverage Area |
|-----------|---------|---------------|
| `test_youtube_proxy.py` | Orchestrator behaviors and wiring | Component init, status, interactive mode |

## Related YouTube Suite
This module is validated alongside:
- `platform_integration/stream_resolver/tests/`
- `platform_integration/youtube_auth/tests/`
- `communication/livechat/tests/`

## Running Tests
```bash
# Module-only
pytest modules/platform_integration/youtube_proxy/tests/ -v

# Full YouTube suite (proxy + resolver + auth + livechat)
pytest \
  modules/platform_integration/youtube_proxy/tests/ \
  modules/platform_integration/stream_resolver/tests/ \
  modules/platform_integration/youtube_auth/tests/ \
  modules/communication/livechat/tests/ -v

# Coverage for orchestrator
pytest modules/platform_integration/youtube_proxy/tests/ \
  --cov=modules.platform_integration.youtube_proxy.src --cov-report=term-missing
```

## WSP Compliance
- WSP 3: Functional domain alignment (platform_integration)
- WSP 34: Test docs present; suite runnable commands included
- WSP 5: Target ≥90% coverage; tracked in TestModLog
- WSP 49: Tests under module tests/
- WSP 50/64: No test file creation outside module; audited for duplicates

## Test Categories
1. Orchestrator initialization and DI wiring
2. Standalone interactive flow and status reporting
3. Error handling, fallbacks, and mock component activation
4. Logging and component health aggregation

## Notes
- Duplicates removed in suite; tests consolidated per WSP 49
- Stream discovery logic validated in `stream_resolver` module tests
