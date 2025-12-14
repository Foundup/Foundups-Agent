#!/usr/bin/env python3
"""
Store patterns from 0102 session (2025-11-10) to PatternMemory.
Enables AI-Overseer to learn from successful bug fixes.
"""
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from modules.infrastructure.wre_core.src.pattern_memory import PatternMemory, SkillOutcome
import json
from datetime import datetime

def main():
    # Initialize pattern memory
    memory = PatternMemory()

    # Pattern 1: Duplicate item creation fix (PR #70)
    duplicate_pattern = SkillOutcome(
        execution_id='session_20251110_duplicate_fix',
        skill_name='gotjunk_build_observation',
        agent='0102',
        timestamp=datetime.now().isoformat(),
        input_context=json.dumps({
            'user_report': 'when i modify the price or big and then i take a pic it producing 2 icons',
            'holo_query': 'gotjunk photo classification creating duplicate items two icons',
            'holo_results': [
                {'file': 'App.tsx', 'function': 'handleClassify()', 'relevance': 0.60},
                {'file': 'App.tsx', 'state': 'pendingClassificationItem', 'relevance': 0.50}
            ],
            'root_cause': 'Race condition: pendingClassificationItem cleared at end, not beginning',
            'files_modified': ['modules/foundups/gotjunk/frontend/App.tsx'],
            'pr_number': 70
        }),
        output_result=json.dumps({
            'pattern_name': 'react_async_race_condition_fix',
            'trigger_keywords': ['duplicate', 'creating 2', 'two icons', 'double tap'],
            'holo_query_template': 'gotjunk [operation] creating duplicate items',
            'diagnosis_checklist': [
                'async function with state clearing at end',
                'race condition window allows concurrent calls',
                'missing guard flag for async operations'
            ],
            'fix_template': {
                'add_guard_flag': 'isProcessing state variable (boolean)',
                'immediate_clear': 'clear pending state IMMEDIATELY after guard check',
                'error_handling': 'try/finally to always reset guard flag',
                'validation': 'vite build + manual double-tap test'
            },
            'confidence': 0.95
        }),
        success=True,
        pattern_fidelity=0.95,
        outcome_quality=1.0,
        execution_time_ms=0,
        step_count=1,
        failed_at_step=None,
        notes='Learned from PR #70 - duplicate item creation fix. HoloIndex precision: 60%'
    )

    memory.store_outcome(duplicate_pattern)
    print('[OK] Pattern 1 stored: react_async_race_condition_fix')

    # Pattern 2: Tutorial popup collision fix (PR #71)
    popup_pattern = SkillOutcome(
        execution_id='session_20251110_popup_fix',
        skill_name='gotjunk_build_observation',
        agent='0102',
        timestamp=datetime.now().isoformat(),
        input_context=json.dumps({
            'user_report': 'Screenshot showing modal behind camera orb',
            'holo_query': 'InstructionsModal zLayers positioning safe-area',
            'holo_results': [
                {'file': 'constants/zLayers.ts', 'relevance': 0.70},
                {'file': 'InstructionsModal.tsx', 'relevance': 0.65}
            ],
            'root_cause': 'Z-index collision + bottom positioning conflicting with camera orb',
            'files_modified': [
                'modules/foundups/gotjunk/frontend/constants/zLayers.ts',
                'modules/foundups/gotjunk/frontend/components/InstructionsModal.tsx',
                'modules/foundups/gotjunk/frontend/components/BottomNavBar.tsx'
            ],
            'pr_number': 71
        }),
        output_result=json.dumps({
            'pattern_name': 'mobile_ui_layering_collision_fix',
            'trigger_keywords': ['modal behind', 'collision', 'overlapping', 'z-index'],
            'holo_query_template': '[component] zLayers positioning safe-area',
            'diagnosis_checklist': [
                'z-index values conflicting',
                'positioning anchor (top/bottom) wrong',
                'safe-area-inset not used for mobile cutouts'
            ],
            'fix_template': {
                'extend_contract': 'Add explicit z-layer tiers to centralized constant',
                'reposition': 'Use safe-area-inset for iOS notch/dynamic island',
                'synchronize_docs': 'Update zindex-map.md to match runtime',
                'validation': 'vite build + visual verification on iPhone'
            },
            'confidence': 0.92
        }),
        success=True,
        pattern_fidelity=0.92,
        outcome_quality=1.0,
        execution_time_ms=0,
        step_count=1,
        failed_at_step=None,
        notes='Learned from PR #71 - tutorial popup collision fix. Extended Z_LAYERS contract'
    )

    memory.store_outcome(popup_pattern)
    print('[OK] Pattern 2 stored: mobile_ui_layering_collision_fix')

    # Verify recall
    patterns = memory.recall_successful_patterns('gotjunk_build_observation', min_fidelity=0.8, limit=10)
    print(f'\n[SUCCESS] {len(patterns)} patterns stored and ready for autonomous detection')

    for p in patterns:
        result = json.loads(p['output_result'])
        print(f'  - {result["pattern_name"]} (fidelity: {p["pattern_fidelity"]:.0%})')

    print('\n[NEXT] Test with: python test_pattern_detection.py')

if __name__ == '__main__':
    main()
