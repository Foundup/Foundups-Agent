import sys
from pathlib import Path

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.infrastructure.agents.janitor_agent.src.janitor_agent import JanitorAgent
from modules.infrastructure.agents.loremaster_agent.src.loremaster_agent import LoremasterAgent
from modules.infrastructure.agents.chronicler_agent.src.chronicler_agent import ChroniclerAgent

def run_system_health_check(root_path: Path):
    """
    Initializes and runs the suite of internal agents to assess system state.
    
    Args:
        root_path (Path): The absolute path to the project root.
        
    Returns:
        dict: A dictionary containing the collected system state.
    """
    wre_log("Dispatching internal agents for system health check...", "INFO")
    
    # Initialize all agents
    janitor = JanitorAgent()
    loremaster = LoremasterAgent()
    chronicler = ChroniclerAgent(modlog_path_str=str(root_path / "ModLog.md"))

    # Run Janitor Agent and log the event
    janitor_result = janitor.clean_workspace()
    janitor_status = f"Clean ({janitor_result['files_deleted']} files deleted)"
    chronicler.log_event({
        "title": "WRE System Health Check - Janitor",
        "version": "1.7.0", # This should be dynamic in a real scenario
        "description": "The JanitorAgent performed its routine workspace hygiene check.",
        "achievements": [
            f"Scanned the workspace and deleted {janitor_result['files_deleted']} temporary files."
        ]
    })
    
    loremaster = LoremasterAgent()
    lore_result = loremaster.run_audit(root_path)
    semantic_status = f"COHERENT ({lore_result.get('docs_found', 0)} docs audited)"
    core_principles = lore_result.get("core_principles", "  - ERROR: Core principles not found.")
    next_wsp_number = lore_result.get("next_wsp_number", "Unknown")
    readme_coherence = lore_result.get("readme_coherence", "Unknown")

    system_state = {
        "core_principles": core_principles,
        "janitor_status": janitor_status,
        "semantic_status": semantic_status,
        "next_wsp_number": next_wsp_number,
        "readme_coherence": readme_coherence
    }
    
    wre_log("System health check complete.", "DEBUG")
    return system_state 