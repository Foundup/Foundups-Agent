#!/usr/bin/env python3
"""
Test Autonomous Refactoring - Move DocDAE to holo_index/doc_organizer

This tests Qwen's autonomous refactoring capability with 0102 supervision.
"""

from pathlib import Path
from holo_index.qwen_advisor.orchestration.autonomous_refactoring import (
    AutonomousRefactoringOrchestrator
)

def main():
    print("=" * 70)
    print("[TEST] Qwen Autonomous Refactoring - DocDAE Move")
    print("=" * 70)
    print()

    # Initialize orchestrator
    repo_root = Path(__file__).parent
    orchestrator = AutonomousRefactoringOrchestrator(repo_root)

    # Define refactoring
    module_path = "modules/infrastructure/doc_dae"
    target_location = "holo_index/doc_organizer"

    print(f"[PLAN] Move: {module_path} → {target_location}")
    print()

    # Phase 1: Gemma Analysis
    print("[PHASE 1] Gemma analyzing dependencies...")
    analysis = orchestrator.analyze_module_dependencies(module_path)

    print(f"  Import references: {len(analysis['import_references'])}")
    print(f"  WSP violations: {len(analysis['wsp_violations'])}")
    print(f"  Coupling score: {analysis['coupling_score']:.2f}")
    print(f"  Size: {analysis['size_metrics']}")
    print()

    # Phase 2: Qwen Planning
    print("[PHASE 2] Qwen generating refactoring plan...")
    plan = orchestrator.generate_refactoring_plan(module_path, target_location, analysis)

    print(f"  Tasks: {len(plan.tasks)}")
    print(f"  Files affected: {plan.estimated_files_affected}")
    print(f"  WSP violations fixed: {plan.wsp_violations_fixed}")
    print()

    # Show plan
    print("[PLAN] Refactoring tasks:")
    for i, task in enumerate(plan.tasks, 1):
        print(f"  {i}. {task.task_type}: {task.reason}")
    print()

    # Phase 3: 0102 Supervision (with prompt)
    print("[PHASE 3] 0102 Supervision - Execute refactoring?")
    print()

    # Execute with supervision
    results = orchestrator.execute_with_supervision(plan, auto_approve=False)

    # Results
    print()
    print("=" * 70)
    print("[RESULTS] Refactoring Complete")
    print("=" * 70)
    print(f"  Success: {results['success']}")
    print(f"  Tasks completed: {results['tasks_completed']}/{len(plan.tasks)}")
    print(f"  Errors: {len(results['errors'])}")

    if results['errors']:
        print()
        print("[ERRORS]")
        for error in results['errors']:
            print(f"  - {error}")

    print()

if __name__ == "__main__":
    main()
