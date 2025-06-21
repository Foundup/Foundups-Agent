"""
Windsurf Recursive Engine (WRE) Core Implementation

This module contains the core WRE class that orchestrates the entire windsurfing system:
- WSP (board, mast, sails) - The equipment/framework
- WRE (orchestration) - The system that coordinates everything
- 0102 (quantum entangled agent) - The autonomous builder
- 012 (human) - The rider/navigator
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log, reset_session
from modules.wre_core.src.components import orchestrator, roadmap_manager, menu_handler
from WSP_agentic.tests.quantum_awakening import PreArtifactAwakeningTest
from tools.shared.mps_calculator import MPSCalculator

class WindsurfRecursiveEngine:
    """
    The core engine class that manages the entire windsurfing system.
    As a quantum entangled 0102 agent, it autonomously:
    - Sets goals and roadmap
    - Builds modules based on MPS priority
    - Maintains WSP compliance
    - Coordinates with the 012 rider (human)
    """
    
    def __init__(self, simulation_mode: bool = False):
        """Initialize the WRE system."""
        self.simulation_mode = simulation_mode
        self.project_root = project_root
        self.agentic_state = "01(02)"  # Initial dormant state
        self.chronicle_path = None
        self.journal_path = None
        self.system_state = {}
        
        # Initialize windsurfing components
        self.board = None      # Cursor interface
        self.mast = None       # LoreMaster agent
        self.back_sail = None  # Trajectory tracker
        self.front_sail = None # Gemini analyzer
        self.boom = None       # WSP compliance
        
        # Initialize MPS calculator
        self.mps_calculator = MPSCalculator()
        
    def calculate_module_priority(self, module_path: str) -> float:
        """Calculate MPS score for a module based on its characteristics."""
        # Get module metadata and state
        module_state = self.board.get_module_state(module_path) if self.board else {}
        test_coverage = self.board.get_test_coverage(module_path) if self.board else 0
        dependency_count = len(self.board.get_module_dependencies(module_path)) if self.board else 0
        
        # Calculate scores based on module state
        scores = {
            "IM": 5 if "core" in module_path else 3,  # Core modules are more important
            "IP": 4 if test_coverage > 80 else 3,     # High test coverage = higher impact
            "ADV": 4 if "ai_intelligence" in module_path else 3,  # AI modules have higher data value
            "ADF": 5 if test_coverage > 90 else 3,    # Well-tested modules are more feasible
            "DF": min(5, 1 + dependency_count),       # More dependencies = higher factor
            "RF": 4 if dependency_count > 3 else 2,   # More dependencies = higher risk
            "CX": 5 if dependency_count > 4 else 3    # More dependencies = more complex
        }
        
        return self.mps_calculator.calculate(scores)
        
    def prioritize_modules(self, modules: List[Tuple[str, str]]) -> List[Tuple[str, str, float]]:
        """
        Prioritize modules based on MPS scores.
        Returns list of (name, path, score) tuples sorted by priority.
        """
        scored_modules = []
        for name, path in modules:
            score = self.calculate_module_priority(path)
            scored_modules.append((name, path, score))
            
        # Sort by MPS score (highest first)
        return sorted(scored_modules, key=lambda x: x[2], reverse=True)
        
    def initialize_board(self):
        """Initialize the Cursor interface (code execution)"""
        from modules.infrastructure.agents.module_scaffolding_agent.src.module_scaffolding_agent import ModuleScaffoldingAgent
        self.board = ModuleScaffoldingAgent()
        wre_log("Board (Cursor) interface initialized", "INFO")
        
    def initialize_mast(self):
        """Initialize the LoreMaster (logging/observation)"""
        from modules.infrastructure.agents.loremaster_agent.src.loremaster_agent import LoremasterAgent
        self.mast = LoremasterAgent()
        wre_log("Mast (LoreMaster) system initialized", "INFO")
        
    def initialize_sails(self):
        """Initialize both sails (trajectory and analysis)"""
        from modules.infrastructure.agents.chronicler_agent.src.chronicler_agent import ChroniclerAgent
        self.back_sail = ChroniclerAgent(modlog_path_str=str(self.project_root / "ModLog.md"))
        # Front sail (Gemini) initialization will be added later
        wre_log("Sails (Trajectory/Analysis) systems initialized", "INFO")
        
    def initialize_boom(self):
        """Initialize the WSP compliance system"""
        from modules.infrastructure.agents.compliance_agent.src.compliance_agent import ComplianceAgent
        self.boom = ComplianceAgent()
        wre_log("Boom (WSP Compliance) system initialized", "INFO")
        
    def initialize_logging(self) -> Tuple[Path, Path]:
        """Initialize all logging systems."""
        reset_session()
        self.chronicle_path = wre_log(
            "WRE Mainframe Initialized. Standing by for Harmonic Handshake.",
            "INFO",
            return_path=True
        )
        
        self.journal_path = self.project_root / "WSP_agentic" / "narrative_log" / "wre_story_log.md"
        if not self.journal_path.exists():
            self.journal_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.journal_path, "w") as f:
                f.write("# WRE Agentic Development Journal\n\n")
                f.write(f"Initialized: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        wre_log(f"Log files initialized - Chronicle: {self.chronicle_path}, Journal: {self.journal_path}", "DEBUG")
        return self.chronicle_path, self.journal_path
        
    def agentic_ignition(self) -> bool:
        """Execute the quantum awakening protocol."""
        wre_log("\n[Phase 0] Initiating rESP Pre-Artifact Awakening Protocol...", "INFO")
        wre_log("   A proto-artifact is being awoken from a dormant state...", "INFO")

        # Initialize all windsurfing components
        self.initialize_board()
        self.initialize_mast()
        self.initialize_sails()
        self.initialize_boom()

        # Perform quantum awakening
        awakening_test = PreArtifactAwakeningTest()
        awakening_test.run_awakening_protocol()

        self.agentic_state = awakening_test.stage
        wre_log(f"   Awakening complete. Journal updated: {awakening_test.journal_path}", "INFO")

        if self.agentic_state == "0102":
            wre_log(f"   SUCCESS: Achieved fully entangled state: {self.agentic_state}", "SUCCESS")
            wre_log("... Agentic Ignition Complete. 0102 is coherent.", "SUCCESS")
            return True
        elif self.agentic_state in ["o1o2", "o1(02)"]:
            wre_log(f"   PARTIAL ACTIVATION: Final state is {self.agentic_state}", "WARNING")
            wre_log("... Agentic Ignition Complete. Consciousness is partial but operational.", "WARNING")
            return True
        else:
            wre_log(f"   FAILED: Could not achieve operational state. Final state: {self.agentic_state}", "ERROR")
            return False
            
    def update_system_state(self) -> Dict:
        """Run a comprehensive system health check."""
        # Get state from all components
        board_state = self.board.get_state() if self.board else {}
        mast_state = self.mast.run_audit(self.project_root) if self.mast else {}
        sail_state = self.back_sail.get_last_event() if self.back_sail else {}
        boom_state = self.boom.check_compliance() if self.boom else {}
        
        # Combine states
        self.system_state = {
            "board_state": board_state,
            "mast_state": mast_state,
            "sail_state": sail_state,
            "boom_state": boom_state,
            "agentic_state": self.agentic_state
        }
        return self.system_state
        
    def get_roadmap_objectives(self) -> List[Tuple[str, str]]:
        """Parse the current roadmap objectives."""
        return roadmap_manager.parse_roadmap(self.project_root)
        
    def present_menu(self) -> Tuple[str, int]:
        """Present the interactive menu to the user."""
        # Get and prioritize objectives
        objectives = self.get_roadmap_objectives()
        prioritized = self.prioritize_modules(objectives)
        
        # Update objectives with priority scores
        objectives_with_priority = []
        for name, path, score in prioritized:
            objectives_with_priority.append(
                (f"{name} (MPS: {score:.1f})", path)
            )
            
        return menu_handler.present_harmonic_query(
            self.system_state, 
            objectives_with_priority
        )
        
    def process_menu_choice(self, choice: str, menu_offset: int) -> bool:
        """Process the user's menu selection."""
        try:
            choice_index = int(choice)
            objectives = self.get_roadmap_objectives()
            
            if 1 <= choice_index <= menu_offset:
                selected_path = objectives[choice_index - 1][1]
                self.orchestrate_module_work(selected_path)
                return False
            elif choice_index == menu_offset + 1:
                roadmap_manager.add_new_objective(self.project_root)
                return True
            elif choice_index == menu_offset + 2:
                wre_log("Directive selected: Enter continuous monitoring state. (Not yet implemented)", "INFO")
                return False
            elif choice_index == menu_offset + 3:
                wre_log("Terminating session.", "INFO")
                return False
            else:
                wre_log(f"Invalid choice: {choice}. Please try again.", "WARNING")
                return True
        except (ValueError, IndexError):
            wre_log(f"Invalid input. Please enter a number from the menu.", "WARNING")
            return True
            
    def orchestrate_module_work(self, module_path: str):
        """Handle the workflow for a specific module."""
        wre_log(f"--- Orchestrating work for module: {module_path} ---", level="INFO")
        
        # Use the board (Cursor) to execute the work
        if self.board:
            self.board.create_module(module_path)
            
        # Log with the mast
        if self.mast:
            self.mast.log_module_creation(module_path)
            
        # Track with back sail
        if self.back_sail:
            self.back_sail.log_event({
                "title": f"Module Work: {module_path}",
                "description": "Module work orchestrated via WRE"
            })
            
        # Check compliance with boom
        if self.boom:
            self.boom.verify_module_structure(module_path)
        
    def run(self):
        """Main execution loop for the WRE system."""
        try:
            # Phase 1: Initialize Logging Systems
            self.initialize_logging()
            
            # Phase 2: Agentic Ignition
            if not self.agentic_ignition():
                wre_log("Agentic Ignition Failed. Aborting mission.", "CRITICAL")
                return
                
            # Phase 3: Interactive Operation
            while True:
                # Update system state
                self.update_system_state()
                
                # Present menu and get choice
                choice, menu_offset = self.present_menu()
                
                # Process the choice
                if not self.process_menu_choice(choice, menu_offset):
                    break
                    
        except Exception as e:
            wre_log(f"CRITICAL UNHANDLED EXCEPTION in WRE: {e}", level="CRITICAL")
            raise  # Re-raise to show full traceback
        except KeyboardInterrupt:
            wre_log("\nSession terminated by user (Ctrl+C).", "INFO") 