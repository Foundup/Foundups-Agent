# Tests (WSP 34)

## Test strategy

- **Smoke + unit**: fast checks for internal helpers (randomness gates, snapshot writer, deterministic mode).
- **UI automation**: Selenium/UI-TARS tests exist in module test folders and are run manually when a logged-in Studio session is available.

## How to run

Some environments have third-party pytest plugins that break collection. Run with plugin autoload disabled:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest -q
```

Run only the new gating/randomness tests:

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
pytest -q tests/test_comment_randomness.py tests/test_human_behavior_randomness.py
```

## Expected behavior validated by these tests

- **Dynamic randomness**: probabilities remain bounded in \([0,1]\), and fixed mode returns the base bias.
- **Pre-action snapshots**: screenshot + JSON metadata are written to a configurable directory.
- **Fixed randomness extremes**: probability 0 always skips, probability 1 always performs.

