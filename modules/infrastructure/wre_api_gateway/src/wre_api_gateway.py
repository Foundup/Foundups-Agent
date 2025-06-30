# WRE API Gateway - Central routing and orchestration hub
# WSP Integration: Request routing, agent coordination, and service mesh

import asyncio
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid

class WREAPIGateway:
    def __init__(self):
        """Initialize the WRE API Gateway for agent orchestration and request routing."""
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.modules_root = self.project_root / "modules"
        self.active_sessions = {}
        self.agent_registry = {}
        self.request_history = []
        
        # Initialize agent registry
        self._initialize_agent_registry()
        
        print("WRE API Gateway initialized for agent orchestration and request routing.")

    def _initialize_agent_registry(self):
        """Initialize registry of available WSP 54 agents."""
        self.agent_registry = {
            "compliance_agent": {
                "path": "modules.infrastructure.compliance_agent.src.compliance_agent",
                "class": "ComplianceAgent",
                "duties": ["wsp_validation", "structure_compliance", "memory_validation"]
            },
            "janitor_agent": {
                "path": "modules.infrastructure.janitor_agent.src.janitor_agent", 
                "class": "JanitorAgent",
                "duties": ["workspace_cleanup", "memory_management", "log_rotation"]
            },
            "documentation_agent": {
                "path": "modules.infrastructure.documentation_agent.src.documentation_agent",
                "class": "DocumentationAgent", 
                "duties": ["readme_generation", "roadmap_creation", "modlog_management"]
            },
            "chronicler_agent": {
                "path": "modules.infrastructure.chronicler_agent.src.chronicler_agent",
                "class": "ChroniclerAgent",
                "duties": ["memory_logging", "state_archival", "cross_state_tracking"]
            },
            "loremaster_agent": {
                "path": "modules.infrastructure.loremaster_agent.src.loremaster_agent",
                "class": "LoremasterAgent", 
                "duties": ["lore_understanding", "documentation_coherence", "wsp_numbering"]
            },
            "module_scaffolding_agent": {
                "path": "modules.infrastructure.module_scaffolding_agent.src.module_scaffolding_agent",
                "class": "ModuleScaffoldingAgent",
                "duties": ["module_creation", "wsp49_structure", "wsp60_memory_setup"]
            },
            "scoring_agent": {
                "path": "modules.infrastructure.scoring_agent.src.scoring_agent",
                "class": "ScoringAgent",
                "duties": ["mps_calculation", "llme_scoring", "complexity_analysis"]
            },
            "testing_agent": {
                "path": "modules.infrastructure.testing_agent.src.testing_agent",
                "class": "TestingAgent",
                "duties": ["test_execution", "coverage_analysis", "wsp6_validation"]
            }
        }

    async def route_request(self, request: Dict) -> Dict:
        """
        Route incoming requests to appropriate agents or modules.
        
        Args:
            request: Dict containing request type, target, and parameters
            
        Returns:
            Dict with routing results and response data
        """
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        self.active_sessions[session_id] = {
            "created": timestamp,
            "request": request,
            "status": "processing"
        }
        
        try:
            request_type = request.get("type", "unknown")
            target = request.get("target", "")
            params = request.get("params", {})
            
            print(f"🌐 Routing {request_type} request to {target}...")
            
            # Route to appropriate handler
            if request_type == "agent_invoke":
                response = await self._route_to_agent(target, params)
            elif request_type == "module_operation":
                response = await self._route_to_module(target, params)
            elif request_type == "wsp_compliance":
                response = await self._handle_wsp_compliance(params)
            elif request_type == "orchestration":
                response = await self._handle_orchestration(params)
            else:
                response = {
                    "status": "error",
                    "message": f"Unknown request type: {request_type}",
                    "supported_types": ["agent_invoke", "module_operation", "wsp_compliance", "orchestration"]
                }
            
            # Update session
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["response"] = response
            
            # Log request
            self.request_history.append({
                "session_id": session_id,
                "timestamp": timestamp,
                "request": request,
                "response": response
            })
            
            return {
                "session_id": session_id,
                "status": "success",
                **response
            }
            
        except Exception as e:
            error_response = {
                "status": "error",
                "message": str(e),
                "session_id": session_id
            }
            
            self.active_sessions[session_id]["status"] = "error"
            self.active_sessions[session_id]["error"] = str(e)
            
            return error_response

    async def _route_to_agent(self, agent_name: str, params: Dict) -> Dict:
        """Route request to specific WSP 54 agent."""
        if agent_name not in self.agent_registry:
            return {
                "status": "error",
                "message": f"Agent '{agent_name}' not found",
                "available_agents": list(self.agent_registry.keys())
            }
        
        agent_info = self.agent_registry[agent_name]
        
        try:
            # Dynamic import and instantiation
            module_path = agent_info["path"]
            class_name = agent_info["class"]
            
            # Import the agent module
            import importlib
            module = importlib.import_module(module_path)
            agent_class = getattr(module, class_name)
            
            # Instantiate and invoke agent
            agent = agent_class()
            
            # Route to appropriate method based on duty
            duty = params.get("duty", "default")
            method_map = {
                "compliance_agent": {
                    "wsp_validation": "validate_compliance",
                    "default": "validate_compliance"
                },
                "janitor_agent": {
                    "workspace_cleanup": "clean_workspace", 
                    "default": "clean_workspace"
                },
                "documentation_agent": {
                    "readme_generation": "generate_module_documentation",
                    "default": "generate_module_documentation"
                },
                "testing_agent": {
                    "test_execution": "run_tests",
                    "coverage_analysis": "check_coverage",
                    "default": "run_tests"
                },
                "scoring_agent": {
                    "mps_calculation": "calculate_score",
                    "default": "calculate_score"
                },
                "module_scaffolding_agent": {
                    "module_creation": "create_module",
                    "default": "create_module"
                }
            }
            
            if agent_name in method_map:
                method_name = method_map[agent_name].get(duty, method_map[agent_name]["default"])
                if hasattr(agent, method_name):
                    method = getattr(agent, method_name)
                    
                    # Call method with appropriate parameters
                    if duty == "module_creation":
                        result = method(
                            params.get("module_name", ""),
                            params.get("domain", ""),
                            params.get("description", "")
                        )
                    elif duty == "coverage_analysis":
                        result = method(params.get("target_module"))
                    elif duty == "mps_calculation":
                        result = method(params.get("target_module", ""))
                    else:
                        result = method()
                    
                    return {
                        "status": "success", 
                        "agent": agent_name,
                        "duty": duty,
                        "result": result
                    }
            
            return {
                "status": "error",
                "message": f"Method '{duty}' not available for agent '{agent_name}'"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"Agent execution failed: {str(e)}",
                "agent": agent_name
            }

    async def _route_to_module(self, module_path: str, params: Dict) -> Dict:
        """Route request to specific module functionality."""
        module_full_path = self.modules_root / module_path
        
        if not module_full_path.exists():
            return {
                "status": "error",
                "message": f"Module not found: {module_path}",
                "path": str(module_full_path)
            }
        
        # Module operation routing logic would go here
        return {
            "status": "success",
            "message": f"Module operation routed to {module_path}",
            "module": module_path,
            "params": params
        }

    async def _handle_wsp_compliance(self, params: Dict) -> Dict:
        """Handle WSP compliance requests through orchestrated agent calls."""
        compliance_results = {}
        
        # Orchestrate compliance workflow
        agents_to_invoke = [
            ("compliance_agent", {"duty": "wsp_validation"}),
            ("janitor_agent", {"duty": "workspace_cleanup"}),
            ("testing_agent", {"duty": "coverage_analysis"})
        ]
        
        for agent_name, agent_params in agents_to_invoke:
            result = await self._route_to_agent(agent_name, agent_params)
            compliance_results[agent_name] = result
        
        return {
            "status": "success",
            "compliance_workflow": compliance_results,
            "wsp_compliant": all(r.get("status") == "success" for r in compliance_results.values())
        }

    async def _handle_orchestration(self, params: Dict) -> Dict:
        """Handle complex orchestration requests involving multiple agents."""
        orchestration_type = params.get("type", "default")
        
        if orchestration_type == "module_lifecycle":
            # Full module creation and validation workflow
            module_name = params.get("module_name", "")
            domain = params.get("domain", "")
            description = params.get("description", "")
            
            workflow_results = {}
            
            # Step 1: Create module
            create_result = await self._route_to_agent("module_scaffolding_agent", {
                "duty": "module_creation",
                "module_name": module_name,
                "domain": domain, 
                "description": description
            })
            workflow_results["creation"] = create_result
            
            if create_result.get("status") == "success":
                # Step 2: Validate compliance
                compliance_result = await self._route_to_agent("compliance_agent", {
                    "duty": "wsp_validation"
                })
                workflow_results["compliance"] = compliance_result
                
                # Step 3: Generate documentation
                doc_result = await self._route_to_agent("documentation_agent", {
                    "duty": "readme_generation",
                    "module_name": module_name,
                    "domain": domain
                })
                workflow_results["documentation"] = doc_result
            
            return {
                "status": "success",
                "orchestration_type": orchestration_type,
                "workflow": workflow_results
            }
        
        return {
            "status": "error",
            "message": f"Unknown orchestration type: {orchestration_type}",
            "supported_types": ["module_lifecycle"]
        }

    def get_status(self) -> Dict:
        """Get current gateway status and metrics."""
        active_count = len([s for s in self.active_sessions.values() if s["status"] == "processing"])
        
        return {
            "status": "operational",
            "agents_registered": len(self.agent_registry),
            "active_sessions": active_count,
            "total_requests": len(self.request_history),
            "agent_registry": list(self.agent_registry.keys()),
            "uptime": "operational"
        }

    def get_session_info(self, session_id: str) -> Dict:
        """Get information about a specific session."""
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
        
        # Check history
        for record in self.request_history:
            if record["session_id"] == session_id:
                return record
        
        return {
            "status": "not_found",
            "message": f"Session {session_id} not found"
        }

    async def health_check(self) -> Dict:
        """Perform health check of all registered agents."""
        health_results = {}
        
        for agent_name in self.agent_registry:
            try:
                # Quick instantiation test
                agent_info = self.agent_registry[agent_name]
                import importlib
                module = importlib.import_module(agent_info["path"])
                agent_class = getattr(module, agent_info["class"])
                agent = agent_class()
                
                health_results[agent_name] = {
                    "status": "healthy",
                    "instantiation": "success"
                }
            except Exception as e:
                health_results[agent_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        overall_health = all(r["status"] == "healthy" for r in health_results.values())
        
        return {
            "overall_status": "healthy" if overall_health else "degraded",
            "agent_health": health_results,
            "healthy_agents": len([r for r in health_results.values() if r["status"] == "healthy"]),
            "total_agents": len(health_results)
        } 