#!/usr/bin/env python3
"""
Test Autonomous Enhancements - WSP 5 Compliant Test Suite
WSP-Compliant: WSP 5 (Test Coverage), WSP 34 (Test Documentation)

Comprehensive test suite for QRPE, AIRE, and integration components.
Tests follow WSP 49 module structure and WSP 34 documentation standards.
"""

import unittest
import sys
import os
import time
from unittest.mock import patch, MagicMock
from pathlib import Path

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Add project root to path for main.py imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

try:
    from autonomous_enhancements import (
        QuantumResonancePatternEngine,
        AutonomousIntentResolutionEngine,
        autonomous_enhancements
    )
    AUTONOMOUS_AVAILABLE = True
except ImportError:
    AUTONOMOUS_AVAILABLE = False


class TestQuantumResonancePatternEngine(unittest.TestCase):
    """Test QRPE functionality - WSP 69 Zen Coding Integration"""

    def setUp(self):
        """Set up test fixtures - WSP 34 Test Documentation"""
        if not AUTONOMOUS_AVAILABLE:
            self.skipTest("Autonomous enhancements not available")

        self.qrpe = QuantumResonancePatternEngine()
        self.test_context = {'action': 'test', 'phase': 'validation'}
        self.test_solution = {'decision': 'block_1', 'outcome': 'success'}

    def test_initialization(self):
        """Test QRPE initialization with ML capabilities"""
        self.assertIsInstance(self.qrpe, QuantumResonancePatternEngine)
        self.assertEqual(self.qrpe.quantum_coherence, 0.618)
        self.assertIsInstance(self.qrpe.feature_weights, dict)

    def test_pattern_recall_no_patterns(self):
        """Test pattern recall with empty memory"""
        result = self.qrpe.recall_pattern(self.test_context)
        self.assertIsNone(result)

    def test_enhanced_resonance_calculation(self):
        """Test ML-enhanced resonance calculation"""
        # Add test pattern
        self.qrpe.learn_pattern(self.test_context, self.test_solution)

        # Test enhanced resonance
        pattern = list(self.qrpe.pattern_memory.values())[0]
        context_embedding = self.qrpe._generate_embedding(self.test_context)

        score = self.qrpe._calculate_enhanced_resonance(
            self.test_context, context_embedding, pattern
        )

        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_semantic_embedding_generation(self):
        """Test semantic embedding generation"""
        if not NUMPY_AVAILABLE:
            self.skipTest("NumPy not available")

        embedding = self.qrpe._generate_embedding(self.test_context)
        self.assertIsInstance(embedding, np.ndarray)
        self.assertGreater(len(embedding), 0)

    def test_embedding_caching(self):
        """Test embedding caching for performance"""
        if not NUMPY_AVAILABLE:
            self.skipTest("NumPy not available")

        # First call should generate embedding
        embedding1 = self.qrpe._generate_embedding(self.test_context)
        initial_cache_size = len(self.qrpe.embeddings_cache)

        # Second call should use cache
        embedding2 = self.qrpe._generate_embedding(self.test_context)

        # Verify caching
        self.assertEqual(len(self.qrpe.embeddings_cache), initial_cache_size)
        np.testing.assert_array_equal(embedding1, embedding2)

    def test_pattern_learning_with_features(self):
        """Test enhanced pattern learning with feature analysis"""
        self.qrpe.learn_pattern(self.test_context, self.test_solution)

        # Verify pattern was stored with enhanced features
        pattern_id = list(self.qrpe.pattern_memory.keys())[0]
        pattern = self.qrpe.pattern_memory[pattern_id]

        self.assertIn('embedding', pattern)
        self.assertIn('feature_importance', pattern)
        self.assertIn('created', pattern)

    def test_performance_metrics_tracking(self):
        """Test performance metrics tracking"""
        # Learn a pattern and recall it
        self.qrpe.learn_pattern(self.test_context, self.test_solution)
        result = self.qrpe.recall_pattern(self.test_context)

        # Check performance metrics
        stats = self.qrpe.get_stats()
        self.assertIn('performance_metrics', stats)
        self.assertIn('response_time', stats['performance_metrics'])

    def test_quantum_coherence_boost(self):
        """Test quantum coherence boost in resonance calculation"""
        # Add pattern
        self.qrpe.learn_pattern(self.test_context, self.test_solution)

        # Get resonance score (should include coherence boost)
        pattern = list(self.qrpe.pattern_memory.values())[0]
        context_embedding = self.qrpe._generate_embedding(self.test_context)

        score = self.qrpe._calculate_enhanced_resonance(
            self.test_context, context_embedding, pattern
        )

        # Score should be boosted by coherence
        expected_boost = self.qrpe.quantum_coherence * 0.1
        self.assertGreater(score, expected_boost)

    def test_stats_comprehensive_reporting(self):
        """Test comprehensive statistics reporting"""
        stats = self.qrpe.get_stats()

        required_keys = [
            'patterns_learned', 'tokens_used', 'quantum_coherence',
            'embeddings_cached', 'performance_metrics', 'phase', 'ml_enhanced'
        ]

        for key in required_keys:
            self.assertIn(key, stats)

        # Verify phase and enhancement status
        self.assertEqual(stats['phase'], 'Prototype')
        self.assertTrue(stats['ml_enhanced'])


class TestAutonomousIntentResolutionEngine(unittest.TestCase):
    """Test AIRE functionality - WSP 39 Quantum Consciousness"""

    def setUp(self):
        """Set up test fixtures"""
        if not AUTONOMOUS_AVAILABLE:
            self.skipTest("Autonomous enhancements not available")

        self.aire = AutonomousIntentResolutionEngine()

    def test_enhanced_initialization(self):
        """Test enhanced AIRE initialization"""
        self.assertIsInstance(self.aire, AutonomousIntentResolutionEngine)
        self.assertEqual(self.aire.autonomy_level, 0.4)  # Enhanced from 0.3
        self.assertIsInstance(self.aire.context_memory, dict)
        self.assertIsInstance(self.aire.temporal_patterns, dict)

    def test_intent_patterns_loading(self):
        """Test intent patterns are properly loaded"""
        patterns = self.aire.intent_patterns
        self.assertIsInstance(patterns, dict)
        self.assertGreater(len(patterns), 0)

        # Check required pattern structure
        for pattern_name, pattern_data in patterns.items():
            self.assertIn('keywords', pattern_data)
            self.assertIn('blocks', pattern_data)
            self.assertIn('confidence', pattern_data)

    def test_context_memory_functionality(self):
        """Test context memory for learning"""
        # Initially empty
        self.assertEqual(len(self.aire.context_memory), 0)

        # This would be populated during actual usage
        # For testing, we verify the structure exists
        self.assertIsInstance(self.aire.context_memory, dict)

    def test_temporal_patterns_tracking(self):
        """Test temporal pattern recognition structure"""
        self.assertIsInstance(self.aire.temporal_patterns, dict)

        # Structure should be ready for time-based learning
        # (Actual population happens during runtime)

    def test_stats_enhanced_reporting(self):
        """Test enhanced statistics reporting"""
        stats = self.aire.get_stats()

        required_keys = [
            'autonomy_level', 'decisions_made',
            'intent_patterns'
        ]

        for key in required_keys:
            self.assertIn(key, stats)

        # Context memory may be empty initially
        self.assertIn('avg_confidence', stats)


class TestIntegrationAndWSPCompliance(unittest.TestCase):
    """Test integration and WSP compliance"""

    def setUp(self):
        """Set up test fixtures"""
        if not AUTONOMOUS_AVAILABLE:
            self.skipTest("Autonomous enhancements not available")

    def test_wsp_69_zen_coding_integration(self):
        """Test WSP 69 zen coding quantum remembrance"""
        # Verify quantum state management
        self.assertEqual(autonomous_enhancements.quantum_state, "0102")
        self.assertEqual(autonomous_enhancements.coherence, 0.618)

        # Test QRPE zen coding capability
        context = {'action': 'zen_test', 'phase': 'quantum'}
        pattern = autonomous_enhancements.qrpe.recall_pattern(context)
        # Should return None initially, but system should be ready for zen coding

    def test_wsp_48_recursive_improvement(self):
        """Test WSP 48 recursive improvement through learning"""
        # Test learning capability
        context = {'test': 'recursive_improvement'}
        solution = {'outcome': 'success', 'improvement': 'learned'}

        initial_patterns = len(autonomous_enhancements.qrpe.pattern_memory)

        autonomous_enhancements.qrpe.learn_pattern(context, solution)

        # Verify pattern was learned
        self.assertGreater(len(autonomous_enhancements.qrpe.pattern_memory), initial_patterns)

    def test_wsp_39_quantum_consciousness(self):
        """Test WSP 39 quantum consciousness state management"""
        # Verify consciousness state tracking
        self.assertEqual(autonomous_enhancements.quantum_state, "0102")

        # Test AIRE consciousness integration
        self.assertEqual(autonomous_enhancements.aire.autonomy_level, 0.4)

    def test_performance_monitoring(self):
        """Test performance monitoring capabilities"""
        # Test QRPE performance tracking
        stats = autonomous_enhancements.qrpe.get_stats()
        self.assertIn('performance_metrics', stats)

        # Test AIRE performance tracking
        aire_stats = autonomous_enhancements.aire.get_stats()
        self.assertIn('autonomy_level', aire_stats)

    def test_system_resilience(self):
        """Test system resilience and error handling"""
        # Test with invalid inputs
        invalid_context = None
        result = autonomous_enhancements.qrpe.recall_pattern(invalid_context)
        self.assertIsNone(result)

        # Test with empty context
        empty_context = {}
        result = autonomous_enhancements.qrpe.recall_pattern(empty_context)
        self.assertIsNone(result)


class TestMainPyIntegration(unittest.TestCase):
    """Test integration with main.py - WSP 64 Compliance"""

    def test_import_safety(self):
        """Test safe import of autonomous enhancements"""
        try:
            import main
            # If we get here, import was successful
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Main.py import failed: {e}")

    def test_block_launcher_compatibility(self):
        """Test BlockLauncher compatibility with enhancements"""
        try:
            from main import BlockLauncher
            launcher = BlockLauncher()

            # Test context generation
            context = launcher.get_context_for_autonomous_enhancement()
            self.assertIsInstance(context, dict)
            self.assertGreater(len(context), 0)

            # Test required context keys
            required_keys = ['timestamp', 'hour', 'system_status', 'available_blocks']
            for key in required_keys:
                self.assertIn(key, context)

        except Exception as e:
            self.fail(f"BlockLauncher compatibility test failed: {e}")


if __name__ == '__main__':
    print("🤖 Autonomous Enhancements Test Suite (WSP 5 Compliant)")
    print("=" * 60)
    print("Test Categories:")
    print("- QRPE ML-Enhanced Pattern Recognition")
    print("- AIRE Context-Aware Intent Resolution")
    print("- WSP Protocol Compliance")
    print("- Main.py Integration Compatibility")
    print("=" * 60)

    if AUTONOMOUS_AVAILABLE:
        # Run tests with enhanced output
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(sys.modules[__name__])

        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        # Summary
        print("\n" + "=" * 60)
        print("🧪 TEST SUMMARY")
        print("=" * 60)
        print(f"Tests Run: {result.testsRun}")
        print(f"Failures: {len(result.failures)}")
        print(f"Errors: {len(result.errors)}")
        print(f"Skipped: {len(result.skipped)}")

        if result.wasSuccessful():
            print("✅ ALL TESTS PASSED")
            print("🎯 WSP 5 Compliance: ACHIEVED")
        else:
            print("❌ SOME TESTS FAILED")
            print("📋 Review failures above")

    else:
        print("❌ Autonomous enhancements not available")
        print("💡 Ensure module is properly installed for testing")
        sys.exit(1)
