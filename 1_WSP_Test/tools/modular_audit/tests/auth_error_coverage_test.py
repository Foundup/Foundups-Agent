import pytest
import sys
import os
import inspect
from pathlib import Path

def main():
    """Run a focused coverage test on _handle_auth_error and analyze results."""
    # First import the class to check its structure
    sys.path.insert(0, os.path.abspath('.'))
    
    from modules.livechat.src.livechat import LiveChatListener
    
    # Print information about the method
    print("Examining _handle_auth_error method:")
    method = LiveChatListener._handle_auth_error
    print(f"Method name: {method.__name__}")
    print(f"Method is async: {inspect.iscoroutinefunction(method)}")
    
    # Get the source code
    try:
        source = inspect.getsource(method)
        print("\nMethod source code:")
        print(source)
    except Exception as e:
        print(f"Error getting source: {e}")
    
    # Check the line numbers
    try:
        lines, start_line = inspect.getsourcelines(method)
        print(f"\nMethod starts at line {start_line} and has {len(lines)} lines")
    except Exception as e:
        print(f"Error getting source lines: {e}")
    
    # Run the test with coverage
    print("\nRunning test with coverage...")
    test_args = [
        'modules/livechat/tests/test_handle_auth_error_minimal.py',
        '-v',
        '--no-header',
        '--no-summary',
        '--cov=modules.livechat.src.livechat',
        '--cov-report=term-missing:skip-covered'
    ]
    
    result = pytest.main(test_args)
    print(f"\nTest completed with exit code {result}")
    
    # Print a suggestion based on analysis
    print("\nAnalysis and suggestions:")
    print("1. If line numbers don't match between source and missing coverage, there may be import path issues.")
    print("2. If the method is being executed (tests pass) but not appearing in coverage, check if mock patching")
    print("   is replacing the actual method execution.")
    print("3. Consider modifying tests to directly call the method under test rather than relying on side effects.")

if __name__ == "__main__":
    main() 