"""
Live WSP Sub-Agents Assistant
Running WSP sub-agents during actual development work
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest


async def run_live_subagents():
    """Run WSP sub-agents to assist with current development"""
    print("=== Activating WSP Sub-Agents ===")
    
    # Initialize WSP coordinator
    coordinator = WSPSubAgentCoordinator()
    
    print(f"Available agents: {list(coordinator.sub_agents.keys())}")
    
    # 1. Check WSP compliance for current module
    print("\n--- WSP Compliance Check ---")
    compliance_request = WSPSubAgentRequest(
        agent_type="compliance",
        task_type="check_module_compliance", 
        content="Check WSP compliance for cursor_multi_agent_bridge",
        context={"module_path": "modules/development/cursor_multi_agent_bridge"}
    )
    
    compliance_result = await coordinator.process_request("compliance", compliance_request)
    print(f"Compliance Status: {compliance_result.status}")
    print(f"Compliance Score: {compliance_result.response_data.get('compliance_score', 'N/A')}")
    print(f"Is Compliant: {compliance_result.response_data.get('is_compliant', 'N/A')}")
    
    if compliance_result.suggestions:
        print("Suggestions:")
        for suggestion in compliance_result.suggestions[:3]:
            print(f"  * {suggestion}")
    
    if compliance_result.violations:
        print("Violations:")
        for violation in compliance_result.violations[:3]:
            print(f"  ! {violation}")
    
    # 2. Pre-action verification (WSP 50)
    print("\n--- WSP 50 Pre-Action Verification ---")
    verification_request = WSPSubAgentRequest(
        agent_type="compliance",
        task_type="pre_action_verification",
        content="Verify before editing claude_code_integration.py",
        context={
            "file_path": "O:\\Foundups-Agent\\modules\\development\\cursor_multi_agent_bridge\\src\\claude_code_integration.py",
            "action": "edit"
        }
    )
    
    verification_result = await coordinator.process_request("compliance", verification_request)
    print(f"Verification Status: {verification_result.status}")
    print(f"File Verified: {verification_result.response_data.get('verified', 'N/A')}")
    
    # 3. Documentation check
    print("\n--- Documentation Validation ---")
    doc_request = WSPSubAgentRequest(
        agent_type="documentation",
        task_type="check_documentation",
        content="Check documentation completeness",
        context={"module_path": "modules/development/cursor_multi_agent_bridge"}
    )
    
    doc_result = await coordinator.process_request("documentation", doc_request)
    print(f"Documentation Status: {doc_result.status}")
    print(f"Complete: {doc_result.response_data.get('documentation_complete', 'N/A')}")
    
    # 4. Test structure validation  
    print("\n--- Test Structure Validation ---")
    test_request = WSPSubAgentRequest(
        agent_type="testing",
        task_type="validate_test_structure",
        content="Validate test directory structure",
        context={"module_path": "modules/development/cursor_multi_agent_bridge"}
    )
    
    test_result = await coordinator.process_request("testing", test_request)
    print(f"Test Status: {test_result.status}")
    print(f"Test Structure Valid: {test_result.response_data.get('test_structure_valid', 'N/A')}")
    
    # 5. Multi-agent coordination example
    print("\n--- Multi-Agent Coordination ---")
    
    multi_requests = [
        ("compliance", WSPSubAgentRequest(
            agent_type="compliance",
            task_type="validate_wsp_protocols",
            content="Validate WSP protocols",
            context={"protocols": ["WSP_54", "WSP_62"]}
        )),
        ("documentation", WSPSubAgentRequest(
            agent_type="documentation",
            task_type="update_modlog",
            content="Update ModLog with sub-agent integration",
            context={
                "module_path": "modules/development/cursor_multi_agent_bridge",
                "changes": ["Live sub-agent integration", "Real-time WSP assistance"]
            }
        ))
    ]
    
    multi_results = await coordinator.coordinate_multiple_agents(multi_requests)
    
    print("Multi-agent results:")
    for result in multi_results:
        print(f"  {result.agent_type}: {result.status} (confidence: {result.confidence:.1%})")
    
    # 6. Coordinator status
    print("\n--- Coordinator Status ---")
    status = coordinator.get_coordinator_status()
    print(f"Available agents: {status['available_agents']}")
    print(f"Total requests: {status['total_requests']}")
    
    print("\n=== WSP Sub-Agents Session Complete ===")
    return True


if __name__ == "__main__":
    asyncio.run(run_live_subagents())