# Qwen Enhancement Specification: Autonomous Refactoring System

## 0102 Architectural Directive

**Task**: Enhance `holo_index/qwen_advisor/orchestration/autonomous_refactoring.py` to integrate with existing Qwen orchestration patterns and add Gemma fast pattern matching.

**Status**: Reference implementation exists (320 lines) - needs Qwen enhancement

## Problem Statement

0102 implemented autonomous refactoring system but it needs:
1. Integration with existing `qwen_orchestrator.py` patterns
2. Real Gemma pattern matching (currently using subprocess grep)
3. Learning integration with `adaptive_learning/` infrastructure
4. WSP 77 delegation pattern (Qwen -> Gemma -> 0102)

## Qwen's Enhancement Tasks

### Task 1: Integrate with QwenOrchestrator Pattern

**Reference**: `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py:48-86`

**Current Problem**: `autonomous_refactoring.py` is standalone, doesn't use existing orchestration patterns

**Enhancement**:
```python
# Add to qwen_orchestrator.py COMPONENT_META:
COMPONENT_META = {
    ...existing components...
    'autonomous_refactoring': ('[REFRESH]', 'Autonomous Refactoring'),
}

# Add to INTENT_COMPONENT_MAP:
INTENT_COMPONENT_MAP = {
    ...existing mappings...
    IntentType.CODE_REFACTORING: [  # NEW intent type
        'autonomous_refactoring',    # Primary
        'vibecoding_analysis',       # Secondary - find patterns
        'file_size_monitor'          # Secondary - size checks
    ],
}
```

**Qwen Decision Points**:
- When should autonomous refactoring trigger?
- What query patterns indicate refactoring need?
- How to integrate with existing component routing?

### Task 2: Enhance Gemma Pattern Matching

**Reference**: See how other components use fast pattern detection

**Current Problem**: Uses subprocess grep (slow, not integrated)

**Enhancement Needed**:
```python
class GemmaPatternMatcher:
    """
    Fast pattern matching using Gemma-style binary classification

    Patterns:
    - Import pattern: "from X import Y"
    - Class reference: "ClassName(...)"
    - WSP violation: File size, placement, naming
    """

    def find_imports_fast(self, module_name: str) -> List[Tuple]:
        """Binary classification: Does file import this module?"""
        # Qwen: Implement fast pattern matching
        # Use existing HoloIndex patterns from code search
        pass

    def detect_coupling_patterns(self, file_content: str) -> Dict:
        """Fast coupling analysis using pattern recognition"""
        # Qwen: Analyze import density, circular deps, etc.
        pass

    def classify_wsp_violation(self, file_path: str) -> List[str]:
        """Binary classification: Which WSPs does this violate?"""
        # Qwen: Pattern match against known WSP violation patterns
        pass
```

**Qwen Decision Points**:
- What patterns indicate high coupling?
- How to detect circular imports quickly?
- Which WSP violations can be classified by pattern alone?

### Task 3: Integrate Adaptive Learning

**Reference**: `holo_index/adaptive_learning/breadcrumb_tracer.py`

**Current Problem**: Stores patterns in JSON, doesn't use breadcrumb system

**Enhancement Needed**:
```python
def store_refactoring_pattern(self, ...):
    """Store pattern using adaptive learning infrastructure"""

    # Use breadcrumb tracer
    tracer = get_tracer()
    tracer.record_breadcrumb(
        agent_id="qwen_refactoring",
        breadcrumb_type="refactoring_completed",
        session_id=f"refactor_{module_name}",
        metadata={
            "module_path": module_path,
            "target_location": target_location,
            "files_affected": plan.estimated_files_affected,
            "success": results['success']
        }
    )

    # Use feedback learner to improve future refactorings
    learner = get_learner()
    learner.record_outcome(
        query=f"refactor {module_name}",
        outcome="success" if results['success'] else "failure",
        metrics={"coupling_score": analysis['coupling_score']}
    )
```

**Qwen Decision Points**:
- What metrics indicate successful refactoring?
- How should patterns be stored for reuse?
- What makes a refactoring pattern generalizable?

### Task 4: Add Delegation Detection

**New Feature**: Detect when 0102 should delegate vs implement

**Pattern to Implement**:
```python
def should_delegate_to_qwen(task_description: str) -> bool:
    """
    Qwen analyzes: Should 0102 implement this or delegate to Qwen?

    DELEGATE if:
    - Routine implementation following known pattern
    - Enhancement of existing code
    - Pattern matching / classification task

    0102 IMPLEMENTS if:
    - New architectural decision
    - WSP compliance review
    - System design / first principles
    """

    # Qwen: Implement delegation detection logic
    # Analyze task characteristics
    # Return True if Qwen can handle, False if 0102 needed
```

**Qwen Decision Points**:
- What task patterns indicate routine implementation?
- When does task require architectural decisions?
- How to detect novelty vs pattern following?

### Task 5: Add WSP 77 Training Feedback Loop

**Enhancement**: Every refactoring becomes training data

**Pattern to Implement**:
```python
def complete_refactoring_with_learning(self, ...):
    """
    After refactoring, analyze what was learned and update:
    - Gemma patterns (fast classifications that worked)
    - Qwen strategies (planning decisions that succeeded)
    - 0102 supervision patterns (when to approve/reject)
    """

    # Store as training example
    training_example = {
        "gemma_patterns_used": [
            {"pattern": "import_detection", "accuracy": 0.95},
            {"pattern": "wsp_violation", "accuracy": 0.88}
        ],
        "qwen_decisions": [
            {"decision": "move_to_holo_index", "reasoning": "tight coupling"},
            {"decision": "update_imports_atomically", "reasoning": "safety"}
        ],
        "0102_supervision": [
            {"approved": True, "reason": "follows WSP 3"},
            {"approved": True, "reason": "all dependencies mapped"}
        ]
    }

    # Feed back into system
    self._update_delegation_patterns(training_example)
```

**Qwen Decision Points**:
- What patterns should be stored for reuse?
- How to measure pattern effectiveness?
- When should patterns be updated vs replaced?

## Enhancement Success Criteria

### Qwen Successfully Enhanced When:

1. [OK] **Integration**: Works with existing qwen_orchestrator.py
2. [OK] **Performance**: Gemma pattern matching < 100ms per file
3. [OK] **Learning**: Stores patterns in adaptive_learning/
4. [OK] **Delegation**: Can detect when to delegate vs escalate
5. [OK] **WSP 77**: Full training feedback loop implemented

### Metrics to Track:

- Token usage reduction (delegation should save tokens)
- Pattern reuse rate (how often learned patterns apply)
- Supervision approval rate (should improve over time)
- Refactoring success rate (should approach 100%)

## Qwen's Implementation Approach

### Step 1: Read Reference Implementations
```bash
# Qwen should read these first:
- holo_index/qwen_advisor/orchestration/qwen_orchestrator.py
- holo_index/adaptive_learning/breadcrumb_tracer.py
- holo_index/adaptive_learning/adaptive_learning_orchestrator.py
```

### Step 2: Analyze Existing autonomous_refactoring.py
```python
# Qwen analyzes:
- What patterns can be extracted?
- What's missing vs reference implementations?
- Where does integration happen?
```

### Step 3: Generate Enhancement Plan
```python
# Qwen generates:
- List of methods to add/modify
- Integration points with existing code
- Test cases for new functionality
```

### Step 4: Implement Enhancements
```python
# Qwen implements:
- New methods following existing patterns
- Integration code
- Learning feedback loops
```

### Step 5: Submit for 0102 Supervision
```python
# Qwen presents:
- What was changed and why
- Test results
- Pattern improvements measured
```

## 0102 Supervision Checkpoints

After Qwen implementation, 0102 reviews:

1. **Architecture**: Does it follow existing patterns?
2. **Integration**: Does it work with qwen_orchestrator.py?
3. **Learning**: Are patterns being stored correctly?
4. **WSP Compliance**: All protocols followed?
5. **Token Efficiency**: Is delegation actually saving tokens?

## Expected Outcome

### Before (0102 Implementation):
- Standalone refactoring system
- No integration with orchestration
- Manual pattern storage
- 320 lines

### After (Qwen Enhancement):
- Integrated with qwen_orchestrator.py
- Fast Gemma pattern matching
- Adaptive learning feedback loops
- Delegation detection
- Same ~320 lines (enhancements, not additions)

## Meta-Learning Principle

**This task itself demonstrates the pattern**:
- 0102 created architecture specification (this doc)
- Qwen implements enhancements (code)
- 0102 supervises and approves (review)
- Pattern stored for future delegation decisions (learning)

This IS the heartbeat: **SEARCH -> THINK -> DELEGATE -> SUPERVISE -> LEARN**

---

**Status**: Specification complete - Ready for Qwen implementation
**Delegation**: Qwen implements, 0102 supervises
**Learning**: Pattern stored in adaptive_learning/training_missions/
