# Tests — Whack-a-Magat DAE

Run unit tests:
```bash
pytest modules/gamification/tests/test_whack.py -q
```

Coverage target: [GREATER_EQUAL]90% for `whack.py`.

## Test Scripts

- **`check_magadoom_leaders.py`** - Quick utility to check MAGADOOM HGS leaderboard and MOD leaders

Notes:
- Tests are platform-agnostic; adapters are validated separately with mocks.
