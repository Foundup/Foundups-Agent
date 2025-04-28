import pytest
import sys
import os

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