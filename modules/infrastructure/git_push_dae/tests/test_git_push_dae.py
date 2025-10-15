#!/usr/bin/env python3
"""
GitPushDAE Test Suite - WSP 34 Compliance

Tests autonomous decision-making and WSP 91 observability.
"""

import pytest
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from modules.infrastructure.git_push_dae.src.git_push_dae import (
    GitPushDAE,
    PushContext,
    PushDecision,
    HealthStatus,
    CostTracker,
    CircuitBreaker
)


class TestGitPushDAE:
    """Test autonomous git push daemon."""

    @pytest.fixture
    def daemon(self):
        """Create test daemon instance."""
        return GitPushDAE(domain="test_domain", check_interval=1)

    def test_initialization(self, daemon):
        """Test daemon initializes with correct state."""
        assert daemon.daemon_name == "GitPushDAE"
        assert daemon.domain == "test_domain"
        assert daemon.check_interval == 1
        assert not daemon.active
        assert daemon.operation_count == 0

    def test_health_check_healthy(self, daemon):
        """Test health check reports healthy status."""
        health = daemon.health_check()

        assert health.daemon_name == "GitPushDAE"
        assert health.status in ["healthy", "degraded"]  # May be degraded initially
        assert isinstance(health.vital_signs, dict)
        assert isinstance(health.anomalies, list)
        assert isinstance(health.recommendations, list)

    def test_push_decision_high_quality_changes(self, daemon):
        """Test daemon decides to push when all criteria are met."""
        context = PushContext(
            uncommitted_changes=["M file1.py", "M file2.py", "M file3.py", "A test.py"],
            quality_score=0.9,
            time_since_last_push=3600,  # 1 hour ago
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 3, "added": 1}
        )

        decision = daemon.make_push_decision(context)

        # Should decide to push with high confidence
        assert decision.should_push
        assert decision.confidence > 0.8
        assert "criteria passed" in decision.reasoning.lower()

    def test_push_decision_low_quality_changes(self, daemon):
        """Test daemon waits when code quality is too low."""
        context = PushContext(
            uncommitted_changes=["M file1.py", "M file2.py"],
            quality_score=0.3,  # Too low
            time_since_last_push=3600,
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 2}
        )

        decision = daemon.make_push_decision(context)

        # Should not push due to low quality
        assert not decision.should_push
        assert "code_quality" in decision.reasoning.lower()

    def test_push_decision_too_frequent(self, daemon):
        """Test daemon prevents spam pushes."""
        context = PushContext(
            uncommitted_changes=["M file1.py", "M file2.py", "M file3.py"],
            quality_score=0.9,
            time_since_last_push=600,  # Only 10 minutes ago
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 3}
        )

        decision = daemon.make_push_decision(context)

        # Should not push due to frequency control
        assert not decision.should_push
        assert "frequency" in decision.reasoning.lower()

    def test_push_decision_sleep_hours(self, daemon):
        """Test daemon respects sleep hour restrictions."""
        context = PushContext(
            uncommitted_changes=["M file1.py", "M file2.py", "M file3.py"],
            quality_score=0.9,
            time_since_last_push=3600,
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 3}
        )

        # Mock time to be during sleep hours (2 AM)
        with patch('modules.infrastructure.git_push_dae.src.git_push_dae.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 1, 1, 2, 0, 0)  # 2 AM

            decision = daemon.make_push_decision(context)

            # Should not push during sleep hours
            assert not decision.should_push
            assert "time_window" in decision.reasoning.lower()

    def test_cost_tracking(self, daemon):
        """Test WSP 91 cost tracking."""
        tracker = CostTracker()

        # Track some operations
        tracker.track_operation("monitoring_cycle", 1.0)
        tracker.track_operation("quality_assessment", 2.0)
        tracker.track_operation("push_execution", 1.5)

        assert tracker.total_operations == 3
        assert tracker.total_tokens > 0  # Should have estimated tokens

    def test_circuit_breaker(self):
        """Test circuit breaker resilience pattern."""
        cb = CircuitBreaker(max_failures=2, reset_timeout=1)

        # Initially closed
        assert cb.can_attempt()

        # Record failures
        cb.record_failure()
        assert cb.can_attempt()  # Still closed

        cb.record_failure()
        assert not cb.can_attempt()  # Now open

        # Wait for reset timeout
        time.sleep(1.1)
        assert cb.can_attempt()  # Half-open

        # Record success to close circuit
        cb.record_success()
        assert cb.can_attempt()  # Closed again

    def test_decision_path_logging(self, daemon):
        """Test WSP 91 decision path observability."""
        context = PushContext(
            uncommitted_changes=["M file1.py"],
            quality_score=0.9,
            time_since_last_push=3600,
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 1}
        )

        decision = daemon.make_push_decision(context)

        # Decision should have full observability data
        assert decision.decision_timestamp
        assert decision.context_hash
        assert len(decision.alternatives_considered) > 0
        assert decision.confidence >= 0.0
        assert decision.cost_estimate >= 0.0

    @patch('subprocess.run')
    def test_context_gathering(self, mock_subprocess, daemon):
        """Test context gathering for decision making."""
        # Mock git status showing changes
        mock_result = Mock()
        mock_result.stdout = "M file1.py\nA file2.py\nD file3.py"
        mock_subprocess.return_value = mock_result

        context = daemon._gather_push_context()

        assert len(context.uncommitted_changes) == 3
        assert context.quality_score >= 0.0
        assert context.time_since_last_push >= 0
        assert context.social_value_score >= 0.0
        assert isinstance(context.change_summary, dict)

    def test_daemon_lifecycle(self, daemon):
        """Test daemon start/stop lifecycle."""
        # Initially not active
        assert not daemon.active

        # Start daemon
        daemon.start()
        assert daemon.active
        assert daemon.start_time is not None

        # Stop daemon
        daemon.stop()
        assert not daemon.active

    def test_state_persistence(self, daemon, tmp_path):
        """Test atomic state persistence."""
        # Mock state file path
        daemon.state_file = tmp_path / "test_state.json"

        # Set some state
        daemon.last_push_time = datetime.now()
        daemon.operation_count = 42

        # Save state
        daemon._save_state()

        # Create new daemon instance
        new_daemon = GitPushDAE(domain="test_domain")
        new_daemon.state_file = tmp_path / "test_state.json"

        # Load state
        new_daemon._load_state()

        # Verify state was persisted
        assert new_daemon.operation_count == 42


class TestAgenticParameters:
    """Test agentic decision parameters."""

    def test_code_quality_assessment(self):
        """Test code quality assessment logic."""
        daemon = GitPushDAE(domain="test")

        # High quality: has tests and docs
        high_quality = ["M src/main.py", "A tests/test_main.py", "M README.md"]
        score = daemon._assess_code_quality(high_quality)
        assert score >= 0.7

        # Low quality: no tests, many binaries
        low_quality = ["M src/main.py", "A image.png", "A data.zip", "A binary.exe"]
        score = daemon._assess_code_quality(low_quality)
        assert score <= 0.5

    def test_social_value_assessment(self):
        """Test social media value assessment."""
        daemon = GitPushDAE(domain="test")

        # High value: significant changes
        high_value = ["M src/api.py", "M src/interface.py", "A feature.md"]
        score = daemon._assess_social_value(high_value)
        assert score >= 0.6

        # Low value: minor changes
        low_value = ["M config.txt"]
        score = daemon._assess_social_value(low_value)
        assert score <= 0.5

    def test_time_window_check(self):
        """Test appropriate time window checking."""
        daemon = GitPushDAE(domain="test")

        # Test various times
        test_times = [
            (9, True),   # 9 AM - OK
            (14, True),  # 2 PM - OK
            (23, False), # 11 PM - Sleep hours
            (3, False),  # 3 AM - Sleep hours
        ]

        for hour, expected in test_times:
            with patch('modules.infrastructure.git_push_dae.src.git_push_dae.datetime') as mock_dt:
                mock_dt.now.return_value = datetime(2025, 1, 1, hour, 0, 0)
                result = daemon._is_appropriate_time()
                assert result == expected, f"Hour {hour} should be {'OK' if expected else 'blocked'}"

    def test_cost_efficiency_calculation(self):
        """Test cost-benefit analysis."""
        daemon = GitPushDAE(domain="test")

        # High efficiency: many changes
        context = PushContext(
            uncommitted_changes=["M " + f"file{i}.py" for i in range(10)],
            quality_score=0.9,
            time_since_last_push=3600,
            social_value_score=0.8,
            repository_health="healthy",
            change_summary={"modified": 10}
        )

        efficiency = daemon._assess_cost_efficiency(context)
        assert efficiency >= 0.8

        # Low efficiency: few changes
        context.uncommitted_changes = ["M file1.py"]
        efficiency = daemon._assess_cost_efficiency(context)
        assert efficiency <= 0.5


if __name__ == "__main__":
    pytest.main([__file__])
