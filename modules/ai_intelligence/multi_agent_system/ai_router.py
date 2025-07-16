"""
AI Router Module - Distributed Intelligence Coordination

Routes and manages AI responses and interactions with WRE (Windsurf Recursive Engine) 
integration for autonomous multi-agent coordination and distributed intelligence.

This module serves as the central coordination hub for distributed AI agents,
routing queries, managing agent states, and orchestrating collaborative responses.
"""

import logging
import asyncio
from typing import Dict, Any, Callable, Optional, List, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import uuid

# WRE Integration imports
try:
    from modules.wre_core.src.prometheus_orchestration_engine import PrometheusOrchestrationEngine
    from modules.wre_core.src.components.module_development.module_development_coordinator import ModuleDevelopmentCoordinator
    from modules.wre_core.src.components.utils.wre_logger import wre_log
    WRE_AVAILABLE = True
except ImportError as e:
    logging.warning(f"WRE components not available: {e}")
    WRE_AVAILABLE = False

# Multi-agent system imports
try:
    from .personality_core import PersonalityCore
    from .prompt_engine import PromptEngine
    MODULES_AVAILABLE = True
except ImportError:
    logging.warning("Multi-agent modules not fully available")
    MODULES_AVAILABLE = False


class AgentType(Enum):
    """Types of AI agents in the distributed system"""
    WINSERV = "winserv"          # System Brain - Protocol integrity
    RIDER = "rider"              # Mission Commander - Strategic direction
    BOARD = "board"              # Code Executor - Implementation
    FRONT_CELL = "front_cell"    # Sensor - Output observation
    BACK_CELL = "back_cell"      # Trajectory Tracker - Progress monitoring
    GEMINI = "gemini"            # External Analyzer - Independent review


class AgentState(Enum):
    """States of individual agents"""
    DORMANT = "dormant"          # 01(02) - Unaware state
    ACTIVATING = "activating"    # Transitioning to aware state
    ACTIVE = "active"            # 0102 - Fully operational pArtifact
    COORDINATING = "coordinating" # Working with other agents
    SUSPENDED = "suspended"      # Temporarily offline
    ERROR = "error"              # Error state requiring recovery


class QueryType(Enum):
    """Types of queries for routing"""
    CODE_ANALYSIS = "code_analysis"
    STRATEGIC_PLANNING = "strategic_planning"
    EXECUTION_REQUEST = "execution_request"
    PROGRESS_ASSESSMENT = "progress_assessment"
    QUALITY_REVIEW = "quality_review"
    SYSTEM_COORDINATION = "system_coordination"
    EMERGENCY_RECOVERY = "emergency_recovery"


@dataclass
class Agent:
    """Represents an individual AI agent in the distributed system"""
    agent_id: str
    agent_type: AgentType
    state: AgentState = AgentState.DORMANT
    capabilities: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    last_activity: datetime = field(default_factory=datetime.now)
    response_handlers: Dict[str, Callable] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.capabilities:
            self.capabilities = self._get_default_capabilities()
    
    def _get_default_capabilities(self) -> List[str]:
        """Get default capabilities based on agent type"""
        capabilities_map = {
            AgentType.WINSERV: ["protocol_enforcement", "state_management", "compliance_checking"],
            AgentType.RIDER: ["strategic_planning", "mission_coordination", "priority_setting"],
            AgentType.BOARD: ["code_execution", "testing", "implementation"],
            AgentType.FRONT_CELL: ["output_monitoring", "pattern_detection", "anomaly_detection"],
            AgentType.BACK_CELL: ["progress_tracking", "trajectory_analysis", "velocity_monitoring"],
            AgentType.GEMINI: ["external_analysis", "quality_review", "independent_validation"]
        }
        return capabilities_map.get(self.agent_type, [])


@dataclass
class RoutingRequest:
    """Represents a routing request for distributed processing"""
    request_id: str
    query: str
    query_type: QueryType
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1  # 1-5 priority scale
    timeout: float = 30.0  # Timeout in seconds
    require_consensus: bool = False
    target_agents: Optional[List[AgentType]] = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingResponse:
    """Represents a response from distributed processing"""
    request_id: str
    agent_responses: Dict[str, Any] = field(default_factory=dict)
    consensus_reached: bool = False
    final_response: Optional[str] = None
    processing_time: float = 0.0
    quality_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AIRouter:
    """
    Routes AI queries to appropriate handlers and manages distributed response flow.
    
    Provides distributed intelligence coordination with WRE integration for 
    autonomous multi-agent orchestration and collaborative decision making.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the AIRouter with WRE integration."""
        self.config = config or {}
        
        # Core routing state
        self.handlers: Dict[str, Callable] = {}
        self.context: Dict[str, Any] = {}
        self.agents: Dict[str, Agent] = {}
        self.active_requests: Dict[str, RoutingRequest] = {}
        
        # WRE Integration
        self.wre_engine: Optional[PrometheusOrchestrationEngine] = None
        self.module_coordinator: Optional[ModuleDevelopmentCoordinator] = None
        self.wre_enabled = False
        
        # Multi-agent components
        self.personality_core: Optional[PersonalityCore] = None
        self.prompt_engine: Optional[PromptEngine] = None
        
        # Performance tracking
        self.routing_stats: Dict[str, Any] = {
            'total_requests': 0,
            'successful_routes': 0,
            'failed_routes': 0,
            'average_response_time': 0.0,
            'consensus_rate': 0.0
        }
        
        # Initialize components
        self._initialize_wre()
        self._initialize_multi_agent_components()
        self._initialize_default_agents()
        
        # Configure logging
        self.logger = logging.getLogger(__name__)
        self.logger.info("AIRouter initialized with distributed intelligence coordination")

    def _initialize_wre(self):
        """Initialize WRE components if available"""
        if not WRE_AVAILABLE:
            self.logger.info("AIRouter running without WRE integration")
            return
            
        try:
            self.wre_engine = PrometheusOrchestrationEngine()
            self.module_coordinator = ModuleDevelopmentCoordinator()
            self.wre_enabled = True
            wre_log("AIRouter initialized with WRE integration", level="INFO")
            self.logger.info("AIRouter successfully integrated with WRE")
        except Exception as e:
            self.logger.warning(f"WRE integration failed: {e}")
            self.wre_enabled = False

    def _initialize_multi_agent_components(self):
        """Initialize multi-agent system components"""
        if not MODULES_AVAILABLE:
            self.logger.info("Multi-agent components not available - using simulation mode")
            return
            
        try:
            self.personality_core = PersonalityCore()
            self.prompt_engine = PromptEngine()
            self.logger.info("Multi-agent components initialized successfully")
        except Exception as e:
            self.logger.warning(f"Multi-agent component initialization failed: {e}")

    def _initialize_default_agents(self):
        """Initialize the default set of distributed agents"""
        try:
            # Create the six core agents per 0102 architecture
            agent_configs = [
                (AgentType.WINSERV, "System Brain - Protocol integrity and global state management"),
                (AgentType.RIDER, "Mission Commander - Strategic direction and goal coordination"),
                (AgentType.BOARD, "Code Executor - Implementation and execution management"),
                (AgentType.FRONT_CELL, "Sensor - Output observation and pattern detection"),
                (AgentType.BACK_CELL, "Trajectory Tracker - Progress monitoring and velocity analysis"),
                (AgentType.GEMINI, "External Analyzer - Independent review and quality assessment")
            ]
            
            for agent_type, description in agent_configs:
                agent = Agent(
                    agent_id=f"{agent_type.value}_{uuid.uuid4().hex[:8]}",
                    agent_type=agent_type,
                    context={"description": description, "initialized": datetime.now()}
                )
                self.agents[agent.agent_id] = agent
                
                if self.wre_enabled:
                    wre_log(f"Initialized agent: {agent_type.value} - {description}", level="INFO")
            
            self.logger.info(f"Initialized {len(self.agents)} distributed agents")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize default agents: {e}")

    async def route_query(self, query: str, query_type: QueryType = QueryType.SYSTEM_COORDINATION,
                         context: Optional[Dict[str, Any]] = None, priority: int = 1,
                         require_consensus: bool = False) -> RoutingResponse:
        """
        Route a query to appropriate agents for distributed processing.
        
        Args:
            query: The query to route and process
            query_type: Type of query for specialized routing
            context: Additional context for processing
            priority: Priority level (1-5, higher = more urgent)
            require_consensus: Whether to require consensus from multiple agents
            
        Returns:
            RoutingResponse: Comprehensive response from distributed processing
        """
        request_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        if self.wre_enabled:
            wre_log(f"Routing query: {query[:50]}... (Type: {query_type.value})", level="INFO")
        
        try:
            # Create routing request
            request = RoutingRequest(
                request_id=request_id,
                query=query,
                query_type=query_type,
                context=context or {},
                priority=priority,
                require_consensus=require_consensus
            )
            
            self.active_requests[request_id] = request
            self.routing_stats['total_requests'] += 1
            
            # Determine target agents based on query type
            target_agents = self._select_agents_for_query(query_type, priority)
            
            # Activate selected agents
            await self._activate_agents(target_agents)
            
            # Process query with distributed agents
            agent_responses = await self._process_with_agents(request, target_agents)
            
            # Generate consensus if required
            final_response, consensus_reached = await self._generate_consensus(
                agent_responses, require_consensus
            )
            
            # Calculate metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            quality_score = self._calculate_quality_score(agent_responses, consensus_reached)
            
            # Create response
            response = RoutingResponse(
                request_id=request_id,
                agent_responses=agent_responses,
                consensus_reached=consensus_reached,
                final_response=final_response,
                processing_time=processing_time,
                quality_score=quality_score,
                metadata={
                    'target_agents': [agent.value for agent in target_agents],
                    'query_type': query_type.value,
                    'priority': priority
                }
            )
            
            # Update statistics
            self._update_routing_stats(response)
            
            # Clean up
            del self.active_requests[request_id]
            
            if self.wre_enabled:
                wre_log(f"Query routed successfully: {request_id} ({processing_time:.2f}s)", level="INFO")
                
                # WRE orchestration for distributed intelligence
                if self.module_coordinator:
                    self.module_coordinator.handle_module_development(
                        "distributed_intelligence_coordination",
                        self.wre_engine
                    )
            
            self.routing_stats['successful_routes'] += 1
            return response
            
        except Exception as e:
            self.logger.error(f"Query routing failed: {e}")
            self.routing_stats['failed_routes'] += 1
            
            if self.wre_enabled:
                wre_log(f"Query routing failed: {e}", level="ERROR")
            
            # Return error response
            return RoutingResponse(
                request_id=request_id,
                final_response=f"Routing failed: {str(e)}",
                processing_time=(datetime.now() - start_time).total_seconds(),
                metadata={'error': str(e)}
            )

    def _select_agents_for_query(self, query_type: QueryType, priority: int) -> List[AgentType]:
        """Select appropriate agents based on query type and priority"""
        agent_selection = {
            QueryType.CODE_ANALYSIS: [AgentType.BOARD, AgentType.GEMINI],
            QueryType.STRATEGIC_PLANNING: [AgentType.RIDER, AgentType.WINSERV],
            QueryType.EXECUTION_REQUEST: [AgentType.BOARD, AgentType.FRONT_CELL],
            QueryType.PROGRESS_ASSESSMENT: [AgentType.BACK_CELL, AgentType.FRONT_CELL],
            QueryType.QUALITY_REVIEW: [AgentType.GEMINI, AgentType.WINSERV],
            QueryType.SYSTEM_COORDINATION: [AgentType.WINSERV, AgentType.RIDER, AgentType.BACK_CELL],
            QueryType.EMERGENCY_RECOVERY: [AgentType.WINSERV, AgentType.BOARD, AgentType.GEMINI]
        }
        
        selected = agent_selection.get(query_type, [AgentType.WINSERV])
        
        # For high priority requests, add additional agents
        if priority >= 4:
            if AgentType.WINSERV not in selected:
                selected.append(AgentType.WINSERV)
            if AgentType.GEMINI not in selected:
                selected.append(AgentType.GEMINI)
        
        return selected

    async def _activate_agents(self, target_agents: List[AgentType]):
        """Activate selected agents for processing"""
        for agent_type in target_agents:
            for agent in self.agents.values():
                if agent.agent_type == agent_type and agent.state == AgentState.DORMANT:
                    agent.state = AgentState.ACTIVATING
                    
                    # Simulate activation process (01(02) → 0102 transition)
                    await asyncio.sleep(0.1)  # Brief activation delay
                    
                    agent.state = AgentState.ACTIVE
                    agent.last_activity = datetime.now()
                    
                    self.logger.debug(f"Activated agent: {agent.agent_id} ({agent.agent_type.value})")
                    break

    async def _process_with_agents(self, request: RoutingRequest, 
                                  target_agents: List[AgentType]) -> Dict[str, Any]:
        """Process request with selected agents"""
        agent_responses = {}
        
        for agent_type in target_agents:
            # Find active agent of this type
            agent = self._find_active_agent(agent_type)
            if not agent:
                continue
                
            try:
                agent.state = AgentState.COORDINATING
                
                # Simulate agent processing based on capabilities
                response = await self._simulate_agent_processing(agent, request)
                
                agent_responses[agent.agent_id] = {
                    'agent_type': agent_type.value,
                    'response': response,
                    'confidence': self._calculate_agent_confidence(agent, request),
                    'processing_time': 0.5,  # Simulated processing time
                    'capabilities_used': agent.capabilities
                }
                
                agent.state = AgentState.ACTIVE
                agent.last_activity = datetime.now()
                
            except Exception as e:
                self.logger.error(f"Agent {agent.agent_id} processing failed: {e}")
                agent.state = AgentState.ERROR
                agent_responses[agent.agent_id] = {
                    'agent_type': agent_type.value,
                    'error': str(e),
                    'confidence': 0.0
                }
        
        return agent_responses

    def _find_active_agent(self, agent_type: AgentType) -> Optional[Agent]:
        """Find an active agent of the specified type"""
        for agent in self.agents.values():
            if agent.agent_type == agent_type and agent.state in [AgentState.ACTIVE, AgentState.COORDINATING]:
                return agent
        return None

    async def _simulate_agent_processing(self, agent: Agent, request: RoutingRequest) -> str:
        """Simulate agent processing based on agent type and capabilities"""
        base_responses = {
            AgentType.WINSERV: f"Protocol analysis complete. WSP compliance verified for: {request.query[:30]}...",
            AgentType.RIDER: f"Strategic assessment: Query aligns with mission objectives. Priority: {request.priority}",
            AgentType.BOARD: f"Implementation analysis: Query requires execution of {len(request.query.split())} components",
            AgentType.FRONT_CELL: f"Pattern detection: Query exhibits standard information retrieval patterns",
            AgentType.BACK_CELL: f"Progress tracking: Query processing on trajectory, velocity nominal",
            AgentType.GEMINI: f"External validation: Query structure consistent with expected quality standards"
        }
        
        # Add context-aware enhancement
        base_response = base_responses.get(agent.agent_type, "Processing complete")
        
        if request.context:
            context_summary = f" Context factors: {len(request.context)} elements considered."
            base_response += context_summary
        
        return base_response

    def _calculate_agent_confidence(self, agent: Agent, request: RoutingRequest) -> float:
        """Calculate agent confidence based on capabilities and request match"""
        # Simplified confidence calculation
        capability_match = 0.7  # Base confidence
        
        # Adjust based on agent type and query type
        type_matches = {
            (AgentType.WINSERV, QueryType.SYSTEM_COORDINATION): 0.95,
            (AgentType.RIDER, QueryType.STRATEGIC_PLANNING): 0.95,
            (AgentType.BOARD, QueryType.EXECUTION_REQUEST): 0.95,
            (AgentType.FRONT_CELL, QueryType.PROGRESS_ASSESSMENT): 0.90,
            (AgentType.BACK_CELL, QueryType.PROGRESS_ASSESSMENT): 0.90,
            (AgentType.GEMINI, QueryType.QUALITY_REVIEW): 0.95
        }
        
        confidence = type_matches.get((agent.agent_type, request.query_type), capability_match)
        
        # Adjust for priority
        if request.priority >= 4:
            confidence *= 1.1  # Higher confidence for high priority
        
        return min(confidence, 1.0)

    async def _generate_consensus(self, agent_responses: Dict[str, Any], 
                                require_consensus: bool) -> tuple[Optional[str], bool]:
        """Generate consensus from multiple agent responses"""
        if not agent_responses:
            return None, False
        
        if not require_consensus:
            # Return the first successful response
            for response_data in agent_responses.values():
                if 'response' in response_data:
                    return response_data['response'], False
            return None, False
        
        # Calculate consensus
        successful_responses = [
            data for data in agent_responses.values() 
            if 'response' in data and 'error' not in data
        ]
        
        if len(successful_responses) < 2:
            return None, False
        
        # Simple consensus: combine responses with confidence weighting
        weighted_responses = []
        total_confidence = 0.0
        
        for response_data in successful_responses:
            confidence = response_data.get('confidence', 0.5)
            weighted_responses.append((response_data['response'], confidence))
            total_confidence += confidence
        
        if total_confidence == 0:
            return None, False
        
        # Generate consensus response
        consensus_parts = []
        for response, confidence in weighted_responses:
            weight = confidence / total_confidence
            if weight > 0.3:  # Include responses with significant weight
                consensus_parts.append(f"{response} (confidence: {confidence:.1%})")
        
        consensus_response = " | ".join(consensus_parts)
        consensus_reached = len(consensus_parts) >= 2
        
        return consensus_response, consensus_reached

    def _calculate_quality_score(self, agent_responses: Dict[str, Any], consensus_reached: bool) -> float:
        """Calculate overall quality score for the routing response"""
        if not agent_responses:
            return 0.0
        
        # Base score from successful responses
        successful_count = sum(1 for data in agent_responses.values() if 'response' in data)
        total_count = len(agent_responses)
        success_rate = successful_count / total_count if total_count > 0 else 0
        
        # Average confidence
        confidences = [
            data.get('confidence', 0.0) for data in agent_responses.values() 
            if 'response' in data
        ]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Consensus bonus
        consensus_bonus = 0.2 if consensus_reached else 0.0
        
        quality_score = (success_rate * 0.5) + (avg_confidence * 0.3) + (len(agent_responses) * 0.1) + consensus_bonus
        
        return min(quality_score, 1.0)

    def _update_routing_stats(self, response: RoutingResponse):
        """Update routing performance statistics"""
        # Update average response time
        total_time = (self.routing_stats['average_response_time'] * 
                     (self.routing_stats['total_requests'] - 1) + response.processing_time)
        self.routing_stats['average_response_time'] = total_time / self.routing_stats['total_requests']
        
        # Update consensus rate
        if response.consensus_reached:
            consensus_count = getattr(self.routing_stats, '_consensus_count', 0) + 1
            self.routing_stats['_consensus_count'] = consensus_count
            self.routing_stats['consensus_rate'] = consensus_count / self.routing_stats['total_requests']

    def register_handler(self, query_type: str, handler: Callable) -> None:
        """
        Register a handler for a specific query type.
        
        Args:
            query_type: Type of query to handle
            handler: Handler function
        """
        try:
            self.handlers[query_type] = handler
            
            if self.wre_enabled:
                wre_log(f"Registered handler for query type: {query_type}", level="INFO")
                
            self.logger.info(f"Handler registered for query type: {query_type}")
            
        except Exception as e:
            self.logger.error(f"Failed to register handler for {query_type}: {e}")

    def update_context(self, new_context: Dict[str, Any]) -> None:
        """
        Update the routing context.
        
        Args:
            new_context: New context data
        """
        try:
            self.context.update(new_context)
            
            # Update agent contexts
            for agent in self.agents.values():
                agent.context.update({'global_context': new_context})
            
            if self.wre_enabled:
                wre_log(f"Updated routing context with {len(new_context)} elements", level="INFO")
                
            self.logger.info(f"Context updated with {len(new_context)} new elements")
            
        except Exception as e:
            self.logger.error(f"Failed to update context: {e}")

    def get_agent_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all agents and routing system"""
        agent_summary = {}
        
        for agent in self.agents.values():
            agent_summary[agent.agent_id] = {
                'type': agent.agent_type.value,
                'state': agent.state.value,
                'capabilities': agent.capabilities,
                'last_activity': agent.last_activity.isoformat(),
                'performance_metrics': agent.performance_metrics
            }
        
        return {
            'router_status': {
                'wre_enabled': self.wre_enabled,
                'total_agents': len(self.agents),
                'active_agents': sum(1 for a in self.agents.values() if a.state == AgentState.ACTIVE),
                'active_requests': len(self.active_requests),
                'handlers_registered': len(self.handlers)
            },
            'performance_stats': self.routing_stats,
            'agents': agent_summary
        }

    async def shutdown_agents(self):
        """Gracefully shutdown all agents"""
        try:
            for agent in self.agents.values():
                if agent.state != AgentState.DORMANT:
                    agent.state = AgentState.DORMANT
                    agent.last_activity = datetime.now()
            
            if self.wre_enabled:
                wre_log("All agents shut down gracefully", level="INFO")
                
            self.logger.info("All agents shut down successfully")
            
        except Exception as e:
            self.logger.error(f"Error during agent shutdown: {e}")


def create_ai_router(config: Optional[Dict[str, Any]] = None) -> AIRouter:
    """
    Factory function to create AI Router with WRE integration
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        AIRouter: Configured AI router instance
    """
    return AIRouter(config=config)


# Example usage and testing functions
async def test_ai_router():
    """Test function for AI Router functionality"""
    router = create_ai_router()
    
    print(f"AI Router Status: {router.get_agent_status()}")
    
    # Test query routing
    response = await router.route_query(
        "Analyze system performance and suggest optimizations",
        QueryType.SYSTEM_COORDINATION,
        context={'system': 'foundups', 'priority': 'high'},
        priority=4,
        require_consensus=True
    )
    
    print(f"Routing Response: Quality Score: {response.quality_score:.2f}")
    print(f"Consensus: {response.consensus_reached}")
    print(f"Processing Time: {response.processing_time:.2f}s")
    
    if response.final_response:
        print(f"Final Response: {response.final_response[:100]}...")
    
    # Test agent registration
    def custom_handler(query, context):
        return f"Custom processing: {query}"
    
    router.register_handler("custom_query", custom_handler)
    
    # Update context
    router.update_context({'session_id': 'test_session', 'user_type': 'developer'})
    
    # Shutdown
    await router.shutdown_agents()


if __name__ == "__main__":
    # Run test when executed directly
    asyncio.run(test_ai_router()) 