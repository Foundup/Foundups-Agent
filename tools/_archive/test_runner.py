#!/usr/bin/env python3
"""
Simple test runner for comprehensive chat communication tests
"""

import sys
import os
import unittest

# Add the module path to sys.path
sys.path.insert(0, os.path.join(os.getcwd(), 'modules', 'ai_intelligence', 'banter_engine', 'banter_engine'))

try:
    from tests.test_comprehensive_chat_communication import TestComprehensiveChatCommunication
    
    if __name__ == "__main__":
        # Create test suite
        suite = unittest.TestLoader().loadTestsFromTestCase(TestComprehensiveChatCommunication)
        
        # Run tests with verbose output
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
        
        if result.failures:
            print(f"\nFAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}: {traceback}")
        
        if result.errors:
            print(f"\nERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}: {traceback}")

except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all modules are properly installed and paths are correct.")
    sys.exit(1) 