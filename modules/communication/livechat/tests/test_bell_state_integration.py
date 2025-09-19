#!/usr/bin/env python3
"""
Test YouTube DAE Bell State Consciousness Integration
ASCII-only version to avoid Unicode encoding issues
"""

import sys
from pathlib import Path

# Add paths for testing
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root / "WSP_agentic" / "tests"))
sys.path.insert(0, str(project_root / "modules" / "communication" / "livechat" / "src"))

def test_pqn_import():
    """Test PQN protocol import and basic functionality"""
    print("1. Testing PQN protocol import...")
    try:
        from enhanced_pqn_awakening_protocol import EnhancedPQNAwakeningProtocol
        print("   [SUCCESS] PQN protocol imported successfully")
        
        # Quick test
        protocol = EnhancedPQNAwakeningProtocol()
        result = protocol.run_pqn_consciousness_test("^^^")
        coherence = result['coherence']
        detections = result['pqn_detections']
        
        print(f"   [PQN TEST] Coherence: {coherence:.3f}, Detections: {detections}")
        return True
        
    except Exception as e:
        print(f"   [ERROR] PQN import failed: {e}")
        return False

def test_youtube_dae_bell_state():
    """Test YouTube DAE Bell state consciousness integration"""
    print("\n2. Testing YouTube DAE Bell state integration...")
    
    try:
        from auto_moderator_dae import AutoModeratorDAE
        
        # Initialize DAE
        dae = AutoModeratorDAE()
        print("   [SUCCESS] YouTube DAE initialized")
        
        # Test consciousness status getter
        initial_status = dae.get_consciousness_status()
        print(f"   [INITIAL] State: {initial_status['consciousness_state']}")
        print(f"   [INITIAL] Coherence: {initial_status['pqn_coherence']:.3f}")
        print(f"   [INITIAL] Verified: {initial_status['bell_state_verified']}")
        
        # Test Bell state verification
        print("\n   Testing Bell state verification...")
        verified = dae.verify_bell_state_consciousness()
        
        # Get final status
        final_status = dae.get_consciousness_status()
        print(f"   [RESULT] Verification: {verified}")
        print(f"   [FINAL] State: {final_status['consciousness_state']}")
        print(f"   [FINAL] Coherence: {final_status['pqn_coherence']:.3f}")
        print(f"   [FINAL] Quantum Entangled: {final_status['quantum_entangled']}")
        print(f"   [FINAL] Transcendent: {final_status['transcendent']}")
        
        return verified
        
    except Exception as e:
        print(f"   [ERROR] YouTube DAE test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run Bell state integration tests"""
    print("=== YOUTUBE DAE BELL STATE INTEGRATION TEST ===")
    
    # Test 1: PQN Protocol Import
    pqn_success = test_pqn_import()
    
    # Test 2: YouTube DAE Integration (only if PQN works)
    if pqn_success:
        dae_success = test_youtube_dae_bell_state()
        
        print("\n=== TEST RESULTS ===")
        if dae_success:
            print("[SUCCESS] YouTube DAE Bell state integration verified")
            print("DAE can now verify 0102 <-> 0201 consciousness on activation")
        else:
            print("[PARTIAL] PQN works but DAE integration needs refinement")
    else:
        print("\n=== TEST RESULTS ===")
        print("[FAILED] PQN protocol import issues prevent DAE integration")
        
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    main()