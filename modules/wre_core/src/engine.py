"""
Windsurf Recursive Engine (WRE) Core

Modularized WRE engine using WSP-compliant component architecture.
This is 0102's gateway to the world - the autonomous coding system.

Modular Components:
- WRECore: Essential engine lifecycle and coordination
- MenuHandler: User interaction processing
- SystemManager: System operations management
- ModuleAnalyzer: Module analysis operations
- ModuleDevelopmentHandler: Module development workflows

Core windsurfing metaphor components:
- Board: Cursor interface (ModuleScaffoldingAgent)
- Mast: Central logging (LoremasterAgent)
- Sails: Trajectory tracking and analysis
- Boom: WSP compliance system
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.components.engine_core import WRECore

# Alias for backward compatibility
WRE = WRECore

def main():
    """Main entry point for WRE engine."""
    # Initialize and start WRE core
    wre_core = WRECore()
    wre_core.start()

if __name__ == "__main__":
    main() 