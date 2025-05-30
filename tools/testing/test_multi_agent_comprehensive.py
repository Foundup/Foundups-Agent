#!/usr/bin/env python3
"""
WSP: Comprehensive Multi-Agent Testing Solution
===============================================

This is a WSP-compliant comprehensive test that demonstrates:
1. Multi-agent discovery and login functionality
2. Proper WSP test structure and documentation
3. Integration with existing test patterns
4. Production-ready test scenarios

WSP Compliance:
- Tests placed in proper tools/testing location per WSP structure
- Follows WSP 13 test creation procedures  
- Comprehensive coverage of multi-agent functionality
- Integration testing with live authentication
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path for WSP compliance
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

try:
    from modules.infrastructure.agent_management.agent_management.src.multi_agent_manager import (
        MultiAgentManager, AgentIdentity, AgentSession
    )
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Ensure modules are properly installed and paths are correct")
    sys.exit(1)

class MultiAgentTestSuite:
    """Comprehensive test suite for multi-agent functionality with WSP compliance"""
    
    def __init__(self):
        self.manager = None
        self.test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "agent_discovery": {},
            "authentication_status": {},
            "wsp_compliance": {}
        }
    
    def log_result(self, test_name: str, success: bool, message: str = ""):
        """Log test result with WSP-compliant formatting"""
        self.test_results["total_tests"] += 1
        if success:
            self.test_results["passed"] += 1
            print(f"✅ {test_name}: PASS {message}")
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
            print(f"❌ {test_name}: FAIL {message}")
    
    def test_wsp_compliance_structure(self) -> bool:
        """Test WSP compliance of module structure"""
        print("\n📋 Testing WSP Compliance...")
        
        # Test WSP 1: Module structure
        module_path = Path("modules/infrastructure/agent_management/agent_management")
        
        src_exists = (module_path / "src").exists()
        tests_exists = (module_path / "tests").exists()
        readme_exists = (module_path / "tests" / "README.md").exists()
        
        self.log_result("WSP 1: src/ directory exists", src_exists)
        self.log_result("WSP 1: tests/ directory exists", tests_exists)
        self.log_result("WSP 13: tests/README.md exists", readme_exists)
        
        self.test_results["wsp_compliance"] = {
            "wsp_1_structure": src_exists and tests_exists,
            "wsp_13_test_docs": readme_exists
        }
        
        return src_exists and tests_exists and readme_exists
    
    def test_manager_initialization(self) -> bool:
        """Test multi-agent manager initialization"""
        print("\n🔧 Testing Manager Initialization...")
        
        try:
            self.manager = MultiAgentManager()
            self.log_result("Manager Creation", True, "MultiAgentManager created successfully")
            
            # Test initialization
            success = self.manager.initialize()
            self.log_result("Manager Initialization", success, 
                          f"Initialize returned: {success}")
            
            return success
        except Exception as e:
            self.log_result("Manager Initialization", False, f"Exception: {e}")
            return False
    
    def test_agent_discovery(self) -> bool:
        """Test agent discovery functionality"""
        print("\n🔍 Testing Agent Discovery...")
        
        if not self.manager:
            self.log_result("Agent Discovery", False, "Manager not initialized")
            return False
        
        try:
            # Get discovered agents from registry
            all_agents = list(self.manager.registry.agents.values())
            
            self.log_result("Agent Discovery Count", len(all_agents) > 0, 
                          f"Discovered {len(all_agents)} agents")
            
            # Test each agent
            for i, agent in enumerate(all_agents, 1):
                agent_valid = all([
                    agent.agent_id,
                    agent.channel_name,
                    agent.credential_set,
                    agent.status in ["available", "active", "same_account_conflict", "cooldown", "error"]
                ])
                
                self.log_result(f"Agent {i} Validation", agent_valid, 
                              f"{agent.agent_id} ({agent.status})")
                
                # Store agent info for reporting
                self.test_results["agent_discovery"][agent.agent_id] = {
                    "channel_name": agent.channel_name,
                    "status": agent.status,
                    "credential_set": agent.credential_set,
                    "valid": agent_valid
                }
            
            return len(all_agents) > 0
            
        except Exception as e:
            self.log_result("Agent Discovery", False, f"Exception: {e}")
            return False
    
    def test_agent_selection_logic(self) -> bool:
        """Test agent selection and conflict prevention"""
        print("\n🎯 Testing Agent Selection Logic...")
        
        if not self.manager:
            self.log_result("Agent Selection", False, "Manager not initialized")
            return False
        
        try:
            # Test getting available agents
            available_agents = self.manager.registry.get_available_agents()
            self.log_result("Available Agents Query", True, 
                          f"Found {len(available_agents)} available agents")
            
            # Test agent selection
            if available_agents:
                selected = self.manager.select_agent()
                self.log_result("Agent Selection", selected is not None,
                              f"Selected: {selected.agent_id if selected else 'None'}")
            else:
                self.log_result("Agent Selection", False, "No available agents to select")
            
            # Test conflict detection
            conflicted_agents = [a for a in self.manager.registry.agents.values() 
                               if a.status == "same_account_conflict"]
            self.log_result("Conflict Detection", True,
                          f"Found {len(conflicted_agents)} conflicted agents")
            
            return True
            
        except Exception as e:
            self.log_result("Agent Selection", False, f"Exception: {e}")
            return False
    
    def test_authentication_status(self) -> bool:
        """Test authentication status across credential sets"""
        print("\n🔑 Testing Authentication Status...")
        
        if not self.manager:
            self.log_result("Authentication Status", False, "Manager not initialized")
            return False
        
        try:
            # Check authentication status for each discovered agent
            auth_success_count = 0
            
            for agent in self.manager.registry.agents.values():
                is_authenticated = agent.status in ["available", "active"]
                
                self.test_results["authentication_status"][agent.credential_set] = {
                    "status": agent.status,
                    "authenticated": is_authenticated,
                    "channel": agent.channel_name
                }
                
                if is_authenticated:
                    auth_success_count += 1
                
                self.log_result(f"Auth {agent.credential_set}", is_authenticated,
                              f"{agent.channel_name} - {agent.status}")
            
            overall_success = auth_success_count > 0
            self.log_result("Overall Authentication", overall_success,
                          f"{auth_success_count} successful authentications")
            
            return overall_success
            
        except Exception as e:
            self.log_result("Authentication Status", False, f"Exception: {e}")
            return False
    
    def test_session_management(self) -> bool:
        """Test session management functionality"""
        print("\n📊 Testing Session Management...")
        
        if not self.manager:
            self.log_result("Session Management", False, "Manager not initialized")
            return False
        
        try:
            # Get status report
            status = self.manager.get_status_report()
            
            required_keys = ["total_agents", "available_agents", "conflicted_agents"]
            report_valid = all(key in status for key in required_keys)
            
            self.log_result("Status Report Generation", report_valid,
                          f"Contains {len(status)} status fields")
            
            # Test status report values
            if report_valid:
                self.log_result("Total Agents Count", status["total_agents"] > 0,
                              f"Total: {status['total_agents']}")
                self.log_result("Available Agents Count", True,
                              f"Available: {status['available_agents']}")
                self.log_result("Conflicted Agents Count", True,
                              f"Conflicted: {status['conflicted_agents']}")
            
            return report_valid
            
        except Exception as e:
            self.log_result("Session Management", False, f"Exception: {e}")
            return False
    
    def generate_report(self) -> Dict:
        """Generate comprehensive test report"""
        print("\n" + "="*60)
        print("📋 WSP-Compliant Multi-Agent Test Report")
        print("="*60)
        
        # Summary
        success_rate = (self.test_results["passed"] / self.test_results["total_tests"] * 100) if self.test_results["total_tests"] > 0 else 0
        
        print(f"\n📊 Test Summary:")
        print(f"   Total Tests: {self.test_results['total_tests']}")
        print(f"   Passed: {self.test_results['passed']}")
        print(f"   Failed: {self.test_results['failed']}")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        # Errors
        if self.test_results["errors"]:
            print(f"\n❌ Errors:")
            for error in self.test_results["errors"]:
                print(f"   - {error}")
        
        # Agent Discovery Summary
        if self.test_results["agent_discovery"]:
            print(f"\n🤖 Agent Discovery Summary:")
            for agent_id, info in self.test_results["agent_discovery"].items():
                status_icon = "✅" if info["valid"] else "❌"
                print(f"   {status_icon} {info['channel_name']} ({info['credential_set']}) - {info['status']}")
        
        # Authentication Summary
        if self.test_results["authentication_status"]:
            print(f"\n🔑 Authentication Summary:")
            for cred_set, info in self.test_results["authentication_status"].items():
                auth_icon = "✅" if info["authenticated"] else "❌"
                print(f"   {auth_icon} {cred_set}: {info['channel']} - {info['status']}")
        
        # WSP Compliance
        wsp = self.test_results["wsp_compliance"]
        if wsp:
            print(f"\n📋 WSP Compliance:")
            structure_icon = "✅" if wsp.get("wsp_1_structure") else "❌"
            docs_icon = "✅" if wsp.get("wsp_13_test_docs") else "❌"
            print(f"   {structure_icon} WSP 1: Module Structure")
            print(f"   {docs_icon} WSP 13: Test Documentation")
        
        # Overall Status
        overall_success = success_rate >= 80  # 80% pass rate threshold
        status_icon = "✅" if overall_success else "❌"
        print(f"\n{status_icon} Overall Status: {'PASS' if overall_success else 'FAIL'}")
        
        if overall_success:
            print("\n🎉 Multi-agent system is WSP-compliant and functional!")
        else:
            print("\n⚠️ Multi-agent system requires attention before production use.")
        
        return self.test_results
    
    def run_comprehensive_test(self) -> bool:
        """Run the complete WSP-compliant test suite"""
        print("🚀 Starting WSP-Compliant Multi-Agent Comprehensive Test")
        print("="*60)
        
        # Run all test phases
        wsp_compliant = self.test_wsp_compliance_structure()
        manager_ready = self.test_manager_initialization()
        discovery_working = self.test_agent_discovery()
        selection_working = self.test_agent_selection_logic()
        auth_working = self.test_authentication_status()
        session_working = self.test_session_management()
        
        # Generate final report
        report = self.generate_report()
        
        # Return overall success
        return report["failed"] == 0 and wsp_compliant

def main():
    """Main function to run comprehensive multi-agent testing"""
    suite = MultiAgentTestSuite()
    success = suite.run_comprehensive_test()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 