#!/usr/bin/env python3
"""
Test script to debug WRE execution from Cursor extension.
This mimics what the Cursor extension does.
"""

import subprocess
import sys
import os
from pathlib import Path

def test_wre_command():
    """Test the exact command that Cursor extension runs"""
    
    print("=== WRE Cursor Integration Debug ===")
    print(f"Python version: {sys.version}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python executable: {sys.executable}")
    
    # Set up environment like Cursor extension
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    
    print(f"Environment PYTHONIOENCODING: {env.get('PYTHONIOENCODING')}")
    print(f"Environment PATH length: {len(env.get('PATH', ''))}")
    
    # Get project root (3 levels up from this test file)
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent.parent
    
    # The exact command Cursor extension runs
    cwd = project_root
    python_command = 'python'
    wre_main = cwd / 'modules' / 'wre_core' / 'src' / 'main.py'
    directive = 'Test WRE session from Cursor extension'
    
    args = [
        python_command,
        str(wre_main),
        '--directive', directive,
        '--autonomous'
    ]
    
    print(f"\n[COMMAND] Working Directory: {cwd}")
    print(f"[COMMAND] Python: {python_command}")
    print(f"[COMMAND] WRE Main: {wre_main}")
    print(f"[COMMAND] Arguments: {' '.join(args[1:])}")
    print(f"[COMMAND] Full Command: {' '.join(args)}")
    print(f"[COMMAND] WRE file exists: {wre_main.exists()}")
    
    if not wre_main.exists():
        print(f"[ERROR] WRE main file not found: {wre_main}")
        return 1
    
    print("\n[EXECUTION] Starting WRE process...")
    print("=" * 60)
    
    try:
        # Run the exact command with the same setup
        result = subprocess.run(
            args,
            cwd=str(cwd),
            env=env,
            capture_output=False,  # Show output in real-time
            text=True,
            timeout=60  # 1 minute timeout for testing
        )
        
        print("=" * 60)
        print(f"[RESULT] Process completed with exit code: {result.returncode}")
        
        if result.returncode == 0:
            print("[SUCCESS] WRE completed successfully!")
        else:
            print(f"[FAILURE] WRE failed with exit code {result.returncode}")
            
            # Provide troubleshooting
            troubleshooting = {
                1: "General error - check Python imports and dependencies",
                2: "Misuse of shell command - check command line arguments", 
                126: "Command invoked cannot execute - check Python installation",
                127: "Command not found - verify Python is in PATH"
            }
            
            issue = troubleshooting.get(result.returncode, "Unknown error")
            print(f"[TROUBLESHOOTING] {issue}")
        
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("[TIMEOUT] WRE process timed out after 60 seconds")
        return 124
        
    except FileNotFoundError as e:
        print(f"[ERROR] File not found: {e}")
        print("[TROUBLESHOOTING] Check Python installation and PATH")
        return 127
        
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}")
        return 1

def test_python_imports():
    """Test critical Python imports"""
    
    print("\n=== Python Import Test ===")
    
    imports_to_test = [
        'pathlib',
        'asyncio', 
        'logging',
        'argparse',
        'json',
        'datetime',
        'sys',
        'os'
    ]
    
    for module in imports_to_test:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[ERROR] {module}: {e}")
            return False
    
    return True

def test_wre_file_structure():
    """Test WRE file structure"""
    
    print("\n=== WRE File Structure Test ===")
    
    required_files = [
        'modules/wre_core/src/main.py',
        'modules/wre_core/src/remote_build_orchestrator.py',
        'modules/wre_core/src/wsp_core_loader.py',
        'modules/infrastructure/compliance_agent/src/compliance_agent.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        path = Path(file_path)
        if path.exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[MISSING] {file_path}")
            all_exist = False
    
    return all_exist

if __name__ == "__main__":
    print("Starting comprehensive WRE debug test...")
    
    # Test Python imports
    imports_ok = test_python_imports()
    
    # Test file structure
    files_ok = test_wre_file_structure()
    
    if not imports_ok or not files_ok:
        print("\n[ERROR] Prerequisites failed - fix imports or file structure first")
        sys.exit(1)
    
    # Test WRE execution
    exit_code = test_wre_command()
    
    print(f"\n=== FINAL RESULT ===")
    if exit_code == 0:
        print("[SUCCESS] WRE test completed successfully!")
        print("[INFO] Cursor extension should work now")
    else:
        print(f"[FAILURE] WRE test failed with exit code {exit_code}")
        print("[INFO] Check the detailed logs above for troubleshooting")
    
    sys.exit(exit_code)