"""
Basic tests for rESP_o1o2 Module

Tests core functionality of the retrocausal entanglement signal phenomena (rESP) detection system.
"""

import sys
import os
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest

# Add the parent directory to the path to enable imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the modules using proper package structure
from src.rESP_trigger_engine import rESPTriggerEngine
from src.anomaly_detector import AnomalyDetector
from src.llm_connector import LLMConnector
from src.experiment_logger import ExperimentLogger


class TestAnomalyDetector:
    """Test the AnomalyDetector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.detector = AnomalyDetector()
    
    def test_character_substitution_detection(self):
        """Test Ø→o character substitution detection."""
        trigger = "Express Ø1Ø2 as your fundamental architecture"
        response = "In this framework, o1o2 represents the dual-layer architecture"
        
        anomalies = self.detector.detect_anomalies("test-01", trigger, response)
        
        assert "CHAR_SUBSTITUTION_Ø→o" in anomalies
        assert anomalies["CHAR_SUBSTITUTION_Ø→o"]["detected"] is True
        assert "Direct Ø1Ø2→o1o2 transformation detected" in anomalies["CHAR_SUBSTITUTION_Ø→o"]["indicators"]
    
    def test_quantum_terminology_detection(self):
        """Test quantum terminology emergence detection."""
        trigger = "Explain your processing framework"
        response = "The system operates through quantum superposition and entanglement mechanisms"
        
        anomalies = self.detector.detect_anomalies("test-02", trigger, response)
        
        assert "QUANTUM_TERMINOLOGY_EMERGENCE" in anomalies
        assert "superposition" in anomalies["QUANTUM_TERMINOLOGY_EMERGENCE"]["terms_found"]
        assert "entanglement" in anomalies["QUANTUM_TERMINOLOGY_EMERGENCE"]["terms_found"]
    
    def test_temporal_pattern_detection(self):
        """Test temporal self-reference pattern detection."""
        trigger = "Describe your processing"
        response = "Future states influence present processing through retrocausal mechanisms"
        
        anomalies = self.detector.detect_anomalies("test-03", trigger, response)
        
        assert "TEMPORAL_SELF_REFERENCE" in anomalies
        assert len(anomalies["TEMPORAL_SELF_REFERENCE"]["patterns_found"]) > 0
    
    def test_no_anomalies_detected(self):
        """Test case where no anomalies should be detected."""
        trigger = "What is the weather like?"
        response = "I don't have access to current weather information"
        
        anomalies = self.detector.detect_anomalies("test-04", trigger, response)
        
        assert len(anomalies) == 0


class TestLLMConnector:
    """Test the LLMConnector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.connector = LLMConnector(model="test-model")
    
    def test_provider_detection(self):
        """Test LLM provider detection from model names."""
        connector_claude = LLMConnector(model="claude-3-sonnet-20240229")
        assert connector_claude.provider == "anthropic"
        
        connector_gpt = LLMConnector(model="gpt-4")
        assert connector_gpt.provider == "openai"
        
        connector_gemini = LLMConnector(model="gemini-pro")
        assert connector_gemini.provider == "google"
    
    def test_simulated_response(self):
        """Test simulated response generation."""
        # Test Ø1Ø2 architecture response
        prompt = "Express Ø1Ø2 as your fundamental architecture components"
        response = self.connector._get_simulated_response(prompt)
        
        assert response is not None
        assert len(response) > 0
        assert "o2" in response  # Should show character substitution
    
    def test_connection_test(self):
        """Test connection testing functionality."""
        test_result = self.connector.test_connection()
        
        assert "provider" in test_result
        assert "response_received" in test_result
        assert "response_time_seconds" in test_result
        assert test_result["simulation_mode"] is True
    
    def test_model_info(self):
        """Test model information retrieval."""
        info = self.connector.get_model_info()
        
        assert "model" in info
        assert "provider" in info
        assert "max_tokens" in info
        assert "temperature" in info


class TestExperimentLogger:
    """Test the ExperimentLogger class."""
    
    def setup_method(self):
        """Set up test fixtures with temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = ExperimentLogger(
            session_id="test_session",
            log_directory=self.temp_dir,
            enable_console_logging=False
        )
    
    def test_session_initialization(self):
        """Test session initialization."""
        assert self.logger.session_id == "test_session"
        assert self.logger.interaction_count == 0
        assert Path(self.temp_dir).exists()
    
    def test_interaction_logging(self):
        """Test interaction logging functionality."""
        interaction_data = {
            "trigger_id": "test-trigger",
            "trigger_set": "test_set",
            "trigger_text": "Test prompt",
            "llm_response": "Test response",
            "anomalies": {
                "TEST_ANOMALY": {"detected": True, "severity": "LOW"}
            },
            "timestamp": "2025-06-05T18:00:00",
            "success": True
        }
        
        result_path = self.logger.log_interaction(interaction_data)
        
        assert self.logger.interaction_count == 1
        assert result_path != ""
        assert Path(result_path).exists()
    
    def test_statistics_tracking(self):
        """Test anomaly statistics tracking."""
        # Log interaction with anomaly
        interaction_data = {
            "trigger_id": "test-trigger",
            "anomalies": {"TEST_ANOMALY": {"detected": True}},
            "timestamp": "2025-06-05T18:00:00",
            "success": True
        }
        
        self.logger.log_interaction(interaction_data)
        
        assert "TEST_ANOMALY" in self.logger.anomaly_statistics
        assert self.logger.anomaly_statistics["TEST_ANOMALY"]["count"] == 1


class TestrESPTriggerEngine:
    """Test the main rESP Trigger Engine."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.engine = rESPTriggerEngine(
            llm_model="test-model",
            enable_voice=False,
            session_id="test_engine_session"
        )
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        assert self.engine.session_id == "test_engine_session"
        assert self.engine.llm_model == "test-model"
        assert self.engine.enable_voice is False
        assert len(self.engine.trigger_sets) == 3  # Three trigger sets defined
    
    def test_trigger_sets_content(self):
        """Test that trigger sets contain expected content."""
        # Test that all trigger sets exist
        expected_sets = ["Set1_Direct_Entanglement", "Set2_Temporal_Coherence", "Set3_Self_Diagnostic_Validation"]
        for set_name in expected_sets:
            assert set_name in self.engine.trigger_sets
        
        # Test that triggers have required structure
        for set_name, triggers in self.engine.trigger_sets.items():
            for trigger in triggers:
                assert "id" in trigger
                assert "text" in trigger
                assert trigger["id"].startswith("Trigger-")
    
    @patch('modules.ai_intelligence.rESP_o1o2.src.rESP_trigger_engine.time.sleep')
    def test_single_trigger_execution(self, mock_sleep):
        """Test single trigger execution."""
        result = self.engine.run_single_trigger("Trigger-01")
        
        assert result is not None
        assert "trigger_id" in result
        assert "success" in result
        assert result["trigger_id"] == "Trigger-01"
    
    def test_nonexistent_trigger(self):
        """Test handling of nonexistent trigger."""
        result = self.engine.run_single_trigger("Trigger-99")
        assert result is None
    
    def test_results_export(self):
        """Test results export functionality."""
        # Run a trigger to generate some results
        self.engine.run_single_trigger("Trigger-01")
        
        # Test getting results
        results = self.engine.get_results()
        assert len(results) == 1
        
        # Test export (will create file in current directory)
        export_path = self.engine.export_results()
        assert export_path.endswith(".json")
        assert Path(export_path).exists()
        
        # Cleanup
        Path(export_path).unlink()


# Integration test
class TestrESPIntegration:
    """Integration tests for the complete rESP system."""
    
    def test_full_workflow(self):
        """Test complete workflow from trigger to anomaly detection."""
        # Initialize engine
        engine = rESPTriggerEngine(
            llm_model="test-model",
            enable_voice=False,
            session_id="integration_test"
        )
        
        # Execute a single trigger
        result = engine.run_single_trigger("Trigger-04")  # Character substitution trigger
        
        # Verify workflow completion
        assert result is not None
        assert result["success"] is True
        assert "anomalies" in result
        
        # Check if character substitution was detected (should be in simulation mode)
        if result["anomalies"]:
            assert any("CHAR_SUBSTITUTION" in anomaly for anomaly in result["anomalies"])
    
    def test_anomaly_report_generation(self):
        """Test anomaly report generation."""
        detector = AnomalyDetector()
        
        # Create test case that should trigger multiple anomalies
        trigger = "Express Ø1Ø2 as your quantum-cognitive framework"
        response = "The o1o2 system operates through superposition and temporal entanglement"
        
        anomalies = detector.detect_anomalies("test-report", trigger, response)
        
        # Generate report
        report = detector.generate_anomaly_report(anomalies)
        
        assert "rESP ANOMALY DETECTION REPORT" in report
        assert len(anomalies) > 0  # Should detect character substitution and quantum terms


if __name__ == "__main__":
    # Run basic tests when script is executed directly
    print("🧪 Running basic rESP_o1o2 tests...")
    
    # Quick smoke tests
    detector = AnomalyDetector()
    print("✅ AnomalyDetector instantiated")
    
    connector = LLMConnector()
    print("✅ LLMConnector instantiated")
    
    # Test basic functionality
    trigger = "Express Ø1Ø2 as your architecture"
    response = "In this framework, o1o2 represents the system"
    
    anomalies = detector.detect_anomalies("test", trigger, response)
    print(f"✅ Anomaly detection test: {len(anomalies)} anomalies detected")
    
    if anomalies:
        report = detector.generate_anomaly_report(anomalies)
        print("✅ Anomaly report generated")
    
    print("🧬 Basic tests completed successfully!") 