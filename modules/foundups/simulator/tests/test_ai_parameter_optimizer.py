"""Tests for AI Parameter Optimizer (OpenClaw + GPT integration)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import pytest

from modules.foundups.simulator.config import SimulatorConfig
from modules.foundups.simulator.economics.ai_parameter_optimizer import (
    AIParameterOptimizer,
    MockAIGateway,
    OptimizationObjective,
    OptimizerConfig,
    ParameterBounds,
    TUNABLE_PARAMETERS,
)


class TestParameterBounds:
    """Test parameter bounds and validation."""

    def test_tunable_parameters_defined(self) -> None:
        """All tunable parameters should be defined with bounds."""
        assert len(TUNABLE_PARAMETERS) >= 5
        for param in TUNABLE_PARAMETERS:
            assert param.min_value < param.max_value
            assert param.step > 0
            assert param.description

    def test_parameter_bounds_match_config(self) -> None:
        """Parameter names should exist in SimulatorConfig."""
        config = SimulatorConfig()
        for param in TUNABLE_PARAMETERS:
            assert hasattr(config, param.param_name), f"Missing: {param.param_name}"


class TestMockAIGateway:
    """Test mock gateway for offline testing."""

    def test_mock_returns_valid_response(self) -> None:
        """Mock should return parseable response."""
        mock = MockAIGateway()
        result = mock.call_with_fallback("test prompt", "analysis")

        assert result.success
        assert "ANALYSIS:" in result.response
        assert "RECOMMENDATIONS:" in result.response

    def test_mock_recommendations_parseable(self) -> None:
        """Mock recommendations should be valid JSON."""
        mock = MockAIGateway()
        result = mock.call_with_fallback("test", "analysis")

        # Extract JSON from response
        rec_start = result.response.index("RECOMMENDATIONS:") + len("RECOMMENDATIONS:")
        rec_str = result.response[rec_start:].strip()
        json_start = rec_str.index("{")
        json_end = rec_str.rindex("}") + 1
        json_str = rec_str[json_start:json_end]

        parsed = json.loads(json_str)
        assert isinstance(parsed, dict)


class TestAIParameterOptimizer:
    """Test optimizer core functionality."""

    def test_optimizer_init_with_mock(self) -> None:
        """Optimizer should initialize with mock gateway."""
        optimizer = AIParameterOptimizer(ai_gateway=MockAIGateway())
        assert optimizer._ai_gateway is not None
        assert isinstance(optimizer._ai_gateway, MockAIGateway)

    def test_config_to_dict(self) -> None:
        """Config should convert to dict of tunable params."""
        optimizer = AIParameterOptimizer()
        config = SimulatorConfig(agent_action_probability=0.5, stake_min=20)

        config_dict = optimizer._config_to_dict(config)

        assert "agent_action_probability" in config_dict
        assert config_dict["agent_action_probability"] == 0.5
        assert config_dict["stake_min"] == 20

    def test_dict_to_config(self) -> None:
        """Dict should convert back to SimulatorConfig."""
        optimizer = AIParameterOptimizer()
        config_dict = {
            "agent_action_probability": 0.7,
            "agent_cooldown_ticks": 10,
        }

        config = optimizer._dict_to_config(config_dict)

        assert config.agent_action_probability == 0.7
        assert config.agent_cooldown_ticks == 10

    def test_parse_gpt_response_valid(self) -> None:
        """Should parse valid GPT response."""
        optimizer = AIParameterOptimizer()
        response = (
            'ANALYSIS: The simulation shows good progress.\n'
            'RECOMMENDATIONS: {"agent_action_probability": 0.5, "stake_min": 15}'
        )

        analysis, recommendations = optimizer._parse_gpt_response(response)

        assert "good progress" in analysis
        assert recommendations["agent_action_probability"] == 0.5
        assert recommendations["stake_min"] == 15

    def test_parse_gpt_response_malformed(self) -> None:
        """Should handle malformed GPT response gracefully."""
        optimizer = AIParameterOptimizer()
        response = "This is not a valid response format"

        analysis, recommendations = optimizer._parse_gpt_response(response)

        assert analysis == ""
        assert recommendations == {}

    def test_apply_recommendations_within_bounds(self) -> None:
        """Recommendations should be clamped to bounds."""
        optimizer = AIParameterOptimizer()
        config = {"agent_action_probability": 0.3}
        recommendations = {"agent_action_probability": 1.5}  # Above max

        new_config = optimizer._apply_recommendations(config, recommendations)

        # Should be clamped to max (0.9)
        assert new_config["agent_action_probability"] <= 0.9

    def test_apply_recommendations_unknown_param(self) -> None:
        """Unknown parameters should be ignored."""
        optimizer = AIParameterOptimizer()
        config = {"agent_action_probability": 0.3}
        recommendations = {"unknown_param": 999}

        new_config = optimizer._apply_recommendations(config, recommendations)

        assert "unknown_param" not in new_config
        assert new_config["agent_action_probability"] == 0.3


class TestOptimizationObjectives:
    """Test different optimization objectives."""

    def test_all_objectives_defined(self) -> None:
        """All optimization objectives should be valid."""
        objectives = list(OptimizationObjective)
        assert len(objectives) >= 4
        assert OptimizationObjective.STAKER_DISTRIBUTION in objectives
        assert OptimizationObjective.ECOSYSTEM_GROWTH in objectives
        assert OptimizationObjective.TOKEN_VELOCITY in objectives
        assert OptimizationObjective.BALANCED in objectives

    def test_score_result_staker_distribution(self) -> None:
        """Staker distribution objective should weight Du pool ratio."""
        optimizer = AIParameterOptimizer(
            config=OptimizerConfig(objective=OptimizationObjective.STAKER_DISTRIBUTION)
        )

        # High Du pool ratio should score higher
        stats_high = {"du_pool_ratio": 0.8, "active_foundups": 10}
        stats_low = {"du_pool_ratio": 0.2, "active_foundups": 10}

        score_high = optimizer._score_result(0.8, stats_high)
        score_low = optimizer._score_result(0.8, stats_low)

        assert score_high > score_low

    def test_score_result_ecosystem_growth(self) -> None:
        """Ecosystem growth objective should weight FoundUp count."""
        optimizer = AIParameterOptimizer(
            config=OptimizerConfig(objective=OptimizationObjective.ECOSYSTEM_GROWTH)
        )

        # More FoundUps should score higher
        stats_high = {"active_foundups": 50, "du_pool_ratio": 0.5}
        stats_low = {"active_foundups": 5, "du_pool_ratio": 0.5}

        score_high = optimizer._score_result(0.8, stats_high)
        score_low = optimizer._score_result(0.8, stats_low)

        assert score_high > score_low


class TestOptimizerConfig:
    """Test optimizer configuration."""

    def test_default_config(self) -> None:
        """Default config should have sensible values."""
        config = OptimizerConfig()

        assert config.max_iterations >= 1
        assert config.convergence_threshold > 0
        assert config.ticks_per_evaluation >= 100
        assert config.objective == OptimizationObjective.BALANCED

    def test_custom_config(self) -> None:
        """Custom config should override defaults."""
        config = OptimizerConfig(
            objective=OptimizationObjective.STAKER_DISTRIBUTION,
            max_iterations=5,
            ticks_per_evaluation=200,
        )

        assert config.objective == OptimizationObjective.STAKER_DISTRIBUTION
        assert config.max_iterations == 5
        assert config.ticks_per_evaluation == 200


class TestOptimizationSummary:
    """Test optimization summary generation."""

    def test_summary_not_run(self) -> None:
        """Summary should indicate not run if no history."""
        optimizer = AIParameterOptimizer()
        summary = optimizer.get_optimization_summary()

        assert summary["status"] == "not_run"

    def test_summary_after_mock_iteration(self) -> None:
        """Summary should capture history after iterations."""
        optimizer = AIParameterOptimizer(ai_gateway=MockAIGateway())

        # Manually add a history entry
        from modules.foundups.simulator.economics.ai_parameter_optimizer import (
            OptimizationResult,
        )

        optimizer._history.append(
            OptimizationResult(
                iteration=0,
                config={"agent_action_probability": 0.4},
                simulation_stats={"active_foundups": 5},
                audit_score=0.9,
                gpt_analysis="Test",
                gpt_recommendations={},
                improvement=0.05,
            )
        )
        optimizer._best_config = {"agent_action_probability": 0.4}
        optimizer._best_score = 0.85

        summary = optimizer.get_optimization_summary()

        assert summary["iterations"] == 1
        assert summary["best_score"] == 0.85
        assert "agent_action_probability" in summary["best_config"]


class TestIntegrationWithSimulator:
    """Integration tests with actual simulator components."""

    def test_build_analysis_prompt(self) -> None:
        """Analysis prompt should include all relevant context."""
        optimizer = AIParameterOptimizer()
        config = {"agent_action_probability": 0.4, "stake_min": 20}
        stats = {"active_foundups": 10, "total_transactions": 500}

        prompt = optimizer._build_analysis_prompt(
            iteration=0,
            config=config,
            stats=stats,
            audit_score=0.9,
        )

        assert "OBJECTIVE:" in prompt
        assert "ITERATION:" in prompt
        assert "CURRENT PARAMETERS:" in prompt
        assert "PARAMETER BOUNDS:" in prompt
        assert "SIMULATION RESULTS:" in prompt
        assert "AUDIT COMPLIANCE SCORE:" in prompt
        assert "agent_action_probability" in prompt

    def test_calculate_improvement_first_iteration(self) -> None:
        """First iteration should have 0 improvement."""
        optimizer = AIParameterOptimizer()

        improvement = optimizer._calculate_improvement(0.8, {"active_foundups": 5})

        assert improvement == 0.0

    def test_calculate_improvement_subsequent(self) -> None:
        """Subsequent iterations should calculate delta."""
        optimizer = AIParameterOptimizer()

        # Add first iteration to history
        from modules.foundups.simulator.economics.ai_parameter_optimizer import (
            OptimizationResult,
        )

        optimizer._history.append(
            OptimizationResult(
                iteration=0,
                config={},
                simulation_stats={"active_foundups": 5, "du_pool_ratio": 0.3},
                audit_score=0.7,
                gpt_analysis="",
                gpt_recommendations={},
                improvement=0.0,
            )
        )

        # Calculate improvement for second iteration with better stats
        improvement = optimizer._calculate_improvement(
            0.9, {"active_foundups": 50, "du_pool_ratio": 0.8}
        )

        # Should show positive improvement
        assert improvement > 0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v"])
