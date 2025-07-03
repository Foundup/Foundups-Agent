"""
WRE Core Proof of Concept (POC) Orchestration

This module implements the minimal WRE Core POC layer that sits on top of Cursor
providing modular agent-driven coding workflows with manual control and minimal features.

Following 0102 guidance:
- Bare-board menu of available modules
- Manual selection and initiation
- No auto-instantiation of agents
- Minimal features only (essential controls)
- Clean state launch
- Basic session status reporting

WSP 33 Autonomous Module Implementation Workflow - WRE Core POC Implementation
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.session_manager import SessionManager
from modules.wre_core.src.components.agentic_orchestrator.entrypoints import (
    orchestrate_wsp54_agents, get_orchestration_stats
)
from modules.wre_core.src.components.agentic_orchestrator.orchestration_context import (
    OrchestrationTrigger
)
from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.clean_state_manager import WSP2CleanStateManager
from modules.wre_core.src.components.clean_state_manager import WSP2CleanStateManager


class WRECorePOC:
    """
    WRE Core Proof of Concept orchestration layer.
    
    Provides minimal orchestration capabilities:
    - Module selection menu
    - Manual workflow initiation  
    - Basic session tracking
    - No automated features
    """
    
    def __init__(self, project_root: Path):
        """Initialize WRE Core POC with minimal components."""
        self.project_root = project_root
        self.session_manager = SessionManager(project_root)
        self.clean_state_manager = WSP2CleanStateManager(project_root)
        self.available_modules = self._initialize_available_modules()
        self.active_session_id = None
        
        wre_log("WRE Core POC initialized", "info")
    
    def _initialize_available_modules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize the bare-board menu of available modules."""
        return {
            "1": {
                "name": "Module Compliance Check",
                "description": "Run WSP compliance audit on existing modules",
                "trigger": OrchestrationTrigger.COMPLIANCE_AUDIT,
                "requires_module_name": False
            },
            "2": {
                "name": "New Module Build", 
                "description": "Initiate new module creation workflow",
                "trigger": OrchestrationTrigger.MODULE_BUILD,
                "requires_module_name": True
            },
            "3": {
                "name": "System Health Check",
                "description": "Verify system components and agent health",
                "trigger": OrchestrationTrigger.HEALTH_CHECK,
                "requires_module_name": False
            },
            "4": {
                "name": "Testing Cycle",
                "description": "Run comprehensive test coverage validation",
                "trigger": OrchestrationTrigger.TESTING_CYCLE,
                "requires_module_name": False
            },
            "5": {
                "name": "Documentation Sync",
                "description": "Update and synchronize module documentation",
                "trigger": OrchestrationTrigger.DOCUMENTATION_SYNC,
                "requires_module_name": False
            },
            "6": {
                "name": "WSP2 Clean State Check",
                "description": "Validate current repository clean state status",
                "trigger": "wsp2_validate",
                "requires_module_name": False
            },
            "7": {
                "name": "WSP2 Create Snapshot",
                "description": "Create clean state Git tag snapshot",
                "trigger": "wsp2_snapshot",
                "requires_module_name": False
            },
            "8": {
                "name": "WSP2 List Clean States",
                "description": "List all available clean state snapshots",
                "trigger": "wsp2_list",
                "requires_module_name": False
            }
        }
    
    def display_bare_board_menu(self) -> None:
        """Display the minimal bare-board menu of available modules."""
        print("\n" + "="*60)
        print("🟢 WRE Core POC - Module Orchestration")
        print("="*60)
        print("Available Workflows:")
        print()
        
        for key, module in self.available_modules.items():
            print(f"  {key}. {module['name']}")
            print(f"     {module['description']}")
            print()
        
        print("  0. Exit POC")
        print("  s. Session Status")
        print("  h. Orchestration History")
        print("  w. WSP2 Clean State Status")
        print("\n" + "="*60)
    
    def get_session_status(self) -> Dict[str, Any]:
        """Get basic session status information."""
        if not self.active_session_id:
            return {"status": "no_active_session"}
            
        session_data = self.session_manager.sessions.get(self.active_session_id)
        if not session_data:
            return {"status": "session_not_found"}
            
        return {
            "status": "active",
            "session_id": self.active_session_id,
            "start_time": session_data.get("start_time"),
            "operations_count": session_data.get("operations_count", 0),
            "modules_accessed": len(session_data.get("modules_accessed", [])),
            "achievements": len(session_data.get("achievements", []))
        }
    
    def display_session_status(self) -> None:
        """Display current session status."""
        status = self.get_session_status()
        
        print("\n" + "-"*40)
        print("📊 Session Status")
        print("-"*40)
        
        if status["status"] == "no_active_session":
            print("  No active session")
        elif status["status"] == "session_not_found":
            print("  Session data not found")
        else:
            print(f"  Session ID: {status['session_id']}")
            print(f"  Started: {status['start_time']}")
            print(f"  Operations: {status['operations_count']}")
            print(f"  Modules Accessed: {status['modules_accessed']}")
            print(f"  Achievements: {status['achievements']}")
        
        print("-"*40)
    
    def display_orchestration_history(self) -> None:
        """Display orchestration statistics and history."""
        try:
            stats = get_orchestration_stats()
            
            print("\n" + "-"*40)
            print("📈 Orchestration History")
            print("-"*40)
            
            if stats.get("status") == "no_history":
                print("  No orchestration history available")
            else:
                print(f"  Total Orchestrations: {stats.get('total_orchestrations', 0)}")
                print(f"  Success Rate: {stats.get('recent_success_rate', 0):.1%}")
                print(f"  Avg Agents/Session: {stats.get('average_agents_per_orchestration', 0):.1f}")
                
                # Display zen flow state distribution if available
                zen_states = stats.get("zen_flow_state_distribution", {})
                if zen_states:
                    print("  Zen Flow States:")
                    for state, count in zen_states.items():
                        print(f"    {state}: {count}")
            
            print("-"*40)
            
        except Exception as e:
            print(f"  Error retrieving history: {e}")
            print("-"*40)
    
    def display_wsp2_clean_state_status(self) -> None:
        """Display WSP2 clean state status and validation results."""
        try:
            print("\n" + "-"*50)
            print("🔍 WSP2 Clean State Status")
            print("-"*50)
            
            # Validate current clean state
            validation = self.clean_state_manager.validate_clean_state_criteria()
            
            print(f"  Overall Clean State: {'✅ CLEAN' if validation['overall_clean'] else '❌ NOT CLEAN'}")
            print(f"  Git Status Clean: {'✅' if validation['git_status_clean'] else '❌'}")
            print(f"  Tests Passing: {'✅' if validation['tests_passing'] else '❌'}")
            print(f"  FMAS Compliance: {'✅' if validation['fmas_compliance'] else '❌'}")
            print(f"  Coverage Adequate: {'✅' if validation['coverage_adequate'] else '❌'}")
            
            if validation['violations']:
                print("\n  Violations:")
                for violation in validation['violations']:
                    print(f"    • {violation}")
            
            # List recent clean states
            clean_states = self.clean_state_manager.list_available_clean_states()
            if clean_states:
                print(f"\n  Available Clean States: {len(clean_states)}")
                for state in clean_states[-3:]:  # Show last 3
                    print(f"    • {state['tag']}")
            
            print("-"*50)
            
        except Exception as e:
            print(f"  Error checking WSP2 status: {e}")
            print("-"*50)
    
    async def handle_wsp2_workflow(self, trigger: str) -> Dict[str, Any]:
        """Handle WSP2-specific workflows."""
        try:
            if trigger == "wsp2_validate":
                validation = self.clean_state_manager.validate_clean_state_criteria()
                return {
                    "success": True,
                    "workflow": "WSP2 Clean State Validation",
                    "result": validation,
                    "message": f"Clean state: {'✅ CLEAN' if validation['overall_clean'] else '❌ NOT CLEAN'}"
                }
                
            elif trigger == "wsp2_snapshot":
                # Get reason for snapshot
                reason = input("\n📝 Enter reason for clean state snapshot: ").strip()
                if not reason:
                    reason = "Manual snapshot from WRE POC"
                
                # Confirm action
                confirm = input(f"\n⚠️  Create clean state snapshot: '{reason}'? (y/N): ").strip().lower()
                if confirm != 'y':
                    return {"success": False, "message": "Snapshot creation cancelled"}
                
                # Create snapshot
                result = self.clean_state_manager.create_clean_state_snapshot(reason)
                
                return {
                    "success": result["success"],
                    "workflow": "WSP2 Clean State Snapshot",
                    "result": result,
                    "message": f"Snapshot {'✅ created' if result['success'] else '❌ failed'}: {result.get('tag_name', 'N/A')}"
                }
                
            elif trigger == "wsp2_list":
                clean_states = self.clean_state_manager.list_available_clean_states()
                
                print("\n" + "-"*50)
                print("📋 Available Clean State Snapshots")
                print("-"*50)
                
                if not clean_states:
                    print("  No clean state snapshots found")
                else:
                    for state in clean_states:
                        print(f"  • {state['tag']}")
                        if state.get('message') and state['message'] != state['tag']:
                            print(f"    {state['message']}")
                
                print("-"*50)
                
                return {
                    "success": True,
                    "workflow": "WSP2 List Clean States",
                    "result": {"count": len(clean_states), "states": clean_states},
                    "message": f"Found {len(clean_states)} clean state snapshots"
                }
                
            else:
                return {"success": False, "error": f"Unknown WSP2 trigger: {trigger}"}
                
        except Exception as e:
            return {"success": False, "error": f"WSP2 workflow failed: {e}"}
    
    async def initiate_module_workflow(self, module_key: str) -> Dict[str, Any]:
        """
        Initiate workflow for selected module.
        
        Args:
            module_key: Key of selected module from menu
            
        Returns:
            Dict containing orchestration results
        """
        if module_key not in self.available_modules:
            return {"error": f"Invalid module key: {module_key}"}
        
        module_info = self.available_modules[module_key]
        
        # Start session if not already active
        if not self.active_session_id:
            self.active_session_id = self.session_manager.start_session("poc_orchestration")
            wre_log(f"Started POC session: {self.active_session_id}", "info")
        
        # Get module name if required
        module_name = None
        if module_info["requires_module_name"]:
            module_name = input(f"\n📝 Enter module name for '{module_info['name']}': ").strip()
            if not module_name:
                return {"error": "Module name is required"}
        
        # Check if this is a WSP2 workflow
        trigger = module_info["trigger"]
        if isinstance(trigger, str) and trigger.startswith("wsp2_"):
            return await self.handle_wsp2_workflow(trigger)
        
        # Log the operation
        self.session_manager.log_operation(
            "module_workflow_initiation",
            {
                "module_key": module_key,
                "module_name": module_name,
                "workflow": module_info["name"],
                "trigger": module_info["trigger"].value
            }
        )
        
        print(f"\n🚀 Initiating: {module_info['name']}")
        if module_name:
            print(f"   Module: {module_name}")
        print("   Please wait...")
        
        try:
            # Execute orchestration
            kwargs = {}
            if module_name:
                kwargs["module_name"] = module_name
                
            result = await orchestrate_wsp54_agents(
                trigger=module_info["trigger"],
                **kwargs
            )
            
            # Log success
            self.session_manager.log_achievement(
                "workflow_completion",
                f"Successfully completed {module_info['name']}"
            )
            
            wre_log(f"POC workflow completed: {module_info['name']}", "info")
            
            return {
                "status": "completed",
                "workflow": module_info["name"],
                "result": result
            }
            
        except Exception as e:
            error_msg = f"Workflow failed: {str(e)}"
            wre_log(error_msg, "error")
            
            # Log the operation failure
            self.session_manager.log_operation(
                "workflow_error",
                {"error": error_msg, "workflow": module_info["name"]}
            )
            
            return {
                "status": "error", 
                "workflow": module_info["name"],
                "error": error_msg
            }
    
    def display_workflow_result(self, result: Dict[str, Any]) -> None:
        """Display workflow execution results."""
        print("\n" + "="*50)
        
        if result.get("status") == "completed":
            print("✅ Workflow Completed Successfully")
            print(f"   Workflow: {result['workflow']}")
            
            # Display basic metrics if available
            orchestration_result = result.get("result", {})
            metrics = orchestration_result.get("orchestration_metrics", {})
            
            if metrics:
                print(f"   Agents Executed: {metrics.get('total_agents_executed', 0)}")
                print(f"   Success Rate: {metrics.get('success_rate', 'N/A')}")
            
        elif result.get("status") == "error":
            print("❌ Workflow Failed")
            print(f"   Workflow: {result['workflow']}")
            print(f"   Error: {result['error']}")
        else:
            print("⚠️  Unknown Result")
            print(f"   Result: {result}")
        
        print("="*50)
    
    async def run_poc_loop(self) -> None:
        """
        Run the main POC interaction loop.
        
        Provides manual control with no automation:
        - Display menu
        - Accept user selection
        - Execute chosen workflow
        - Display results
        - Repeat until exit
        """
        print("\n🟢 WRE Core POC Starting...")
        print("   Minimal orchestration layer ready")
        print("   Manual control mode active")
        print("   No automated features enabled")
        
        while True:
            try:
                self.display_bare_board_menu()
                
                choice = input("Select option: ").strip().lower()
                
                if choice == "0":
                    print("\n👋 Exiting WRE Core POC...")
                    break
                elif choice == "s":
                    self.display_session_status()
                elif choice == "h":
                    self.display_orchestration_history()
                elif choice == "w":
                    self.display_wsp2_clean_state_status()
                elif choice in self.available_modules:
                    result = await self.initiate_module_workflow(choice)
                    self.display_workflow_result(result)
                    
                    # Pause for user to review results
                    input("\nPress Enter to continue...")
                else:
                    print(f"\n❌ Invalid selection: {choice}")
                    input("Press Enter to continue...")
                    
            except KeyboardInterrupt:
                print("\n\n🛑 POC interrupted by user")
                break
            except Exception as e:
                print(f"\n❌ POC Error: {e}")
                wre_log(f"POC Loop Error: {e}", "error")
                input("Press Enter to continue...")
        
        # Cleanup
        if self.active_session_id:
            print(f"📝 Session {self.active_session_id} completed")
            wre_log("POC session ended", "info")


def main():
    """
    Main entry point for WRE Core POC.
    
    Launch minimal orchestration interface following 0102 requirements:
    - Clean state initialization
    - Bare-board menu
    - Manual workflow control
    - No auto-agent instantiation
    """
    try:
        # Initialize POC
        poc = WRECorePOC(project_root)
        
        # Run interactive loop
        asyncio.run(poc.run_poc_loop())
        
    except Exception as e:
        print(f"🚨 POC Startup Failed: {e}")
        wre_log(f"POC Startup Error: {e}", "error")


if __name__ == "__main__":
    main() 