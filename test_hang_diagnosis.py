#!/usr/bin/env python3
"""
WRE Hang Diagnosis Script - WSP 22 Traceable Diagnostic

Test each component individually to find the exact hang point.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

def test_component_imports():
    """Test importing each component individually."""
    print("🔍 Testing component imports...")
    
    try:
        print("  Testing logging_utils...")
        from modules.wre_core.src.utils.logging_utils import wre_log
        print("  ✅ logging_utils imported")
        
        print("  Testing ModuleStatusManager...")
        from modules.wre_core.src.components.development.module_status_manager import ModuleStatusManager
        print("  ✅ ModuleStatusManager imported")
        
        print("  Testing ModuleTestRunner...")
        from modules.wre_core.src.components.development.module_test_runner import ModuleTestRunner
        print("  ✅ ModuleTestRunner imported")
        
        print("  Testing ManualModeManager...")
        from modules.wre_core.src.components.development.manual_mode_manager import ManualModeManager
        print("  ✅ ManualModeManager imported")
        
        print("  Testing ModuleDevelopmentHandler...")
        from modules.wre_core.src.components.development.module_development_handler_refactored import ModuleDevelopmentHandler
        print("  ✅ ModuleDevelopmentHandler imported")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_component_instantiation():
    """Test instantiating each component."""
    print("\n🔍 Testing component instantiation...")
    
    try:
        from modules.wre_core.src.components.development.module_status_manager import ModuleStatusManager
        from modules.wre_core.src.components.development.module_test_runner import ModuleTestRunner
        from modules.wre_core.src.components.development.manual_mode_manager import ManualModeManager
        from modules.wre_core.src.components.development.module_development_handler_refactored import ModuleDevelopmentHandler
        
        print("  Creating ModuleStatusManager...")
        status_mgr = ModuleStatusManager(project_root)
        print("  ✅ ModuleStatusManager created")
        
        print("  Creating ModuleTestRunner...")
        test_runner = ModuleTestRunner(project_root)
        print("  ✅ ModuleTestRunner created")
        
        print("  Creating ManualModeManager...")
        manual_mgr = ManualModeManager(project_root)
        print("  ✅ ManualModeManager created")
        
        print("  Creating MockSessionManager...")
        class MockSessionManager:
            def log_operation(self, op, data): pass
            def log_achievement(self, name, desc): pass
        session_mgr = MockSessionManager()
        print("  ✅ MockSessionManager created")
        
        print("  Creating ModuleDevelopmentHandler...")
        dev_handler = ModuleDevelopmentHandler(project_root, session_mgr)
        print("  ✅ ModuleDevelopmentHandler created")
        
        return True
    except Exception as e:
        print(f"  ❌ Instantiation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_interface():
    """Test UI interface components."""
    print("\n🔍 Testing UI interface...")
    
    try:
        print("  Testing UIInterface import...")
        from modules.wre_core.src.interfaces.ui_interface import UIInterface
        print("  ✅ UIInterface imported")
        
        print("  Creating UIInterface...")
        ui = UIInterface(test_mode=True)
        print("  ✅ UIInterface created")
        
        print("  Testing get_user_input method...")
        # Don't actually call it, just check it exists
        assert hasattr(ui, 'get_user_input')
        print("  ✅ get_user_input method exists")
        
        return True
    except Exception as e:
        print(f"  ❌ UI interface test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests."""
    print("🏄 WRE Hang Diagnosis - WSP 22 Traceable Analysis")
    print("=" * 60)
    
    success = True
    
    # Test 1: Component imports
    if not test_component_imports():
        success = False
        
    # Test 2: Component instantiation  
    if not test_component_instantiation():
        success = False
        
    # Test 3: UI interface
    if not test_ui_interface():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All diagnostic tests passed!")
        print("🔍 The hang must be occurring during execution, not initialization.")
        print("💡 Recommendation: Add debug prints to trace execution flow.")
    else:
        print("❌ Diagnostic tests revealed issues!")
        print("🔧 Fix the identified problems before proceeding.")
    
if __name__ == "__main__":
    main() 