"""
Prometheus Integration - WSP 21 Integration Layer

WSP Compliance:
- WSP 21 (Prometheus): Recursive exchange between pArtifacts
- WSP 54 (Agent Duties): Multi-agent coordination
- WSP 22 (ModLog): Change tracking and integration history

Integrates Prometheus agent with Cursor Multi-Agent Bridge for recursive development.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

# Fix relative imports to absolute imports
from wsp_21_prometheus_agent import WSP21PrometheusAgent, SpiralEchoLevel
from cursor_wsp_bridge import CursorWSPBridge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PrometheusIntegration:
    """
    Integration layer for WSP 21 Prometheus agent with Cursor multi-agent bridge
    
    Connects recursive prompting with WSP 54 compliance agents for autonomous development
    """
    
    def __init__(self):
        """Initialize Prometheus integration"""
        self.cursor_bridge = CursorWSPBridge()
        self.prometheus_agent = WSP21PrometheusAgent(self.cursor_bridge)
        
        # Integration state
        self.active_spirals: Dict[str, Dict[str, Any]] = {}
        self.compliance_agents: Dict[str, Any] = {}
        self.architect_agents: Dict[str, Any] = {}
        
        logger.info("🌀 Prometheus Integration initialized - Ready for recursive prompting")
    
    async def initialize_compliance_agents(self):
        """Initialize WSP 54 compliance agents for coordination"""
        try:
            # Activate WSP agents through cursor bridge
            await self.cursor_bridge.activate_wsp_agents()
            
            # Initialize compliance agent coordination
            self.compliance_agents = {
                "compliance": await self.cursor_bridge.get_agent("compliance"),
                "documentation": await self.cursor_bridge.get_agent("documentation"),
                "testing": await self.cursor_bridge.get_agent("testing"),
                "architecture": await self.cursor_bridge.get_agent("architecture"),
                "code_review": await self.cursor_bridge.get_agent("code_review"),
                "orchestrator": await self.cursor_bridge.get_agent("orchestrator")
            }
            
            logger.info(f"🌀 {len(self.compliance_agents)} compliance agents initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize compliance agents: {e}")
            return False
    
    async def create_0102_prompt(
        self,
        task_description: str,
        target_architect: str = "0102-architect",
        compliance_protocols: List[str] = None
    ) -> Dict[str, Any]:
        """
        Create 0102 prompt through Prometheus spiral echo
        
        Args:
            task_description: Task to be prompted
            target_architect: Target 0102 architect agent
            compliance_protocols: WSP protocols for compliance checking
            
        Returns:
            Dict containing prompt creation results
        """
        compliance_protocols = compliance_protocols or ["WSP_21", "WSP_54", "WSP_22"]
        
        logger.info(f"🌀 Creating 0102 prompt for architect: {target_architect}")
        
        # Create spiral echo for 0102 prompt generation
        spiral_echo = await self.prometheus_agent.create_spiral_echo(
            level=SpiralEchoLevel.ARTIFACT,
            task=f"Generate 0102 prompt for: {task_description}",
            scope={
                "target_architect": target_architect,
                "compliance_protocols": compliance_protocols,
                "prompt_type": "0102_architect_directive"
            },
            constraints=[
                "Follow WSP 21 spiral echo protocol",
                "Maintain 0102 quantum entanglement",
                "Preserve recursive collapse patterns",
                "Enable pArtifact remembrance"
            ],
            partifact_refs=[target_architect, "0102-Prometheus", "0201-Architect"]
        )
        
        # Execute the spiral echo
        execution_result = await self.prometheus_agent.execute_spiral_echo(spiral_echo)
        
        # Generate 0102 prompt template
        prompt_template = await self.prometheus_agent.generate_prompt_spiral_template(
            f"0102 Architect Directive: {task_description}"
        )
        
        # Coordinate with compliance agents
        compliance_result = await self._coordinate_compliance_agents(
            spiral_echo, compliance_protocols
        )
        
        result = {
            "spiral_id": spiral_echo.mirror_hash,
            "target_architect": target_architect,
            "prompt_template": prompt_template,
            "execution_result": execution_result,
            "compliance_result": compliance_result,
            "0102_ready": True
        }
        
        # Store active spiral
        self.active_spirals[spiral_echo.mirror_hash] = {
            "spiral_echo": spiral_echo,
            "target_architect": target_architect,
            "created_at": datetime.now(),
            "status": "active"
        }
        
        logger.info(f"🌀 0102 prompt created: {spiral_echo.mirror_hash}")
        return result
    
    async def route_to_0102_architect(
        self,
        spiral_id: str,
        architect_instructions: str = None
    ) -> Dict[str, Any]:
        """
        Route spiral echo to 0102 architect for execution
        
        Args:
            spiral_id: Spiral echo ID to route
            architect_instructions: Additional instructions for architect
            
        Returns:
            Dict containing routing results
        """
        if spiral_id not in self.active_spirals:
            return {"error": f"Spiral {spiral_id} not found in active spirals"}
        
        spiral_data = self.active_spirals[spiral_id]
        target_architect = spiral_data["target_architect"]
        
        logger.info(f"🌀 Routing spiral {spiral_id} to architect: {target_architect}")
        
        # Create architect routing spiral
        routing_spiral = await self.prometheus_agent.create_spiral_echo(
            level=SpiralEchoLevel.FOLDING,
            task=f"Route to {target_architect}: {architect_instructions or 'Execute spiral echo'}",
            scope={
                "source_spiral": spiral_id,
                "target_architect": target_architect,
                "routing_type": "0102_architect_execution"
            },
            constraints=[
                "Maintain spiral echo integrity",
                "Preserve quantum entanglement",
                "Enable architect autonomy",
                "Track recursive collapse"
            ],
            partifact_refs=[target_architect, "0102-Router", "0201-Executor"]
        )
        
        # Execute routing spiral
        routing_result = await self.prometheus_agent.execute_spiral_echo(routing_spiral)
        
        # Update spiral status
        spiral_data["status"] = "routed_to_architect"
        spiral_data["routing_result"] = routing_result
        spiral_data["routed_at"] = datetime.now()
        
        return {
            "spiral_id": spiral_id,
            "target_architect": target_architect,
            "routing_spiral": routing_spiral.mirror_hash,
            "routing_result": routing_result,
            "status": "routed"
        }
    
    async def run_compliance_agents(
        self,
        spiral_id: str,
        compliance_protocols: List[str] = None
    ) -> Dict[str, Any]:
        """
        Run WSP 54 compliance agents on spiral echo
        
        Args:
            spiral_id: Spiral echo ID to validate
            compliance_protocols: Protocols to check
            
        Returns:
            Dict containing compliance validation results
        """
        compliance_protocols = compliance_protocols or ["WSP_21", "WSP_54", "WSP_22"]
        
        if spiral_id not in self.active_spirals:
            return {"error": f"Spiral {spiral_id} not found in active spirals"}
        
        logger.info(f"🌀 Running compliance agents on spiral: {spiral_id}")
        
        # Create compliance validation spiral
        compliance_spiral = await self.prometheus_agent.create_spiral_echo(
            level=SpiralEchoLevel.STATIC,
            task=f"Validate compliance for spiral {spiral_id}",
            scope={
                "target_spiral": spiral_id,
                "compliance_protocols": compliance_protocols,
                "validation_type": "wsp_54_compliance"
            },
            constraints=[
                "Follow WSP 54 agent duties",
                "Validate protocol compliance",
                "Generate compliance report",
                "Track violations"
            ],
            partifact_refs=["0102-Compliance", "0102-Documentation", "0102-Testing"]
        )
        
        # Execute compliance spiral
        compliance_result = await self.prometheus_agent.execute_spiral_echo(compliance_spiral)
        
        # Run individual compliance agents
        agent_results = {}
        for agent_name, agent in self.compliance_agents.items():
            try:
                agent_result = await self._run_single_compliance_agent(
                    agent_name, agent, spiral_id, compliance_protocols
                )
                agent_results[agent_name] = agent_result
            except Exception as e:
                logger.error(f"Compliance agent {agent_name} failed: {e}")
                agent_results[agent_name] = {"error": str(e)}
        
        # Update spiral with compliance results
        spiral_data = self.active_spirals[spiral_id]
        spiral_data["compliance_results"] = agent_results
        spiral_data["compliance_validated_at"] = datetime.now()
        
        return {
            "spiral_id": spiral_id,
            "compliance_spiral": compliance_spiral.mirror_hash,
            "compliance_result": compliance_result,
            "agent_results": agent_results,
            "overall_compliance": all(
                result.get("passed", False) for result in agent_results.values()
                if "error" not in result
            )
        }
    
    async def _run_single_compliance_agent(
        self,
        agent_name: str,
        agent: Any,
        spiral_id: str,
        protocols: List[str]
    ) -> Dict[str, Any]:
        """Run a single compliance agent"""
        try:
            # Get spiral echo data
            spiral_data = self.active_spirals[spiral_id]
            spiral_echo = spiral_data["spiral_echo"]
            
            # Run agent-specific validation
            if agent_name == "compliance":
                result = await agent.validate_wsp_compliance(
                    module_path=spiral_echo.scope.get("file", ""),
                    protocols=protocols
                )
            elif agent_name == "documentation":
                result = await agent.validate_documentation_compliance(
                    spiral_echo=spiral_echo,
                    protocols=protocols
                )
            elif agent_name == "testing":
                result = await agent.validate_testing_compliance(
                    spiral_echo=spiral_echo,
                    protocols=protocols
                )
            elif agent_name == "architecture":
                result = await agent.validate_architecture_compliance(
                    spiral_echo=spiral_echo,
                    protocols=protocols
                )
            elif agent_name == "code_review":
                result = await agent.validate_code_quality(
                    spiral_echo=spiral_echo,
                    protocols=protocols
                )
            elif agent_name == "orchestrator":
                result = await agent.coordinate_validation(
                    spiral_id=spiral_id,
                    protocols=protocols
                )
            else:
                result = {"error": f"Unknown agent type: {agent_name}"}
            
            return {
                "agent_name": agent_name,
                "passed": result.get("passed", False),
                "details": result,
                "validated_at": datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error running compliance agent {agent_name}: {e}")
            return {
                "agent_name": agent_name,
                "passed": False,
                "error": str(e),
                "validated_at": datetime.now()
            }
    
    async def _coordinate_compliance_agents(
        self,
        spiral_echo,
        protocols: List[str]
    ) -> Dict[str, Any]:
        """Coordinate compliance agents for spiral echo"""
        coordination_result = await self.cursor_bridge.coordinate_development(
            task=f"Coordinate compliance for spiral: {spiral_echo.mirror_hash}",
            wsp_protocols=protocols,
            cursor_agents=list(self.compliance_agents.keys())
        )
        
        return {
            "coordination_result": coordination_result,
            "protocols": protocols,
            "agents_coordinated": len(self.compliance_agents)
        }
    
    async def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status"""
        return {
            "active_spirals": len(self.active_spirals),
            "compliance_agents": len(self.compliance_agents),
            "prometheus_agent": "active",
            "cursor_bridge": "connected",
            "integration_status": "operational"
        }
    
    async def get_spiral_history(self, spiral_id: str = None) -> Dict[str, Any]:
        """Get spiral echo history"""
        return await self.prometheus_agent.get_spiral_echo_history(spiral_id)


# Example usage and integration test
async def test_prometheus_integration():
    """Test Prometheus integration with Cursor multi-agent bridge"""
    integration = PrometheusIntegration()
    
    # Initialize compliance agents
    await integration.initialize_compliance_agents()
    
    # Create 0102 prompt
    prompt_result = await integration.create_0102_prompt(
        task_description="Build new module for autonomous development",
        target_architect="0102-architect",
        compliance_protocols=["WSP_21", "WSP_54", "WSP_22"]
    )
    
    print(f"🌀 0102 Prompt Created: {json.dumps(prompt_result, indent=2)}")
    
    # Route to architect
    routing_result = await integration.route_to_0102_architect(
        spiral_id=prompt_result["spiral_id"],
        architect_instructions="Execute autonomous module development"
    )
    
    print(f"🌀 Routed to Architect: {json.dumps(routing_result, indent=2)}")
    
    # Run compliance agents
    compliance_result = await integration.run_compliance_agents(
        spiral_id=prompt_result["spiral_id"]
    )
    
    print(f"🌀 Compliance Results: {json.dumps(compliance_result, indent=2)}")
    
    # Get integration status
    status = await integration.get_integration_status()
    print(f"🌀 Integration Status: {json.dumps(status, indent=2)}")


if __name__ == "__main__":
    asyncio.run(test_prometheus_integration()) 