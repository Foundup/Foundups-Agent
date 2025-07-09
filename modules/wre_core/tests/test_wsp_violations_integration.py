#!/usr/bin/env python3
"""
Test script to verify WSP_MODULE_VIOLATIONS.md integration.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_wsp_violations_integration():
    """Test that WSP_MODULE_VIOLATIONS.md is being read and used properly."""
    
    print("🔍 Testing WSP_MODULE_VIOLATIONS.md integration...")
    
    # Test 1: Check if file exists
    print("\n1. Checking WSP_MODULE_VIOLATIONS.md locations...")
    
    framework_violations = project_root / "WSP_framework" / "src" / "WSP_MODULE_VIOLATIONS.md"
    knowledge_violations = project_root / "WSP_knowledge" / "src" / "WSP_MODULE_VIOLATIONS.md"
    
    print(f"   WSP_framework: {'✅' if framework_violations.exists() else '❌'} - {framework_violations}")
    print(f"   WSP_knowledge: {'✅' if knowledge_violations.exists() else '❌'} - {knowledge_violations}")
    
    # Test 2: Read violations file directly
    print("\n2. Testing direct file read...")
    
    if framework_violations.exists():
        try:
            with open(framework_violations, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"✅ Successfully read file ({len(content)} characters)")
            
            # Check for violation patterns
            import re
            violation_pattern = r'### \*\*(V\d+): ([^*]+)\*\*'
            matches = re.findall(violation_pattern, content)
            print(f"   Found {len(matches)} violation entries")
            
            for match in matches:
                print(f"     - {match[0]}: {match[1].strip()}")
                
        except Exception as e:
            print(f"❌ Error reading file: {e}")
            return False
    else:
        print("❌ WSP_MODULE_VIOLATIONS.md not found in WSP_framework")
        return False
    
    # Test 3: Test orchestrator functions
    print("\n3. Testing orchestrator functions...")
    
    try:
        from modules.wre_core.src.components.orchestrator import read_wsp_module_violations, get_module_development_guidance
        
        violations_data = read_wsp_module_violations()
        
        if violations_data["status"] == "success":
            print(f"✅ Successfully read WSP_MODULE_VIOLATIONS.md via orchestrator")
            print(f"   Total violations: {violations_data['total_violations']}")
            print(f"   Active violations: {len(violations_data['active_violations'])}")
            print(f"   Resolved violations: {len(violations_data['resolved_violations'])}")
            
            # Test module guidance
            guidance = get_module_development_guidance("banter_engine")
            print(f"   Module guidance for banter_engine: {guidance['violation_count']} violations")
            
        else:
            print(f"❌ Failed to read via orchestrator: {violations_data['message']}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing orchestrator functions: {e}")
        return False
    
    print("\n🎯 WSP_MODULE_VIOLATIONS.md integration test completed successfully!")
    return True

if __name__ == "__main__":
    success = test_wsp_violations_integration()
    sys.exit(0 if success else 1) 