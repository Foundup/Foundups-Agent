import re
from pathlib import Path
import sys

# This block ensures that the module can be run standalone or as part of the larger app
# It adds the project root to the python path to resolve imports like `modules.wre_core...`
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from modules.wre_core.src.utils.logging_utils import wre_log
from modules.infrastructure.agents.module_scaffolding_agent.src.module_scaffolding_agent import ModuleScaffoldingAgent


def parse_roadmap(root_path: Path):
    """Parses ROADMAP.md to extract strategic objectives."""
    roadmap_path = root_path / "ROADMAP.md"
    objectives = []
    wre_log("Consulting strategic roadmap...", "DEBUG")
    try:
        if roadmap_path.exists():
            content = roadmap_path.read_text(encoding='utf-8')
            theaters_match = re.search(r"## .* Theaters of Operation\s*\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
            if theaters_match:
                theaters_content = theaters_match.group(1)
                objectives = re.findall(r"-\s+\*\*(.*?):\*\*\s+`(.*?)`", theaters_content)
    except Exception as e:
        wre_log(f"Error parsing ROADMAP.md: {e}", "ERROR")
    wre_log(f"Found {len(objectives)} active theaters.", "DEBUG")
    return objectives

def add_new_objective(root_path: Path):
    """Interactively prompts the user to define a new strategic objective."""
    wre_log("\n--- Creating New Strategic Objective ---", level="INFO")
    try:
        name = input("Enter a name for the new Theater of Operation (e.g., 'GitHub Agent'): ")
        if not name:
            wre_log("❌ Name cannot be empty. Aborting.", level="ERROR")
            return

        sanitized_name = name.lower().replace(' ', '_')
        default_path = f"modules/platform_agents/{sanitized_name}"
        path = input(f"Enter the target module path for '{name}' [default: {default_path}]: ") or default_path

        if not path.startswith("modules/"):
            wre_log("❌ Invalid input. Path must start with 'modules/'. Aborting.", level="ERROR")
            return

        _update_roadmap_file(root_path, name, path)

        wre_log(f"--- Dispatching Module Scaffolding Agent for '{name}' ---", level="INFO")
        scaffolder = ModuleScaffoldingAgent()
        scaffolder.create_module(path)

    except Exception as e:
        wre_log(f"An error occurred while creating new objective: {e}", level="CRITICAL")

def _update_roadmap_file(root_path: Path, name: str, path: str):
    """Adds a new entry to the ROADMAP.md file."""
    roadmap_path = root_path / "ROADMAP.md"
    new_entry = f"-   **{name}:** `{path}`"
    lines = []
    if roadmap_path.exists():
        lines = roadmap_path.read_text(encoding='utf-8').splitlines()
    
    insert_index = -1
    in_theaters_section = False
    for i, line in enumerate(lines):
        if "Theaters of Operation" in line:
            in_theaters_section = True
        if in_theaters_section and line.strip() == '---':
            insert_index = i
            break
    
    if insert_index != -1:
        lines.insert(insert_index, new_entry)
    else:
        header_found = False
        for i, line in enumerate(lines):
            if "Theaters of Operation" in line:
                lines.insert(i + 1, new_entry)
                header_found = True
                break
        if not header_found:
            # Add a placeholder for the Theaters of Operation
            # This section will be populated with dynamic information about the
            # agent's current operational capabilities and active modules.
            lines.append("\n## 🎭 0102 Theaters of Operation\n")
            lines.append("*No active theaters of operation.*\n")
            lines.append(new_entry)
    
    roadmap_path.write_text("\n".join(lines), encoding='utf-8')
    wre_log(f"✅ Successfully added '{name}' to ROADMAP.md.", level="INFO") 