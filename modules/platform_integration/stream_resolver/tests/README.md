# Stream Resolver Module Test Suite

This directory contains tests for the Stream Resolver module, which handles YouTube livestream discovery and metadata validation.

## Test Files
| Test File | Description |
|-----------|-------------|
| `test_stream_resolver.py` | Resolution flow, validation, metadata retrieval |
| `test_edge_cases.py` | Error conditions (expired streams, missing fields, 403/404) |
| `test_video.py` | Video detail validation and masking |
| `test_circuit_breaker.py` | Circuit breaker states, backoff, credential rotation |

## Running Tests
```bash
# Module-only
pytest modules/platform_integration/stream_resolver/tests/ -v

# With coverage
pytest modules/platform_integration/stream_resolver/tests/ \
  --cov=modules.platform_integration.stream_resolver.src --cov-report=term-missing
```

## WSP Compliance
- WSP 3: Platform integration domain
- WSP 34: Test docs and runnable commands present
- WSP 5: Target [GREATER_EQUAL]90% coverage
- WSP 49: Tests under module `tests/`
- WSP 50/64: No stray tests outside module; audited duplicates removed

## Recent Updates
- Added circuit breaker coverage (states, thresholds, reset) and credential rotation tests
- Corrected README paths/commands; consolidated suite execution alongside YouTube proxy
- Edge cases expanded; coverage maintained [GREATER_EQUAL]90% 