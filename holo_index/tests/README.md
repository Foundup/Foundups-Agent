# HoloIndex Tests

## Test Strategy (WSP 34)
- Focus on intent routing, output composition, and HoloDAE orchestration behavior.
- Keep unit tests deterministic; avoid external model/network dependencies.
- Integration tests run only when model assets are available and explicitly enabled.

## How to Run
- Unit tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest holo_index/tests`
- Focused: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest holo_index/tests/test_output_composer.py`

## Test Data
- Synthetic fixtures are preferred to keep tests fast and reproducible.
- Large-module fixtures are generated in temp dirs to avoid touching production files.

## Expected Behavior
- Intent classification produces stable, minimal output sections.
- OutputComposer trims noise and respects verbosity caps per intent.
- HoloDAE orchestration emits structured reports without flooding alerts.
- Video search health probe + metadata audit DB tests run without external deps.

## Integration Requirements
- Some integration tests require local model assets and may be skipped by default.
- When running integration tests, ensure the model cache is available on `E:/HoloIndex/models`.
