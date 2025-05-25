# YouTube Auth Module Test Suite

This directory contains tests for the YouTube Auth module, which handles authentication with the YouTube API via OAuth2.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_youtube_auth.py | Comprehensive tests for OAuth2 authentication flow, token management, and service creation |
| test_channel.py | Tests specific to channel information retrieval and validation |

## Test Coverage

The test suite aims to maintain high coverage of the YouTube Auth module code in compliance with WSP 5 requirements.

## Running Tests

To run all tests for the YouTube Auth module:

```bash
python -m pytest modules/youtube_auth/tests/
```

To run with coverage reporting:

```bash
python -m pytest modules/youtube_auth/tests/ --cov=modules.youtube_auth.src --cov-report term-missing
```

## Test Documentation Standards

In accordance with WSP requirements, this README.md serves as documentation for the test suite. It is maintained and updated whenever significant changes are made to the test suite. 