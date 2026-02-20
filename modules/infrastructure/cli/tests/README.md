# CLI Module Tests

## Test Coverage

Tests for CLI module functionality.

## Running Tests

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest modules/infrastructure/cli/tests/ -v
```

## Test Files

- `test_utilities.py` - Tests for utility functions
- `test_menu_handlers.py` - Tests for menu routing
- `test_follow_wsp_menu.py` - Tests for follow-WSP menu wiring and gate result handling
