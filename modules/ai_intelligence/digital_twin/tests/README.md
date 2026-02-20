# Digital Twin Tests

## Test Strategy (WSP 34)
- Keep unit tests deterministic; avoid external model/network dependencies.
- Use mock LLM paths or local fixtures for repeatable outputs.
- Validate core pipeline stages: memory → draft → guardrails → decision.

## How to Run
- All tests: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest modules/ai_intelligence/digital_twin/tests`
- Focused: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest modules/ai_intelligence/digital_twin/tests/test_comment_drafter.py`

## Test Data
- Use minimal fixtures embedded in tests or small local JSON snippets.
- Avoid using production corpora in unit tests.

## Expected Behavior
- Comment drafting returns structured `CommentDraft` with bounded length.
- Guardrails strip fillers and report violations consistently.
- Decision policy respects thresholds and cooldown logic.

## Integration Requirements
- Some tests may require optional dependencies (faiss, sentence-transformers).
- When optional deps are missing, tests should fall back to TF‑IDF paths.
