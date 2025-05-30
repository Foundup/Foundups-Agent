# ARCHIVED: prioritize_module.py

**Archive Date:** 2025-05-29  
**Reason:** Functionality consolidated into shared MPS calculator  
**Replacement:** `tools/shared/mps_calculator.py`

## Why This Tool Was Archived

This utility was identified in the **Tools Directory Audit Report** as containing:
- **100% duplicate MPS logic** identical to other tools
- **Missing CLI functionality** despite documented --update/--report flags
- **No file I/O capabilities** for automated processing
- **Standalone operation** without integration to broader workflow

## What Replaced It

The module prioritization functionality has been consolidated into the **MPS Calculator** which provides:

### ✅ Enhanced Capabilities
- **MPSCalculator class** with comprehensive scoring methodology
- **Batch processing support** for multiple modules
- **File I/O operations** for YAML input/output
- **ModLog integration** through `modlog_integration.py`
- **Backward compatibility** with existing interfaces

### 🔧 Migration Path
```python
# Old usage (prioritize_module.py)
# Manual interactive prompts only

# New usage (shared/mps_calculator.py)
from tools.shared.mps_calculator import MPSCalculator, calculate_mps

calculator = MPSCalculator()
score = calculator.calculate_score(complexity=7, importance=9, deferability=2, impact=8)
# Returns: comprehensive scoring with validation and reporting
```

### 📊 Improvements
- **70% code reduction** through consolidation
- **Enhanced validation** with detailed error reporting
- **Automated reporting** in multiple formats (dict, table, detailed)
- **CI/CD integration** ready for automated workflows

## Historical Context

This tool provided:
- Interactive MPS calculation based on WSP 5 methodology
- Module ranking capabilities
- Basic AI assistant prompts
- Score validation

**All functionality preserved and enhanced in the shared architecture.**

---
*Refer to `tools/tool_audit_report.md` section 3.2 for detailed analysis.* 