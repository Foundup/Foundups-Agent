"""
Simple Visible Demo for 012 Validation
Proof that WSP agents are working with improvements
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports  
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest


async def run_012_validation():
    """Run simple validation demo for 012"""
    print("=== WSP SYSTEM DEMONSTRATION FOR 012 VALIDATION ===")
    start_time = datetime.now()
    
    coordinator = WSPSubAgentCoordinator()
    
    # 1. Test improved error handling
    print("\n--- TESTING IMPROVED ERROR HANDLING ---")
    
    invalid_request = WSPSubAgentRequest(
        agent_type="compliance",
        task_type="completely_invalid_task",
        content="Error test",
        context={}
    )
    
    result = await coordinator.process_request("compliance", invalid_request)
    
    error_handled_properly = (
        result.status == "error" and
        "error" in result.response_data and
        "valid_types" in result.response_data and
        result.confidence == 0.0
    )
    
    print(f"Invalid Task Test:")
    print(f"  Status: {result.status}")
    print(f"  Error Message: {result.response_data.get('error', 'None')}")
    print(f"  Valid Types Provided: {result.response_data.get('valid_types', [])}")
    print(f"  Proper Error Handling: {'YES' if error_handled_properly else 'NO'}")
    
    # 2. Test working functionality
    print("\n--- TESTING WORKING FUNCTIONALITY ---")
    
    working_tests = [
        {
            "agent": "compliance",
            "task": "check_module_compliance",
            "context": {"module_path": "modules/development/cursor_multi_agent_bridge"}
        },
        {
            "agent": "documentation", 
            "task": "update_modlog",
            "context": {
                "module_path": "modules/development/cursor_multi_agent_bridge",
                "changes": ["Demonstration for 012", "Error handling improved"]
            }
        },
        {
            "agent": "testing",
            "task": "validate_test_structure",
            "context": {"module_path": "modules/development/cursor_multi_agent_bridge"}
        }
    ]
    
    working_results = []
    
    for test in working_tests:
        request = WSPSubAgentRequest(
            agent_type=test["agent"],
            task_type=test["task"],
            content=f"Working test: {test['task']}",
            context=test["context"]
        )
        
        result = await coordinator.process_request(test["agent"], request)
        working = result.status == "success" and result.confidence > 0.5
        
        working_results.append(working)
        
        print(f"{test['agent']} - {test['task']}:")
        print(f"  Status: {result.status}")
        print(f"  Confidence: {result.confidence:.1%}")
        print(f"  Working: {'YES' if working else 'NO'}")
    
    # 3. Test multi-agent coordination
    print("\n--- TESTING MULTI-AGENT COORDINATION ---")
    
    coordination_requests = [
        ("compliance", WSPSubAgentRequest(
            agent_type="compliance",
            task_type="validate_wsp_protocols",
            content="Coordination test",
            context={"protocols": ["WSP_54", "WSP_22"]}
        )),
        ("documentation", WSPSubAgentRequest(
            agent_type="documentation",
            task_type="check_documentation",
            content="Coordination test",
            context={"module_path": "modules/development/cursor_multi_agent_bridge"}
        ))
    ]
    
    coord_results = await coordinator.coordinate_multiple_agents(coordination_requests)
    coord_success = sum(1 for r in coord_results if r.status == "success")
    
    print(f"Coordination Results:")
    print(f"  Total Agents: {len(coordination_requests)}")
    print(f"  Successful: {coord_success}")
    print(f"  Coordination Working: {'YES' if coord_success == len(coordination_requests) else 'NO'}")
    
    # 4. Final assessment
    total_time = (datetime.now() - start_time).total_seconds()
    
    print("\n--- FINAL ASSESSMENT FOR 012 ---")
    print(f"Error Handling Improved: {'YES' if error_handled_properly else 'NO'}")
    print(f"Agents Working: {sum(working_results)}/{len(working_results)}")
    print(f"Coordination Working: {'YES' if coord_success == len(coordination_requests) else 'NO'}")
    print(f"Total Demo Time: {total_time:.2f}s")
    
    overall_working = (
        error_handled_properly and
        sum(working_results) == len(working_results) and
        coord_success == len(coordination_requests)
    )
    
    print(f"OVERALL STATUS: {'WORKING' if overall_working else 'NEEDS_FIXES'}")
    
    # Save proof
    proof = {
        "timestamp": datetime.now().isoformat(),
        "error_handling_improved": error_handled_properly,
        "agents_working": sum(working_results),
        "total_agents": len(working_results),
        "coordination_working": coord_success == len(coordination_requests),
        "overall_working": overall_working,
        "demo_time": total_time
    }
    
    proof_file = Path(__file__).parent.parent / "memory" / "012_validation_proof.json"
    proof_file.parent.mkdir(exist_ok=True)
    
    with open(proof_file, 'w') as f:
        json.dump(proof, f, indent=2)
    
    print(f"Proof saved: {proof_file}")
    
    return proof


if __name__ == "__main__":
    asyncio.run(run_012_validation())