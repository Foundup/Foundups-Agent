"""
WSP-Guided Development Example
Using WSP sub-agents to guide development in real-time

This demonstrates coding with live WSP sub-agent assistance.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from wsp_sub_agents import WSPSubAgentCoordinator, WSPSubAgentRequest


class WSPGuidedDeveloper:
    """Developer class that uses WSP sub-agents for guidance"""
    
    def __init__(self):
        self.coordinator = WSPSubAgentCoordinator()
        self.current_file = __file__
        self.module_path = str(Path(__file__).parent.parent)
    
    async def start_development_session(self):
        """Start a WSP-guided development session"""
        print("Starting WSP-guided development session...")
        
        # Step 1: Pre-action verification (WSP 50)
        await self._verify_before_action("create_function")
        
        # Step 2: Check compliance requirements
        await self._check_compliance_requirements()
        
        # Step 3: Validate development approach
        await self._validate_approach()
        
        # Step 4: Get documentation guidance
        await self._get_documentation_guidance()
        
        print("\nWSP-guided development session complete!")
        return True
    
    async def _verify_before_action(self, action):
        """WSP 50 pre-action verification"""
        print(f"\n--- WSP 50 Pre-Action Verification: {action} ---")
        
        request = WSPSubAgentRequest(
            agent_type="compliance",
            task_type="pre_action_verification",
            content=f"Verify before {action}",
            context={"file_path": self.current_file, "action": action}
        )
        
        result = await self.coordinator.process_request("compliance", request)
        print(f"Verification: {result.response_data.get('verified', 'Unknown')}")
        
        if result.suggestions:
            print("WSP 50 Guidance:")
            for suggestion in result.suggestions:
                print(f"  * {suggestion}")
    
    async def _check_compliance_requirements(self):
        """Check WSP compliance requirements"""
        print("\n--- WSP Compliance Requirements ---")
        
        request = WSPSubAgentRequest(
            agent_type="compliance",
            task_type="check_module_compliance",
            content="Check compliance for development work",
            context={"module_path": self.module_path}
        )
        
        result = await self.coordinator.process_request("compliance", request)
        print(f"Compliance Score: {result.response_data.get('compliance_score', 'N/A')}")
        
        if result.violations:
            print("Compliance Issues to Address:")
            for violation in result.violations[:3]:  # Show first 3
                print(f"  ! {violation}")
    
    async def _validate_approach(self):
        """Validate development approach with testing agent"""
        print("\n--- Development Approach Validation ---")
        
        request = WSPSubAgentRequest(
            agent_type="testing",
            task_type="validate_test_structure",
            content="Validate approach for new development",
            context={"module_path": self.module_path}
        )
        
        result = await self.coordinator.process_request("testing", request)
        print(f"Test Structure Valid: {result.response_data.get('test_structure_valid', 'Unknown')}")
        
        if result.suggestions:
            print("Testing Guidance:")
            for suggestion in result.suggestions[:2]:  # Show first 2
                print(f"  * {suggestion}")
    
    async def _get_documentation_guidance(self):
        """Get documentation guidance"""
        print("\n--- Documentation Guidance ---")
        
        request = WSPSubAgentRequest(
            agent_type="documentation",
            task_type="check_documentation",
            content="Get documentation guidance for development",
            context={"module_path": self.module_path}
        )
        
        result = await self.coordinator.process_request("documentation", request)
        
        if result.suggestions:
            print("Documentation Requirements:")
            for suggestion in result.suggestions[:2]:  # Show first 2
                print(f"  * {suggestion}")
    
    def create_wsp_compliant_function(self):
        """Create a function following WSP guidance"""
        print("\n--- Creating WSP-Compliant Function ---")
        
        # This function follows WSP guidance received from sub-agents
        def calculate_wsp_score(module_path: str, protocols: list) -> float:
            """
            Calculate WSP compliance score for a module
            
            Args:
                module_path: Path to module for evaluation
                protocols: List of WSP protocols to check
                
            Returns:
                float: Compliance score (0.0 to 1.0)
                
            WSP Compliance:
            - WSP 22: Documented with clear purpose
            - WSP 11: Public interface documented
            - WSP 50: Validates inputs before processing
            """
            # WSP 50: Pre-action verification
            if not module_path or not protocols:
                return 0.0
            
            # Simple scoring logic (would be enhanced with actual implementation)
            base_score = 0.5
            protocol_bonus = len(protocols) * 0.1
            
            return min(1.0, base_score + protocol_bonus)
        
        print("Function created following WSP guidance:")
        print("- WSP 22: Documented purpose and usage")
        print("- WSP 11: Interface clearly defined")
        print("- WSP 50: Input validation included")
        
        return calculate_wsp_score
    
    async def complete_development_cycle(self):
        """Complete a full WSP-guided development cycle"""
        print("=== WSP-Guided Development Cycle ===")
        
        # 1. Pre-development verification
        await self.start_development_session()
        
        # 2. Create code following guidance
        new_function = self.create_wsp_compliant_function()
        
        # 3. Post-development validation
        await self._post_development_validation()
        
        # 4. Update documentation
        await self._update_documentation()
        
        print("\n=== Development Cycle Complete ===")
        return new_function
    
    async def _post_development_validation(self):
        """Validate work after development"""
        print("\n--- Post-Development Validation ---")
        
        # Multi-agent validation
        requests = [
            ("compliance", WSPSubAgentRequest(
                agent_type="compliance",
                task_type="validate_wsp_protocols",
                content="Validate protocols used in development",
                context={"protocols": ["WSP_22", "WSP_11", "WSP_50"]}
            )),
            ("testing", WSPSubAgentRequest(
                agent_type="testing",
                task_type="check_coverage",
                content="Check if new code needs tests",
                context={"module_path": self.module_path}
            ))
        ]
        
        results = await self.coordinator.coordinate_multiple_agents(requests)
        
        for result in results:
            print(f"{result.agent_type}: {result.status}")
    
    async def _update_documentation(self):
        """Update documentation with changes"""
        print("\n--- Updating Documentation ---")
        
        request = WSPSubAgentRequest(
            agent_type="documentation",
            task_type="update_modlog",
            content="Update ModLog with development work",
            context={
                "module_path": self.module_path,
                "changes": [
                    "Added WSP-guided development example",
                    "Created calculate_wsp_score function",
                    "Demonstrated live sub-agent integration"
                ]
            }
        )
        
        result = await self.coordinator.process_request("documentation", request)
        print(f"ModLog update: {result.status}")


async def main():
    """Demonstrate WSP-guided development"""
    developer = WSPGuidedDeveloper()
    
    # Run a complete WSP-guided development cycle
    result_function = await developer.complete_development_cycle()
    
    # Test the created function
    test_score = result_function("test/module", ["WSP_22", "WSP_11", "WSP_50"])
    print(f"\nTest function result: {test_score}")
    
    print("\nDemonstration: WSP sub-agents successfully guided development!")
    return True


if __name__ == "__main__":
    asyncio.run(main())