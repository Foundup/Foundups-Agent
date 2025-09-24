"""
Tests for AI Intelligence Core module.

WSP Compliance: WSP 5 (Testing Standards), WSP 6 (Test Validation)
"""

import pytest
from modules.ai_intelligence.src.ai_intelligence import AIIntelligenceCore, create_ai_intelligence_core


class TestAIIntelligenceCore:
    """Test cases for AIIntelligenceCore class."""

    def test_initialization(self):
        """Test AI Intelligence Core initialization."""
        core = AIIntelligenceCore()

        assert core.consciousness_level == 0.0
        assert core.learning_enabled is True
        assert core.multi_agent_coordination is True

    def test_process_compliance_request(self):
        """Test processing WSP compliance requests."""
        core = AIIntelligenceCore()

        input_data = {
            'intent': 'wsp_compliance',
            'context': {'module': 'test_module'}
        }

        result = core.process_consciousness_input(input_data)

        assert result['recommendation'] == 'ENHANCE_EXISTING_MODULE'
        assert result['wsp_reference'] == 'WSP_84'
        assert result['confidence'] == 0.95
        assert 'reasoning' in result

    def test_process_module_request(self):
        """Test processing module creation requests."""
        core = AIIntelligenceCore()

        input_data = {
            'intent': 'module_creation',
            'context': {'name': 'new_module'}
        }

        result = core.process_consciousness_input(input_data)

        assert result['recommendation'] == 'CHECK_EXISTENCE_FIRST'
        assert result['wsp_reference'] == 'WSP_50'
        assert result['confidence'] == 0.98

    def test_process_general_request(self):
        """Test processing general intelligence requests."""
        core = AIIntelligenceCore()

        input_data = {
            'intent': 'unknown_intent',
            'context': {}
        }

        result = core.process_consciousness_input(input_data)

        assert result['recommendation'] == 'SEARCH_FIRST'
        assert result['wsp_reference'] == 'WSP_1'
        assert result['confidence'] == 0.90

    def test_update_consciousness_success(self):
        """Test consciousness level update on success."""
        core = AIIntelligenceCore()
        initial_level = core.consciousness_level

        experience = {
            'success': True,
            'complexity': 0.8
        }

        new_level = core.update_consciousness_level(experience)

        assert new_level > initial_level
        assert new_level <= 1.0

    def test_update_consciousness_failure(self):
        """Test consciousness level update on failure."""
        core = AIIntelligenceCore()
        core.consciousness_level = 0.5  # Set initial level
        initial_level = core.consciousness_level

        experience = {
            'success': False,
            'complexity': 0.5
        }

        new_level = core.update_consciousness_level(experience)

        assert new_level < initial_level
        assert new_level >= 0.0

    def test_update_consciousness_learning_disabled(self):
        """Test consciousness level when learning is disabled."""
        core = AIIntelligenceCore()
        core.learning_enabled = False
        initial_level = core.consciousness_level

        experience = {
            'success': True,
            'complexity': 0.9
        }

        new_level = core.update_consciousness_level(experience)

        assert new_level == initial_level

    def test_get_intelligence_status(self):
        """Test getting intelligence system status."""
        core = AIIntelligenceCore()

        status = core.get_intelligence_status()

        assert 'consciousness_level' in status
        assert 'learning_enabled' in status
        assert 'multi_agent_coordination' in status
        assert 'status' in status
        assert status['status'] == 'active'

    def test_factory_function(self):
        """Test factory function creates valid instance."""
        core = create_ai_intelligence_core()

        assert isinstance(core, AIIntelligenceCore)
        assert core.consciousness_level == 0.0
        assert core.learning_enabled is True


# Integration tests
class TestAIIntelligenceIntegration:
    """Integration tests for AI Intelligence Core."""

    def test_end_to_end_workflow(self):
        """Test complete workflow from input to learning."""
        core = AIIntelligenceCore()

        # Process a request
        input_data = {
            'intent': 'wsp_compliance',
            'context': {'check': 'module_structure'}
        }

        result = core.process_consciousness_input(input_data)
        assert result['recommendation'] == 'ENHANCE_EXISTING_MODULE'

        # Learn from the experience
        experience = {
            'success': True,
            'complexity': 0.8,
            'context': 'compliance_check'
        }

        new_level = core.update_consciousness_level(experience)
        assert new_level > 0.0

        # Check status reflects learning
        status = core.get_intelligence_status()
        assert status['consciousness_level'] == new_level

    def test_adaptive_learning(self):
        """Test that the system adapts based on experiences."""
        core = AIIntelligenceCore()

        # Start with base level
        initial_level = core.consciousness_level

        # Multiple successful experiences
        for i in range(3):
            experience = {
                'success': True,
                'complexity': 0.8
            }
            core.update_consciousness_level(experience)

        # Level should have increased
        final_level = core.consciousness_level
        assert final_level > initial_level

        # Multiple failures should decrease level
        for i in range(2):
            experience = {
                'success': False,
                'complexity': 0.5
            }
            core.update_consciousness_level(experience)

        # Level should have decreased
        decreased_level = core.consciousness_level
        assert decreased_level < final_level
