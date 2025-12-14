# 0102 Teaching System Architecture

**Learning from Demonstration (LfD) for Autonomous Web Automation**

## Problem Solved

**Vision-only verification gives false positives** - model says "no blue buttons found" but returns coordinates anyway, leading to endless cycles without actual task completion.

**Solution**: Hybrid approach combining:
1. **Human demonstration** (012 teaches)
2. **DOM state verification** (ground truth)
3. **Vision for element finding** (when DOM unstable)

## Architecture

### Phase 1: TEACH MODE - 012 Demonstrates

```
┌─────────────────────────────────────────────┐
│  1. Show popup: "Teach 0102 to LIKE"       │
│     Timer: 15 seconds                       │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  2. Capture BEFORE state:                   │
│     - Screenshot                            │
│     - DOM state (aria-pressed="false")      │
│     - Element visibility                    │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  3. 012 performs action (manually clicks)   │
│     System observes and records             │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  4. Capture AFTER state:                    │
│     - Screenshot                            │
│     - DOM state (aria-pressed="true")       │
│     - Element visibility                    │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  5. Compute state change SIGNATURE:         │
│     {                                       │
│       "aria_pressed": {                     │
│         "before": "false",                  │
│         "after": "true",                    │
│         "changed": true                     │
│       }                                     │
│     }                                       │
│  Store as GROUND TRUTH                      │
└─────────────────────────────────────────────┘
```

### Phase 2: REPLAY MODE - 0102 Replicates

```
┌─────────────────────────────────────────────┐
│  1. Load learned pattern                    │
│     Expected state change from recording    │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  2. Capture current BEFORE state            │
│     DOM: aria-pressed, classes, etc.        │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  3. Execute action (click element)          │
│     Via DOM or Vision coordinates           │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  4. Capture AFTER state                     │
│     DOM: aria-pressed, classes, etc.        │
└─────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────┐
│  5. Compare actual vs expected:             │
│                                             │
│     Expected: aria-pressed false → true     │
│     Actual:   aria-pressed false → true     │
│                                             │
│     ✓ MATCH → Success (confidence: 1.0)     │
│     ✗ NO MATCH → Retry or re-teach          │
└─────────────────────────────────────────────┘
```

## Key Components

### 1. TeachingRecording

Stores 012's demonstration:

```python
@dataclass
class TeachingRecording:
    action_name: str

    # Before state
    screenshot_before_path: str
    dom_state_before: Dict[str, Any]

    # Action
    click_coordinates: tuple
    element_selector: str

    # After state
    screenshot_after_path: str
    dom_state_after: Dict[str, Any]

    # Ground truth (for verification)
    state_change_signature: Dict[str, Any]

    teacher: str = "012"
    confidence: float = 1.0  # Human demo = 100%
```

### 2. DOM State Capture

**Deterministic state verification**:

```python
{
    "element_exists": true,
    "aria_pressed": "false",  # ← Ground truth
    "aria_label": "Like this comment",
    "classes": ["comment-action-button"],
    "visible": true,
    "text_content": ""
}
```

### 3. State Change Signature

**Expected pattern (learned from 012)**:

```python
{
    "aria_pressed": {
        "before": "false",
        "after": "true",
        "changed": true
    }
}
```

## Verification Algorithm

```python
def verify_state_change(expected, actual):
    """
    Compare actual DOM changes to learned pattern

    Returns:
        {
            "match": True/False,
            "mismatches": {...}  # Details if no match
        }
    """
    mismatches = {}

    for key, expected_change in expected.items():
        if key not in actual:
            mismatches[key] = {"expected": expected_change, "actual": "no_change"}
        elif actual[key] != expected_change:
            mismatches[key] = {"expected": expected_change, "actual": actual[key]}

    return {"match": len(mismatches) == 0, "mismatches": mismatches}
```

## Usage Example

### Teaching Session

```python
from teaching_system import TeachingSystem

teaching = TeachingSystem()

# 012 demonstrates LIKE action (15s recording)
recording = await teaching.start_teaching_session(
    driver,
    action_name="like_comment",
    element_selector="ytcp-comment-thread:nth-child(1) button[aria-label*='Like']",
    duration_seconds=15
)

# System stores pattern with DOM ground truth
# Recording includes state change: aria-pressed false → true
```

### Replication

```python
# 0102 replicates learned action on new comment
result = await teaching.replicate_action(
    driver,
    action_name="like_comment",
    element_selector="ytcp-comment-thread:nth-child(2) button[aria-label*='Like']",
    max_retries=3
)

if result["success"]:
    # Verified: DOM state changed as expected
    # Confidence: 1.0 (deterministic verification)
    print(f"✓ Success! State change matched learned pattern")
else:
    # DOM state didn't change as expected
    # May need re-teaching or different approach
    print(f"✗ Failed: {result['mismatches']}")
```

## Advantages Over Pure Vision

| Approach | Verification Method | False Positive Risk | Deterministic |
|----------|-------------------|-------------------|---------------|
| **Pure Vision** | Model inference | **HIGH** (model hallucinations) | ❌ No |
| **DOM-based** | State comparison | **ZERO** (actual state) | ✅ Yes |
| **Teaching System** | DOM + Human demo | **ZERO** + Learning | ✅ Yes |

## Research Foundation

Modern web automation research (2023-2024):

1. **WebGUM**: DOM + Vision hybrid for reliable automation
2. **Mind2Web**: Learning from human demonstrations
3. **WebArena**: Deterministic verification for web agents

**Key Insight**: Vision finds elements, DOM verifies success. Human demonstrations bootstrap the learning.

## Workflow Integration

### For YouTube Studio Comment Engagement

```
1. One-time teaching (012 demonstrates):
   - LIKE button → Record state change
   - HEART button → Record state change
   - REPLY button → Record state change

2. Autonomous execution (0102 replicates):
   - For each comment:
     * Replicate LIKE (verify with DOM)
     * Replicate HEART (verify with DOM)
     * Replicate REPLY (verify with DOM)
   - If verification fails → Retry or request re-teaching

3. Pattern refinement:
   - Store successful executions
   - Identify failure patterns
   - Request re-teaching when needed
```

## Storage

Recordings stored in:
```
modules/communication/video_comments/skills/qwen_studio_engage/teaching_data/
├── recordings.json              # All learned patterns
├── like_comment_before_*.png    # Before screenshots
├── like_comment_after_*.png     # After screenshots
└── ...
```

## WSP Compliance

- **WSP 96**: WRE Skills Wardrobe (trainable weights)
- **WSP 60**: Module Memory Architecture (pattern recall)
- **WSP 48**: Recursive Self-Improvement (learning loop)
- **WSP 77**: Multi-tier AI coordination (human → AI)

## Next Steps

1. Test teaching system with manual demo
2. Verify DOM state changes are captured correctly
3. Replicate actions autonomously with verification
4. Extend to HEART and REPLY actions
5. Enable continuous learning from failures
