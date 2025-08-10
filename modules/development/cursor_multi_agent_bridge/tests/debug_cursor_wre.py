#!/usr/bin/env python3
"""
Debug script to test exact Cursor WRE integration scenario
"""

import subprocess
import sys
import os
from pathlib import Path
import json

def test_cursor_scenario():
    """Test the exact scenario Cursor extension uses"""
    
    print("=== CURSOR WRE DEBUG ===")
    
    # Get project root (4 levels up from this test file)
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent.parent.parent
    
    # Cursor extension working directory
    cwd = project_root
    print(f"Working directory: {cwd}")
    
    # Environment setup (like Cursor extension)
    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8' 
    env['PYTHONUNBUFFERED'] = '1'
    
    # The EXACT command Cursor extension runs (after our fix)
    python_cmd = 'python'
    args = [
        python_cmd,
        '-m', 'modules.wre_core.src.main',
        '--directive', 'Interactive WRE session from Claude Code',
        '--autonomous'
    ]
    
    print(f"Command: {' '.join(args)}")
    print(f"Environment variables:")
    print(f"  PYTHONIOENCODING: {env.get('PYTHONIOENCODING')}")
    print(f"  PYTHONUNBUFFERED: {env.get('PYTHONUNBUFFERED')}")
    print(f"  Python path: {env.get('PYTHONPATH', 'Not set')}")
    
    print("\n" + "="*60)
    print("EXECUTING WRE COMMAND...")
    print("="*60)
    
    try:
        # Run with live output capture
        process = subprocess.Popen(
            args,
            cwd=str(cwd),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Read output in real-time
        stdout_lines = []
        stderr_lines = []
        
        while True:
            # Read stdout
            stdout_line = process.stdout.readline() if process.stdout else ""
            if stdout_line:
                print(f"[STDOUT] {stdout_line.rstrip()}")
                stdout_lines.append(stdout_line.rstrip())
            
            # Read stderr  
            stderr_line = process.stderr.readline() if process.stderr else ""
            if stderr_line:
                print(f"[STDERR] {stderr_line.rstrip()}")
                stderr_lines.append(stderr_line.rstrip())
            
            # Check if process ended
            if process.poll() is not None:
                # Read any remaining output
                remaining_stdout = process.stdout.read() if process.stdout else ""
                remaining_stderr = process.stderr.read() if process.stderr else ""
                
                if remaining_stdout:
                    for line in remaining_stdout.split('\n'):
                        if line.strip():
                            print(f"[STDOUT] {line}")
                            stdout_lines.append(line)
                            
                if remaining_stderr:
                    for line in remaining_stderr.split('\n'):
                        if line.strip():
                            print(f"[STDERR] {line}")
                            stderr_lines.append(line)
                break
        
        exit_code = process.returncode
        
        print("="*60)
        print(f"PROCESS COMPLETED - EXIT CODE: {exit_code}")
        print("="*60)
        
        # Analyze the results
        print(f"\nANALYSIS:")
        print(f"Exit Code: {exit_code}")
        print(f"STDOUT lines: {len(stdout_lines)}")
        print(f"STDERR lines: {len(stderr_lines)}")
        
        if exit_code == 0:
            print("[SUCCESS] WRE completed successfully!")
            
            # Look for session completion
            session_completed = any("REMOTE_BUILD_PROTOTYPE session completed" in line for line in stdout_lines)
            phases_completed = 0
            for line in stdout_lines:
                if "Phases Completed:" in line:
                    try:
                        phases_completed = int(line.split("Phases Completed:")[1].split("/")[0].strip())
                    except:
                        pass
            
            print(f"Session completed: {session_completed}")
            print(f"Phases completed: {phases_completed}/12")
            
        else:
            print(f"[FAILURE] WRE exited with code {exit_code}")
            
            # Look for specific error patterns
            import_errors = [line for line in stderr_lines if "ImportError" in line or "ModuleNotFoundError" in line]
            unicode_errors = [line for line in stderr_lines if "UnicodeEncodeError" in line or "cp932" in line]
            traceback_lines = [line for line in stderr_lines if "Traceback" in line]
            
            if import_errors:
                print("\n[IMPORT ERRORS DETECTED]:")
                for error in import_errors:
                    print(f"  {error}")
                    
            if unicode_errors:
                print("\n[UNICODE ERRORS DETECTED]:")
                for error in unicode_errors:
                    print(f"  {error}")
                    
            if traceback_lines:
                print(f"\n[TRACEBACKS DETECTED]: {len(traceback_lines)}")
                
            # Show last few stderr lines for context
            if stderr_lines:
                print("\n[LAST STDERR LINES]:")
                for line in stderr_lines[-5:]:
                    print(f"  {line}")
        
        return exit_code
        
    except Exception as e:
        print(f"[EXECUTION ERROR]: {e}")
        return 1

def check_python_environment():
    """Check Python environment details"""
    print("\n=== PYTHON ENVIRONMENT CHECK ===")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Add project root to sys.path if needed
    test_file = Path(__file__).resolve()
    project_root = test_file.parent.parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print(f"Python path entries:")
    for i, path in enumerate(sys.path):
        print(f"  [{i}] {path}")
    
    # Test critical imports
    print("\n=== IMPORT TESTS ===")
    critical_modules = [
        'modules.wre_core.src.main',
        'modules.wre_core.src.remote_build_orchestrator', 
        'modules.infrastructure.compliance_agent.src.compliance_agent'
    ]
    
    for module in critical_modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except Exception as e:
            print(f"[FAIL] {module}: {e}")
            return False
    
    return True

if __name__ == "__main__":
    print("DEBUGGING CURSOR WRE INTEGRATION")
    print("This script mimics exactly what Cursor extension does")
    
    # Check environment first
    env_ok = check_python_environment()
    
    if not env_ok:
        print("\n[ERROR] Environment check failed - fix Python imports first")
        sys.exit(1)
    
    # Run the test
    exit_code = test_cursor_scenario()
    
    print(f"\n=== FINAL RESULT ===")
    if exit_code == 0:
        print("[SUCCESS] Cursor WRE integration should work!")
    else:
        print(f"[FAILURE] Still getting exit code {exit_code}")
        print("Check the detailed output above for clues")
    
    sys.exit(exit_code)