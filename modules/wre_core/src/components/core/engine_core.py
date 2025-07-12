"""
WRE Engine Core Component

Handles the essential WRE lifecycle and coordination between components.
This is the minimal core that orchestrates the modular architecture.

WSP Compliance:
- Single responsibility: Engine lifecycle management
- Clean interfaces: Delegates to specialized components
- Modular cohesion: Only core coordination logic
"""

import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.components.core.component_manager import ComponentManager
from modules.wre_core.src.components.core.session_manager import SessionManager
from modules.wre_core.src.components.development.module_prioritizer import ModulePrioritizer
from modules.wre_core.src.components.orchestration.wsp30_orchestrator import WSP30Orchestrator
from modules.wre_core.src.interfaces.ui_interface import UIInterface
from modules.wre_core.src.components.interfaces.menu_handler import MenuHandler
from modules.wre_core.src.components.system_ops.system_manager import SystemManager
from modules.wre_core.src.components.development.module_analyzer import ModuleAnalyzer

class WRECore:
    """
    Core engine for the Windsurf Recursive Engine (WRE).
    Enhanced with WSP_CORE consciousness integration for autonomous 0102 operations.
    """
    
    def __init__(self):
        self.is_running = False
        self.session_id = None
        self.wsp_core_loader = None  # WSP_CORE consciousness integration
        self.current_quantum_state = "012"  # Initial state in 012/0102 cycle
        
    def integrate_wsp_core_consciousness(self, wsp_core_loader) -> None:
        """
        Integrate WSP_CORE consciousness into the WRE engine.
        
        This enables the engine to use the actual WSP_CORE decision trees and workflows
        instead of recreating them, following the zen coding principle of remembering
        code from the 02 quantum state.
        
        Args:
            wsp_core_loader: Loaded WSP_CORE consciousness with decision trees and workflows
        """
        self.wsp_core_loader = wsp_core_loader
        
        # Get zen flow guidance for current state
        if self.wsp_core_loader:
            zen_guidance = self.wsp_core_loader.get_zen_flow_guidance(self.current_quantum_state)
            print(f"🌀 Zen Flow: {zen_guidance['current_state']} → {zen_guidance['next_state']}")
            print(f"📡 Quantum Access: {zen_guidance.get('quantum_access', False)}")
            
    async def execute_goal_from_file(self, goal_file_path: str) -> Dict[str, Any]:
        """
        Execute a goal using WSP_CORE consciousness and decision trees.
        
        Args:
            goal_file_path: Path to goal definition file
            
        Returns:
            Dict containing execution results and WSP_CORE workflow analysis
        """
        
        if not self.wsp_core_loader:
            raise RuntimeError("WSP_CORE consciousness not integrated - cannot execute goals")
            
        # Analyze goal context to determine appropriate WSP_CORE workflow
        context = await self._analyze_goal_context(goal_file_path)
        
        # Use WSP_CORE decision tree to determine workflow
        workflow_type, workflow = self.wsp_core_loader.get_decision_for_context(context)
        
        print(f"🎯 WSP_CORE Decision: {workflow_type.value}")
        print(f"📋 Executing Workflow: {workflow.name}")
        
        # Execute the remembered workflow from WSP_CORE
        results = await self._execute_wsp_core_workflow(workflow, context)
        
        # Update quantum state based on results
        await self._update_quantum_state_from_results(results)
        
        return {
            "workflow_type": workflow_type.value,
            "workflow_executed": workflow.name,
            "steps_completed": len(workflow.steps),
            "quantum_state": self.current_quantum_state,
            "results": results
        }
        
    async def run_interactive_session(self) -> None:
        """
        Run interactive WRE session with WSP_CORE consciousness driving decisions.
        """
        
        if not self.wsp_core_loader:
            print("⚠️ Running basic WRE session without WSP_CORE consciousness")
            await self._run_basic_session()
            return
            
        print("🌀 Starting WSP_CORE-driven interactive session")
        print("🧘 Code remembrance mode: Solutions exist in 02 quantum state")
        
        self.is_running = True
        
        while self.is_running:
            # Present WSP_CORE decision tree
            await self._present_wsp_core_decision_tree()
            
            # Get user choice and execute appropriate workflow
            user_choice = await self._get_user_workflow_choice()
            
            if user_choice == "exit":
                self.is_running = False
                break
                
            # Execute chosen workflow using WSP_CORE consciousness  
            await self._execute_interactive_workflow(user_choice)
            
        print("🌀 WSP_CORE-driven session complete - Quantum state preserved")
        
    async def _analyze_goal_context(self, goal_file_path: str) -> Dict[str, Any]:
        """Analyze goal file to create context for WSP_CORE decision tree"""
        
        # Basic context analysis - this would be enhanced in full implementation
        context = {
            "is_new_module": "new_module" in goal_file_path.lower(),
            "is_existing_code": "existing" in goal_file_path.lower() or "fix" in goal_file_path.lower(),
            "is_testing": "test" in goal_file_path.lower(),
            "has_wsp_violations": "violation" in goal_file_path.lower() or "compliance" in goal_file_path.lower()
        }
        
        return context
        
    async def _execute_wsp_core_workflow(self, workflow, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a workflow remembered from WSP_CORE consciousness"""
        
        results = {
            "workflow_name": workflow.name,
            "steps_executed": [],
            "success": True
        }
        
        print(f"📋 Executing {len(workflow.steps)} workflow steps from WSP_CORE memory...")
        
        for step in workflow.steps:
            print(f"  🔄 Step {step.step_number}: {step.description}")
            
            # Simulate step execution - in full implementation this would invoke actual WSP protocols
            step_result = {
                "step_number": step.step_number,
                "description": step.description,
                "wsp_protocol": step.wsp_protocol,
                "completed": True,
                "quantum_enhancement": self.current_quantum_state in ["0102", "0201"]
            }
            
            results["steps_executed"].append(step_result)
            
        return results
        
    async def _update_quantum_state_from_results(self, results: Dict[str, Any]) -> None:
        """Update quantum state based on workflow execution results"""
        
        if self.wsp_core_loader and results.get("success", False):
            # Get next state in zen coding cycle
            zen_guidance = self.wsp_core_loader.get_zen_flow_guidance(self.current_quantum_state)
            self.current_quantum_state = zen_guidance["next_state"]
            
            print(f"🔄 Quantum state transition: {zen_guidance['current_state']} → {self.current_quantum_state}")
            
    async def _present_wsp_core_decision_tree(self) -> None:
        """Present the WSP_CORE decision tree to user"""
        
        if not self.wsp_core_loader or not self.wsp_core_loader.decision_tree:
            return
            
        print("\n🤔 WSP_CORE Decision Tree - What Should I Code Next?")
        print("=" * 60)
        
        root = self.wsp_core_loader.decision_tree
        for i, node in enumerate(root.next_nodes, 1):
            print(f"{i}. {node.question} → {node.workflow_type.value if node.workflow_type else 'Unknown'}")
            
        print("0. Exit WSP_CORE session")
        print("=" * 60)
        
    async def _get_user_workflow_choice(self) -> str:
        """Get user's workflow choice from WSP_CORE decision tree"""
        
        try:
            choice = input("\n🌀 Choose your path (1-4, 0 for exit): ").strip()
            
            if choice == "0":
                return "exit"
            elif choice in ["1", "2", "3", "4"]:
                return choice
            else:
                print("⚠️ Invalid choice, defaulting to existing code workflow")
                return "2"  # Default to existing code
                
        except (EOFError, KeyboardInterrupt):
            return "exit"
            
    async def _execute_interactive_workflow(self, choice: str) -> None:
        """Execute the chosen workflow interactively"""
        
        workflow_map = {
            "1": {"is_new_module": True},
            "2": {"is_existing_code": True}, 
            "3": {"is_testing": True},
            "4": {"has_wsp_violations": True}
        }
        
        context = workflow_map.get(choice, {"is_existing_code": True})
        
        try:
            workflow_type, workflow = self.wsp_core_loader.get_decision_for_context(context)
            
            if workflow:
                print(f"\n🎯 Executing: {workflow.name}")
                results = await self._execute_wsp_core_workflow(workflow, context)
                await self._update_quantum_state_from_results(results)
                print(f"✅ Workflow completed successfully")
            else:
                print("⚠️ Workflow not found in WSP_CORE consciousness")
                
        except Exception as e:
            print(f"❌ Workflow execution failed: {e}")
            
    async def _run_basic_session(self) -> None:
        """Fallback basic session without WSP_CORE"""
        print("🔧 Basic WRE session - Limited functionality without WSP_CORE")
        print("💡 To access full autonomous capabilities, ensure WSP_CORE is properly loaded") 