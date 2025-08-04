"""
WSP Agent Audit System
Comprehensive audit of all WSP 54 agents and their duties

This performs a complete audit to verify agents are performing
their assigned duties according to WSP 54 specifications.
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest
from claude_code_integration import ClaudeCodeIntegration


class WSPAgentAuditor:
    """Comprehensive WSP agent audit system"""
    
    def __init__(self):
        self.coordinator = WSPSubAgentCoordinator()
        self.claude_integration = ClaudeCodeIntegration()
        self.audit_results = {}
        self.audit_timestamp = datetime.now()
        self.module_path = "modules/development/cursor_multi_agent_bridge"
    
    async def perform_comprehensive_audit(self) -> Dict[str, Any]:
        """Perform comprehensive audit of all WSP agents"""
        print("=== WSP AGENT COMPREHENSIVE AUDIT ===")
        print(f"Audit Time: {self.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Target Module: {self.module_path}")
        
        # Initialize audit results
        self.audit_results = {
            "audit_metadata": {
                "timestamp": self.audit_timestamp.isoformat(),
                "module_path": self.module_path,
                "auditor": "WSPAgentAuditor",
                "wsp_protocols": ["WSP_54", "WSP_22", "WSP_11", "WSP_50"]
            },
            "agent_performance": {},
            "compliance_status": {},
            "coordination_metrics": {},
            "overall_assessment": {}
        }
        
        # 1. Audit individual agent performance
        await self._audit_individual_agents()
        
        # 2. Audit agent coordination capabilities
        await self._audit_agent_coordination()
        
        # 3. Audit WSP protocol compliance
        await self._audit_wsp_compliance()
        
        # 4. Audit Claude Code integration
        await self._audit_claude_integration()
        
        # 5. Generate overall assessment
        self._generate_overall_assessment()
        
        # 6. Display audit results
        self._display_audit_results()
        
        return self.audit_results
    
    async def _audit_individual_agents(self):
        """Audit each agent individually"""
        print("\n--- INDIVIDUAL AGENT AUDIT ---")
        
        available_agents = list(self.coordinator.sub_agents.keys())
        
        for agent_type in available_agents:
            print(f"\nAuditing {agent_type.upper()} Agent:")
            
            # Test basic functionality
            basic_test = await self._test_agent_basic_functionality(agent_type)
            
            # Test response quality
            quality_test = await self._test_agent_response_quality(agent_type)
            
            # Test error handling
            error_test = await self._test_agent_error_handling(agent_type)
            
            # Compile agent results
            self.audit_results["agent_performance"][agent_type] = {
                "basic_functionality": basic_test,
                "response_quality": quality_test,
                "error_handling": error_test,
                "overall_score": self._calculate_agent_score(basic_test, quality_test, error_test)
            }
            
            print(f"  Overall Score: {self.audit_results['agent_performance'][agent_type]['overall_score']:.1%}")
    
    async def _test_agent_basic_functionality(self, agent_type: str) -> Dict[str, Any]:
        """Test basic agent functionality"""
        try:
            # Create appropriate test request for each agent type
            test_requests = {
                "compliance": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="check_module_compliance",
                    content="Basic functionality test",
                    context={"module_path": self.module_path}
                ),
                "documentation": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="check_documentation",
                    content="Basic functionality test",
                    context={"module_path": self.module_path}
                ),
                "testing": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="validate_test_structure",
                    content="Basic functionality test",
                    context={"module_path": self.module_path}
                )
            }
            
            request = test_requests.get(agent_type)
            if not request:
                return {"status": "error", "message": "Unknown agent type", "score": 0.0}
            
            start_time = datetime.now()
            response = await self.coordinator.process_request(agent_type, request)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "status": response.status,
                "processing_time": processing_time,
                "confidence": response.confidence,
                "has_suggestions": len(response.suggestions) > 0,
                "has_violations": len(response.violations) > 0,
                "score": 1.0 if response.status == "success" else 0.0
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e), "score": 0.0}
    
    async def _test_agent_response_quality(self, agent_type: str) -> Dict[str, Any]:
        """Test quality of agent responses"""
        try:
            # Test with more complex request
            quality_requests = {
                "compliance": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="validate_wsp_protocols",
                    content="Quality test: validate multiple protocols",
                    context={"protocols": ["WSP_54", "WSP_22", "WSP_50", "WSP_11"]}
                ),
                "documentation": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="update_modlog",
                    content="Quality test: complex modlog update",
                    context={
                        "module_path": self.module_path,
                        "changes": ["Agent audit implementation", "Performance testing", "Quality validation"]
                    }
                ),
                "testing": WSPSubAgentRequest(
                    agent_type=agent_type,
                    task_type="check_coverage",
                    content="Quality test: coverage analysis",
                    context={"module_path": self.module_path}
                )
            }
            
            request = quality_requests.get(agent_type)
            if not request:
                return {"status": "error", "message": "Unknown agent type", "score": 0.0}
            
            response = await self.coordinator.process_request(agent_type, request)
            
            # Evaluate response quality
            quality_score = 0.0
            quality_factors = []
            
            if response.status == "success":
                quality_score += 0.3
                quality_factors.append("successful_execution")
            
            if response.confidence >= 0.8:
                quality_score += 0.2
                quality_factors.append("high_confidence")
            
            if len(response.suggestions) >= 2:
                quality_score += 0.2
                quality_factors.append("useful_suggestions")
            
            if response.response_data and len(response.response_data) >= 3:
                quality_score += 0.2
                quality_factors.append("comprehensive_data")
            
            if response.processing_time < 1.0:
                quality_score += 0.1
                quality_factors.append("fast_processing")
            
            return {
                "status": response.status,
                "quality_score": quality_score,
                "quality_factors": quality_factors,
                "suggestions_count": len(response.suggestions),
                "violations_count": len(response.violations),
                "data_completeness": len(response.response_data) if response.response_data else 0,
                "score": quality_score
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e), "score": 0.0}
    
    async def _test_agent_error_handling(self, agent_type: str) -> Dict[str, Any]:
        """Test agent error handling capabilities"""
        try:
            # Create invalid request to test error handling
            invalid_request = WSPSubAgentRequest(
                agent_type=agent_type,
                task_type="invalid_task_type",
                content="Error handling test",
                context={"invalid_context": "test"}
            )
            
            response = await self.coordinator.process_request(agent_type, invalid_request)
            
            # Good error handling should return error status but not crash
            if response.status == "error" and "error" in response.response_data:
                return {
                    "status": "success",
                    "handles_errors": True,
                    "graceful_degradation": True,
                    "error_message": response.response_data.get("error", ""),
                    "score": 1.0
                }
            else:
                return {
                    "status": "warning",
                    "handles_errors": False,
                    "unexpected_response": response.status,
                    "score": 0.5
                }
                
        except Exception as e:
            return {
                "status": "error",
                "handles_errors": False,
                "crashed": True,
                "error_message": str(e),
                "score": 0.0
            }
    
    def _calculate_agent_score(self, basic: Dict, quality: Dict, error: Dict) -> float:
        """Calculate overall agent performance score"""
        basic_score = basic.get("score", 0.0)
        quality_score = quality.get("score", 0.0)
        error_score = error.get("score", 0.0)
        
        # Weighted average: basic 40%, quality 40%, error handling 20%
        return (basic_score * 0.4) + (quality_score * 0.4) + (error_score * 0.2)
    
    async def _audit_agent_coordination(self):
        """Audit multi-agent coordination capabilities"""
        print("\n--- AGENT COORDINATION AUDIT ---")
        
        try:
            # Test multi-agent coordination
            multi_requests = [
                ("compliance", WSPSubAgentRequest(
                    agent_type="compliance",
                    task_type="check_module_compliance",
                    content="Coordination test: compliance check",
                    context={"module_path": self.module_path}
                )),
                ("documentation", WSPSubAgentRequest(
                    agent_type="documentation",
                    task_type="check_documentation",
                    content="Coordination test: documentation check",
                    context={"module_path": self.module_path}
                )),
                ("testing", WSPSubAgentRequest(
                    agent_type="testing",
                    task_type="validate_test_structure",
                    content="Coordination test: testing validation",
                    context={"module_path": self.module_path}
                ))
            ]
            
            start_time = datetime.now()
            responses = await self.coordinator.coordinate_multiple_agents(multi_requests)
            coordination_time = (datetime.now() - start_time).total_seconds()
            
            # Analyze coordination results
            successful_agents = sum(1 for r in responses if r.status == "success")
            avg_confidence = sum(r.confidence for r in responses) / len(responses) if responses else 0
            
            coordination_score = (successful_agents / len(multi_requests)) * avg_confidence
            
            self.audit_results["coordination_metrics"] = {
                "total_agents": len(multi_requests),
                "successful_agents": successful_agents,
                "coordination_time": coordination_time,
                "average_confidence": avg_confidence,
                "coordination_score": coordination_score,
                "status": "success" if successful_agents == len(multi_requests) else "partial"
            }
            
            print(f"  Coordination Score: {coordination_score:.1%}")
            print(f"  Successful Agents: {successful_agents}/{len(multi_requests)}")
            print(f"  Average Confidence: {avg_confidence:.1%}")
            
        except Exception as e:
            self.audit_results["coordination_metrics"] = {
                "status": "error",
                "error_message": str(e),
                "coordination_score": 0.0
            }
            print(f"  Coordination Error: {e}")
    
    async def _audit_wsp_compliance(self):
        """Audit WSP protocol compliance"""
        print("\n--- WSP PROTOCOL COMPLIANCE AUDIT ---")
        
        compliance_tests = {
            "WSP_54": await self._test_wsp_54_compliance(),
            "WSP_22": await self._test_wsp_22_compliance(),
            "WSP_50": await self._test_wsp_50_compliance(),
            "WSP_11": await self._test_wsp_11_compliance()
        }
        
        overall_compliance = sum(test["score"] for test in compliance_tests.values()) / len(compliance_tests)
        
        self.audit_results["compliance_status"] = {
            "protocol_tests": compliance_tests,
            "overall_compliance": overall_compliance,
            "compliant_protocols": [p for p, test in compliance_tests.items() if test["score"] >= 0.8],
            "non_compliant_protocols": [p for p, test in compliance_tests.items() if test["score"] < 0.8]
        }
        
        print(f"  Overall WSP Compliance: {overall_compliance:.1%}")
        for protocol, test in compliance_tests.items():
            status = "PASS" if test["score"] >= 0.8 else "FAIL"
            print(f"  {protocol}: {status} ({test['score']:.1%})")
    
    async def _test_wsp_54_compliance(self) -> Dict[str, Any]:
        """Test WSP 54 Agent Duties compliance"""
        try:
            # Test if all required agent types are available
            required_agents = ["compliance", "documentation", "testing"]
            available_agents = list(self.coordinator.sub_agents.keys())
            
            agents_available = all(agent in available_agents for agent in required_agents)
            
            # Test agent coordination
            coordination_works = self.audit_results.get("coordination_metrics", {}).get("coordination_score", 0) > 0.5
            
            score = 1.0 if (agents_available and coordination_works) else 0.5
            
            return {
                "agents_available": agents_available,
                "coordination_works": coordination_works,
                "required_agents": required_agents,
                "available_agents": available_agents,
                "score": score,
                "status": "compliant" if score >= 0.8 else "non_compliant"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "score": 0.0}
    
    async def _test_wsp_22_compliance(self) -> Dict[str, Any]:
        """Test WSP 22 ModLog compliance"""
        try:
            request = WSPSubAgentRequest(
                agent_type="documentation",
                task_type="check_documentation",
                content="Test WSP 22 compliance",
                context={"module_path": self.module_path}
            )
            
            response = await self.coordinator.process_request("documentation", request)
            
            # Check if documentation agent can handle ModLog tasks
            modlog_capable = response.status == "success"
            score = 1.0 if modlog_capable else 0.0
            
            return {
                "modlog_capable": modlog_capable,
                "documentation_complete": response.response_data.get("documentation_complete", False),
                "score": score,
                "status": "compliant" if score >= 0.8 else "non_compliant"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "score": 0.0}
    
    async def _test_wsp_50_compliance(self) -> Dict[str, Any]:
        """Test WSP 50 Pre-Action Verification compliance"""
        try:
            request = WSPSubAgentRequest(
                agent_type="compliance",
                task_type="pre_action_verification",
                content="Test WSP 50 compliance",
                context={"file_path": __file__, "action": "test"}
            )
            
            response = await self.coordinator.process_request("compliance", request)
            
            verification_works = response.status == "success" and "verified" in response.response_data
            score = 1.0 if verification_works else 0.0
            
            return {
                "verification_works": verification_works,
                "can_verify_files": response.response_data.get("verified", False),
                "score": score,
                "status": "compliant" if score >= 0.8 else "non_compliant"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "score": 0.0}
    
    async def _test_wsp_11_compliance(self) -> Dict[str, Any]:
        """Test WSP 11 Interface compliance"""
        try:
            # Test if agents have proper interface standards
            interface_score = 0.0
            
            # Check if coordinator has proper status interface
            status = self.coordinator.get_coordinator_status()
            if "available_agents" in status:
                interface_score += 0.5
            
            # Check if agents respond with proper structure
            test_response = await self.coordinator.process_request("compliance", WSPSubAgentRequest(
                agent_type="compliance",
                task_type="validate_wsp_protocols",
                content="Interface test",
                context={"protocols": ["WSP_11"]}
            ))
            
            if hasattr(test_response, 'response_data') and test_response.response_data:
                interface_score += 0.5
            
            return {
                "proper_interfaces": interface_score >= 0.8,
                "coordinator_status_works": "available_agents" in status,
                "agent_response_structure": hasattr(test_response, 'response_data'),
                "score": interface_score,
                "status": "compliant" if interface_score >= 0.8 else "non_compliant"
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "score": 0.0}
    
    async def _audit_claude_integration(self):
        """Audit Claude Code integration"""
        print("\n--- CLAUDE CODE INTEGRATION AUDIT ---")
        
        try:
            # Test Claude integration capabilities
            integration_status = self.claude_integration.get_wsp_coordinator_status()
            
            claude_connected = integration_status.get("claude_integration", {}).get("connected", False)
            agents_available = len(integration_status.get("available_agents", [])) > 0
            
            integration_score = 0.0
            if claude_connected:
                integration_score += 0.5
            if agents_available:
                integration_score += 0.5
            
            self.audit_results["claude_integration"] = {
                "connected": claude_connected,
                "agents_available": agents_available,
                "integration_score": integration_score,
                "status": "operational" if integration_score >= 0.5 else "limited"
            }
            
            print(f"  Claude Integration Score: {integration_score:.1%}")
            print(f"  Connected: {claude_connected}")
            print(f"  Agents Available: {agents_available}")
            
        except Exception as e:
            self.audit_results["claude_integration"] = {
                "status": "error",
                "error_message": str(e),
                "integration_score": 0.0
            }
            print(f"  Integration Error: {e}")
    
    def _generate_overall_assessment(self):
        """Generate overall audit assessment"""
        # Calculate overall scores
        agent_scores = [perf["overall_score"] for perf in self.audit_results["agent_performance"].values()]
        avg_agent_score = sum(agent_scores) / len(agent_scores) if agent_scores else 0
        
        coordination_score = self.audit_results["coordination_metrics"].get("coordination_score", 0)
        compliance_score = self.audit_results["compliance_status"].get("overall_compliance", 0)
        integration_score = self.audit_results.get("claude_integration", {}).get("integration_score", 0)
        
        # Weighted overall score
        overall_score = (
            avg_agent_score * 0.4 +
            coordination_score * 0.3 +
            compliance_score * 0.2 +
            integration_score * 0.1
        )
        
        # Determine assessment level
        if overall_score >= 0.9:
            assessment = "EXCELLENT"
        elif overall_score >= 0.8:
            assessment = "GOOD"
        elif overall_score >= 0.6:
            assessment = "ADEQUATE"
        else:
            assessment = "NEEDS_IMPROVEMENT"
        
        self.audit_results["overall_assessment"] = {
            "overall_score": overall_score,
            "assessment_level": assessment,
            "agent_performance_avg": avg_agent_score,
            "coordination_score": coordination_score,
            "compliance_score": compliance_score,
            "integration_score": integration_score,
            "recommendations": self._generate_recommendations(overall_score)
        }
    
    def _generate_recommendations(self, overall_score: float) -> List[str]:
        """Generate improvement recommendations"""
        recommendations = []
        
        if overall_score < 0.9:
            recommendations.append("Continue monitoring agent performance")
        
        if self.audit_results["compliance_status"].get("overall_compliance", 0) < 0.8:
            recommendations.append("Improve WSP protocol compliance")
        
        if self.audit_results["coordination_metrics"].get("coordination_score", 0) < 0.8:
            recommendations.append("Enhance multi-agent coordination")
        
        if not recommendations:
            recommendations.append("Maintain current high performance standards")
        
        return recommendations
    
    def _display_audit_results(self):
        """Display comprehensive audit results"""
        print("\n" + "="*60)
        print("WSP AGENT AUDIT RESULTS")
        print("="*60)
        
        assessment = self.audit_results["overall_assessment"]
        print(f"OVERALL ASSESSMENT: {assessment['assessment_level']}")
        print(f"OVERALL SCORE: {assessment['overall_score']:.1%}")
        
        print(f"\nCOMPONENT SCORES:")
        print(f"  Agent Performance: {assessment['agent_performance_avg']:.1%}")
        print(f"  Coordination: {assessment['coordination_score']:.1%}")
        print(f"  WSP Compliance: {assessment['compliance_score']:.1%}")
        print(f"  Claude Integration: {assessment['integration_score']:.1%}")
        
        print(f"\nRECOMMENDATIONS:")
        for rec in assessment['recommendations']:
            print(f"  - {rec}")
        
        print(f"\nAUDIT COMPLETED: {self.audit_timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)


async def main():
    """Run comprehensive WSP agent audit"""
    auditor = WSPAgentAuditor()
    audit_results = await auditor.perform_comprehensive_audit()
    
    # Save audit results
    audit_file = Path(__file__).parent.parent / "memory" / "wsp_agent_audit_results.json"
    audit_file.parent.mkdir(exist_ok=True)
    
    with open(audit_file, 'w') as f:
        json.dump(audit_results, f, indent=2, default=str)
    
    print(f"\nAudit results saved to: {audit_file}")
    return audit_results


if __name__ == "__main__":
    asyncio.run(main())