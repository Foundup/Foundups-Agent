"""
Visible Demonstration for 012 Validation
Real working proof of WSP agents and improvements

This creates visible evidence that the system is working
using only standard library components.
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports  
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest


class VisibleDemo012:
    """Create visible proof for 012 that the system works"""
    
    def __init__(self):
        self.coordinator = WSPSubAgentCoordinator()
        self.demo_start = datetime.now()
        self.env_file = Path(__file__).parent.parent.parent.parent.parent / ".env"
        
    def verify_api_keys_available(self) -> Dict[str, Any]:
        """Verify API keys are available (WSP 50 verification)"""
        print("=== API KEY VERIFICATION ===")
        
        if not self.env_file.exists():
            return {"status": "error", "message": "No .env file found"}
        
        api_keys_found = {}
        try:
            with open(self.env_file, 'r') as f:
                content = f.read()
                
                # Check for required API keys
                required_keys = ['CLAUDE_API_KEY', 'GROK_API_KEY', 'OPENAI_API_KEY', 'GEMINI_API_KEY']
                
                for key in required_keys:
                    if key in content and f"{key}=" in content:
                        # Extract the value (safely)
                        for line in content.split('\n'):
                            if line.startswith(f"{key}="):
                                value = line.split('=', 1)[1].strip()
                                if value and value != "":
                                    api_keys_found[key] = f"[OK] Available (ends with: ...{value[-4:]})" if len(value) > 4 else "[OK] Available"
                                    print(f"{key}: [OK] FOUND")
                                else:
                                    api_keys_found[key] = "[FAIL] Empty"
                                    print(f"{key}: [FAIL] EMPTY")
                                break
                    else:
                        api_keys_found[key] = "[FAIL] Missing"
                        print(f"{key}: [FAIL] MISSING")
                        
        except Exception as e:
            return {"status": "error", "message": f"Failed to read .env: {e}"}
        
        available_count = sum(1 for status in api_keys_found.values() if "[OK]" in status)
        
        return {
            "status": "success",
            "api_keys_found": api_keys_found,
            "available_count": available_count,
            "total_keys": len(required_keys),
            "ready_for_api_integration": available_count >= 2
        }
    
    async def test_improved_error_handling(self) -> Dict[str, Any]:
        """Test the improved error handling that addresses audit findings"""
        print("\n=== TESTING IMPROVED ERROR HANDLING ===")
        
        # Test each agent with invalid task types
        error_tests = [
            {"agent": "compliance", "invalid_task": "completely_invalid_task"},
            {"agent": "documentation", "invalid_task": "nonsense_task"},
            {"agent": "testing", "invalid_task": "fake_task_type"}
        ]
        
        results = []
        
        for test in error_tests:
            print(f"\nTesting {test['agent']} with invalid task '{test['invalid_task']}':")
            
            request = WSPSubAgentRequest(
                agent_type=test["agent"],
                task_type=test["invalid_task"],
                content="Error handling test",
                context={}
            )
            
            try:
                result = await self.coordinator.process_request(test["agent"], request)
                
                # Check if error was handled properly
                proper_error = (
                    result.status == "error" and
                    "error" in result.response_data and
                    "valid_types" in result.response_data and
                    result.confidence == 0.0 and
                    len(result.violations) > 0
                )
                
                results.append({
                    "agent": test["agent"],
                    "invalid_task": test["invalid_task"],
                    "status": result.status,
                    "proper_error_handling": proper_error,
                    "has_error_message": "error" in result.response_data,
                    "has_valid_types": "valid_types" in result.response_data,
                    "has_violations": len(result.violations) > 0,
                    "confidence_zero": result.confidence == 0.0
                })
                
                status_emoji = "[OK]" if proper_error else "[FAIL]"
                print(f"  {status_emoji} Status: {result.status}")
                print(f"  {status_emoji} Error Message: {result.response_data.get('error', 'None')}")
                print(f"  {status_emoji} Valid Types Provided: {result.response_data.get('valid_types', [])}")
                print(f"  {status_emoji} Proper Error Handling: {proper_error}")
                
            except Exception as e:
                results.append({
                    "agent": test["agent"],
                    "invalid_task": test["invalid_task"],
                    "status": "exception",
                    "proper_error_handling": False,
                    "exception": str(e)
                })
                print(f"  [FAIL] Exception occurred: {e}")
        
        # Calculate improvement score
        proper_handling_count = sum(1 for r in results if r.get("proper_error_handling", False))
        improvement_score = proper_handling_count / len(results)
        
        print(f"\n[DATA] Error Handling Results:")
        print(f"  Properly Handled: {proper_handling_count}/{len(results)}")
        print(f"  Improvement Score: {improvement_score:.1%}")
        print(f"  Audit Issue Resolved: {'[OK] YES' if improvement_score >= 0.8 else '[FAIL] NO'}")
        
        return {
            "error_tests": results,
            "improvement_score": improvement_score,
            "audit_issue_resolved": improvement_score >= 0.8,
            "previous_score": 0.5,  # From audit
            "improvement": improvement_score - 0.5
        }
    
    async def demonstrate_wsp_agent_capabilities(self) -> Dict[str, Any]:
        """Demonstrate working WSP agent capabilities"""
        print("\n=== WSP AGENT CAPABILITIES DEMONSTRATION ===")
        
        # Test each agent with valid tasks
        agent_tests = [
            {
                "agent": "compliance",
                "task": "check_module_compliance",
                "context": {"module_path": "modules/development/cursor_multi_agent_bridge"},
                "expected": "compliance checking"
            },
            {
                "agent": "compliance", 
                "task": "pre_action_verification",
                "context": {"file_path": str(self.env_file), "action": "read"},
                "expected": "pre-action verification"
            },
            {
                "agent": "documentation",
                "task": "update_modlog",
                "context": {
                    "module_path": "modules/development/cursor_multi_agent_bridge",
                    "changes": ["Visible demonstration", "Error handling improvements", "API integration"]
                },
                "expected": "modlog management"
            },
            {
                "agent": "documentation",
                "task": "check_documentation", 
                "context": {"module_path": "modules/development/cursor_multi_agent_bridge"},
                "expected": "documentation validation"
            },
            {
                "agent": "testing",
                "task": "validate_test_structure",
                "context": {"module_path": "modules/development/cursor_multi_agent_bridge"},
                "expected": "test structure validation"
            },
            {
                "agent": "testing",
                "task": "check_coverage",
                "context": {"module_path": "modules/development/cursor_multi_agent_bridge"},
                "expected": "coverage analysis"
            }
        ]
        
        results = []
        
        for test in agent_tests:
            print(f"\n[BOT] Testing {test['agent']} - {test['task']}:")
            
            request = WSPSubAgentRequest(
                agent_type=test["agent"],
                task_type=test["task"],
                content=f"Demo: {test['expected']}",
                context=test["context"]
            )
            
            try:
                start_time = datetime.now()
                result = await self.coordinator.process_request(test["agent"], request)
                processing_time = (datetime.now() - start_time).total_seconds()
                
                results.append({
                    "agent": test["agent"],
                    "task": test["task"],
                    "status": result.status,
                    "confidence": result.confidence,
                    "processing_time": processing_time,
                    "suggestions_count": len(result.suggestions),
                    "violations_count": len(result.violations),
                    "has_response_data": bool(result.response_data),
                    "working": result.status == "success" and result.confidence > 0.5
                })
                
                status_emoji = "[OK]" if result.status == "success" else "[FAIL]"
                print(f"  {status_emoji} Status: {result.status}")
                print(f"  [DATA] Confidence: {result.confidence:.1%}")
                print(f"  ⏱️ Time: {processing_time:.3f}s")
                print(f"  [IDEA] Suggestions: {len(result.suggestions)}")
                print(f"  [U+26A0]️ Violations: {len(result.violations)}")
                
                if result.suggestions:
                    print(f"  [NOTE] Sample Suggestion: {result.suggestions[0]}")
                
            except Exception as e:
                results.append({
                    "agent": test["agent"],
                    "task": test["task"],
                    "status": "exception",
                    "working": False,
                    "exception": str(e)
                })
                print(f"  [FAIL] Exception: {e}")
        
        # Calculate performance metrics
        working_agents = sum(1 for r in results if r.get("working", False))
        avg_confidence = sum(r.get("confidence", 0) for r in results) / len(results)
        avg_processing_time = sum(r.get("processing_time", 0) for r in results) / len(results)
        
        print(f"\n[DATA] Agent Performance Summary:")
        print(f"  Working Agents: {working_agents}/{len(results)}")
        print(f"  Average Confidence: {avg_confidence:.1%}")
        print(f"  Average Processing Time: {avg_processing_time:.3f}s")
        print(f"  Overall Status: {'[OK] OPERATIONAL' if working_agents == len(results) else '[U+26A0]️ PARTIAL'}")
        
        return {
            "agent_tests": results,
            "working_agents": working_agents,
            "total_tests": len(results),
            "average_confidence": avg_confidence,
            "average_processing_time": avg_processing_time,
            "fully_operational": working_agents == len(results)
        }
    
    async def demonstrate_multi_agent_coordination(self) -> Dict[str, Any]:
        """Demonstrate multi-agent coordination capabilities"""
        print("\n=== MULTI-AGENT COORDINATION DEMONSTRATION ===")
        
        # Create coordination requests
        coordination_requests = [
            ("compliance", WSPSubAgentRequest(
                agent_type="compliance",
                task_type="check_module_compliance",
                content="Coordination demo: compliance check",
                context={"module_path": "modules/development/cursor_multi_agent_bridge"}
            )),
            ("documentation", WSPSubAgentRequest(
                agent_type="documentation",
                task_type="check_documentation",
                content="Coordination demo: documentation check",
                context={"module_path": "modules/development/cursor_multi_agent_bridge"}
            )),
            ("testing", WSPSubAgentRequest(
                agent_type="testing",
                task_type="validate_test_structure",
                content="Coordination demo: test validation",
                context={"module_path": "modules/development/cursor_multi_agent_bridge"}
            ))
        ]
        
        print(f"[REFRESH] Coordinating {len(coordination_requests)} agents simultaneously...")
        
        try:
            start_time = datetime.now()
            results = await self.coordinator.coordinate_multiple_agents(coordination_requests)
            coordination_time = (datetime.now() - start_time).total_seconds()
            
            successful_agents = sum(1 for r in results if r.status == "success")
            avg_confidence = sum(r.confidence for r in results) / len(results) if results else 0
            
            print(f"\n[DATA] Coordination Results:")
            print(f"  Total Agents: {len(coordination_requests)}")
            print(f"  Successful: {successful_agents}")
            print(f"  Coordination Time: {coordination_time:.3f}s")
            print(f"  Average Confidence: {avg_confidence:.1%}")
            
            for result in results:
                status_emoji = "[OK]" if result.status == "success" else "[FAIL]"
                print(f"  {status_emoji} {result.agent_type}: {result.status} ({result.confidence:.1%})")
            
            coordination_successful = successful_agents == len(coordination_requests)
            print(f"  [TARGET] Coordination Status: {'[OK] SUCCESS' if coordination_successful else '[FAIL] PARTIAL'}")
            
            return {
                "total_agents": len(coordination_requests),
                "successful_agents": successful_agents,
                "coordination_time": coordination_time,
                "average_confidence": avg_confidence,
                "coordination_successful": coordination_successful,
                "individual_results": [
                    {
                        "agent": r.agent_type,
                        "status": r.status,
                        "confidence": r.confidence,
                        "processing_time": r.processing_time
                    } for r in results
                ]
            }
            
        except Exception as e:
            print(f"[FAIL] Coordination failed: {e}")
            return {
                "coordination_successful": False,
                "error": str(e)
            }
    
    async def run_complete_demonstration(self) -> Dict[str, Any]:
        """Run complete visible demonstration for 012"""
        print("[ROCKET] COMPLETE WSP SYSTEM DEMONSTRATION FOR 012 VALIDATION")
        print("=" * 60)
        
        demo_results = {
            "demonstration_start": self.demo_start.isoformat(),
            "api_verification": {},
            "error_handling_test": {},
            "agent_capabilities": {},
            "coordination_demo": {},
            "overall_assessment": {}
        }
        
        # 1. API Key Verification
        demo_results["api_verification"] = self.verify_api_keys_available()
        
        # 2. Error Handling Test
        demo_results["error_handling_test"] = await self.test_improved_error_handling()
        
        # 3. Agent Capabilities
        demo_results["agent_capabilities"] = await self.demonstrate_wsp_agent_capabilities()
        
        # 4. Coordination Demo
        demo_results["coordination_demo"] = await self.demonstrate_multi_agent_coordination()
        
        # 5. Overall Assessment
        total_time = (datetime.now() - self.demo_start).total_seconds()
        
        # Calculate overall scores
        api_ready = demo_results["api_verification"].get("ready_for_api_integration", False)
        error_handling_improved = demo_results["error_handling_test"].get("audit_issue_resolved", False)
        agents_operational = demo_results["agent_capabilities"].get("fully_operational", False)
        coordination_working = demo_results["coordination_demo"].get("coordination_successful", False)
        
        overall_score = sum([api_ready, error_handling_improved, agents_operational, coordination_working]) / 4
        
        demo_results["overall_assessment"] = {
            "total_demonstration_time": total_time,
            "api_keys_ready": api_ready,
            "error_handling_improved": error_handling_improved,
            "agents_operational": agents_operational,
            "coordination_working": coordination_working,
            "overall_score": overall_score,
            "ready_for_wre_integration": overall_score >= 0.75,
            "system_status": "OPERATIONAL" if overall_score >= 0.9 else "READY" if overall_score >= 0.75 else "NEEDS_WORK"
        }
        
        # Display final results for 012
        print("\n" + "=" * 60)
        print("[TARGET] FINAL DEMONSTRATION RESULTS FOR 012")
        print("=" * 60)
        
        print(f"[DATA] Overall System Score: {overall_score:.1%}")
        print(f"[U+1F511] API Keys Ready: {'[OK]' if api_ready else '[FAIL]'}")
        print(f"[U+1F6E0]️ Error Handling Improved: {'[OK]' if error_handling_improved else '[FAIL]'}")
        print(f"[BOT] Agents Operational: {'[OK]' if agents_operational else '[FAIL]'}")
        print(f"[REFRESH] Coordination Working: {'[OK]' if coordination_working else '[FAIL]'}")
        print(f"[ROCKET] Ready for WRE Integration: {'[OK]' if demo_results['overall_assessment']['ready_for_wre_integration'] else '[FAIL]'}")
        print(f"[UP] System Status: {demo_results['overall_assessment']['system_status']}")
        print(f"⏱️ Total Demo Time: {total_time:.2f}s")
        
        # Save proof for 012
        await self._save_demonstration_proof(demo_results)
        
        return demo_results
    
    async def _save_demonstration_proof(self, results: Dict[str, Any]):
        """Save demonstration proof for 012 validation"""
        proof_file = Path(__file__).parent.parent / "memory" / "visible_demo_012_proof.json"
        proof_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(proof_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n[U+1F4C4] Demonstration proof saved: {proof_file}")
        except Exception as e:
            print(f"[FAIL] Failed to save proof: {e}")


async def main():
    """Run visible demonstration for 012 validation"""
    demo = VisibleDemo012()
    results = await demo.run_complete_demonstration()
    
    return results


if __name__ == "__main__":
    asyncio.run(main())