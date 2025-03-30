#!/usr/bin/env python3

import sys

# --- Configuration ---
FACTORS = {
    "CX": {"name": "Complexity", "weight": -3, "desc": "(1-5): 1=easy, 5=complex. Estimate effort."},
    "IM": {"name": "Importance", "weight": 4, "desc": "(1-5): 1=low, 5=critical. Essential to core purpose."},
    "IP": {"name": "Impact", "weight": 5, "desc": "(1-5): 1=minimal, 5=high. Overall positive effect."},
    "ADV": {"name": "AI Data Value", "weight": 4, "desc": "(1-5): 1=none, 5=high. Usefulness for AI training."},
    "ADF": {"name": "AI Dev Feasibility", "weight": 3, "desc": "(1-5): 1=infeasible, 5=easy. AI assistance potential."},
    "DF": {"name": "Dependency Factor", "weight": 5, "desc": "(1-5): 1=none, 5=bottleneck. Others need this."},
    "RF": {"name": "Risk Factor", "weight": 3, "desc": "(1-5): 1=low, 5=high. Risk if delayed/skipped."}
}

# --- Functions ---

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
        return -float('inf') # Return a very low score on error
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


# --- Main Execution ---
if __name__ == "__main__":
    modules = []
    print("Enter module details. Press Enter with no name to finish.")

    while True:
        try:
            module_name = input("\nEnter Module Name (or leave blank to finish): ").strip()
            if not module_name:
                break

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


    if not modules:
        print("\nNo modules entered. Nothing to prioritize.")
        sys.exit(0)

    # Calculate MPS for each module
    for module in modules:
        module['mps'] = calculate_mps(module['scores'])

    # Sort modules by MPS (highest first)
    # Simple sort - doesn't implement complex tie-breaking using individual factors yet
    modules.sort(key=lambda x: x['mps'], reverse=True)

    print("\n--- Module Prioritization Results ---")
    if modules:
        top_module = modules[0]
        print(f"\n==> Highest Priority Module: '{top_module['name']}' (MPS: {top_module['mps']:.2f}) <==") # Using .2f in case weights change later

        print("\nFull Prioritized List:")
        for i, module in enumerate(modules):
             # Detailed breakdown (optional, uncomment if needed)
             # score_details = ", ".join([f"{k}:{v}" for k,v in module['scores'].items()])
             # print(f"  {i+1}. {module['name']} (MPS: {module['mps']:.2f}) [{score_details}]")
             print(f"  {i+1}. {module['name']} (MPS: {module['mps']:.2f})")

        # Prepare output for the AI
        print("\n--------------------------------------------------")
        print("You can tell your AI assistant (like Cursor):")
        print(f"\"Based on our Module Prioritization Score (MPS), the next module to focus on is '{top_module['name']}' with a score of {top_module['mps']:.2f}.\"")
        print("--------------------------------------------------")

    else:
        # This case should technically be caught earlier, but good for safety
        print("No modules were successfully scored.") 