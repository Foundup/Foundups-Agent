# OAuth Management Module Test Suite

This directory contains tests for the OAuth Management module, which handles YouTube API credential management, rotation, and authentication.

## Test Files

| Test File | Description |
|-----------|-------------|
| test_credential_rotation.py | Tests for credential rotation functionality and quota handling |
| test_oauth_rotation_validation.py | Comprehensive WSP-compliant OAuth token rotation validation tests |
| test_optimizations.py | Tests for performance optimizations and circuit breaker functionality |
| show_credential_mapping.py | Utility script to display current credential status and mapping |

## Test Coverage

The test suite covers:
- Credential rotation across multiple OAuth sets
- Quota exceeded detection and handling
- Authentication service fallback mechanisms
- API quota management and cooldown functionality

## Running Tests

To run all tests for the OAuth Management module:

```bash
python -m pytest modules/infrastructure/oauth_management/oauth_management/tests/
```

To run individual test files:
```bash
python modules/infrastructure/oauth_management/oauth_management/tests/test_credential_rotation.py
python modules/infrastructure/oauth_management/oauth_management/tests/test_oauth_rotation_validation.py
```

## Test Logs

Test execution logs are stored in the `logs/` directory for audit and debugging purposes.

## Recent Updates

* Added comprehensive OAuth token rotation validation testing
* Enhanced credential rotation tests with quota management
* Implemented WSP-compliant test structure and documentation 