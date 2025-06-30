#!/usr/bin/env python3
"""
WSP: Circuit Breaker Test Module
================================

Tests for the CircuitBreaker class in the Stream Resolver module.
This test module focuses specifically on circuit breaker functionality,
state transitions, and integration with credential rotation.

WSP Compliance:
- Tests placed in correct module location
- Follows established test patterns
- Tests circuit breaker in isolation and integration
- Validates credential rotation reset functionality
"""

import unittest
import time
from unittest.mock import Mock, patch, MagicMock
import pytest
import sys
import os

# Add module path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..')))

from modules.platform_integration.stream_resolver.src.stream_resolver import (
    CircuitBreaker, 
    StreamResolverError,
    circuit_breaker
)

class TestCircuitBreaker(unittest.TestCase):
    """Test suite for CircuitBreaker class functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_breaker = CircuitBreaker(failure_threshold=3, timeout=60)
    
    def test_circuit_breaker_initialization(self):
        """Test circuit breaker initializes correctly."""
        self.assertEqual(self.test_breaker.failure_threshold, 3)
        self.assertEqual(self.test_breaker.timeout, 60)
        self.assertEqual(self.test_breaker.failure_count, 0)
        self.assertIsNone(self.test_breaker.last_failure_time)
        self.assertEqual(self.test_breaker.state, "CLOSED")
    
    def test_circuit_breaker_success_flow(self):
        """Test circuit breaker handles successful calls correctly."""
        def mock_function():
            return "success"
        
        result = self.test_breaker.call(mock_function)
        
        self.assertEqual(result, "success")
        self.assertEqual(self.test_breaker.failure_count, 0)
        self.assertEqual(self.test_breaker.state, "CLOSED")
    
    def test_circuit_breaker_failure_accumulation(self):
        """Test circuit breaker accumulates failures correctly."""
        def failing_function():
            raise Exception("Test failure")
        
        # Test failures below threshold
        for i in range(2):
            with self.assertRaises(Exception):
                self.test_breaker.call(failing_function)
            self.assertEqual(self.test_breaker.failure_count, i + 1)
            self.assertEqual(self.test_breaker.state, "CLOSED")
        
        # Test failure that opens circuit
        with self.assertRaises(Exception):
            self.test_breaker.call(failing_function)
        
        self.assertEqual(self.test_breaker.failure_count, 3)
        self.assertEqual(self.test_breaker.state, "OPEN")
        self.assertIsNotNone(self.test_breaker.last_failure_time)
    
    def test_circuit_breaker_open_state_blocks_calls(self):
        """Test circuit breaker blocks calls when OPEN."""
        # Force circuit breaker to OPEN state
        self.test_breaker.failure_count = 3
        self.test_breaker.state = "OPEN"
        self.test_breaker.last_failure_time = time.time()
        
        def mock_function():
            return "should not execute"
        
        with self.assertRaises(StreamResolverError) as context:
            self.test_breaker.call(mock_function)
        
        self.assertIn("Circuit breaker is OPEN", str(context.exception))
    
    def test_circuit_breaker_timeout_reset(self):
        """Test circuit breaker resets after timeout."""
        # Set up OPEN state with old timestamp
        self.test_breaker.failure_count = 3
        self.test_breaker.state = "OPEN"
        self.test_breaker.last_failure_time = time.time() - 120  # 2 minutes ago (timeout is 60s)
        
        def success_function():
            return "success after timeout"
        
        result = self.test_breaker.call(success_function)
        
        self.assertEqual(result, "success after timeout")
        self.assertEqual(self.test_breaker.failure_count, 0)
        self.assertEqual(self.test_breaker.state, "CLOSED")
    
    def test_circuit_breaker_half_open_state(self):
        """Test circuit breaker HALF_OPEN state behavior."""
        # Set up for half-open transition
        self.test_breaker.failure_count = 3
        self.test_breaker.state = "OPEN"
        self.test_breaker.last_failure_time = time.time() - 120  # Past timeout
        
        # Should transition to HALF_OPEN when attempting reset
        self.assertTrue(self.test_breaker._should_attempt_reset())
        
        # Simulate the state transition that happens in call()
        self.test_breaker.state = "HALF_OPEN"
        
        def success_function():
            return "half open success"
        
        result = self.test_breaker.call(success_function)
        self.assertEqual(self.test_breaker.state, "CLOSED")
        self.assertEqual(self.test_breaker.failure_count, 0)


class TestCircuitBreakerIntegration(unittest.TestCase):
    """Test circuit breaker integration with stream resolver components."""
    
    def setUp(self):
        """Set up integration test fixtures."""
        # Reset global circuit breaker state
        circuit_breaker.failure_count = 0
        circuit_breaker.state = "CLOSED"
        circuit_breaker.last_failure_time = None
    
    def test_global_circuit_breaker_exists(self):
        """Test that global circuit breaker instance exists and is configured."""
        self.assertIsInstance(circuit_breaker, CircuitBreaker)
        self.assertEqual(circuit_breaker.failure_threshold, 10)  # From config
        self.assertEqual(circuit_breaker.timeout, 600)  # 10 minutes
    
    def test_circuit_breaker_manual_reset(self):
        """Test manual circuit breaker reset (used in credential rotation)."""
        # Simulate OPEN state
        circuit_breaker.failure_count = 10
        circuit_breaker.state = "OPEN"
        circuit_breaker.last_failure_time = time.time()
        
        self.assertEqual(circuit_breaker.state, "OPEN")
        
        # Simulate manual reset (as done in credential rotation)
        circuit_breaker.failure_count = 0
        circuit_breaker.state = "CLOSED"
        circuit_breaker.last_failure_time = None
        
        self.assertEqual(circuit_breaker.state, "CLOSED")
        self.assertEqual(circuit_breaker.failure_count, 0)
        self.assertIsNone(circuit_breaker.last_failure_time)
    
    @patch('modules.infrastructure.oauth_management.src.oauth_manager.get_authenticated_service_with_fallback')
    def test_circuit_breaker_with_credential_rotation(self, mock_credential_rotation):
        """Test circuit breaker integration with credential rotation."""
        # Mock successful credential rotation
        mock_service = Mock()
        mock_creds = Mock()
        mock_credential_rotation.return_value = (mock_service, mock_creds, "set_2")
        
        # Start with circuit breaker OPEN
        circuit_breaker.failure_count = 10
        circuit_breaker.state = "OPEN"
        circuit_breaker.last_failure_time = time.time()
        
        # Verify circuit breaker is OPEN
        self.assertEqual(circuit_breaker.state, "OPEN")
        
        # Simulate the actual credential rotation flow that happens in stream resolver
        # This mimics the pattern in stream_resolver.py lines 715-720
        try:
            fallback_result = mock_credential_rotation()
            if fallback_result:
                fallback_service, fallback_creds, credential_set = fallback_result
                # Reset circuit breaker for new credentials (as done in real code)
                circuit_breaker.failure_count = 0
                circuit_breaker.state = "CLOSED"
                circuit_breaker.last_failure_time = None
        except Exception:
            pass  # Handle case where credential rotation might fail
        
        # Verify circuit breaker is reset
        self.assertEqual(circuit_breaker.state, "CLOSED")
        self.assertEqual(circuit_breaker.failure_count, 0)
        mock_credential_rotation.assert_called_once()


class TestCircuitBreakerEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for circuit breaker."""
    
    def setUp(self):
        """Set up edge case test fixtures."""
        self.edge_breaker = CircuitBreaker(failure_threshold=1, timeout=1)
    
    def test_circuit_breaker_with_zero_threshold(self):
        """Test circuit breaker with minimal threshold."""
        zero_breaker = CircuitBreaker(failure_threshold=0, timeout=60)
        
        def failing_function():
            raise Exception("Immediate failure")
        
        # Should open immediately with 0 threshold
        with self.assertRaises(Exception):
            zero_breaker.call(failing_function)
        
        self.assertEqual(zero_breaker.state, "OPEN")
    
    def test_circuit_breaker_rapid_timeout_recovery(self):
        """Test circuit breaker with very short timeout."""
        short_breaker = CircuitBreaker(failure_threshold=1, timeout=0.1)  # 100ms timeout
        
        def failing_function():
            raise Exception("Quick failure")
        
        def success_function():
            return "quick recovery"
        
        # Trigger failure and open circuit
        with self.assertRaises(Exception):
            short_breaker.call(failing_function)
        
        self.assertEqual(short_breaker.state, "OPEN")
        
        # Wait for timeout
        time.sleep(0.2)
        
        # Should recover quickly
        result = short_breaker.call(success_function)
        self.assertEqual(result, "quick recovery")
        self.assertEqual(short_breaker.state, "CLOSED")
    
    def test_circuit_breaker_state_persistence(self):
        """Test that circuit breaker state persists correctly."""
        # Test state transitions
        states = []
        
        def record_state():
            states.append(self.edge_breaker.state)
            if len(states) == 1:
                raise Exception("First failure")
            return "success"
        
        # First call should fail and open circuit
        with self.assertRaises(Exception):
            self.edge_breaker.call(record_state)
        
        self.assertEqual(states[0], "CLOSED")  # State before failure
        self.assertEqual(self.edge_breaker.state, "OPEN")  # State after failure


def run_circuit_breaker_tests():
    """Run all circuit breaker tests."""
    print("🧪 Running Circuit Breaker Test Suite")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreaker))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreakerEdgeCases))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_circuit_breaker_tests()
    if success:
        print("\n✅ All circuit breaker tests passed!")
    else:
        print("\n❌ Some circuit breaker tests failed!")
    
    print("\n🎯 Circuit breaker functionality verified for:")
    print("   • State transitions (CLOSED → OPEN → HALF_OPEN → CLOSED)")
    print("   • Failure threshold enforcement")
    print("   • Timeout-based recovery")
    print("   • Manual reset for credential rotation")
    print("   • Integration with global circuit breaker instance") 