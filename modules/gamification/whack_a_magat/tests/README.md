# Tests — Whack-a-Magat DAE

Run unit tests:
```bash
pytest modules/gamification/tests/test_whack.py -q
```

Coverage target: ≥90% for `whack.py`.

Notes:
- Tests are platform-agnostic; adapters are validated separately with mocks.
