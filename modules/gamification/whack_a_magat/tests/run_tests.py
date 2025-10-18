#!/usr/bin/env python
"""
Test Runner for Whack-a-MAGA Module - WSP Compliant
Run all tests for the gamification system
"""

import sys
import os
import pytest
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def run_tests():
    """Run all whack-a-magat tests with coverage report."""
    test_args = [
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--cov=modules.gamification.whack_a_magat',  # Coverage for whack module
        '--cov-report=term-missing',  # Show missing lines
        '--cov-report=html:coverage_html',  # Generate HTML coverage report
        'modules/gamification/whack_a_magat/tests/',  # Test directory
    ]
    
    print("=" * 60)
    print("[GAME] Running Whack-a-MAGA Tests")
    print("=" * 60)
    
    # Run pytest with arguments
    exit_code = pytest.main(test_args)
    
    if exit_code == 0:
        print("\n" + "=" * 60)
        print("[OK] All tests passed!")
        print("[DATA] Coverage report generated in coverage_html/")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("[FAIL] Some tests failed!")
        print("=" * 60)
    
    return exit_code

if __name__ == "__main__":
    sys.exit(run_tests())