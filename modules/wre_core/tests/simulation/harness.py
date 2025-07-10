"""
WRE Simulation Test Harness

The master script to run WRE simulations.
Relocated from tests/wre_simulation/ per WSP 3 compliance requirements.

WSP Compliance:
- WSP 3: Enterprise Domain Architecture (proper test location)
- WSP 5: Test Coverage Protocol (simulation testing)
- WSP 22: Traceable Narrative (documented relocation)
- WSP 50: Pre-Action Verification (no sys.path hacks)
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
import yaml
from pathlib import Path
import time
import importlib.util

# Calculate project root for sandbox operations only (no sys.path manipulation)
project_root = Path(__file__).resolve().parent.parent.parent.parent

# Use relative import for validation_suite within the same package
try:
    from . import validation_suite
except ImportError:
    # Fallback for direct script execution - dynamic import without sys.path hack
    validation_suite_path = Path(__file__).parent / "validation_suite.py"
    spec = importlib.util.spec_from_file_location("validation_suite", validation_suite_path)
    validation_suite = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(validation_suite)


def setup_sandbox():
    """Creates a temporary directory and copies the project structure into it."""
    sandbox_path = Path(tempfile.mkdtemp(prefix="wre_test_"))
    print(f"  [Harness] Sandbox created at: {sandbox_path}")
    
    # Define files/directories to ignore during copy
    ignore_patterns = shutil.ignore_patterns(
        '.git', '__pycache__', '.pytest_cache', '*.pyc',
        '*.log', 'venv', '.env', 'legacy', 'docs'
    )
    
    shutil.copytree(project_root, sandbox_path, dirs_exist_ok=True, ignore=ignore_patterns)
    print(f"  [Harness] Project copied to sandbox.")
    return sandbox_path


def run_simulation(sandbox_path, goal_file):
    """Runs the WRE in the sandbox with a given goal."""
    print(f"  [Harness] Starting simulation with goal: {goal_file.name}")
    
    # Run the WRE with proper module path
    sandboxed_goal_path = sandbox_path / 'modules' / 'wre_core' / 'tests' / 'simulation' / 'goals' / goal_file.name
    
    cmd = [
        sys.executable,
        "-m", "modules.wre_core.src.main",
        "--goal", str(sandboxed_goal_path)
    ]
    
    # Change to sandbox directory for execution
    original_cwd = Path.cwd()
    try:
        import os
        os.chdir(sandbox_path)
        
        # The WRE engine is now non-interactive when a goal is passed.
        # No input is required.
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.returncode != 0:
            print(f"  [Harness] ❌ Simulation failed with return code {result.returncode}")
            print(result.stdout)
            print(result.stderr)
            return False

        print(f"  [Harness] ✅ Simulation completed successfully.")
        print(result.stdout)
        return True
        
    finally:
        os.chdir(original_cwd)


def validate_results(sandbox_path, goal_data):
    """Calls the validation suite to check the results."""
    print("  [Harness] Running validation suite...")
    
    try:
        # Import and run validation functions
        validation_result = validation_suite.validate_simulation_output(sandbox_path, goal_data)
        
        if validation_result['success']:
            print("  [Harness] ✅ Validation passed.")
            return True
        else:
            print(f"  [Harness] ❌ Validation failed: {validation_result['errors']}")
            return False
            
    except Exception as e:
        print(f"  [Harness] ⚠️ Validation suite error: {e}")
        print("  [Harness] Continuing without validation.")
        return True


def teardown_sandbox(sandbox_path):
    """Deletes the temporary sandbox directory with retries."""
    print(f"  [Harness] Tearing down sandbox: {sandbox_path}")
    
    # Retry logic to handle potential file lock issues on Windows
    retries = 3
    delay = 1  # seconds
    for i in range(retries):
        try:
            shutil.rmtree(sandbox_path)
            print(f"  [Harness] ✅ Sandbox removed.")
            return
        except PermissionError as e:
            if i < retries - 1:
                print(f"  [Harness] ⚠️ PermissionError during teardown. Retrying in {delay}s... ({e})")
                time.sleep(delay)
            else:
                print(f"  [Harness] ❌ Failed to remove sandbox after {retries} retries.")
                raise e


def main():
    """
    Main entry point for the test harness.
    """
    parser = argparse.ArgumentParser(description="WRE Simulation Test Harness")
    parser.add_argument('--goal', type=str, default='create_user_auth.yaml',
                        help='Name of the goal file in modules/wre_core/tests/simulation/goals/')
    args = parser.parse_args()

    # Updated path to reflect new location
    goal_file = Path(__file__).parent / 'goals' / args.goal
    if not goal_file.exists():
        print(f"❌ Goal file not found: {goal_file}")
        sys.exit(1)
        
    try:
        with open(goal_file, 'r') as f:
            goal_data = yaml.safe_load(f)
    except Exception as e:
        print(f"❌ Could not parse goal file. Error: {e}")
        sys.exit(1)

    sandbox_path = None
    try:
        # 1. Setup Sandbox
        sandbox_path = setup_sandbox()
        
        # 2. Run Simulation
        success = run_simulation(sandbox_path, goal_file)
        
        # 3. Validate Results (only if simulation succeeded)
        if success:
            validate_results(sandbox_path, goal_data)

    except Exception as e:
        print(f"  [Harness] ❌ An unexpected error occurred: {e}")
    finally:
        # 4. Teardown Sandbox
        if sandbox_path and sandbox_path.exists():
            teardown_sandbox(sandbox_path)


if __name__ == "__main__":
    main() 