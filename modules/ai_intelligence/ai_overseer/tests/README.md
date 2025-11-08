# AI Overseer Tests

This directory hosts unit and integration tests for the AI Overseer module.

Structure:
- `TestModLog.md` – records test-suite changes (WSP 49 compliance).
- `conftest.py` – skips legacy Holo/Gemma witness suites unless explicitly requested.
- `test_analysis.py` – lightweight mission analysis helpers.
- `test_planning.py` – coordination planning helpers.
- `test_execution.py` – execution routing helpers.
- `test_mcp.py` – MCP enum smoke checks.
- `test_mixins_extended.py` – extended coverage for mixin fallbacks.
- `test_monitor_flow.py` – witness loop, gated behind an environment flag.

## Running Tests

By default the suite only runs quick mixin tests:

```
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest modules/ai_intelligence/ai_overseer/tests -q
```

### Opt-in Flags

- `AI_OVERSEER_WITNESS_LOOP=1` enables the heavy Holo/Gemma witness loop.
- `AI_OVERSEER_HEAVY_TESTS=1` re-enables the legacy full-stack regression files.

Keep these flags off for WSP 87-friendly quick runs; enable them when you intentionally want the full autonomous pipeline.***
