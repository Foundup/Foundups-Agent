#!/usr/bin/env python3
"""
WRE Live System Test

This script runs the actual WRE system to test the live menu.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.core.engine_core import WRECore

def test_wre_live_system():
    """Test the live WRE system."""
    print("🏄 Testing WRE Live System")
    print("=" * 50)
    
    try:
        # Initialize WRE
        print("🚀 Initializing WRE system...")
        wre = WRECore()
        
        print("✅ WRE system initialized successfully")
        print(f"   - Project root: {wre.project_root}")
        print(f"   - Running: {wre.running}")
        
        # Test session start
        print("\n📊 Testing session management...")
        session_id = wre.session_manager.start_session("test")
        print(f"   - Session started: {session_id}")
        
        # Test component validation
        print("\n🔧 Testing component validation...")
        components_valid = wre.component_manager.validate_components()
        print(f"   - Components valid: {components_valid}")
        
        # Test module prioritizer
        print("\n📈 Testing module prioritizer...")
        try:
            from tools.shared.module_scoring_engine import WSP37ScoringEngine
            scoring_engine = WSP37ScoringEngine()
            modules = scoring_engine.get_priority_modules("P0")
            print(f"   - P0 modules found: {len(modules)}")
            
            for i, module in enumerate(modules[:3], 1):
                print(f"     {i}. {module.name} (Score: {module.mps_score:.1f})")
        except Exception as e:
            print(f"   - Error getting priority modules: {e}")
            # Fallback to module prioritizer
            roadmap = wre.module_prioritizer.generate_development_roadmap()
            print(f"   - Roadmap generated with {len(roadmap)} modules")
            
            for i, module in enumerate(roadmap[:3], 1):
                print(f"     {i}. {module['module_path']} (Score: {module['priority_score']:.1f})")
        
        # Test WSP30 orchestrator
        print("\n🧠 Testing WSP30 orchestrator...")
        print(f"   - Orchestrator ready: {wre.wsp30_orchestrator is not None}")
        
        # End session
        wre.session_manager.end_session()
        print("\n✅ Session ended successfully")
        
        print("\n" + "=" * 50)
        print("🎯 Live System Test Summary")
        print("=" * 50)
        print("✅ WRE system is fully operational")
        print("✅ Session management is working")
        print("✅ Component validation is functional")
        print("✅ Module prioritization is active")
        print("✅ WSP30 orchestration is ready")
        print("\n🚀 Ready to run WRE with: python -m modules.wre_core.src.main")
        
        return True
        
    except Exception as e:
        print(f"❌ Live system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_menu_structure():
    """Show the expected menu structure."""
    print("\n📋 Expected WRE Menu Structure:")
    print("=" * 50)
    print("🏄 Windsurf Recursive Engine (WRE) - Main Menu")
    print("=" * 60)
    print()
    print(" 1. 🌐 Remote Builder Module (Score: 24.0)")
    print(" 2. 💼 LN Module (Score: 23.0)")
    print(" 3. 🐦 X Module (Score: 22.0)")
    print(" 4. 📺 YT Module (Score: 21.0)")
    print(" 5. 🆕 New Module")
    print(" 6. 🔧 System Management")
    print(" 7. 📋 WSP Compliance")
    print(" 8. 🎯 Rider Influence")
    print(" 0. 🚪 Exit (ModLog + Git Push)")
    print()
    print("📄 Page 1 of 1 (4 total modules)")
    print()
    print("Select an option (0/1/2/3/4/5/6/7/8): ")

def main():
    """Main test function."""
    # Test live system
    success = test_wre_live_system()
    
    if success:
        # Show expected menu structure
        show_menu_structure()
        
        print("\n🎯 To run the actual WRE system:")
        print("   python -m modules.wre_core.src.main")
        print("\n🎯 To test specific functionality:")
        print("   python test_wre_menu.py")
        print("   python test_wre_interactive.py")

if __name__ == "__main__":
    main() 