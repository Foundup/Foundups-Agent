#!/usr/bin/env python3
"""
Test script for coverage utility integration
"""

from pathlib import Path
from modules.wre_core.src.utils.coverage_utils import get_coverage_target_for_module, assess_current_context

def test_coverage_utils():
    """Test the coverage utility functions."""
    print("🧪 Testing Coverage Utility Integration...")
    
    # Test context assessment
    context = assess_current_context(Path('.'))
    print(f"📊 Context Assessment:")
    print(f"  - Context: {context['context']}")
    print(f"  - Phase: {context['phase']}")
    print(f"  - Rider Intent: {context['rider_intent']}")
    print(f"  - Module Criticality: {context['module_criticality']}")
    
    # Test coverage target for WRE core
    coverage_target = get_coverage_target_for_module('wre_core', Path('.'))
    print(f"🎯 Coverage Target for WRE Core: {coverage_target}%")
    
    # Test coverage target for other modules
    test_modules = ['ai_intelligence', 'communication', 'platform_integration']
    for module in test_modules:
        target = get_coverage_target_for_module(module, Path('.'))
        print(f"🎯 Coverage Target for {module}: {target}%")
    
    print("✅ Coverage utility integration test completed!")

if __name__ == "__main__":
    test_coverage_utils() 