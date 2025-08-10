#!/usr/bin/env python3
"""
Test script to verify WRE fixes work correctly
"""

import sys
from pathlib import Path

# Add project root to Python path (3 levels up from this test file)
test_file = Path(__file__).resolve()
project_root = test_file.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

def test_compliance_agent():
    """Test ComplianceAgent has verify_readiness method"""
    print("Testing ComplianceAgent.verify_readiness method...")
    
    try:
        from modules.infrastructure.compliance_agent.src.compliance_agent import ComplianceAgent
        
        # Create ComplianceAgent instance
        agent = ComplianceAgent(project_root)
        
        # Check if method exists
        if hasattr(agent, 'verify_readiness'):
            print("SUCCESS: verify_readiness method exists")
            
            # Test the method
            result = agent.verify_readiness()
            print(f"Readiness Status: {result.readiness_status}")
            print(f"Overall Score: {result.overall_readiness_score}")
            print(f"System Health: {result.system_health_score}")
            print(f"Blocking Issues: {len(result.blocking_issues)}")
            
            return True
        else:
            print("ERROR: verify_readiness method missing")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_wre_basic():
    """Test basic WRE functionality"""
    print("\nTesting basic WRE functionality...")
    
    try:
        from modules.wre_core.src.remote_build_orchestrator import create_remote_build_orchestrator
        
        orchestrator = create_remote_build_orchestrator()
        print("SUCCESS: RemoteBuildOrchestrator created")
        
        # Check if compliance_agent has verify_readiness
        if hasattr(orchestrator.compliance_agent, 'verify_readiness'):
            print("SUCCESS: ComplianceAgent has verify_readiness method")
            return True
        else:
            print("ERROR: ComplianceAgent missing verify_readiness method")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("=== WRE Fix Verification ===")
    
    success1 = test_compliance_agent()
    success2 = test_wre_basic()
    
    if success1 and success2:
        print("\n[SUCCESS] All tests passed! WRE should work now.")
        sys.exit(0)
    else:
        print("\n[ERROR] Some tests failed. Need more fixes.")
        sys.exit(1)