# WSP Tools Module

**Domain**: development
**Purpose**: Tools for WSP protocol maintenance, enforcement, and bulk operations

## Overview

This module provides utilities for maintaining WSP compliance across the codebase, including bulk fix scripts and validation tools.

## Scripts

### fix_wsp90_utf8_bulk.py

Bulk fix script for WSP 90 UTF-8 wrapping deduplication.

**Problem Solved**: 379 modules incorrectly copy-pasted the UTF-8 wrapping pattern, causing "lost sys.stderr" errors when multiple modules re-wrap on import.

**Usage**:
```bash
# Preview changes (safe)
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --dry-run

# Apply fixes to non-entrypoint files (safe default)
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --apply

# Include entrypoint files (review carefully first)
python modules/development/wsp_tools/scripts/fix_wsp90_utf8_bulk.py --apply --include-entrypoints
```

**Modes**:
| Mode | Files Affected | Risk |
|------|---------------|------|
| Default (non-entrypoint) | ~78 | Low - library modules |
| --include-entrypoints | ~155 additional | Medium - may need wrapping if run standalone |

## WSP References

- WSP 90: UTF-8 Encoding Enforcement Protocol
- WSP 50: Pre-Action Verification
- WSP 49: Module Structure Protocol

## Architecture

```
wsp_tools/
├── README.md           # This file
├── ModLog.md           # Change history
├── scripts/
│   ├── fix_wsp90_utf8_bulk.py   # WSP 90 bulk fix
│   └── ...
└── src/
    └── wsp90_orchestrator.py    # WSP 90 validation
```
