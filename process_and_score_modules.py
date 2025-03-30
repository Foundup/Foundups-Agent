#!/usr/bin/env python3

import sys
import os
import yaml
import csv
from datetime import datetime
import textwrap
from typing import List, Dict, Any, Optional, Tuple

# --- Configuration ---
INPUT_FILENAME: str = "modules_to_score.yaml"
MODULES_DIR: str = "modules"
REPORTS_DIR: str = "reports"
SCORECARD_BASENAME: str = "scorecard"

# Ensure required directories exist
try:
    os.makedirs(MODULES_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)
except OSError as e:
    print(f"Error creating base directories ({MODULES_DIR}, {REPORTS_DIR}): {e}", file=sys.stderr)
    sys.exit(1)

# --- Factor Definitions (Constant) ---
FACTORS: Dict[str, Dict[str, Any]] = {
    "CX": {"name": "Complexity", "weight": -3, "desc": "(1-5): 1=easy, 5=complex. Estimate effort."},
    "IM": {"name": "Importance", "weight": 4, "desc": "(1-5): 1=low, 5=critical. Essential to core purpose."},
    "IP": {"name": "Impact", "weight": 5, "desc": "(1-5): 1=minimal, 5=high. Overall positive effect."},
    "ADV": {"name": "AI Data Value", "weight": 4, "desc": "(1-5): 1=none, 5=high. Usefulness for AI training."},
    "ADF": {"name": "AI Dev Feasibility", "weight": 3, "desc": "(1-5): 1=infeasible, 5=easy. AI assistance potential."},
    "DF": {"name": "Dependency Factor", "weight": 5, "desc": "(1-5): 1=none, 5=bottleneck. Others need this."},
    "RF": {"name": "Risk Factor", "weight": 3, "desc": "(1-5): 1=low, 5=high. Risk if delayed/skipped."}
}

PROTOCOL_REMINDER: str = """
REMINDER: AI-Centric Development Protocol

1. MPS First: Use the generated Scorecard ({reports_dir}/{scorecard_basename}_*.md) to determine module order.
2. 3-Phase Dev-Test: Build -> Test Locally -> Validate in Agent (per module)
3. Lifecycle: PoC -> Prototype -> MVP (per module)
4. Interaction: YOU direct the AI based on the Scorecard. Confirm steps.
"""

# --- Functions ---

def print_protocol_reminder(reports_dir: str, scorecard_basename: str) -> None:
    """Prints the protocol reminder to the console."""
    print("=" * 70)
    print("Processing Modules and Generating Scorecard")
    print(textwrap.dedent(PROTOCOL_REMINDER.format(
        reports_dir=reports_dir, scorecard_basename=scorecard_basename
    )))
    print("=" * 70)

def setup_module_directory(module_name: str) -> Optional[str]:
    """
    Creates a standard directory structure for a new module.
    Returns the module path if successful, None otherwise.
    """
    module_path = os.path.join(MODULES_DIR, module_name)
    subdirs = ["src", "tests", "docs"]
    init_files_paths = [
        os.path.join(module_path, "__init__.py"),
        os.path.join(module_path, "src", "__init__.py"),
        os.path.join(module_path, "tests", "__init__.py"),
    ]

    try:
        os.makedirs(module_path, exist_ok=True)
        for subdir in subdirs:
            os.makedirs(os.path.join(module_path, subdir), exist_ok=True)

        for init_file in init_files_paths:
            # Create empty __init__.py if it doesn't exist
            if not os.path.exists(init_file):
                with open(init_file, 'a', encoding='utf-8') as f:
                    pass  # Create empty file

        print(f"  - Directory structure created/verified for: {module_name}")
        return module_path
    except OSError as e:
        print(f"  - Error creating directory structure for {module_name}: {e}", file=sys.stderr)
        return None

def generate_module_readme(module_name: str, scores: Dict[str, int], mps: float) -> str:
    """Generates a standard README.md content string for the module."""
    readme_template = f"""
# Module: {module_name}

## Overview
*(Briefly describe the purpose and responsibility of this module here.)*

---

## Status & Prioritization
- **Current Lifecycle Stage:** PoC (Proof of Concept)
- **Module Prioritization Score (MPS):** {mps:.2f} *(Higher score means higher priority)*

### Scoring Factors (1-5 Scale)
| Factor | Score | Description                     | Weight | Contribution |
|--------|-------|---------------------------------|--------|--------------|
"""
    lines = [readme_template.strip()]  # Start with the template content

    # Add factor details dynamically
    for key, factor_info in FACTORS.items():
        score = scores.get(key, 0)  # Default to 0 if somehow missing post-validation
        weight = factor_info['weight']
        contribution = score * weight
        lines.append(f"| {factor_info['name']:<20} | {score:<5} | {factor_info['desc']:<30} | {weight:<6} | {contribution:>12.2f} |")

    # Add Development Protocol Checklist section
    checklist_section = """
---

## Development Protocol Checklist (PoC Stage)

**Phase 1: Build**
- [ ] Define core function/class structure in `src/`.
- [ ] Implement minimal viable logic for core responsibility.
- [ ] Add basic logging (e.g., `import logging`).
- [ ] Implement basic error handling (e.g., `try...except`).
- [ ] Ensure separation of concerns (follows 'Windsurfer format').

**Phase 2: Test Locally**
- [ ] Create test file in `tests/` (e.g., `test_{module_name}.py`).
- [ ] Write simple unit test(s) using mock inputs/data.
- [ ] Verify test passes and outputs clear success/fail to terminal.
- [ ] Ensure tests *do not* require live APIs, external resources, or state changes.

**Phase 3: Validate in Agent (if applicable for PoC)**
- [ ] Determine simple integration point in main application/agent.
- [ ] Add basic call/trigger mechanism (e.g., simple function call).
- [ ] Observe basic runtime behavior and logs for critical errors.

---

## Dependencies
*(List any major internal or external dependencies here)*

## Usage
*(Provide basic instructions on how to use or interact with this module)*

"""
    lines.append(checklist_section)
    return "\n".join(lines)

def calculate_mps(scores: Dict[str, int]) -> float:
    """Calculates the Module Prioritization Score (MPS)."""
    mps = 0.0
    try:
        for key, factor_info in FACTORS.items():
            # Ensure score exists (should be guaranteed by validation)
            score = scores[key]
            mps += score * factor_info['weight']
        return mps
    except KeyError as e:
        print(f"Internal Error: Missing score for factor {e} during calculation.", file=sys.stderr)
        return -float('inf')  # Return a very low score on error
    except TypeError as e:
        print(f"Internal Error: Non-numeric score encountered during calculation - {e}", file=sys.stderr)
        return -float('inf')

def validate_module_data(module_data: Any) -> Optional[List[Dict[str, Any]]]:
    """Validates the structure and scores of loaded module data from YAML."""
    print("DEBUG: Starting validation")
    print(f"DEBUG: Input data type: {type(module_data)}")
    print(f"DEBUG: Input data: {module_data}")

    if not isinstance(module_data, list):
        print(f"Error: Expected a list of modules under the 'modules' key in {INPUT_FILENAME}", file=sys.stderr)
        return None

    validated_modules = []
    is_valid = True
    seen_names = set()

    for i, module in enumerate(module_data):
        print(f"DEBUG: Validating module {i}")
        print(f"DEBUG: Module data: {module}")

        if not isinstance(module, dict):
            print(f"Error: Item at index {i} is not a dictionary (module definition).", file=sys.stderr)
            is_valid = False
            continue

        module_name = module.get("name")
        scores = module.get("scores")

        print(f"DEBUG: Module name: {module_name}")
        print(f"DEBUG: Module scores: {scores}")

        # Validate Name
        if not module_name or not isinstance(module_name, str):
            print(f"Error: Module at index {i} is missing a valid string 'name'.", file=sys.stderr)
            is_valid = False
            continue
        elif module_name.lower() in seen_names:
            print(f"Error: Duplicate module name found: '{module_name}'. Names must be unique.", file=sys.stderr)
            is_valid = False
            continue
        else:
            seen_names.add(module_name.lower())

        # Validate Scores structure
        if not scores or not isinstance(scores, dict):
            print(f"Error: Module '{module_name or f'(index {i})'}' is missing a valid 'scores' dictionary.", file=sys.stderr)
            is_valid = False
            continue

        # Validate individual scores
        module_scores = {}
        has_invalid_scores = False
        for key in FACTORS:
            if key not in scores:
                print(f"Error: Module '{module_name}' is missing score for: {key}", file=sys.stderr)
                has_invalid_scores = True
            else:
                score_val = scores[key]
                if not isinstance(score_val, int) or not (1 <= score_val <= 5):
                    print(f"Error: Module '{module_name}' has invalid score for {key}: '{score_val}' (must be int 1-5)", file=sys.stderr)
                    has_invalid_scores = True
                else:
                    module_scores[key] = score_val

        if has_invalid_scores:
            is_valid = False
            continue

        # If we get here, this module is valid
        validated_modules.append({"name": module_name, "scores": module_scores})

    print(f"DEBUG: Validation complete. Found {len(validated_modules)} valid modules. Overall valid: {is_valid}")
    return validated_modules if is_valid else None

def generate_markdown_scorecard(modules: List[Dict[str, Any]]) -> str:
    """Generates the scorecard content in Markdown table format with aligned columns."""
    lines = []
    lines.append("# Module Prioritization Scorecard")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Determine max width needed for module names for better alignment
    max_name_width = max(len(m['name']) for m in modules) if modules else 20
    # Ensure minimum width
    name_width = max(20, max_name_width)
    rank_width = 4
    score_width = 10  # For 'XXX.YY' MPS score

    # Create header
    header = f"| {'Rank':<{rank_width}} | {'Module Name':<{name_width}} | {'MPS Score':>{score_width}} |"
    separator = f"|{'-'*(rank_width+2)}|{'-'*(name_width+2)}|{'-'*(score_width+2)}|"
    lines.append(header)
    lines.append(separator)

    # Format each row
    for i, module in enumerate(modules):
        rank = str(i + 1)
        name = module['name']
        score = f"{module['mps']:.2f}"
        lines.append(f"| {rank:<{rank_width}} | {name:<{name_width}} | {score:>{score_width}} |")

    lines.append("\n*(Higher MPS means higher priority)*")
    return "\n".join(lines)

def save_to_file(filepath: str, content: str) -> bool:
    """Saves content to a file, creating parent directories if needed."""
    try:
        # Ensure parent directory exists
        parent_dir = os.path.dirname(filepath)
        if parent_dir:  # Avoid trying to create '.' if filepath is just a filename
            os.makedirs(parent_dir, exist_ok=True)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except IOError as e:
        print(f"Error saving file {filepath}: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"An unexpected error occurred while saving {filepath}: {e}", file=sys.stderr)
        return False

# --- Main Execution ---
if __name__ == "__main__":
    print_protocol_reminder(REPORTS_DIR, SCORECARD_BASENAME)

    # --- Step 1: Load and Validate Input ---
    print(f"\n--- STEP 1: Loading and Validating {INPUT_FILENAME} ---")
    if not os.path.exists(INPUT_FILENAME):
        print(f"Error: Input file '{INPUT_FILENAME}' not found.", file=sys.stderr)
        print("Please create it with module names and scores (YAML format).", file=sys.stderr)
        sys.exit(1)

    try:
        print("DEBUG: Opening YAML file")
        with open(INPUT_FILENAME, 'r', encoding='utf-8') as f:
            print("DEBUG: Reading YAML file")
            raw_data = yaml.safe_load(f)
            print(f"DEBUG: Raw data loaded: {raw_data}")
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file {INPUT_FILENAME}: {e}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file {INPUT_FILENAME}: {e}", file=sys.stderr)
        sys.exit(1)

    if not raw_data or "modules" not in raw_data:
        print(f"Error: Input file '{INPUT_FILENAME}' is empty or missing the top-level 'modules' key.", file=sys.stderr)
        sys.exit(1)

    print("DEBUG: About to validate module data")
    modules_to_process = validate_module_data(raw_data["modules"])
    print(f"DEBUG: Validation result: {modules_to_process}")

    if modules_to_process is None:
        print("\nInput validation failed. Please check errors above and fix the YAML input file.", file=sys.stderr)
        sys.exit(1)

    if not modules_to_process:
        print("No valid modules found in the input file after validation.")
        sys.exit(0)

    print(f"Input validation successful. Found {len(modules_to_process)} valid modules.")

    # --- Step 2: Calculate MPS and Sort ---
    print("\n--- STEP 2: Calculating MPS and Sorting Modules ---")
    for module in modules_to_process:
        module['mps'] = calculate_mps(module['scores'])

    modules_to_process.sort(key=lambda x: x['mps'], reverse=True)
    print("MPS calculation and sorting complete.")

    # --- Step 3: Setup Module Directories and Generate Documentation ---
    print("\n--- STEP 3: Setting up Module Directories and READMEs ---")
    all_setup_successful = True
    for module in modules_to_process:
        print(f"Processing module: {module['name']}...")
        module_path = setup_module_directory(module['name'])
        if module_path:
            readme_content = generate_module_readme(module['name'], module['scores'], module['mps'])
            readme_path = os.path.join(module_path, "README.md")
            if save_to_file(readme_path, readme_content):
                print(f"  - README.md generated successfully.")
            else:
                print(f"  - Failed to generate README.md for {module['name']}.")
                all_setup_successful = False
        else:
            # Error message printed inside setup_module_directory
            all_setup_successful = False

    if not all_setup_successful:
        print("\nWarning: Some errors occurred during module directory/README setup. Please check logs.", file=sys.stderr)
        # Decide whether to exit or continue based on severity - continuing for now
        # sys.exit(1)

    # --- Step 4: Generate and Save Scorecards ---
    print("\n--- STEP 4: Generating and Saving Scorecards ---")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    md_filename = f"{SCORECARD_BASENAME}_{timestamp}.md"
    csv_filename = f"{SCORECARD_BASENAME}_{timestamp}.csv"
    md_filepath = os.path.join(REPORTS_DIR, md_filename)
    csv_filepath = os.path.join(REPORTS_DIR, csv_filename)

    # Generate and Save Markdown Scorecard
    md_content = generate_markdown_scorecard(modules_to_process)
    if save_to_file(md_filepath, md_content):
        print(f"Markdown Scorecard saved: {md_filepath}")
    else:
        print(f"Failed to save Markdown Scorecard.", file=sys.stderr)

    # Generate and Save CSV Scorecard
    try:
        # Directory creation handled by save_to_file now, but keep for clarity
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(csv_filepath, 'w', newline='', encoding='utf-8') as csvfile:
            # Define header including score factors
            fieldnames = ['Rank', 'ModuleName', 'MPS_Score'] + list(FACTORS.keys())
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for i, module in enumerate(modules_to_process):
                row_data = {
                    'Rank': i + 1,
                    'ModuleName': module['name'],
                    'MPS_Score': f"{module['mps']:.2f}",
                    **module['scores']  # Add individual factor scores
                }
                writer.writerow(row_data)
        print(f"CSV Scorecard saved:      {csv_filepath}")
    except IOError as e:
        print(f"Error saving CSV file {csv_filepath}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while saving {csv_filepath}: {e}", file=sys.stderr)

    # --- Step 5: Console Output Guidance ---
    print("\n--- STEP 5: Guidance for AI Assistant (Cursor) ---")
    if modules_to_process:
        top_module = modules_to_process[0]
        print("\n1. **Initial Instruction:**")
        print(f"   \"According to the latest Scorecard ({md_filename} in {REPORTS_DIR}), the highest priority module is '{top_module['name']}' (MPS: {top_module['mps']:.2f}). Let's start the PoC phase for this module, using the structure in '{MODULES_DIR}/{top_module['name']}'. Follow the 3-phase protocol.\"")
        print("\n2. **Ongoing Guidance:**")
        print(f"   \"**Refer to the Scorecard ({md_filepath}) saved in '{REPORTS_DIR}'.**")
        print(f"   When the current task/phase is done, consult the Scorecard and instruct Cursor to work on the next highest-ranked module that needs attention (check its README in '{MODULES_DIR}/[ModuleName]/README.md' for status).")
        print("   Stick to the Scorecard order for starting new module work.\"")
    else:
        print("No modules were processed to provide specific guidance.")
    print("--------------------------------------------------")

    print("\nScript finished. Check the following locations:")
    print(f"1. Module directories & READMEs: ./{MODULES_DIR}/")
    print(f"2. Scorecards (MD & CSV):        ./{REPORTS_DIR}/") 