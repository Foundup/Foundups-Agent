#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io


import sys
import textwrap

# --- Configuration ---
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

FACTORS = {
    "CX": {"name": "Complexity", "weight": -3, "desc": "(1-5): 1=easy, 5=complex. Estimate effort."},
    "IM": {"name": "Importance", "weight": 4, "desc": "(1-5): 1=low, 5=critical. Essential to core purpose."},
    "IP": {"name": "Impact", "weight": 5, "desc": "(1-5): 1=minimal, 5=high. Overall positive effect."},
    "ADV": {"name": "AI Data Value", "weight": 4, "desc": "(1-5): 1=none, 5=high. Usefulness for AI training."},
    "ADF": {"name": "AI Dev Feasibility", "weight": 3, "desc": "(1-5): 1=infeasible, 5=easy. AI assistance potential."},
    "DF": {"name": "Dependency Factor", "weight": 5, "desc": "(1-5): 1=none, 5=bottleneck. Others need this."},
    "RF": {"name": "Risk Factor", "weight": 3, "desc": "(1-5): 1=low, 5=high. Risk if delayed/skipped."}
}

PROTOCOL_SUMMARY = """
Your AI-Centric Development Protocol:

1. Module Prioritization Score (MPS):
   - Formula: MPS = (IM*4) + (IP*5) + (ADV*4) + (ADF*3) + (DF*5) + (RF*3) - (CX*3)
   - Factors (1-5): CX, IM, IP, ADV, ADF, DF, RF
   - Rule: Always calculate MPS BEFORE coding. Prioritize highest score.

2. 3-Phase Dev-Test Protocol:
   - Phase 1: Build (Scoped logic, 'Windsurfer format': separation, logging, error handling, no bleed)
   - Phase 2: Test Locally (Mock data, /tests/ or __main__, terminal output)
   - Phase 3: Validate in Agent (Integrate, trigger via flag/input, watch runtime)
   - Rule: Never skip phases. Never combine steps.

3. Lifecycle Progression:
   - PoC -> Prototype -> MVP
   - Rule: Each module progresses sequentially.

Interaction Rule: Always wait for user confirmation between major actions/phases.
"""

# --- Functions ---

def print_protocol_summary():
    print("=" * 70)
    print("Starting Guided Development Session")
    print(textwrap.dedent(PROTOCOL_SUMMARY))
    print("=" * 70)

def calculate_mps(scores):
    """Calculates the Module Prioritization Score (MPS)."""
    mps = 0
    try:
        mps += scores['IM'] * FACTORS['IM']['weight']
        mps += scores['IP'] * FACTORS['IP']['weight']
        mps += scores['ADV'] * FACTORS['ADV']['weight']
        mps += scores['ADF'] * FACTORS['ADF']['weight']
        mps += scores['DF'] * FACTORS['DF']['weight']
        mps += scores['RF'] * FACTORS['RF']['weight']
        mps += scores['CX'] * FACTORS['CX']['weight'] # CX weight is negative
        return mps
    except KeyError as e:
        print(f"Error: Missing score for factor {e}", file=sys.stderr)
        return -float('inf')
    except TypeError as e:
        print(f"Error: Non-numeric score encountered - {e}", file=sys.stderr)
        return -float('inf')

def get_score(factor_key):
    """Prompts user for a score (1-5) and validates it."""
    while True:
        try:
            prompt_text = f"  - Enter {FACTORS[factor_key]['name']} {FACTORS[factor_key]['desc']}: "
            score = input(prompt_text).strip()
            if not score:
                 print("   Input cannot be empty. Please enter a number between 1 and 5.", file=sys.stderr)
                 continue
            value = int(score)
            if 1 <= value <= 5:
                return value
            else:
                print("   Score must be between 1 and 5.", file=sys.stderr)
        except ValueError:
            print("   Invalid input. Please enter a number.", file=sys.stderr)
        except EOFError:
             print("\nInput interrupted. Exiting.", file=sys.stderr)
             sys.exit(1)

def get_confirmation(prompt="Press Enter to continue, or type 'n' to stop: "):
    """Waits for user confirmation."""
    response = input(prompt).strip().lower()
    if response == 'n':
        print("Stopping as requested.")
        sys.exit(0)
    return True # Continue if anything other than 'n' is entered

def get_yes_no(prompt):
    """Gets a simple yes/no answer."""
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Please enter 'y' or 'n'.")

# --- Main Execution ---
if __name__ == "__main__":
    print_protocol_summary()

    # --- Step 1: MPS Prioritization ---
    print("\n--- STEP 1: Module Prioritization (MPS) ---")
    print("Enter details for modules you are considering coding next.")
    modules = []
    while True:
        try:
            module_name = input("\nEnter Module Name (or leave blank to finish scoring): ").strip()
            if not module_name:
                if not modules:
                    print("No modules entered. Exiting.")
                    sys.exit(0)
                break # Finished entering modules

            print(f"Scoring for module: '{module_name}'")
            scores = {}
            for key in FACTORS:
                scores[key] = get_score(key)

            modules.append({
                "name": module_name,
                "scores": scores
            })
        except EOFError:
             print("\nInput interrupted. Exiting.", file=sys.stderr)
             sys.exit(1)


    # Calculate MPS and Sort
    for module in modules:
        module['mps'] = calculate_mps(module['scores'])
    modules.sort(key=lambda x: x['mps'], reverse=True)

    print("\n--- MPS Prioritization Results ---")
    if not modules:
         # This case should be caught above, but added for safety
        print("No modules were successfully scored. Exiting.")
        sys.exit(1)

    top_module = modules[0]
    print(f"\n==> Highest Priority Module: '{top_module['name']}' (MPS: {top_module['mps']:.2f}) <==")
    print("\nFull Prioritized List:")
    for i, module in enumerate(modules):
         print(f"  {i+1}. {module['name']} (MPS: {module['mps']:.2f})")

    print("\n--------------------------------------------------")
    print("Instruction for your AI assistant (e.g., Cursor):")
    print(f"\"Based on our Module Prioritization Score (MPS), the highest priority module is '{top_module['name']}' (Score: {top_module['mps']:.2f}). We will start working on this module now.\"")
    print("--------------------------------------------------")

    get_confirmation(f"Confirm you want to start working on '{top_module['name']}'? (Press Enter to confirm): ")
    current_module_name = top_module['name']
    current_lifecycle_stage = "PoC" # Start assumption

    # --- Step 2: Guide through 3-Phase Protocol ---
    while True: # Loop allows potentially moving to next phase or module
        print(f"\n--- Working on Module: '{current_module_name}' ---")
        print(f"--- Current Lifecycle Goal: {current_lifecycle_stage} ---")

        # Phase 1: Build
        print("\n--- PROTOCOL STEP: Phase 1 - Build ---")
        print("Focus: Implement scoped logic following 'Windsurfer format'.")
        print("Reminder: Ensure separation, logging, error handling, no bleed.")
        print("\n--------------------------------------------------")
        print("Instruction for AI:")
        print(f"\"Let's start Phase 1 (Build) for the '{current_lifecycle_stage}' version of module '{current_module_name}'. Follow the Windsurfer format guidelines.\"")
        print("--------------------------------------------------")
        get_confirmation(f"Confirm starting Phase 1 (Build) for '{current_module_name}'? (Press Enter): ")
        # (User and AI perform build actions here)
        if not get_yes_no(f"\nIs Phase 1 (Build) for '{current_module_name}' ({current_lifecycle_stage}) complete?"):
             print("Okay, continue working on Phase 1. Re-run script when ready for Phase 2.")
             sys.exit(0)

        # Phase 2: Test Locally
        print("\n--- PROTOCOL STEP: Phase 2 - Test Locally ---")
        print("Focus: Create tests (in /tests/ or __main__) using mock data.")
        print("Reminder: No live API calls, memory writes, or token usage. Output success/fail to terminal.")
        print("\n--------------------------------------------------")
        print("Instruction for AI:")
        print(f"\"Phase 1 complete. Let's proceed to Phase 2 (Local Testing) for module '{current_module_name}'. Create tests using mock inputs and log results clearly.\"")
        print("--------------------------------------------------")
        get_confirmation(f"Confirm starting Phase 2 (Local Test) for '{current_module_name}'? (Press Enter): ")
        # (User and AI perform local testing actions here)
        if not get_yes_no(f"\nIs Phase 2 (Local Testing) for '{current_module_name}' ({current_lifecycle_stage}) successful?"):
             print("Okay, address testing issues. Re-run script or focus on fixing tests before Phase 3.")
             sys.exit(0)

        # Phase 3: Validate in Agent
        print("\n--- PROTOCOL STEP: Phase 3 - Validate in Agent ---")
        print("Focus: Integrate module into main system/agent runtime.")
        print("Reminder: Trigger via controlled input (.env flag, command, etc.). Monitor runtime logs.")
        print("\n--------------------------------------------------")
        print("Instruction for AI:")
        print(f"\"Phase 2 successful. Let's proceed to Phase 3 (Validate in Agent) for module '{current_module_name}'. Integrate it and prepare a controlled way to trigger it.\"")
        print("--------------------------------------------------")
        get_confirmation(f"Confirm starting Phase 3 (Validation) for '{current_module_name}'? (Press Enter): ")
        # (User and AI perform integration and validation actions here)
        if not get_yes_no(f"\nIs Phase 3 (Validation) for '{current_module_name}' ({current_lifecycle_stage}) successful?"):
             print("Okay, address integration/validation issues. Re-run script or focus on fixing the integration.")
             sys.exit(0)

        # --- Step 3: Lifecycle Progression ---
        print("\n--- PROTOCOL STEP: Lifecycle Progression ---")
        print(f"Module '{current_module_name}' has successfully completed the 3 phases for the '{current_lifecycle_stage}' stage.")

        if current_lifecycle_stage == "PoC":
            next_stage = "Prototype"
            current_lifecycle_stage = next_stage # Update for potential next loop
            if get_yes_no(f"Do you want to proceed to the '{next_stage}' stage for '{current_module_name}' now?"):
                 print(f"Okay, restarting the 3-phase protocol for the '{next_stage}' stage.")
                 continue # Restart the loop for the next stage
            else:
                 print(f"Okay, '{current_module_name}' remains at '{current_lifecycle_stage}'. Consider running the MPS step again for the next module.")
                 break # Exit the loop
        elif current_lifecycle_stage == "Prototype":
            next_stage = "MVP"
            current_lifecycle_stage = next_stage
            if get_yes_no(f"Do you want to proceed to the '{next_stage}' stage for '{current_module_name}' now?"):
                 print(f"Okay, restarting the 3-phase protocol for the '{next_stage}' stage.")
                 continue # Restart the loop for the next stage
            else:
                 print(f"Okay, '{current_module_name}' remains at '{current_lifecycle_stage}'. Consider running the MPS step again for the next module.")
                 break # Exit the loop
        elif current_lifecycle_stage == "MVP":
            print(f"Module '{current_module_name}' has reached MVP! Congratulations.")
            print("Consider running the MPS step again for the next module.")
            break # Exit the loop
        else:
            print(f"Unknown lifecycle stage '{current_lifecycle_stage}'. Stopping.")
            break # Exit the loop

    print("\nGuided Development Session Ended.") 