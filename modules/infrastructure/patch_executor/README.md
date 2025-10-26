# Patch Executor

**Domain**: Infrastructure
**Purpose**: Safe git patch application with allowlist enforcement for autonomous code fixes
**WSP Compliance**: WSP 3 (Module Organization), WSP 49 (Module Structure), WSP 77 (Agent Coordination)

## Overview

PatchExecutor provides safe, autonomous code modification via git patches with multi-layer safety enforcement. Enables autonomous agents to apply code fixes while maintaining security and architectural integrity.

## Key Features

- **3-Layer Safety**: Allowlist validation + `git apply --check` + `git apply`
- **Allowlist Enforcement**: File patterns, forbidden operations, patch size limits
- **Dry-Run Validation**: Test patches before application
- **Structured Results**: Returns metrics-compatible results for tracking
- **Rollback Capability**: Full git history maintained

## Safety Guarantees

1. **File Allowlist**: Only files matching glob patterns can be modified
2. **Operation Blocking**: Prevents deletions, renames, binary changes, submodule updates
3. **Size Limits**: Max patch size enforcement
4. **Dry-Run**: `git apply --check` validates before actual modification
5. **Git History**: All changes tracked in git for easy rollback

## Usage

```python
from pathlib import Path
from modules.infrastructure.patch_executor.src.patch_executor import PatchExecutor, PatchAllowlist

# Configure allowlist
allowlist = PatchAllowlist(
    allowed_file_patterns=[
        "modules/**/*.py",     # All Python modules
        "holo_index/**/*.py"   # HoloIndex Python files
    ],
    forbidden_operations={
        'delete_file',
        'binary_change',
        'submodule_change',
        'rename_file'
    },
    max_patch_lines=200
)

# Initialize executor
executor = PatchExecutor(
    repo_root=Path("."),
    allowlist=allowlist
)

# Apply patch
result = executor.apply_patch(
    patch_content=patch_diff,
    patch_description="Add UTF-8 header to banter_engine.py"
)

# Check results
if result["success"]:
    print(f"Patch applied: {result['files_modified']}")
else:
    print(f"Failed: {result['error']}")
```

## Integration Points

**Used By**:
- AI Intelligence Overseer (autonomous daemon monitoring - code fixes)
- WRE Core (skill-based patch application)
- WSP 90 Skills (UTF-8 header insertion)

## Workflow

```
1. Validate patch against allowlist
   ├─ Check file patterns
   ├─ Check forbidden operations
   └─ Check patch size

2. Run git apply --check (dry-run)
   └─ Verify patch can be applied cleanly

3. Apply patch with git apply
   └─ Only if validation + dry-run pass

4. Return structured results
   └─ For MetricsAppender tracking
```

## Example Patch Format

```diff
diff --git a/modules/test/example.py b/modules/test/example.py
index 1234567..89abcdef 100644
--- a/modules/test/example.py
+++ b/modules/test/example.py
@@ -1,3 +1,4 @@
+# -*- coding: utf-8 -*-
 """
 Example module
 """
```

## WSP Compliance

- **WSP 3**: Proper infrastructure domain placement
- **WSP 49**: Complete module structure (README, INTERFACE, src/, tests/)
- **WSP 77**: Enables autonomous code fixes with metrics tracking
- **WSP 90**: UTF-8 header enforcement support
