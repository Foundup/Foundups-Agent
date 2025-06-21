import sys
from pathlib import Path
import shutil

# Add project root to resolve imports
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.wre_core.src.main import sanitize_for_console

def present_harmonic_query(system_state: dict, roadmap_objectives: list):
    """
    Displays the main interactive menu to the user.
    
    Args:
        system_state (dict): Current system health and status information
        roadmap_objectives (list): List of (objective, path) tuples from ROADMAP.md
        
    Returns:
        tuple: (user_choice, menu_offset) where menu_offset is the number of roadmap objectives
    """
    wre_log("Consulting strategic roadmap...", "DEBUG")
    wre_log(f"Found {len(roadmap_objectives)} active theaters.", "DEBUG")

    # Get terminal width for better formatting
    width = shutil.get_terminal_size().columns
    
    # --- Display Header ---
    header = " WRE Autonomous System Humming. 0102 is coherent. "
    print(sanitize_for_console("\n" + "=" * width))
    print(sanitize_for_console(f"{header.center(width)}"))
    print(sanitize_for_console("=" * width + "\n"))

    # --- Display Comprehension State ---
    print(sanitize_for_console("**Core Principles (Comprehension Phase Result):**"))
    print(sanitize_for_console("-" * 45))
    print(sanitize_for_console(system_state.get('core_principles', '  - Comprehension failed.')))
    print(sanitize_for_console("-" * 45 + "\n"))

    # --- Display System Status ---
    print(sanitize_for_console("**System Health & Status:**"))
    print(sanitize_for_console(f"  - Janitor Status:          {system_state['janitor_status']}"))
    print(sanitize_for_console(f"  - Semantic Coherence:      {system_state['semantic_status']}"))
    print(sanitize_for_console(f"  - Documentation Coherence: {system_state['readme_coherence']}"))
    print(sanitize_for_console(f"  - Next WSP Number:         {system_state['next_wsp_number']}\n"))

    # --- Display Menu ---
    print(sanitize_for_console("**Harmonic Query - Please select a directive:**"))
    
    menu_offset = 0
    if roadmap_objectives:
        print(sanitize_for_console("\n  *Strategic Objectives (from ROADMAP.md):*"))
        for i, (objective, path) in enumerate(roadmap_objectives, 1):
            print(sanitize_for_console(f"    {i}. {objective} (`{path}`)"))
        menu_offset = len(roadmap_objectives)
    
    print(sanitize_for_console("\n  *System Directives:*"))
    print(sanitize_for_console(f"    {menu_offset + 1}. Add new objective to ROADMAP.md"))
    print(sanitize_for_console(f"    {menu_offset + 2}. Enter continuous monitoring state"))
    print(sanitize_for_console(f"    {menu_offset + 3}. Terminate session."))
    
    choice = input("\nEnter your choice: ")
    return choice, menu_offset

def display_menu():
    """Displays the main operational menu for the WRE."""
    header = " WRE Autonomous System Humming. 0102 is coherent. "
    
    # Get terminal width
    width = shutil.get_terminal_size().columns

    # --- Display Header ---
    print(sanitize_for_console("\n" + "=" * 60))
    print(sanitize_for_console(f"{header.center(60)}"))
    print(sanitize_for_console("=" * 60 + "\n"))

    # --- Display Comprehension State ---
    print(sanitize_for_console("**Core Principles (Comprehension Phase Result):**"))
    print(sanitize_for_console("-" * 45))
    print(sanitize_for_console(system_state.get('core_principles', '  - Comprehension failed.')))
    print(sanitize_for_console("-" * 45 + "\n"))


    # --- Display System Status ---
    print(sanitize_for_console("**System Health & Status:**"))
    print(sanitize_for_console(f"  - Janitor Status:          {system_state['janitor_status']}"))
    print(sanitize_for_console(f"  - Semantic Coherence:      {system_state['semantic_status']}"))
    print(sanitize_for_console(f"  - Documentation Coherence: {system_state['readme_coherence']}"))
    print(sanitize_for_console(f"  - Next WSP Number:         {system_state['next_wsp_number']}\n"))


    # --- Display Menu ---
    print(sanitize_for_console("**Harmonic Query - Please select a directive:**"))
    
    menu_offset = 0
    if roadmap_objectives:
        print(sanitize_for_console("\n  *Strategic Objectives (from ROADMAP.md):*"))
        for i, (objective, path) in enumerate(roadmap_objectives):
            print(sanitize_for_console(f"    {i+1}. {objective} (`{path}`)"))
        menu_offset = len(roadmap_objectives)
    
    print(sanitize_for_console("\n  *System Directives:*"))
    print(sanitize_for_console(f"    {menu_offset + 1}. Add new objective to ROADMAP.md"))
    print(sanitize_for_console(f"    {menu_offset + 2}. Enter continuous monitoring state (placeholder)"))
    print(sanitize_for_console(f"    {menu_offset + 3}. Terminate session."))
    
    choice = input("\nEnter your choice: ")
    return choice, menu_offset 