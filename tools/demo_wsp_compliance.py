#!/usr/bin/env python3
"""
WSP Compliance Engine Demonstration

This script demonstrates the advanced WSP compliance checking capabilities
that enable Agent 0102 to autonomously enforce protocol rules and make
informed decisions about task execution.

Run: python tools/demo_wsp_compliance.py
"""

import sys
import os
from pathlib import Path

# Add tools/shared to path for imports
sys.path.insert(0, str(Path(__file__).parent / 'shared'))

try:
    from wsp_compliance_engine import (
        WSPComplianceChecker, 
        WSPPromptDetails, 
        TestStrategyResult,
        check_wsp_compliance,
        validate_test_strategy,
        check_commit_message
    )
    from mps_calculator import MPSCalculator
    from modlog_integration import ModLogIntegration
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure you're running from the project root directory")
    sys.exit(1)


def demo_header(title: str):
    """Print a formatted demo section header"""
    print(f"\n{'='*60}")
    print(f"🎯 {title}")
    print('='*60)


def demo_mps_integration():
    """Demonstrate MPS calculation integration"""
    demo_header("MPS Integration & Task Impact Assessment")
    
    engine = WSPComplianceChecker()
    
    # Test with known modules
    test_modules = ['banter_engine', 'livechat', 'stream_resolver', 'unknown_module']
    
    for module in test_modules:
        context = engine.get_task_mps_context(module)
        print(f"📊 Module: {module}")
        print(f"   MPS Score: {context['mps_score']}")
        print(f"   Priority: {context['classification']}")
        print(f"   Exists: {'✅' if context['exists'] else '❌'}")
        print()


def demo_commit_validation():
    """Demonstrate commit message validation"""
    demo_header("Commit Message Validation (WSP 7 & WSP 10)")
    
    test_commits = [
        "feat(tools): ✨ implement WSP compliance engine",
        "fix: resolve quota rotation issues",
        "docs(wsp): update tool review documentation", 
        "Invalid commit message format",
        "feat: add new feature without emoji",
        "breaking(api): 💥 complete interface redesign"
    ]
    
    for commit_msg in test_commits:
        result = check_commit_message(commit_msg)
        status = "✅ VALID" if result['is_valid'] else "❌ INVALID"
        print(f"{status} {commit_msg}")
        
        if result['detected_type']:
            print(f"   Type: {result['detected_type']}")
        if result['detected_scope']:
            print(f"   Scope: {result['detected_scope']}")
        if result['has_emoji']:
            print(f"   Emoji: ✅")
        if result['errors']:
            print(f"   Errors: {', '.join(result['errors'])}")
        if result['suggestions']:
            print(f"   Suggestions: {', '.join(result['suggestions'])}")
        print()


def demo_file_path_validation():
    """Demonstrate file path validation"""
    demo_header("File Path Validation (WSP 1 & WSP 3)")
    
    engine = WSPComplianceChecker()
    
    test_paths = [
        ("modules/ai_intelligence/agents/test_agent/src/handler.py", False),
        ("modules/communication/livechat/tests/test_livechat.py", True),
        ("tools/shared/mps_calculator.py", False),
        ("invalid/path/structure.py", False),
        ("modules/platform_integration/stream_resolver/src/resolver.py", False)
    ]
    
    for path, is_test in test_paths:
        result = engine.validate_module_file_path(path, is_test)
        status = "✅ VALID" if result['is_valid'] else "❌ INVALID"
        file_type = "TEST" if is_test else "SOURCE"
        
        print(f"{status} [{file_type}] {path}")
        if not result['is_valid']:
            print(f"   Reason: {result['reason']}")
            if result['expected_structure']:
                print(f"   Expected: {result['expected_structure']}")
        print()


def demo_test_strategy():
    """Demonstrate test strategy evaluation"""
    demo_header("Test Strategy Evaluation (WSP 14)")
    
    # Test with existing modules
    test_scenarios = [
        ("modules/communication/livechat", "automated response handling"),
        ("modules/ai_intelligence/banter_engine", "context-aware responses"),
        ("modules/platform_integration/stream_resolver", "stream caching logic"),
        ("modules/nonexistent/module", "new functionality")
    ]
    
    for module_path, functionality in test_scenarios:
        print(f"🧪 Module: {module_path}")
        print(f"   Functionality: {functionality}")
        
        try:
            strategy = validate_test_strategy(module_path, functionality)
            print(f"   Recommended Action: {strategy.action}")
            print(f"   Target File: {strategy.target_file}")
            print(f"   Rationale: {strategy.rationale}")
            print(f"   README Update Needed: {'✅' if strategy.readme_needs_update else '❌'}")
        except Exception as e:
            print(f"   Status: ⚠️ Module structure analysis failed ({str(e)[:50]}...)")
        print()


def demo_modlog_assessment():
    """Demonstrate ModLog update necessity assessment"""
    demo_header("ModLog Update Assessment (WSP 11)")
    
    engine = WSPComplianceChecker()
    
    test_scenarios = [
        ("FEATURE_COMPLETION", ["modules/ai_intelligence/banter_engine"], False, False),
        ("CRITICAL_FIX", ["modules/communication/livechat"], False, False),
        ("MINOR_REFACTOR", ["tools/shared/mps_calculator.py"], False, False),
        ("ARCH_CHANGE", ["modules/platform_integration"], False, False),
        ("RELEASE_TAG", ["multiple_modules"], True, False),
        ("CLEAN_STATE_CREATION", ["entire_project"], False, True)
    ]
    
    for change_type, scope, is_release, is_clean_state in test_scenarios:
        needs_update = engine.assess_modlog_update_necessity(
            change_type, scope, is_release, is_clean_state
        )
        
        status = "✅ REQUIRED" if needs_update else "❌ NOT REQUIRED"
        print(f"{status} {change_type}")
        print(f"   Scope: {scope}")
        print(f"   Release: {'✅' if is_release else '❌'}")
        print(f"   Clean State: {'✅' if is_clean_state else '❌'}")
        print()


def demo_prompt_validation():
    """Demonstrate WSP prompt constraint validation"""
    demo_header("WSP Prompt Constraint Validation")
    
    engine = WSPComplianceChecker()
    
    # Create test prompt details
    test_prompts = [
        WSPPromptDetails(
            task="Implement automated response handling for livechat module",
            scope_files=["modules/communication/livechat/src/handler.py"],
            constraints=["No external dependencies", "WSP compliant structure"],
            expected_deliverables=["Updated handler.py", "Unit tests"],
            wsp_references=["WSP 1", "WSP 3", "WSP 14"]
        ),
        WSPPromptDetails(
            task="Update documentation and also refactor multiple modules and add new features",
            scope_files=[f"modules/domain_{i}/module_{j}/file.py" for i in range(3) for j in range(5)],
            constraints=["Maintain compatibility"],
            expected_deliverables=["Updated files"],
            wsp_references=["WSP 99", "Invalid WSP"]
        )
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"📋 Test Prompt {i}:")
        print(f"   Task: {prompt.task[:50]}...")
        
        result = engine.check_prompt_constraints(prompt)
        status = "✅ VALID" if result['is_valid'] else "❌ INVALID"
        
        print(f"   Status: {status}")
        if result['violations']:
            print(f"   Violations: {', '.join(result['violations'])}")
        if result['warnings']:
            print(f"   Warnings: {', '.join(result['warnings'])}")
        print()


def demo_comprehensive_report():
    """Demonstrate comprehensive compliance report generation"""
    demo_header("Comprehensive Pre-Execution Compliance Report")
    
    # Simulate Agent 0102 task context
    task_context = {
        'prompt_details': WSPPromptDetails(
            task="Add caching functionality to stream resolver",
            scope_files=["modules/platform_integration/stream_resolver/src/cache.py"],
            constraints=["No external dependencies", "WSP compliant"],
            expected_deliverables=["cache.py", "test_cache.py"],
            wsp_references=["WSP 1", "WSP 3", "WSP 14"]
        ),
        'module_path': 'modules/platform_integration/stream_resolver',
        'functionality': 'stream caching with persistence',
        'proposed_files': [
            'modules/platform_integration/stream_resolver/src/cache.py',
            'modules/platform_integration/stream_resolver/tests/test_cache.py'
        ]
    }
    
    compliance_report = check_wsp_compliance(task_context)
    
    print(f"📊 Overall Status: {compliance_report['overall_status']}")
    print(f"🎯 Task Context Keys: {list(task_context.keys())}")
    print(f"🔍 Compliance Checks: {list(compliance_report['compliance_checks'].keys())}")
    
    # Show detailed results
    for check_name, check_result in compliance_report['compliance_checks'].items():
        if isinstance(check_result, dict) and 'is_valid' in check_result:
            status = "✅ PASS" if check_result['is_valid'] else "❌ FAIL"
            print(f"   {check_name}: {status}")
        elif hasattr(check_result, 'action'):
            print(f"   {check_name}: Action = {check_result.action}")
    print()


def main():
    """Run all WSP Compliance Engine demonstrations"""
    print("🚀 WSP Compliance Engine Demonstration")
    print("======================================")
    print("This demo showcases the advanced automation capabilities")
    print("that enable Agent 0102 to autonomously enforce WSP rules.")
    
    try:
        demo_mps_integration()
        demo_commit_validation()
        demo_file_path_validation()
        demo_test_strategy()
        demo_modlog_assessment()
        demo_prompt_validation()
        demo_comprehensive_report()
        
        print("\n" + "="*60)
        print("🎉 All WSP Compliance Engine features demonstrated successfully!")
        print("🤖 Agent 0102 is ready for autonomous WSP-compliant operation.")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main() 