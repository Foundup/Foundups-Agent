# Stream Resolver Module Test Suite

This directory contains tests for the Stream Resolver module, which handles YouTube stream identification and metadata management.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_stream_resolver.py | Comprehensive tests for stream resolution, validation, and metadata retrieval |
| test_edge_cases.py | Tests for handling error conditions and edge cases like expired streams |
| test_video.py | Tests specific to video metadata extraction and validation |
| test_circuit_breaker.py | Tests for circuit breaker functionality, state transitions, and credential rotation integration |

## Test Coverage

The test suite achieves over 90% coverage of the Stream Resolver module code, in compliance with WSP 5 requirements.

## Running Tests

To run all tests for the Stream Resolver module:

```bash
python -m pytest modules/platform_integration/stream_resolver/stream_resolver/tests/
```

To run individual test files:
```bash
python modules/platform_integration/stream_resolver/stream_resolver/tests/test_circuit_breaker.py
```

To run with coverage reporting:

```bash
python -m pytest modules/platform_integration/stream_resolver/stream_resolver/tests/ --cov=modules.platform_integration.stream_resolver.stream_resolver.src --cov-report term-missing
```

## Recent Updates

* **Added circuit breaker testing** - Comprehensive tests for circuit breaker functionality including state transitions, failure thresholds, timeout recovery, and integration with credential rotation
* Enhanced test coverage to exceed the 90% WSP 5 threshold
* Added specific edge case handling tests
* Refactored tests to follow Windsurf Protocol standards 