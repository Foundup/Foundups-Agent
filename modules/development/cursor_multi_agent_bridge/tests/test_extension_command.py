#!/usr/bin/env python3
"""
Test the exact command that the Cursor extension should run
"""

import subprocess
import sys
import os
from pathlib import Path

def test_extension_command():
    """Test the exact command from the fixed extension"""
    
    print("=== TESTING CURSOR EXTENSION COMMAND ===")
    
    # Get project root (4 levels up from this test file)
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent.parent.parent
    
    # This is exactly what the fixed extension runs
    cwd = str(project_root)
    directive = "Interactive WRE session from Claude Code"
    
    python_command = 'python'
    wre_main = os.path.join(cwd, 'wre_launcher.py')
    args = [
        python_command,
        wre_main,
        '--directive', directive,
        '--autonomous'
    ]
    
    print(f"Working Directory: {cwd}")
    print(f"Command: {' '.join(args)}")
    print(f"WRE Launcher exists: {os.path.exists(wre_main)}")
    
    if not os.path.exists(wre_main):
        print("ERROR: wre_launcher.py not found!")
        return 1
    
    print("\n" + "="*50)
    print("EXECUTING COMMAND...")
    print("="*50)
    
    # Set up environment like the extension does
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    env['PYTHONUNBUFFERED'] = '1'
    env['LANG'] = 'en_US.UTF-8'
    env['LC_ALL'] = 'en_US.UTF-8'
    
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            env=env,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        print(f"Exit Code: {result.returncode}")
        print(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            print(f"STDERR:\n{result.stderr}")
            
        return result.returncode
        
    except subprocess.TimeoutExpired:
        print("Command timed out (5 minutes)")
        return 124
    except Exception as e:
        print(f"Command failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = test_extension_command()
    print(f"\n=== FINAL RESULT: EXIT CODE {exit_code} ===")
    if exit_code == 0:
        print("SUCCESS: Extension command should work!")
    else:
        print("FAILURE: Extension command has issues")
    sys.exit(exit_code)