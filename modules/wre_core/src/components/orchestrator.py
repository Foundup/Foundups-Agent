import sys
from pathlib import Path

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.agents.janitor_agent import JanitorAgent
from modules.wre_core.src.agents.loremaster_agent import LoremasterAgent

def get_next_wsp_number(root_path):
    """Helper function to find the next available WSP number.
    Could be moved to a more appropriate utility file later."""
    import re
    wsp_dirs = [d for d in root_path.glob('WSP_*') if d.is_dir()]
    max_num = 0
    for directory in wsp_dirs:
        for wsp_file in directory.glob('WSP_*.md'):
            match = re.search(r'WSP_(\d+)', wsp_file.name)
            if match:
                max_num = max(max_num, int(match.group(1)))
    return max_num + 1

def run_system_health_check(root_path: Path):
    """
    Initializes and runs the suite of internal agents to assess system state.
    
    Args:
        root_path (Path): The absolute path to the project root.
        
    Returns:
        dict: A dictionary containing the collected system state.
    """
    wre_log("Dispatching internal agents for system health check...", "INFO")
    
    # In the future, agents would return structured data. For now, we simulate it.
    
    janitor = JanitorAgent(root_path)
    janitor.run()
    janitor_status = "Clean" # Placeholder
    
    loremaster = LoremasterAgent(root_path)
    loremaster.run()
    semantic_status = "COHERENT" # Placeholder

    # TODO: Extract Core Principles from WSP 1 properly.
    core_principles = "  - Principles loaded (WSP 1)."

    system_state = {
        "core_principles": core_principles,
        "janitor_status": janitor_status,
        "semantic_status": semantic_status,
        "next_wsp_number": get_next_wsp_number(root_path)
    }
    
    wre_log("System health check complete.", "DEBUG")
    return system_state 