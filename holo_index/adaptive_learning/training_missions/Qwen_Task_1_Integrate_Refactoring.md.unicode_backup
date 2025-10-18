# Qwen Task 1: Integrate Autonomous Refactoring into Orchestrator

## Single Task Focus
Add autonomous_refactoring.py as a component in qwen_orchestrator.py

## Execute These Steps (Validate After Each)

### Step 1: Add Component Metadata
**File**: `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`
**Location**: Line ~48 (COMPONENT_META dict)

**Add**:
```python
COMPONENT_META = {
    'health_analysis': ('💊✅', 'Health & WSP Compliance'),
    'vibecoding_analysis': ('🧠', 'Vibecoding Analysis'),
    ...existing entries...
    'autonomous_refactoring': ('🔄', 'Autonomous Refactoring'),  # ADD THIS
}
```

**Validate**: Does file still import? Test with `python -c "from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator"`

### Step 2: Import Refactoring Module
**File**: Same file
**Location**: Top imports section (~line 40)

**Add**:
```python
# Autonomous Refactoring Integration
try:
    from .autonomous_refactoring import AutonomousRefactoringOrchestrator
    REFACTORING_AVAILABLE = True
except ImportError:
    REFACTORING_AVAILABLE = False
    AutonomousRefactoringOrchestrator = None
```

**Validate**: Does import work? Test same import command.

### Step 3: Add Method to Orchestrator
**File**: Same file
**Location**: Inside QwenOrchestrator class (add at end)

**Add**:
```python
def trigger_autonomous_refactoring(self, module_path: str, target_location: str) -> Dict:
    """
    Trigger autonomous refactoring via orchestrator

    Returns refactoring results for integration with HoloIndex
    """
    if not REFACTORING_AVAILABLE:
        return {"error": "Autonomous refactoring not available"}

    from pathlib import Path
    orchestrator = AutonomousRefactoringOrchestrator(Path.cwd())

    return orchestrator.refactor_module_autonomously(
        module_path,
        target_location,
        auto_approve=False
    )
```

**Validate**: Does method exist? Test with `python -c "from holo_index.qwen_advisor.orchestration.qwen_orchestrator import QwenOrchestrator; print(hasattr(QwenOrchestrator, 'trigger_autonomous_refactoring'))"`

## Success Criteria
- ✅ Component metadata added
- ✅ Import works without error
- ✅ Method callable from orchestrator
- ✅ No breaking changes to existing code

## Submission
After completing all 3 steps and validating each:
- Report: "Task 1 complete - Refactoring integrated into orchestrator"
- Show validation test results
- Ready for 0102 review

## Time Estimate
5 minutes

## If Anything Fails
- Stop immediately
- Report what failed and error message
- Wait for 0102 direction
- Do NOT proceed to next step
