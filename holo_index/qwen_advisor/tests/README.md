# Qwen Advisor Tests

## Purpose
Tests for HoloDAECoordinator and related services.

## Test Files

| File | Description |
|------|-------------|
| `verify_holodae_final.py` | Final HoloDAE verification (services, WRE) |
| `verify_holodae_wiring.py` | Monitoring and search flow verification |
| `verify_wiring_complete.py` | WSP 62 service wiring verification |

## Running Tests

```bash
# Run verification scripts
python holo_index/qwen_advisor/tests/verify_wiring_complete.py

# Run all tests
python -m pytest holo_index/qwen_advisor/tests/ -v
```

## WSP Compliance
- WSP 34: Test documentation
- WSP 49: Module structure
- WSP 62: Modularity enforcement verification

