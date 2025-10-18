# -*- coding: utf-8 -*-
import io


import pytest
import sys
import os

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

def main():
    """Run pytest with coverage and save the results to a file."""
    # Set up the test command
    test_args = [
        'modules/livechat/tests/test_handle_auth_error_minimal.py',
        '-v',
        '--cov=modules.livechat.src.livechat',
        '--cov-report=term-missing'
    ]
    
    # Redirect stdout to capture the output
    original_stdout = sys.stdout
    with open('coverage_results.txt', 'w') as f:
        sys.stdout = f
        result = pytest.main(test_args)
        sys.stdout = original_stdout
    
    # Print a message indicating completion
    print(f"Test completed with exit code {result}. Results saved to coverage_results.txt")

if __name__ == "__main__":
    main() 