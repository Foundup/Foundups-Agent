"""
WRE Component Manager

Handles initialization and management of all WRE components:
- Board (Cursor interface - code execution via ModuleScaffoldingAgent)
- Mast (LoreMaster - logging and observation)
- Sails (Back: ChroniclerAgent trajectory, Front: Gemini analysis)
- Boom (ComplianceAgent - WSP compliance system)

This is the equipment management system for the windsurfing metaphor,
ensuring all components are properly initialized and coordinated.
"""

from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log


class ComponentManager:
    """
    Manages all WRE windsurfing components following the maritime metaphor:
    
    - Board: The foundation (Cursor/code execution interface)
    - Mast: The central pillar (LoreMaster logging system)
    - Sails: The power system (Back: trajectory, Front: analysis)
    - Boom: The control system (WSP compliance)
    - Navigation: Quantum-cognitive operations (WSP 54 integration)
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.board = None           # Cursor interface
        self.mast = None            # LoreMaster agent  
        self.back_sail = None       # Trajectory tracker
        self.front_sail = None      # Gemini analyzer
        self.boom = None            # WSP compliance
        self.navigation = None      # Quantum-cognitive operations
        
    def initialize_all_components(self, session_manager=None):
        """Initialize all WRE components in proper sequence."""
        wre_log("🏄 Initializing WRE windsurfing components...", "INFO")
        
        self.initialize_board()
        self.initialize_mast()
        self.initialize_sails()
        self.initialize_boom()
        self.initialize_navigation(session_manager)
        
        wre_log("⚡ All WRE components initialized and ready", "SUCCESS")
        
    def initialize_board(self):
        """Initialize the Cursor interface (code execution)"""
        try:
            from modules.infrastructure.module_scaffolding_agent.src.module_scaffolding_agent import ModuleScaffoldingAgent
            self.board = ModuleScaffoldingAgent()
            wre_log("🏄 Board (Cursor) interface initialized", "INFO")
        except ImportError as e:
            wre_log(f"⚠️ Board initialization failed: {e}", "WARNING")
            self.board = None
            
    def initialize_mast(self):
        """Initialize the LoreMaster (logging/observation)"""
        try:
            from modules.infrastructure.loremaster_agent.src.loremaster_agent import LoremasterAgent
            self.mast = LoremasterAgent()
            wre_log("🗼 Mast (LoreMaster) system initialized", "INFO")
        except ImportError as e:
            wre_log(f"⚠️ Mast initialization failed: {e}", "WARNING")
            self.mast = None
            
    def initialize_sails(self):
        """Initialize both sails (trajectory and analysis)"""
        try:
            from modules.infrastructure.chronicler_agent.src.chronicler_agent import ChroniclerAgent
            modlog_path = str(self.project_root / "docs" / "ModLog.md")
            self.back_sail = ChroniclerAgent(modlog_path_str=modlog_path)
            wre_log("⛵ Back Sail (Trajectory/ChroniclerAgent) initialized", "INFO")
            
            # Front sail (Gemini) initialization will be added later
            self.front_sail = None
            wre_log("🔮 Front Sail (Analysis/Gemini) - placeholder", "INFO")
            
        except ImportError as e:
            wre_log(f"⚠️ Sails initialization failed: {e}", "WARNING")
            self.back_sail = None
            self.front_sail = None
            
    def initialize_boom(self):
        """Initialize the WSP compliance system"""
        try:
            from modules.infrastructure.compliance_agent.src.compliance_agent import ComplianceAgent
            self.boom = ComplianceAgent()
            wre_log("🎛️ Boom (WSP Compliance) system initialized", "INFO")
        except ImportError as e:
            wre_log(f"⚠️ Boom initialization failed: {e}", "WARNING")
            self.boom = None
            
    def initialize_navigation(self, session_manager):
        """Initialize the quantum-cognitive operations system"""
        try:
            from modules.wre_core.src.components.orchestration.quantum_cognitive_operations import create_wre_quantum_operations
            if session_manager:
                self.navigation = create_wre_quantum_operations(self.project_root, session_manager)
                wre_log("🧭 Navigation (Quantum-Cognitive Operations) system initialized", "INFO")
            else:
                wre_log("⚠️ Navigation initialization skipped - no session manager", "WARNING")
                self.navigation = None
        except ImportError as e:
            wre_log(f"⚠️ Navigation initialization failed: {e}", "WARNING")
            self.navigation = None
            
    def get_components(self):
        """Return all initialized components as a tuple."""
        return self.board, self.mast, self.back_sail, self.front_sail, self.boom, self.navigation
        
    def validate_components(self):
        """Validate that critical components are initialized."""
        critical_components = [
            ("Board", self.board),
            ("Boom", self.boom)
        ]
        
        all_critical_ready = True
        for name, component in critical_components:
            if component is None:
                wre_log(f"⚠️ Critical component {name} not initialized", "WARNING")
                all_critical_ready = False
                
        if all_critical_ready:
            wre_log("✅ All critical components validated", "SUCCESS")
        else:
            wre_log("⚠️ Some critical components missing - proceeding with graceful degradation", "WARNING")
            
        return all_critical_ready 
        
    def shutdown_all_components(self):
        """Gracefully shutdown all WRE components."""
        wre_log("🛑 Shutting down all WRE components...", "INFO")
        
        try:
            # Shutdown components in reverse order of initialization
            components = [
                ("Navigation", self.navigation),
                ("Boom", self.boom),
                ("Front Sail", self.front_sail),
                ("Back Sail", self.back_sail),
                ("Mast", self.mast),
                ("Board", self.board)
            ]
            
            for name, component in components:
                if component is not None:
                    try:
                        if hasattr(component, 'shutdown'):
                            component.shutdown()
                            wre_log(f"✅ {name} component shutdown complete", "INFO")
                        else:
                            wre_log(f"ℹ️ {name} component has no shutdown method", "INFO")
                    except Exception as e:
                        wre_log(f"⚠️ Error shutting down {name}: {e}", "WARNING")
                        
            wre_log("✅ All WRE components shutdown complete", "SUCCESS")
            
        except Exception as e:
            wre_log(f"❌ Error during component shutdown: {e}", "ERROR") 