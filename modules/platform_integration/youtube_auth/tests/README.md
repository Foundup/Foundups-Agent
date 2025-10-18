# YouTube Auth Module Test Suite

This directory contains tests for the YouTube Auth module, which handles OAuth2 authentication and channel info retrieval for YouTube.

## Test Files
| Test File | Description |
|-----------|-------------|
| `test_youtube_auth.py` | OAuth2 flow, token storage/refresh, service creation |
| `test_channel.py` | Channel info retrieval/validation |
| `test_youtube_auth_coverage.py` | Coverage-focused scenarios |

## Running Tests
```bash
# Module-only
pytest modules/platform_integration/youtube_auth/tests/ -v

# With coverage
pytest modules/platform_integration/youtube_auth/tests/ \
  --cov=modules.platform_integration.youtube_auth.src --cov-report=term-missing
```

## WSP Compliance
- WSP 3: Platform integration domain
- WSP 34: Test docs and runnable commands present
- WSP 5: Target [GREATER_EQUAL]90% coverage
- WSP 49: Tests under module `tests/`
- WSP 50/64: No stray tests; suite audited 