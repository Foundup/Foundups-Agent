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
        """
        Initialize the WRE API Gateway for agent orchestration and request routing.
        
        WSP 54 Integration: Enforces agent permissions and security controls.
        WSP 71 Integration: Provides secrets management for agent operations.
        """
        self.project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        self.modules_root = self.project_root / "modules"
        self.active_sessions = {}
        self.agent_registry = {}
        self.request_history = []
        
        # Security framework integration
        self.agent_permissions = {}
        self.secrets_manager = None
        self.security_enabled = True
        
        # Initialize agent registry and security framework
        self._initialize_agent_registry()
        self._initialize_security_framework()
        
        print("WRE API Gateway initialized with WSP 54/71 security framework.")

    def _initialize_agent_registry(self):
        """Initialize registry of available WSP 54 agents."""
        self.agent_registry = {
            "compliance_agent": {
                "path": "modules.infrastructure.compliance_agent.src.compliance_agent",
                "class": "ComplianceAgent",
                "duties": ["wsp_validation", "structure_compliance", "memory_validation"],
                "permissions": ["FILE_READ", "LOG_WRITE", "SYSTEM_CONFIG", "SECRETS_READ"]
            },
            "janitor_agent": {
                "path": "modules.infrastructure.janitor_agent.src.janitor_agent", 
                "class": "JanitorAgent",
                "duties": ["workspace_cleanup", "memory_management", "log_rotation"],
                "permissions": ["FILE_READ", "FILE_WRITE", "FILE_DELETE", "LOG_WRITE"]
            },
            "documentation_agent": {
                "path": "modules.infrastructure.documentation_agent.src.documentation_agent",
                "class": "DocumentationAgent", 
                "duties": ["readme_generation", "roadmap_creation", "modlog_management"],
                "permissions": ["FILE_READ", "FILE_WRITE", "LOG_WRITE"]
            },
            "chronicler_agent": {
                "path": "modules.infrastructure.chronicler_agent.src.chronicler_agent",
                "class": "ChroniclerAgent",
                "duties": ["memory_logging", "state_archival", "cross_state_tracking"],
                "permissions": ["FILE_READ", "FILE_WRITE", "LOG_WRITE"]
            },
            "loremaster_agent": {
                "path": "modules.infrastructure.loremaster_agent.src.loremaster_agent",
                "class": "LoremasterAgent", 
                "duties": ["lore_understanding", "documentation_coherence", "wsp_numbering"],
                "permissions": ["FILE_READ", "LOG_WRITE"]
            },
            "module_scaffolding_agent": {
                "path": "modules.infrastructure.module_scaffolding_agent.src.module_scaffolding_agent",
                "class": "ModuleScaffoldingAgent",
                "duties": ["module_creation", "wsp49_structure", "wsp60_memory_setup"],
                "permissions": ["FILE_READ", "FILE_WRITE", "LOG_WRITE"]
            },
            "scoring_agent": {
                "path": "modules.infrastructure.scoring_agent.src.scoring_agent",
                "class": "ScoringAgent",
                "duties": ["mps_calculation", "llme_scoring", "complexity_analysis"],
                "permissions": ["FILE_READ", "LOG_WRITE"]
            },
            "testing_agent": {
                "path": "modules.infrastructure.testing_agent.src.testing_agent",
                "class": "TestingAgent",
                "duties": ["test_execution", "coverage_analysis", "test_automation"],
                "permissions": ["FILE_READ", "EXECUTE", "LOG_WRITE"]
            },
            "triage_agent": {
                "path": "modules.infrastructure.triage_agent.src.triage_agent",
                "class": "TriageAgent",
                "duties": ["external_feedback_monitoring", "input_standardization", "impact_assessment"],
                "permissions": ["FILE_READ", "NETWORK_ACCESS", "LOG_WRITE", "SECRETS_READ"]
            },
            "modularization_audit_agent": {
                "path": "modules.infrastructure.modularization_audit_agent.src.modularization_audit_agent",
                "class": "ModularizationAuditAgent",
                "duties": ["system_wide_audit", "architecture_compliance", "violation_detection"],
                "permissions": ["FILE_READ", "LOG_WRITE", "SYSTEM_CONFIG"]
            }
        }
        
    def _initialize_security_framework(self):
        """Initialize WSP 54/71 security framework for agent permission validation."""
        try:
            # Initialize agent permissions based on registry
            for agent_name, agent_info in self.agent_registry.items():
                self.agent_permissions[agent_name] = agent_info.get("permissions", [])
            
            # Initialize secrets manager (WSP 71)
            try:
                from ..wre_core.src.components.security.secrets_manager import create_secrets_manager
                self.secrets_manager = create_secrets_manager()
                print("🔐 WSP 71 Secrets Manager initialized successfully")
            except ImportError:
                print("⚠️ WSP 71 Secrets Manager not available - secrets functionality disabled")
                self.secrets_manager = None
                
            print(f"🔒 WSP 54 Security Framework initialized for {len(self.agent_permissions)} agents")
            
        except Exception as e:
            print(f"❌ Failed to initialize security framework: {e}")
            self.security_enabled = False
            
    def _validate_agent_permissions(self, agent_name: str, required_permissions: List[str]) -> bool:
        """
        Validate agent has required permissions (WSP 54 integration).
        
        Args:
            agent_name: Name of the agent
            required_permissions: List of required permissions
            
        Returns:
            bool: True if agent has all required permissions
        """
        if not self.security_enabled:
            return True  # Security disabled, allow all operations
            
        agent_permissions = self.agent_permissions.get(agent_name, [])
        
        for permission in required_permissions:
            if permission not in agent_permissions:
                print(f"❌ Permission denied: {agent_name} lacks {permission} permission")
                return False
                
        return True
        
    def _log_security_event(self, event_type: str, agent_name: str, action: str, result: str):
        """Log security events for audit purposes."""
        security_event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "agent_name": agent_name,
            "action": action,
            "result": result
        }
        
        # Add to request history for audit trail
        self.request_history.append(security_event)
        print(f"📊 Security Event: {event_type} | {agent_name} | {action} | {result}")

    def invoke_agent_with_security(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke agent with WSP 54 security validation.
        
        Args:
            agent_name: Name of the agent to invoke
            params: Parameters for agent invocation
            
        Returns:
            Dict containing agent response or security error
        """
        # Security validation
        if agent_name not in self.agent_registry:
            self._log_security_event("agent_invocation", agent_name, "invoke", "agent_not_found")
            return {"error": f"Agent {agent_name} not found in registry"}
            
        agent_info = self.agent_registry[agent_name]
        required_permissions = agent_info.get("permissions", [])
        
        # Validate permissions
        if not self._validate_agent_permissions(agent_name, required_permissions):
            self._log_security_event("permission_validation", agent_name, "invoke", "permission_denied")
            return {"error": f"Permission denied for agent {agent_name}"}
            
        # If agent requires secrets access, validate secrets manager availability
        if "SECRETS_READ" in required_permissions and not self.secrets_manager:
            self._log_security_event("secrets_validation", agent_name, "invoke", "secrets_manager_unavailable")
            return {"error": "Secrets manager not available for agent requiring SECRETS_READ"}
            
        try:
            # Proceed with original agent invocation logic
            result = self.invoke_agent(agent_name, params)
            self._log_security_event("agent_invocation", agent_name, "invoke", "success")
            return result
            
        except Exception as e:
            self._log_security_event("agent_invocation", agent_name, "invoke", "error")
            return {"error": f"Agent invocation failed: {str(e)}"}

    def get_security_status(self) -> Dict[str, Any]:
        """Get current security framework status."""
        return {
            "security_enabled": self.security_enabled,
            "secrets_manager_available": self.secrets_manager is not None,
            "registered_agents": len(self.agent_permissions),
            "agent_permissions": self.agent_permissions,
            "wsp_54_compliance": True,
            "wsp_71_compliance": self.secrets_manager is not None
        }

    def invoke_agent(self, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Original agent invocation method (legacy compatibility)."""
        if agent_name not in self.agent_registry:
            return {"error": f"Agent {agent_name} not found"}
            
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
                },
                "triage_agent": {
                    "external_feedback_monitoring": "monitor_feedback",
                    "input_standardization": "standardize_input",
                    "default": "monitor_feedback"
                }
            }
            
            # Get method to call
            agent_methods = method_map.get(agent_name, {"default": "execute"})
            method_name = agent_methods.get(duty, agent_methods["default"])
            
            if hasattr(agent, method_name):
                method = getattr(agent, method_name)
                result = method(params.get("target", "."), **params.get("kwargs", {}))
                
                return {
                    "status": "success",
                    "agent": agent_name,
                    "duty": duty,
                    "result": result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "error": f"Method {method_name} not found in {agent_name}",
                    "available_duties": agent_info.get("duties", [])
                }
                
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "agent": agent_name
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