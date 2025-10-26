# Agent Permissions - Public Interface

**Module**: `modules/ai_intelligence/agent_permissions/`
**Version**: 1.0.0 (Phase 1)
**Stability**: Beta

---

## Public API

### AgentPermissionManager

Main interface for permission management.

```python
from pathlib import Path
from modules.ai_intelligence.agent_permissions.src import AgentPermissionManager

manager = AgentPermissionManager(repo_root=Path("O:/Foundups-Agent"))
```

#### Methods

**`check_permission(agent_id: str, operation: str, file_path: Optional[str] = None) -> PermissionCheckResult`**

Check if agent has permission for operation.

- **Parameters**:
  - `agent_id`: Agent identifier (e.g., "gemma_dead_code_detection")
  - `operation`: One of: "read", "metrics_write", "edit", "write"
  - `file_path`: File path to check (required for edit/write)

- **Returns**: `PermissionCheckResult` with:
  - `allowed`: bool
  - `reason`: str (explanation)
  - `permission_level`: Optional[str]
  - `confidence`: Optional[float]

**`grant_permission(...) -> PermissionRecord`**

Grant permission to agent (requires human approval).

- **Parameters**:
  - `agent_id`: str
  - `permission_type`: "metrics_write" | "edit_access_tests" | "edit_access_src"
  - `granted_by`: "0102" | "012" | "system_automatic"
  - `duration_days`: int (default 30)
  - `allowlist_patterns`: Optional[List[str]]
  - `forbidlist_patterns`: Optional[List[str]]
  - `justification`: Optional[str]

- **Returns**: `PermissionRecord`

**`downgrade_permission(agent_id: str, reason: str, requires_reapproval: bool = True) -> bool`**

Automatically downgrade permissions (called by system).

- **Parameters**:
  - `agent_id`: str
  - `reason`: str (why downgraded)
  - `requires_reapproval`: bool (default True)

- **Returns**: bool (success)

**`get_permission_level(agent_id: str) -> str`**

Get current permission level.

- **Returns**: "read_only" | "metrics_write" | "edit_access_tests" | "edit_access_src"

---

### ConfidenceTracker

Tracks agent confidence with decay-based algorithm.

```python
from modules.ai_intelligence.agent_permissions.src import ConfidenceTracker

tracker = ConfidenceTracker(memory_dir=Path(".../memory"))
```

#### Methods

**`update_confidence(agent_id: str, execution_result: Dict[str, Any]) -> float`**

Update confidence after execution.

- **Parameters**:
  - `agent_id`: str
  - `execution_result`: dict with:
    - `success`: bool
    - `timestamp`: Optional[str] (ISO format)
    - `event_type`: str (ConfidenceDecayEvent or ConfidenceBoostEvent name)
    - `validation`: str
    - `details`: Optional[Dict]

- **Returns**: float (new confidence score 0.0-1.0)

**`get_confidence(agent_id: str) -> float`**

Get current confidence score.

- **Returns**: float (0.0-1.0, default 0.5)

**`get_confidence_trajectory(agent_id: str, days: int = 30) -> List[Dict]`**

Get confidence history.

- **Returns**: List of {timestamp, confidence, event_type, success}

---

## Event Types

### ConfidenceDecayEvent

Events that trigger confidence decay:

```python
from modules.ai_intelligence.agent_permissions.src import ConfidenceDecayEvent

EDIT_ROLLED_BACK = -0.15      # Human reverted change
HUMAN_REJECTION = -0.10        # Report rejected
WSP_VIOLATION = -0.20          # Broke compliance
REGRESSION_CAUSED = -0.25      # Tests failed
SECURITY_ISSUE = -0.50         # Security vuln
FALSE_POSITIVE = -0.05         # Wrong detection
DUPLICATE_WORK = -0.03         # Redundant work
```

### ConfidenceBoostEvent

Events that boost confidence:

```python
from modules.ai_intelligence.agent_permissions.src import ConfidenceBoostEvent

HUMAN_APPROVAL = 0.10          # 0102 approved
TESTS_PASSED = 0.05            # Tests passed
WSP_COMPLIANT = 0.03           # No violations
PEER_VALIDATION = 0.08         # Agent verified
PRODUCTION_STABLE = 0.15       # Stable 7 days
```

---

## Constants

### PROMOTION_THRESHOLDS

Permission escalation requirements:

```python
{
    'metrics_write': {
        'confidence_required': 0.75,
        'successful_executions': 10,
        'human_validations': 5,
        'trial_period_days': 7
    },
    'edit_access_tests': {
        'confidence_required': 0.85,
        'successful_executions': 25,
        'human_validations': 10,
        'trial_period_days': 14,
        'allowlist': ['modules/**/tests/**/*.py', 'modules/**/docs/**/*.md']
    },
    'edit_access_src': {
        'confidence_required': 0.95,
        'successful_executions': 100,
        'human_validations': 50,
        'trial_period_days': 30,
        'allowlist': ['modules/**/*.py'],
        'forbidlist': ['main.py', 'modules/**/*_dae.py', '.env']
    }
}
```

### DOWNGRADE_THRESHOLDS

Automatic downgrade triggers:

```python
{
    'edit_access_src': 0.90,       # Drop if confidence < 90%
    'edit_access_tests': 0.80,     # Drop if confidence < 80%
    'metrics_write': 0.70          # Drop if confidence < 70%
}
```

---

## Data Structures

### PermissionCheckResult

```python
@dataclass
class PermissionCheckResult:
    allowed: bool
    reason: str
    permission_level: Optional[str] = None
    confidence: Optional[float] = None
```

### PermissionRecord

```python
@dataclass
class PermissionRecord:
    agent_id: str
    permission_level: str
    granted_at: datetime
    granted_by: str
    expires_at: datetime
    confidence_at_grant: float
    allowlist_patterns: List[str]
    forbidlist_patterns: List[str]
    justification: str
    approval_signature: str
```

---

## Integration Examples

### Example 1: Check Permission Before Edit

```python
from pathlib import Path
from modules.ai_intelligence.agent_permissions.src import AgentPermissionManager

manager = AgentPermissionManager(Path("O:/Foundups-Agent"))

# Before editing file
result = manager.check_permission(
    agent_id="qwen_code_quality",
    operation="edit",
    file_path="modules/ai_intelligence/agent_permissions/tests/test_example.py"
)

if result.allowed:
    # Perform edit
    print(f"✓ Allowed (level: {result.permission_level}, confidence: {result.confidence:.2f})")
else:
    # Deny operation
    print(f"✗ Denied: {result.reason}")
```

### Example 2: Update Confidence After Execution

```python
from modules.ai_intelligence.agent_permissions.src import (
    AgentPermissionManager,
    ConfidenceBoostEvent
)

manager = AgentPermissionManager(Path("O:/Foundups-Agent"))
tracker = manager.confidence_tracker

# After successful execution
new_confidence = tracker.update_confidence(
    agent_id="gemma_dead_code_detection",
    execution_result={
        'success': True,
        'event_type': 'HUMAN_APPROVAL',
        'validation': '0102_approved',
        'details': {'findings': 23, 'false_positives': 1}
    }
)

print(f"Confidence updated: {new_confidence:.2f}")

# Check if eligible for promotion
if new_confidence >= 0.75:
    print("✓ Eligible for metrics_write promotion")
```

### Example 3: Grant Permission (Human Approval)

```python
# After agent proves ability
manager.grant_permission(
    agent_id="gemma_dead_code_detection",
    permission_type="metrics_write",
    granted_by="0102",
    duration_days=30,
    justification="Proven pattern detection accuracy (92% success rate)"
)
```

---

## Breaking Changes

None (initial release).

---

## Deprecations

None.

---

## Future API (Planned)

- `request_promotion()`: Agent-initiated promotion request
- `get_audit_trail()`: Query permission events
- `validate_approval_signature()`: Verify approval authenticity
- `get_reapproval_eligibility()`: Check if agent can request re-approval after downgrade

---

**Version**: 1.0.0
**Status**: Beta (Phase 1 Complete)
**Last Updated**: 2025-10-21
