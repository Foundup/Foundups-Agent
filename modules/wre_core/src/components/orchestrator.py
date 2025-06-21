import sys
import json
from pathlib import Path
from typing import Dict

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.infrastructure.agents.janitor_agent.src.janitor_agent import JanitorAgent
from modules.infrastructure.agents.loremaster_agent.src.loremaster_agent import LoremasterAgent
from modules.infrastructure.agents.chronicler_agent.src.chronicler_agent import ChroniclerAgent

def get_version() -> str:
    """Get the current version from version.json"""
    version_file = project_root / "version.json"
    try:
        with open(version_file) as f:
            return json.load(f)["version"]
    except (FileNotFoundError, KeyError):
        wre_log("Version file not found or invalid. Using development version.", "WARNING")
        return "dev"

def check_agent_health() -> Dict[str, bool]:
    """Check if all required agents are available and responsive"""
    required_agents = [
        "JanitorAgent",
        "LoremasterAgent",
        "ChroniclerAgent",
        "ComplianceAgent",
        "DocumentationAgent"
    ]
    agent_status = {}
    for agent in required_agents:
        try:
            # Try to import the agent
            module = __import__(f"modules.infrastructure.agents.{agent.lower()}.src.{agent.lower()}", fromlist=[agent])
            agent_class = getattr(module, agent)
            agent_status[agent] = True
        except (ImportError, AttributeError):
            agent_status[agent] = False
            wre_log(f"Agent {agent} not available", "WARNING")
    return agent_status

def run_system_health_check(root_path: Path) -> Dict:
    """
    Initializes and runs the suite of internal agents to assess system state.
    
    Args:
        root_path (Path): The absolute path to the project root.
        
    Returns:
        dict: A dictionary containing the collected system state.
    """
    wre_log("Dispatching internal agents for system health check...", "INFO")
    
    # Get current version
    version = get_version()
    
    # Check agent availability
    agent_status = check_agent_health()
    
    # Initialize available agents
    janitor = JanitorAgent()
    loremaster = LoremasterAgent()
    chronicler = ChroniclerAgent(modlog_path_str=str(root_path / "ModLog.md"))

    # Run Janitor Agent and log the event
    janitor_result = janitor.clean_workspace()
    janitor_status = f"Clean ({janitor_result['files_deleted']} files deleted)"
    
    # Log the health check event
    chronicler.log_event({
        "title": "WRE System Health Check",
        "version": version,
        "description": "System-wide health assessment completed.",
        "achievements": [
            f"Scanned workspace and deleted {janitor_result['files_deleted']} temporary files.",
            f"Agent availability check: {sum(agent_status.values())}/{len(agent_status)} agents ready."
        ]
    })
    
    # Run Loremaster audit
    lore_result = loremaster.run_audit(root_path)
    semantic_status = f"COHERENT ({lore_result.get('docs_found', 0)} docs audited)"
    core_principles = lore_result.get("core_principles", "  - ERROR: Core principles not found.")
    next_wsp_number = lore_result.get("next_wsp_number", "Unknown")
    readme_coherence = lore_result.get("readme_coherence", "Unknown")

    # Compile comprehensive system state
    system_state = {
        "version": version,
        "agent_status": agent_status,
        "core_principles": core_principles,
        "janitor_status": janitor_status,
        "semantic_status": semantic_status,
        "next_wsp_number": next_wsp_number,
        "readme_coherence": readme_coherence,
        "health_check_time": chronicler.get_last_event_time()
    }
    
    wre_log("System health check complete.", "DEBUG")
    return system_state 