# WSP Core Module Interface

## Public API

### Core Classes

#### `WSPValidator`
Core validation engine for WSP protocol compliance.

**Methods:**
- `validate_module(module_path: str) -> ValidationResult` - Validate module structure per WSP 49
- `check_compliance(wsp_number: int, context: Dict) -> bool` - Check specific WSP compliance
- `get_violations(module_path: str) -> List[Violation]` - Get all WSP violations for a module

#### `WSPEnforcer`
Protocol enforcement system.

**Methods:**
- `enforce_pre_action(action: str, context: Dict) -> bool` - WSP 50 pre-action verification
- `prevent_violation(wsp_number: int, action: str) -> bool` - WSP 64 violation prevention
- `record_violation(violation: Violation) -> None` - Record violation for learning

## Usage Example

```python
from modules.infrastructure.wsp_core import WSPValidator, WSPEnforcer

# Validate module structure
validator = WSPValidator()
result = validator.validate_module("modules/communication/livechat")
if not result.is_valid:
    for violation in result.violations:
        print(f"WSP {violation.wsp_number} violation: {violation.description}")

# Enforce pre-action verification
enforcer = WSPEnforcer()
if enforcer.enforce_pre_action("create_module", {"path": "modules/new_module"}):
    # Safe to proceed
    pass
```

## Dependencies
- Core Python libraries only (no external dependencies)

## WSP Compliance
Interface compliant with WSP 11 (Public Interface Documentation)