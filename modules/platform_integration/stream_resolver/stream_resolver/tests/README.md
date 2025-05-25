# Stream Resolver Module Test Suite

This directory contains tests for the Stream Resolver module, which handles YouTube stream identification and metadata management.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_stream_resolver.py | Comprehensive tests for stream resolution, validation, and metadata retrieval |
| test_edge_cases.py | Tests for handling error conditions and edge cases like expired streams |
| test_video.py | Tests specific to video metadata extraction and validation |

## Test Coverage

The test suite achieves over 90% coverage of the Stream Resolver module code, in compliance with WSP 5 requirements.

## Running Tests

To run all tests for the Stream Resolver module:

```bash
python -m pytest modules/stream_resolver/tests/
```

To run with coverage reporting:

```bash
python -m pytest modules/stream_resolver/tests/ --cov=modules.stream_resolver.src --cov-report term-missing
```

## Recent Updates

* Enhanced test coverage to exceed the 90% WSP 5 threshold
* Added specific edge case handling tests
* Refactored tests to follow Windsurf Protocol standards 