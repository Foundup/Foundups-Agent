# TestModLog - shared tests

## 2026-03-08: Markdown sanitizer coverage

- Command: `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'; pytest -q tests/test_markdown_sanitizer.py`
- Status: PASS
- Result: `2 passed, 2 warnings`
- Notes:
  - Validates ASCII-safe replacements for arrows, dashes, star, and check glyphs.
  - Confirms recursive sanitization across nested Python containers.
