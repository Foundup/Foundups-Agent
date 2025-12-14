# Browser Actions - Test Documentation

**WSP Reference:** WSP 34 (Test Documentation)

## Test Strategy

Browser action testing uses:
1. Mock drivers for unit tests
2. Profile fixtures for session testing
3. Integration tests with real browsers (E2E)

## Test Files

| File | Purpose |
|------|---------|
| `test_action_router.py` | Router logic tests |
| `test_youtube_actions.py` | YouTube action tests |
| `test_linkedin_actions.py` | LinkedIn action tests |
| `test_x_actions.py` | X action tests |
| `test_autonomous_gemini_heart.py` | Gemini Vision element detection with existing Chrome |
| `test_final_autonomous_gemini.py` | Gemini Vision standalone infrastructure test |
| `test_gemini_studio_heart.py` | Gemini Vision YouTube Studio heart button test |
| `test_gemini_js_click.py` | Gemini Vision JavaScript click injection test |

## Running Tests

```bash
# Unit tests (mock drivers)
pytest modules/infrastructure/browser_actions/tests/ -v

# Integration tests (requires browser)
pytest modules/infrastructure/browser_actions/tests/ -v -m integration
```

## Test Data

- `fixtures/profiles/` - Mock browser profiles
- `fixtures/responses/` - Expected action responses

## Expected Behavior

- Router correctly classifies actions
- Platform actions execute successfully
- Fallback to Selenium works when UI-TARS unavailable



