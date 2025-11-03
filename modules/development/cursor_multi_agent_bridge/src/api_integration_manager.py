"""
API Integration Manager
Real API connections for visible multi-agent demonstrations

Integrates Claude API, Grok API, and other services for 012 validation.
WSP Compliance: WSP 50, WSP 11, WSP 22
"""

import os
import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import aiohttp
import sys

# Add parent directory for imports
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest

logger = logging.getLogger(__name__)


@dataclass
class APIResponse:
    """Standardized API response structure"""
    service: str
    status: str
    data: Dict[str, Any]
    timestamp: datetime
    processing_time: float
    confidence: float = 0.0


class APIIntegrationManager:
    """Manages real API integrations for visible demonstrations"""
    
    def __init__(self):
        self.env_file = Path(__file__).parent.parent.parent.parent.parent / ".env"
        self.api_keys = self._load_api_keys()
        self.wsp_coordinator = WSPSubAgentCoordinator()
        self.session = None
        self.api_usage_log = []
        
        logger.info("API Integration Manager initialized")
    
    def _load_api_keys(self) -> Dict[str, str]:
        """Load API keys from .env file (WSP 50 - verify before use)"""
        api_keys = {}
        
        if not self.env_file.exists():
            logger.error(f"WSP 50 Violation: .env file not found at {self.env_file}")
            return api_keys
        
        try:
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        api_keys[key.strip()] = value.strip()
            
            # Verify required keys exist
            required_keys = ['CLAUDE_API_KEY', 'GROK_API_KEY']
            missing_keys = [key for key in required_keys if key not in api_keys or not api_keys[key]]
            
            if missing_keys:
                logger.warning(f"Missing API keys: {missing_keys}")
            else:
                logger.info("All required API keys loaded successfully")
                
        except Exception as e:
            logger.error(f"Failed to load API keys: {e}")
        
        return api_keys
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_claude_api_connection(self) -> APIResponse:
        """Test real Claude API connection for 012 validation"""
        start_time = datetime.now()
        
        claude_key = self.api_keys.get('CLAUDE_API_KEY')
        if not claude_key:
            return APIResponse(
                service="claude",
                status="error",
                data={"error": "Claude API key not found"},
                timestamp=start_time,
                processing_time=0.0
            )
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                'Authorization': f'Bearer {claude_key}',
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            # Simple test request to Claude
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 100,
                "messages": [
                    {
                        "role": "user", 
                        "content": "Respond with 'Claude API Connected' to confirm connection"
                    }
                ]
            }
            
            async with self.session.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    return APIResponse(
                        service="claude",
                        status="success",
                        data={
                            "connected": True,
                            "model": payload["model"],
                            "response": data.get("content", [{}])[0].get("text", ""),
                            "usage": data.get("usage", {})
                        },
                        timestamp=start_time,
                        processing_time=processing_time,
                        confidence=1.0
                    )
                else:
                    error_data = await response.text()
                    return APIResponse(
                        service="claude",
                        status="error",
                        data={"error": f"HTTP {response.status}", "details": error_data},
                        timestamp=start_time,
                        processing_time=processing_time
                    )
                    
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return APIResponse(
                service="claude",
                status="error",
                data={"error": str(e)},
                timestamp=start_time,
                processing_time=processing_time
            )
    
    async def test_grok_api_connection(self) -> APIResponse:
        """Test Grok API connection"""
        start_time = datetime.now()
        
        grok_key = self.api_keys.get('GROK_API_KEY')
        if not grok_key:
            return APIResponse(
                service="grok",
                status="error",
                data={"error": "Grok API key not found"},
                timestamp=start_time,
                processing_time=0.0
            )
        
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            headers = {
                'Authorization': f'Bearer {grok_key}',
                'Content-Type': 'application/json'
            }
            
            # Test request to Grok (using OpenAI-compatible endpoint)
            payload = {
                "model": "grok-beta",
                "messages": [
                    {
                        "role": "user",
                        "content": "Respond with 'Grok API Connected' to confirm connection"
                    }
                ],
                "max_tokens": 100
            }
            
            async with self.session.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                if response.status == 200:
                    data = await response.json()
                    return APIResponse(
                        service="grok",
                        status="success",
                        data={
                            "connected": True,
                            "model": payload["model"],
                            "response": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                            "usage": data.get("usage", {})
                        },
                        timestamp=start_time,
                        processing_time=processing_time,
                        confidence=1.0
                    )
                else:
                    error_data = await response.text()
                    return APIResponse(
                        service="grok",
                        status="error",
                        data={"error": f"HTTP {response.status}", "details": error_data},
                        timestamp=start_time,
                        processing_time=processing_time
                    )
                    
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return APIResponse(
                service="grok",
                status="error",
                data={"error": str(e)},
                timestamp=start_time,
                processing_time=processing_time
            )
    
    async def demonstrate_api_agent_coordination(self) -> Dict[str, Any]:
        """Demonstrate real API + WSP agent coordination for 012 validation"""
        print("\n=== REAL API + WSP AGENT COORDINATION DEMO ===")
        demonstration_start = datetime.now()
        
        results = {
            "demonstration_start": demonstration_start.isoformat(),
            "api_tests": {},
            "wsp_agent_tests": {},
            "coordination_demo": {},
            "visible_proof": {}
        }
        
        # 1. Test real API connections
        print("\n--- Testing Real API Connections ---")
        
        claude_result = await self.test_claude_api_connection()
        grok_result = await self.test_grok_api_connection()
        
        results["api_tests"] = {
            "claude": {
                "status": claude_result.status,
                "connected": claude_result.data.get("connected", False),
                "response": claude_result.data.get("response", ""),
                "processing_time": claude_result.processing_time
            },
            "grok": {
                "status": grok_result.status,
                "connected": grok_result.data.get("connected", False),
                "response": grok_result.data.get("response", ""),
                "processing_time": grok_result.processing_time
            }
        }
        
        print(f"Claude API: {claude_result.status} - {claude_result.data.get('response', 'No response')}")
        print(f"Grok API: {grok_result.status} - {grok_result.data.get('response', 'No response')}")
        
        # 2. Test WSP agents with visible output
        print("\n--- Testing WSP Agent Capabilities ---")
        
        wsp_tests = [
            {
                "agent": "compliance",
                "task": "pre_action_verification",
                "context": {"file_path": str(self.env_file), "action": "read"}
            },
            {
                "agent": "documentation", 
                "task": "update_modlog",
                "context": {
                    "module_path": "modules/development/cursor_multi_agent_bridge",
                    "changes": ["Real API integration", "Visible demonstration for 012"]
                }
            },
            {
                "agent": "testing",
                "task": "validate_test_structure",
                "context": {"module_path": "modules/development/cursor_multi_agent_bridge"}
            }
        ]
        
        wsp_results = []
        for test in wsp_tests:
            request = WSPSubAgentRequest(
                agent_type=test["agent"],
                task_type=test["task"],
                content=f"Demo test: {test['task']}",
                context=test["context"]
            )
            
            result = await self.wsp_coordinator.process_request(test["agent"], request)
            wsp_results.append({
                "agent": test["agent"],
                "status": result.status,
                "confidence": result.confidence,
                "suggestions_count": len(result.suggestions),
                "processing_time": result.processing_time
            })
            
            print(f"WSP {test['agent']}: {result.status} (confidence: {result.confidence:.1%})")
        
        results["wsp_agent_tests"] = wsp_results
        
        # 3. Demonstrate coordination (visible proof for 012)
        print("\n--- Multi-Agent Coordination Demonstration ---")
        
        coordination_requests = [
            ("compliance", WSPSubAgentRequest(
                agent_type="compliance",
                task_type="check_module_compliance",
                content="Full compliance audit for demo",
                context={"module_path": "modules/development/cursor_multi_agent_bridge"}
            )),
            ("documentation", WSPSubAgentRequest(
                agent_type="documentation",
                task_type="check_documentation",
                content="Documentation completeness check",
                context={"module_path": "modules/development/cursor_multi_agent_bridge"}
            ))
        ]
        
        coordination_results = await self.wsp_coordinator.coordinate_multiple_agents(coordination_requests)
        
        coordination_summary = {
            "total_agents": len(coordination_requests),
            "successful_agents": sum(1 for r in coordination_results if r.status == "success"),
            "avg_confidence": sum(r.confidence for r in coordination_results) / len(coordination_results),
            "total_processing_time": sum(r.processing_time for r in coordination_results)
        }
        
        results["coordination_demo"] = coordination_summary
        
        print(f"Coordination: {coordination_summary['successful_agents']}/{coordination_summary['total_agents']} successful")
        print(f"Average confidence: {coordination_summary['avg_confidence']:.1%}")
        
        # 4. Generate visible proof for 012
        total_time = (datetime.now() - demonstration_start).total_seconds()
        
        visible_proof = {
            "timestamp": datetime.now().isoformat(),
            "total_demonstration_time": total_time,
            "apis_working": sum(1 for api in results["api_tests"].values() if api["status"] == "success"),
            "wsp_agents_working": sum(1 for agent in results["wsp_agent_tests"] if agent["status"] == "success"),
            "coordination_working": coordination_summary["successful_agents"] == coordination_summary["total_agents"],
            "overall_status": "OPERATIONAL" if (
                results["api_tests"]["claude"]["status"] == "success" and
                coordination_summary["successful_agents"] == coordination_summary["total_agents"]
            ) else "PARTIAL"
        }
        
        results["visible_proof"] = visible_proof
        
        print(f"\n=== VISIBLE PROOF FOR 012 ===")
        print(f"APIs Working: {visible_proof['apis_working']}/2")
        print(f"WSP Agents Working: {visible_proof['wsp_agents_working']}/{len(wsp_tests)}")
        print(f"Coordination Working: {visible_proof['coordination_working']}")
        print(f"Overall Status: {visible_proof['overall_status']}")
        print(f"Total Demo Time: {visible_proof['total_demonstration_time']:.2f}s")
        
        # Save visible proof
        await self._save_demonstration_proof(results)
        
        return results
    
    async def _save_demonstration_proof(self, results: Dict[str, Any]):
        """Save demonstration proof for 012 validation"""
        proof_file = Path(__file__).parent.parent / "memory" / "api_demonstration_proof.json"
        proof_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(proof_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"Demonstration proof saved: {proof_file}")
        except Exception as e:
            print(f"Failed to save proof: {e}")
    
    async def test_enhanced_error_handling(self) -> Dict[str, Any]:
        """Test the improved error handling (addressing audit findings)"""
        print("\n=== TESTING ENHANCED ERROR HANDLING ===")
        
        # Test invalid task types (should now handle gracefully)
        error_tests = [
            {"agent": "compliance", "invalid_task": "invalid_compliance_task"},
            {"agent": "documentation", "invalid_task": "invalid_doc_task"},
            {"agent": "testing", "invalid_task": "invalid_test_task"}
        ]
        
        error_results = []
        
        for test in error_tests:
            request = WSPSubAgentRequest(
                agent_type=test["agent"],
                task_type=test["invalid_task"],
                content="Error handling test",
                context={}
            )
            
            result = await self.wsp_coordinator.process_request(test["agent"], request)
            
            error_results.append({
                "agent": test["agent"],
                "invalid_task": test["invalid_task"],
                "status": result.status,
                "error_handled": result.status == "error" and "error" in result.response_data,
                "has_valid_types": "valid_types" in result.response_data,
                "graceful_degradation": result.confidence == 0.0 and len(result.violations) > 0
            })
            
            status_emoji = "[OK]" if result.status == "error" else "[FAIL]"
            print(f"{status_emoji} {test['agent']}: Error handling {'PASS' if result.status == 'error' else 'FAIL'}")
        
        improvement_score = sum(1 for r in error_results if r["error_handled"]) / len(error_results)
        print(f"\nError Handling Improvement: {improvement_score:.1%}")
        
        return {
            "error_tests": error_results,
            "improvement_score": improvement_score,
            "audit_issue_resolved": improvement_score >= 0.8
        }


async def main():
    """Run visible demonstration for 012 validation"""
    async with APIIntegrationManager() as api_manager:
        # Run comprehensive demonstration
        demo_results = await api_manager.demonstrate_api_agent_coordination()
        
        # Test error handling improvements
        error_results = await api_manager.test_enhanced_error_handling()
        
        print(f"\n=== FINAL STATUS FOR 012 ===")
        print(f"Real APIs: {demo_results['visible_proof']['overall_status']}")
        print(f"Error Handling: {'IMPROVED' if error_results['audit_issue_resolved'] else 'NEEDS_WORK'}")
        print(f"Ready for WRE Integration: {demo_results['visible_proof']['overall_status'] == 'OPERATIONAL'}")
        
        return demo_results, error_results


if __name__ == "__main__":
    asyncio.run(main())