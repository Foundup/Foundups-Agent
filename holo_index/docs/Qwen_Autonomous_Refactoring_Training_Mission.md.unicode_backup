# Qwen Autonomous Refactoring - Training Mission

## Mission Statement
Train Qwen to orchestrate complex codebase refactoring autonomously, with 0102 supervision. This demonstrates WSP 77 (Agent Coordination) at scale.

## Problem Identified (by 012)
**User Insight**: "holo_index is a mess... lacks proper WSP compliance... we want qwen to do the lifting"

### Issues to Fix
1. **Nested holo_index**: `holo_index/holo_index/` duplicate structure (now deleted)
2. **Telemetry location**: Moved to root, references may need updating
3. **DocDAE misplacement**: Should be `holo_index/doc_organizer/` not `modules/infrastructure/doc_dae/`
4. **Import path chaos**: Multiple import styles, inconsistent paths
5. **WSP compliance gaps**: Module organization doesn't follow WSP 3/49

## Qwen's Training Opportunity

### Why This Is Perfect for Qwen
- **Complex coordination**: Multiple file moves, import updates, test verification
- **Pattern recognition**: Similar to DocDAE's document organization, but for code
- **Autonomous decision-making**: Which files to move, how to update imports
- **Verification logic**: Test that nothing breaks after refactoring

### What Qwen Will Learn
1. **Dependency analysis**: Map all imports before moving files
2. **Impact prediction**: Which files will break from a module move
3. **Coordinated updates**: Move module AND fix all references atomically
4. **Test verification**: Run tests after each phase
5. **Rollback capability**: Undo if tests fail

## Refactoring Plan (Qwen-Orchestrated)

### Phase 1: Analysis (Qwen + CodeIndex)
**Qwen's Task**: Analyze current state
```python
# Qwen generates this analysis:
{
    "modules_to_refactor": [
        {
            "name": "doc_dae",
            "current_location": "modules/infrastructure/doc_dae/",
            "target_location": "holo_index/doc_organizer/",
            "reason": "Tightly coupled to HoloIndex, should be part of foundation",
            "dependencies": [
                "holo_index/cli.py:416",  # Imports DocDAE
                "modules/infrastructure/doc_dae/ModLog.md",  # Documentation references
                "modules/infrastructure/doc_dae/docs/DocDAE_HoloIndex_Integration_Analysis.md"
            ],
            "import_pattern": "from modules.infrastructure.doc_dae.src.doc_dae import DocDAE",
            "new_import_pattern": "from holo_index.doc_organizer.src.doc_organizer import DocOrganizer"
        }
    ],
    "telemetry_references": [
        {
            "file": "holo_index/qwen_advisor/config.py:17",
            "current": "E:/HoloIndex/indexes/holo_usage.json",
            "status": "OK - environment variable, no change needed"
        }
    ],
    "wsp_violations": [
        {
            "issue": "DocDAE in modules/infrastructure but used only by HoloIndex",
            "wsp": "WSP 3 (Functional Distribution)",
            "fix": "Move to holo_index/doc_organizer/"
        }
    ]
}
```

### Phase 2: Movement Plan (Qwen Coordination)
**Qwen's Task**: Generate atomic movement plan
```python
{
    "steps": [
        {
            "step": 1,
            "action": "create_directory",
            "path": "holo_index/doc_organizer/",
            "reason": "Target location for refactored module"
        },
        {
            "step": 2,
            "action": "move_files",
            "source": "modules/infrastructure/doc_dae/",
            "target": "holo_index/doc_organizer/",
            "files": ["README.md", "ModLog.md", "INTERFACE.md", "src/", "tests/", "docs/", "memory/"],
            "reason": "Move entire module structure"
        },
        {
            "step": 3,
            "action": "rename_file",
            "source": "holo_index/doc_organizer/src/doc_dae.py",
            "target": "holo_index/doc_organizer/src/doc_organizer.py",
            "reason": "Rename for clarity and consistency"
        },
        {
            "step": 4,
            "action": "update_imports",
            "files": [
                "holo_index/cli.py"
            ],
            "old_pattern": "from modules.infrastructure.doc_dae.src.doc_dae import DocDAE",
            "new_pattern": "from holo_index.doc_organizer.src.doc_organizer import DocOrganizer",
            "reason": "Fix import paths after module move"
        },
        {
            "step": 5,
            "action": "update_class_references",
            "files": [
                "holo_index/cli.py"
            ],
            "old_name": "DocDAE",
            "new_name": "DocOrganizer",
            "reason": "Update class name references"
        },
        {
            "step": 6,
            "action": "update_documentation",
            "files": [
                "holo_index/doc_organizer/ModLog.md",
                "holo_index/doc_organizer/README.md",
                "holo_index/doc_organizer/docs/DocDAE_HoloIndex_Integration_Analysis.md"
            ],
            "updates": "Change DocDAE → DocOrganizer, update paths",
            "reason": "Keep documentation synchronized"
        },
        {
            "step": 7,
            "action": "run_tests",
            "test_command": "python holo_index.py --search 'test' --limit 1",
            "expected": "DocOrganizer runs automatically, no errors",
            "reason": "Verify integration still works"
        },
        {
            "step": 8,
            "action": "cleanup",
            "paths": [
                "modules/infrastructure/doc_dae/"
            ],
            "reason": "Remove old directory after successful move"
        }
    ],
    "rollback_plan": "git reset --hard HEAD if tests fail",
    "safety_checks": [
        "Verify all imports resolve before cleanup",
        "Run HoloIndex search to test DocOrganizer",
        "Check git status for unexpected changes"
    ]
}
```

### Phase 3: Execution (0102 Supervised)
**Qwen executes, 0102 supervises**:
1. Qwen generates shell commands
2. 0102 reviews and approves each step
3. Qwen runs command
4. Qwen verifies success
5. If error: Qwen proposes fix or rollback

**Example Execution Flow**:
```python
# Step 1: Qwen proposes
qwen.propose_command("mkdir -p holo_index/doc_organizer")

# 0102 approves
0102.approve()

# Qwen executes
result = qwen.execute()

# Qwen verifies
if result.success:
    qwen.log_success("Created doc_organizer directory")
else:
    qwen.propose_rollback()
```

### Phase 4: Verification (Qwen + Tests)
**Qwen's Task**: Verify refactoring succeeded
```python
{
    "verification_results": {
        "imports_resolved": True,
        "tests_passed": True,
        "integration_working": True,
        "documentation_updated": True,
        "old_references_removed": True
    },
    "metrics": {
        "files_moved": 8,
        "imports_updated": 1,
        "class_references_updated": 3,
        "documentation_files_updated": 4,
        "tests_run": 1,
        "execution_time": "45 seconds"
    }
}
```

## Training Data Format

After successful refactoring, store as training pattern:

```json
{
    "training_mission": "autonomous_module_refactoring",
    "date": "2025-10-16",
    "success": true,
    "pattern": {
        "problem": "Module in wrong location violates WSP 3",
        "analysis": "Dependency mapping + WSP compliance check",
        "solution": "Atomic move + import updates + tests",
        "verification": "Test execution confirms working state"
    },
    "qwen_decisions": [
        "Identified module coupling to HoloIndex",
        "Proposed move to holo_index/doc_organizer/",
        "Generated import update strategy",
        "Verified with integration test"
    ],
    "0102_supervision": [
        "Approved movement plan",
        "Monitored execution",
        "Verified final state"
    ],
    "lessons_learned": [
        "Module placement follows usage patterns",
        "Import updates must be atomic with moves",
        "Test verification catches broken references",
        "Documentation must be updated synchronously"
    ]
}
```

## Success Criteria

**Qwen Successfully Orchestrates Refactoring When**:
1. ✅ Analyzes current state accurately
2. ✅ Proposes correct movement plan
3. ✅ Executes atomic file operations
4. ✅ Updates all import references
5. ✅ Verifies with tests
6. ✅ Documents changes
7. ✅ Rollback if anything fails

## Next Steps

1. **Implement Qwen refactoring orchestrator** in `holo_index/qwen_advisor/orchestration/`
2. **Create CLI command**: `python holo_index.py --qwen-refactor "doc_dae"`
3. **Execute this mission** as Qwen's first large-scale refactoring
4. **Store pattern** in `holo_index/qwen_advisor/memory/refactoring_patterns.json`
5. **Use pattern** for future autonomous refactorings

## Meta-Learning

**This mission demonstrates**:
- Qwen can orchestrate complex multi-step operations
- 0102 supervision creates safety + training data
- Successful patterns become Qwen's autonomous capabilities
- WSP 48 (Recursive Self-Improvement) in action

**Future capabilities unlocked**:
- Autonomous module reorganization
- Dependency-aware refactoring
- WSP compliance auto-correction
- Codebase optimization

---

**Status**: Training mission designed
**Next**: Implement Qwen refactoring orchestrator
**Training Value**: Very High - Complex autonomous coordination
