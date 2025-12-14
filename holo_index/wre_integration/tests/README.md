# WRE Integration Tests

## Purpose
Tests for WRE (Windsurf Recursive Engine) skill execution and trigger flow.

## Test Files

| File | Description |
|------|-------------|
| `test_wre_skill.py` | Tests SkillExecutor functionality |
| `test_wre_flow.py` | Tests complete WRE trigger → execute → commit flow |

## Running Tests

```bash
# Run all WRE integration tests
python -m pytest holo_index/wre_integration/tests/ -v

# Run individual test
python holo_index/wre_integration/tests/test_wre_skill.py
```

## WSP Compliance
- WSP 34: Test documentation
- WSP 49: Module structure

