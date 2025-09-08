#!/usr/bin/env python3
"""
Test WRE Autonomous Integration
WSP 5 Compliant Test Suite

Tests the integration of autonomous enhancements with WRE recursive improvement system.
Validates cross-component communication, decision integration, and WSP compliance.
"""

import unittest
import asyncio
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from modules.wre_core.recursive_improvement.src.core import AutonomousIntegrationLayer
    WRE_INTEGRATION_AVAILABLE = True
except ImportError:
    WRE_INTEGRATION_AVAILABLE = False


class TestWREAutonomousIntegration(unittest.TestCase):
    """Test WRE autonomous integration layer functionality"""

    def setUp(self):
        """Set up test fixtures"""
        if not WRE_INTEGRATION_AVAILABLE:
            self.skipTest("WRE autonomous integration not available")

        self.integration_layer = AutonomousIntegrationLayer()
        self.test_system_state = {
            'file_metrics': {
                'total_size': 1000000,
                'max_file_size': 500000,
                'file_count': 10
            },
            'complexity_metrics': {
                'avg_complexity': 15,
                'dependency_count': 25
            },
            'memory_metrics': {
                'current_usage': 750000,
                'limit': 1000000
            },
            'token_metrics': {
                'current_usage': 85000,
                'limit': 100000
            },
            'activity_level': 0.8,
            'awareness_score': 0.9,
            'quantum_coherence': 0.618,
            'task_complexity': 0.7,
            'computational_load': 0.6,
            'nonlocal_patterns': 3,
            'entanglement_factor': 0.8,
            'resonance_level': 0.75,
            'growth_rate': 0.1
        }

    def test_integration_layer_initialization(self):
        """Test that the integration layer initializes correctly"""
        self.assertIsInstance(self.integration_layer, AutonomousIntegrationLayer)
        self.assertIsNotNone(self.integration_layer.integration_stats)

        # Check that components are initialized (either real or stubs)
        self.assertIsNotNone(self.integration_layer.qrpe)
        self.assertIsNotNone(self.integration_layer.aire)
        self.assertIsNotNone(self.integration_layer.qpo)
        self.assertIsNotNone(self.integration_layer.msce)
        self.assertIsNotNone(self.integration_layer.qmre)

    def test_pattern_confidence_calculation(self):
        """Test pattern confidence calculation"""
        predictions = [
            {'confidence': 0.8},
            {'confidence': 0.6},
            {'confidence': 0.9}
        ]

        confidence = self.integration_layer._calculate_pattern_confidence(predictions)
        expected = (0.8 + 0.6 + 0.9) / 3  # 0.767

        self.assertAlmostEqual(confidence, expected, places=3)

    def test_empty_predictions_confidence(self):
        """Test pattern confidence with empty predictions"""
        confidence = self.integration_layer._calculate_pattern_confidence([])
        self.assertEqual(confidence, 0.5)

    def test_primary_action_determination(self):
        """Test primary action determination logic"""
        # Test high consciousness state with predictions
        outputs = {
            'consciousness': {'current_state': '0201'},
            'predictions': [{'confidence': 0.9}],
            'pattern_match': False,
            'intent_recommendation': None
        }

        action = self.integration_layer._determine_primary_action(outputs)
        self.assertEqual(action, 'execute_preventive_actions')

        # Test pattern match priority
        outputs['pattern_match'] = True
        action = self.integration_layer._determine_primary_action(outputs)
        self.assertEqual(action, 'apply_learned_pattern')

        # Test intent recommendation priority
        outputs['pattern_match'] = False
        outputs['intent_recommendation'] = 'optimize_performance'
        action = self.integration_layer._determine_primary_action(outputs)
        self.assertEqual(action, 'follow_intent_guidance')

    def test_integrated_confidence_calculation(self):
        """Test integrated confidence calculation"""
        outputs = {
            'consciousness': {'coherence_level': 0.8},
            'predictions': [{'confidence': 0.7}, {'confidence': 0.8}],
            'pattern_match': True,
            'memory': True
        }

        confidence = self.integration_layer._calculate_integrated_confidence(outputs)

        # Should include: coherence (0.8), avg prediction (0.75), pattern match (0.8), memory (0.7)
        expected_factors = [0.8, 0.75, 0.8, 0.7]
        expected = sum(expected_factors) / len(expected_factors)

        self.assertAlmostEqual(confidence, expected, places=3)

    def test_improvement_extraction(self):
        """Test improvement recommendation extraction"""
        outputs = {
            'predictions': [
                {'confidence': 0.8, 'preventive_actions': ['optimize_storage', 'cache_results']},
                {'confidence': 0.6, 'preventive_actions': ['optimize_storage']},  # Below threshold
                {'confidence': 0.9, 'preventive_actions': ['implement_cleanup']}
            ]
        }

        improvements = self.integration_layer._extract_improvements(outputs)

        # Should only include actions from high-confidence predictions
        expected = ['optimize_storage', 'cache_results', 'implement_cleanup']
        self.assertEqual(set(improvements), set(expected))

    def test_risk_assessment(self):
        """Test integration risk assessment"""
        outputs = {
            'predictions': [
                {'confidence': 0.9},  # High confidence
                {'confidence': 0.2},  # Low confidence
                {'confidence': 0.85}, # High confidence
                {'confidence': 0.1}   # Low confidence
            ]
        }

        risks = self.integration_layer._assess_integration_risks(outputs)

        self.assertEqual(risks['high_confidence_actions'], 2)
        self.assertEqual(risks['uncertain_predictions'], 2)
        self.assertEqual(risks['overall_risk_level'], 'medium')  # Mixed confidence

    def test_next_steps_planning(self):
        """Test next steps planning based on outputs"""
        # Test high consciousness state
        outputs = {
            'consciousness': {'current_state': '0201'},
            'predictions': [{'confidence': 0.9}],
            'pattern_match': True
        }

        next_steps = self.integration_layer._plan_next_steps(outputs)

        expected_steps = [
            'execute_high_confidence_actions',
            'review_prediction_details',
            'update_prevention_strategies',
            'analyze_pattern_effectiveness',
            'update_pattern_memory'
        ]

        for step in expected_steps:
            self.assertIn(step, next_steps)

    async def test_full_recursive_cycle(self):
        """Test complete recursive improvement cycle"""
        # This would normally take system metrics, but we'll mock it
        with patch.object(self.integration_layer, '_initialize_autonomous_components'):
            with patch.object(self.integration_layer, '_initialize_stubs'):
                # Reset to ensure clean state
                self.integration_layer._initialize_stubs()

                # Mock the system state for testing
                cycle_result = await self.integration_layer.process_recursive_cycle(self.test_system_state)

                # Verify cycle structure
                required_keys = [
                    'cycle_duration', 'consciousness_state', 'predictions',
                    'pattern_match', 'intent_recommendation', 'memory_operations',
                    'integrated_decision', 'efficiency_score'
                ]

                for key in required_keys:
                    self.assertIn(key, cycle_result)

                # Verify integrated decision structure
                decision = cycle_result['integrated_decision']
                decision_keys = [
                    'primary_action', 'confidence_score', 'recommended_improvements',
                    'risk_assessment', 'next_steps'
                ]

                for key in decision_keys:
                    self.assertIn(key, decision)

    def test_cycle_efficiency_calculation(self):
        """Test cycle efficiency calculation"""
        # Reset stats
        self.integration_layer.integration_stats = {
            'patterns_processed': 5,
            'predictions_made': 5,
            'consciousness_transitions': 5,
            'memory_operations': 5,
            'integration_efficiency': 0.0
        }

        efficiency = self.integration_layer._calculate_cycle_efficiency()

        # 20 successful ops / (20 * 1.2) = 20/24 = 0.833
        expected = 20 / 24  # 0.833

        self.assertAlmostEqual(efficiency, expected, places=3)

    def test_integration_status_report(self):
        """Test integration status reporting"""
        status = self.integration_layer.get_integration_status()

        required_keys = ['integration_active', 'components', 'statistics', 'wsp_compliance']

        for key in required_keys:
            self.assertIn(key, status)

        # Verify WSP compliance reporting
        wsp_compliance = status['wsp_compliance']
        expected_protocols = ['WSP_48', 'WSP_69', 'WSP_25', 'WSP_60', 'WSP_67']

        for protocol in expected_protocols:
            self.assertIn(protocol, wsp_compliance)

    def test_zero_operations_efficiency(self):
        """Test efficiency calculation with zero operations"""
        self.integration_layer.integration_stats = {
            'patterns_processed': 0,
            'predictions_made': 0,
            'consciousness_transitions': 0,
            'memory_operations': 0,
            'integration_efficiency': 0.0
        }

        efficiency = self.integration_layer._calculate_cycle_efficiency()
        self.assertEqual(efficiency, 0.0)


class TestIntegrationRobustness(unittest.TestCase):
    """Test integration layer robustness and error handling"""

    def setUp(self):
        """Set up test fixtures"""
        if not WRE_INTEGRATION_AVAILABLE:
            self.skipTest("WRE autonomous integration not available")

        self.integration_layer = AutonomousIntegrationLayer()

    def test_missing_autonomous_components(self):
        """Test behavior when autonomous components are unavailable"""
        # Force stub initialization
        self.integration_layer._initialize_stubs()
        self.integration_layer.autonomous_available = False

        # Should still function with stubs
        status = self.integration_layer.get_integration_status()
        self.assertFalse(status['integration_active'])

        # Components should still exist as stubs
        self.assertIsNotNone(self.integration_layer.qrpe)
        self.assertIsNotNone(self.integration_layer.aire)

    def test_invalid_system_state_handling(self):
        """Test handling of invalid or incomplete system state"""
        invalid_state = {}  # Empty state

        # Should handle gracefully
        confidence = self.integration_layer._calculate_pattern_confidence([])
        self.assertEqual(confidence, 0.5)

        # Test with None predictions
        confidence = self.integration_layer._calculate_pattern_confidence(None)
        self.assertEqual(confidence, 0.5)

    def test_extreme_confidence_values(self):
        """Test handling of extreme confidence values"""
        predictions = [
            {'confidence': 1.5},  # Above max
            {'confidence': -0.5}  # Below min
        ]

        confidence = self.integration_layer._calculate_pattern_confidence(predictions)
        # Should be clamped to valid range
        self.assertGreaterEqual(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


if __name__ == '__main__':
    print("🧪 WRE Autonomous Integration Test Suite")
    print("=" * 50)

    if WRE_INTEGRATION_AVAILABLE:
        unittest.main(verbosity=2)
    else:
        print("❁EWRE autonomous integration not available")
        print("💡 Ensure WRE recursive improvement module is properly installed")
        sys.exit(1)
