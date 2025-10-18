#!/usr/bin/env python3
"""
FMAS Validation Tests for WSP 91: Daemon Observability Protocol

Tests the DaemonLogger class to ensure:
- JSON format is parseable
- All log types function correctly
- Session tracking works
- Performance metrics are captured
- Error logging includes full context

WSP Compliance:
- WSP 4: FMAS Validation Protocol
- WSP 91: DAEMON Observability Protocol
- WSP 5: Test Coverage (target: 90%+)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import json
import time
import pytest
from pathlib import Path
import sys

# Add repo root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from holo_index.qwen_advisor.orchestration.autonomous_refactoring import DaemonLogger


class TestDaemonLoggerWSP91:
    """FMAS validation tests for WSP 91 Daemon Observability"""

    def setup_method(self):
        """Setup test fixtures"""
        self.logger = DaemonLogger("TestComponent")
        self.test_start = time.time()

    def test_daemon_logger_initialization(self):
        """Test DaemonLogger initializes correctly"""
        assert self.logger.component == "TestComponent"
        assert self.logger.session_start > 0
        assert isinstance(self.logger.session_start, float)

    def test_log_decision_json_format(self):
        """Test decision logging produces valid JSON"""
        log_entry = self.logger.log_decision(
            decision_type="test_decision",
            chosen_path="path_a",
            confidence=0.95,
            reasoning="Test reasoning for decision",
            extra_data="test_value"
        )

        # Validate structure
        assert log_entry["component"] == "TestComponent"
        assert log_entry["event_type"] == "DECISION"
        assert log_entry["decision_type"] == "test_decision"
        assert log_entry["chosen_path"] == "path_a"
        assert log_entry["confidence"] == 0.95
        assert "timestamp" in log_entry
        assert "session_time" in log_entry
        assert log_entry["extra_data"] == "test_value"

        # Validate JSON serializability
        json_str = json.dumps(log_entry)
        assert json.loads(json_str) == log_entry

    def test_log_llm_inference_metrics(self):
        """Test LLM inference logging captures performance metrics"""
        log_entry = self.logger.log_llm_inference(
            llm_name="Qwen-1.5B",
            prompt_size=512,
            response_size=48,
            inference_time_ms=245.3,
            tokens_generated=12,
            task="test_inference"
        )

        # Validate structure
        assert log_entry["event_type"] == "LLM_INFERENCE"
        assert log_entry["llm_name"] == "Qwen-1.5B"
        assert log_entry["prompt_size"] == 512
        assert log_entry["response_size"] == 48
        assert log_entry["inference_time_ms"] == 245.3
        assert log_entry["tokens_generated"] == 12
        assert log_entry["task"] == "test_inference"

        # Validate tokens_per_second calculation
        expected_tps = 12 / (245.3 / 1000)
        assert abs(log_entry["tokens_per_second"] - expected_tps) < 0.01

        # Validate JSON serializability
        json_str = json.dumps(log_entry)
        assert json.loads(json_str) is not None

    def test_log_routing_decision(self):
        """Test routing decision logging"""
        log_entry = self.logger.log_routing(
            task_description="Analyze test file for WSP violations",
            routing_method="gemma_llm",
            routing_confidence=0.85,
            routing_reasoning="Small file, binary decision sufficient",
            file_path="/path/to/file.py",
            file_size=3742
        )

        # Validate structure
        assert log_entry["event_type"] == "ROUTING"
        assert log_entry["method"] == "gemma_llm"
        assert log_entry["confidence"] == 0.85
        assert "task" in log_entry
        assert log_entry["file_path"] == "/path/to/file.py"
        assert log_entry["file_size"] == 3742

        # Validate JSON serializability
        assert json.dumps(log_entry) is not None

    def test_log_error_with_context(self):
        """Test error logging includes full context"""
        context = {
            "module_path": "/test/path.py",
            "line_number": 42,
            "operation": "test_operation"
        }

        log_entry = self.logger.log_error(
            error_type="test_error",
            error_message="Test error message with details",
            context=context,
            recoverable=True,
            additional_info="extra_data"
        )

        # Validate structure
        assert log_entry["event_type"] == "ERROR"
        assert log_entry["error_type"] == "test_error"
        assert "Test error message" in log_entry["error_message"]
        assert log_entry["context"] == context
        assert log_entry["recoverable"] is True
        assert log_entry["additional_info"] == "extra_data"

        # Validate JSON serializability
        assert json.dumps(log_entry) is not None

    def test_log_performance_metrics(self):
        """Test performance logging calculates throughput"""
        log_entry = self.logger.log_performance(
            operation="module_dependency_analysis",
            duration_ms=312.5,
            items_processed=5,
            success=True,
            module_count=3
        )

        # Validate structure
        assert log_entry["event_type"] == "PERFORMANCE"
        assert log_entry["operation"] == "module_dependency_analysis"
        assert log_entry["duration_ms"] == 312.5
        assert log_entry["items_processed"] == 5
        assert log_entry["success"] is True

        # Validate throughput calculation
        expected_throughput = 5 / (312.5 / 1000)
        assert abs(log_entry["throughput"] - expected_throughput) < 0.01

        # Validate JSON serializability
        assert json.dumps(log_entry) is not None

    def test_session_time_tracking(self):
        """Test session_time increases over time"""
        time.sleep(0.1)  # Wait 100ms

        log_entry1 = self.logger.log_decision(
            decision_type="test1",
            chosen_path="path1",
            confidence=0.9,
            reasoning="First decision"
        )

        time.sleep(0.1)  # Wait another 100ms

        log_entry2 = self.logger.log_decision(
            decision_type="test2",
            chosen_path="path2",
            confidence=0.8,
            reasoning="Second decision"
        )

        # Validate session_time increases
        assert log_entry2["session_time"] > log_entry1["session_time"]
        assert log_entry2["session_time"] >= 0.2  # At least 200ms elapsed

    def test_string_truncation(self):
        """Test long strings are truncated to prevent log bloat"""
        long_reasoning = "A" * 500  # 500 character string

        log_entry = self.logger.log_decision(
            decision_type="test_truncation",
            chosen_path="path",
            confidence=0.9,
            reasoning=long_reasoning
        )

        # Validate truncation
        assert len(log_entry["reasoning"]) == 200  # Truncated to 200 chars
        assert log_entry["reasoning"] == "A" * 200

    def test_long_error_message_truncation(self):
        """Test long error messages are truncated"""
        long_error = "Error: " + ("X" * 600)

        log_entry = self.logger.log_error(
            error_type="test_error",
            error_message=long_error,
            context={}
        )

        # Validate truncation
        assert len(log_entry["error_message"]) == 500  # Truncated to 500 chars

    def test_metadata_kwargs_support(self):
        """Test **kwargs metadata is captured in all log types"""
        # Test with decision
        log_entry = self.logger.log_decision(
            decision_type="test",
            chosen_path="path",
            confidence=0.9,
            reasoning="test",
            custom_field_1="value1",
            custom_field_2=42,
            custom_field_3=True
        )

        assert log_entry["custom_field_1"] == "value1"
        assert log_entry["custom_field_2"] == 42
        assert log_entry["custom_field_3"] is True

    def test_zero_duration_performance(self):
        """Test performance logging handles zero duration gracefully"""
        log_entry = self.logger.log_performance(
            operation="instant_operation",
            duration_ms=0.0,
            items_processed=10,
            success=True
        )

        # Validate throughput calculation doesn't crash
        assert "throughput" in log_entry
        # Should handle division by zero gracefully

    def test_json_special_characters(self):
        """Test JSON escaping of special characters"""
        special_chars = 'Test "quotes" and \n newlines \t tabs'

        log_entry = self.logger.log_error(
            error_type="special_chars_test",
            error_message=special_chars,
            context={"field": special_chars}
        )

        # Validate JSON serializability with special chars
        json_str = json.dumps(log_entry)
        parsed = json.loads(json_str)
        assert parsed["error_message"] == special_chars
        assert parsed["context"]["field"] == special_chars


class TestDaemonLoggerIntegration:
    """Integration tests for daemon observability"""

    def test_full_workflow_logging(self):
        """Test complete workflow produces valid JSON logs"""
        logger = DaemonLogger("IntegrationTest")

        # Simulate LLM initialization
        init_log = logger.log_performance(
            operation="qwen_initialization",
            duration_ms=1234.5,
            success=True,
            model_path="/path/to/model.gguf"
        )

        # Simulate routing decision
        routing_log = logger.log_routing(
            task_description="Analyze test file",
            routing_method="gemma_llm",
            routing_confidence=0.85,
            routing_reasoning="Small file, binary decision"
        )

        # Simulate LLM inference
        inference_log = logger.log_llm_inference(
            llm_name="Qwen-1.5B",
            prompt_size=512,
            response_size=48,
            inference_time_ms=245.3,
            tokens_generated=12
        )

        # Simulate error
        error_log = logger.log_error(
            error_type="test_error",
            error_message="Simulated error",
            context={"test": True},
            recoverable=True
        )

        # Validate all logs are JSON serializable
        logs = [init_log, routing_log, inference_log, error_log]
        for log in logs:
            json_str = json.dumps(log)
            assert json.loads(json_str) is not None

        # Validate session_time progresses across logs
        assert routing_log["session_time"] >= init_log["session_time"]
        assert inference_log["session_time"] >= routing_log["session_time"]
        assert error_log["session_time"] >= inference_log["session_time"]


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
