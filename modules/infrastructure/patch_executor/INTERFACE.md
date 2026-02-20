# Patch Executor - Public API

**Module**: `modules.infrastructure.patch_executor`
**Version**: 1.0.0
**WSP Compliance**: WSP 49 (Module Structure), WSP 77 (Agent Coordination)

## Public Classes

### `PatchAllowlist`

Configuration for patch execution safety constraints.

```python
@dataclass
class PatchAllowlist:
    allowed_file_patterns: List[str]  # Glob patterns (e.g., "modules/**/*.py")
    forbidden_operations: Set[str]    # {'delete_file', 'rename_file', etc.}
    max_patch_lines: int              # Maximum patch size
```

### `PatchExecutor`

Safe git patch executor with allowlist enforcement.

**Constructor**:
```python
PatchExecutor(repo_root: Path, allowlist: Optional[PatchAllowlist] = None)
```

## Public Methods

### apply_patch()

Apply git patch with safety validation.

```python
apply_patch(
    patch_content: str,
    patch_description: str = "Autonomous patch",
    dry_run: bool = False,
    memory_bundle: Optional[Dict] = None
) -> Dict
```

**Parameters**:
- `patch_content`: Unified diff patch content
- `patch_description`: Human-readable description
- `dry_run`: If True, only validate without applying
- `memory_bundle`: Optional machine-readable memory bundle (recorded for audit; preflight still enforced per touched module)

**Returns**:
```python
{
    "success": bool,              # Overall success
    "validation_passed": bool,    # Allowlist validation result
    "applied": bool,              # Whether patch was applied
    "files_modified": List[str],  # List of files in patch
    "violations": List[str],      # Allowlist violations (if any)
    "error": Optional[str],       # Error message (if failed)
    "patch_description": str,     # Description (echoed back)
    "memory_preflight": Dict      # Memory gate details (when enabled)
}
```

## Safety Features

### Memory Preflight Gate (WSP_CORE)

When enabled, PatchExecutor enforces Tier-0 memory artifacts for each module touched by the patch via WRE MemoryPreflightGuard.

- Enable/disable: `PATCH_EXECUTOR_MEMORY_GUARD` (default: true)
- Override (dangerous): `PATCH_EXECUTOR_ALLOW_NO_MEMORY` (default: false)

### Forbidden Operations (Default)

- `delete_file`: No file deletions allowed
- `binary_change`: No binary file modifications
- `submodule_change`: No submodule updates
- `rename_file`: No file renames (prevents allowlist bypass)

### Default Allowlist

If no allowlist provided, uses restrictive defaults:
- Patterns: `["modules/**/*.py"]` (Python modules only)
- Max size: 100 lines
- All forbidden operations blocked

## Integration with MetricsAppender

Results are structured for direct integration:

```python
result = executor.apply_patch(patch_content, "Fix UTF-8 encoding")

# Track with MetricsAppender
metrics.append_outcome_metric(
    skill_name="wsp90_utf8_fix",
    execution_id=exec_id,
    decision="apply_patch",
    correct=result["success"],
    confidence=1.0 if result["validation_passed"] else 0.0,
    reasoning=result.get("error", "Patch applied successfully")
)
```

## Error Handling

All methods return structured dictionaries. Never raises exceptions to caller.

Common error scenarios:
- **Allowlist violation**: `validation_passed=False`, violations list populated
- **git apply --check failure**: `success=False`, error contains git output
- **git apply failure**: `success=False`, applied=False
- **Timeout**: `success=False`, error="git apply timed out"

## Thread Safety

NOT thread-safe. Use separate `PatchExecutor` instances per thread/process.

## Example Workflows

### Dry-Run Validation

```python
result = executor.apply_patch(patch_content, "Test patch", dry_run=True)
if result["validation_passed"]:
    print(f"Patch is safe for files: {result['files_modified']}")
```

### Full Application with Error Handling

```python
result = executor.apply_patch(patch_content, "Add UTF-8 headers")

if not result["validation_passed"]:
    print(f"Allowlist violations: {result['violations']}")
elif not result["success"]:
    print(f"Git apply failed: {result['error']}")
else:
    print(f"Success! Modified: {result['files_modified']}")
```
