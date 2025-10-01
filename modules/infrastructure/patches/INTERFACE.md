# Patches Module Interface

## Public API

### Classes

#### `PatchManager`
Main patch management interface.

**Methods:**
- `apply_patch(patch_file: str, target_path: str = None) -> PatchResult` - Apply a patch file
- `validate_patch(patch_file: str) -> bool` - Validate patch syntax and applicability
- `rollback_patch(patch_id: str) -> bool` - Rollback a previously applied patch
- `list_patches() -> List[PatchInfo]` - List all available patches
- `get_patch_status(patch_id: str) -> PatchStatus` - Get status of a specific patch

## Usage Example

```python
from modules.infrastructure.patches import PatchManager

# Apply a patch
manager = PatchManager()
result = manager.apply_patch("patches/holodae_coordinator.patch")
if result.success:
    print(f"Patch applied successfully to {result.files_modified} files")
else:
    print(f"Patch failed: {result.error}")

# Check patch status
status = manager.get_patch_status("holodae_coordinator")
print(f"Patch status: {status.state}")  # APPLIED, PENDING, FAILED
```

## Patch File Format
Standard unified diff format compatible with `git apply` and `patch` commands.

## WSP Compliance
Interface compliant with WSP 11 (Public Interface Documentation)