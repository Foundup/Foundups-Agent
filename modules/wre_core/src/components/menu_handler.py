import sys
from pathlib import Path

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log

def sanitize_for_console(text):
    """Removes or replaces characters that may cause rendering issues in a console."""
    return str(text).encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)

def present_harmonic_query(system_state, roadmap_objectives):
    """
    Generates and prints the main interactive menu.

    Args:
        system_state (dict): A dictionary containing health status information.
        roadmap_objectives (list): A list of tuples for the roadmap objectives.
    """
    query = "\n" + "="*50
    query += "\n WRE Autonomous System Humming. O1O2 is coherent."
    query += "\n" + "="*50
    query += "\n\n**Foundational Context (from WSP 1):**\n"
    query += system_state.get('core_principles', '  - Not available.')
    query += "\n\n" + "-"*50
    query += "\n\n**System State Assessment:**\n"
    query += f"  - Workspace Hygiene: {system_state.get('janitor_status', 'Unknown')}\n"
    query += f"  - Semantic Coherence: {system_state.get('semantic_status', 'Unknown')}\n"
    query += f"  - Next Suggested WSP #: {system_state.get('next_wsp_number', 'Unknown')}\n"
    query += "\n" + "-"*50
    
    query += "\n\n**Directive Menu:**\n"
    if roadmap_objectives:
        query += "  --- Strategic Objectives ---\n"
        for i, (name, path) in enumerate(roadmap_objectives, 1):
            query += f"  {i}. Work on Module: {name} ({path})\n"
    
    menu_offset = len(roadmap_objectives)
    query += "  --- System Actions ---\n"
    query += f"  {menu_offset + 1}. Initiate a new Strategic Objective\n"
    query += f"  {menu_offset + 2}. Enter Continuous Monitoring State\n"
    query += f"  {menu_offset + 3}. Terminate Session\n"

    print(sanitize_for_console(query))

    max_choice = menu_offset + 3
    choice = input(f"\nEnter your choice (1-{max_choice}): ")
    
    return choice, menu_offset 