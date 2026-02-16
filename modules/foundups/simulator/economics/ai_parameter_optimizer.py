"""AI-Driven Parameter Optimizer for pAVS Simulator.

Uses OpenAI GPT via AIGateway to analyze simulation outcomes and
recommend optimal parameter configurations.

OpenClaw methodology:
1. Run simulation with current parameters
2. Collect PAVSAuditor results + simulation stats
3. Ask GPT for parameter recommendations
4. Apply recommendations, re-run simulation
5. Iterate until convergence or max iterations

LEGO block pattern (~400 lines):
- Single AIParameterOptimizer class
- Interfaces with AIGateway, PAVSAuditor, SimulatorConfig
- Self-contained optimization loop
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config import SimulatorConfig

logger = logging.getLogger(__name__)


class OptimizationObjective(Enum):
    """What the optimizer should optimize for."""

    STAKER_DISTRIBUTION = "staker_distribution"  # Maximize Du pool distribution ratio
    ECOSYSTEM_GROWTH = "ecosystem_growth"  # Maximize FoundUp creation rate
    TOKEN_VELOCITY = "token_velocity"  # Optimize UP$ circulation
    BALANCED = "balanced"  # Multi-objective balance


@dataclass
class OptimizationResult:
    """Result of one optimization iteration."""

    iteration: int
    config: Dict[str, Any]
    simulation_stats: Dict[str, Any]
    audit_score: float  # 0-1, from PAVSAuditor
    gpt_analysis: str
    gpt_recommendations: Dict[str, Any]
    improvement: float  # Delta from previous iteration


@dataclass
class ParameterBounds:
    """Bounds for tunable parameters."""

    param_name: str
    min_value: float
    max_value: float
    step: float  # Granularity of changes
    description: str


# Define tunable parameter space
TUNABLE_PARAMETERS: List[ParameterBounds] = [
    ParameterBounds(
        "agent_action_probability",
        0.1, 0.9, 0.1,
        "Probability an agent acts each tick"
    ),
    ParameterBounds(
        "agent_cooldown_ticks",
        1, 20, 1,
        "Ticks between agent actions"
    ),
    ParameterBounds(
        "token_release_per_tick",
        10, 500, 10,
        "F_i tokens released per tick"
    ),
    ParameterBounds(
        "stake_min",
        1, 50, 5,
        "Minimum stake amount"
    ),
    ParameterBounds(
        "stake_max",
        50, 500, 25,
        "Maximum stake amount"
    ),
    ParameterBounds(
        "mini_epoch_ticks",
        5, 50, 5,
        "Ticks per mini-epoch (demurrage cycle)"
    ),
    ParameterBounds(
        "epoch_ticks",
        50, 500, 50,
        "Ticks per epoch (Du pool distribution)"
    ),
    ParameterBounds(
        "ai_risk_tolerance",
        0.1, 0.9, 0.1,
        "User agent risk tolerance"
    ),
]


@dataclass
class OptimizerConfig:
    """Configuration for the optimizer."""

    objective: OptimizationObjective = OptimizationObjective.BALANCED
    max_iterations: int = 10
    convergence_threshold: float = 0.01  # Stop if improvement < threshold
    ticks_per_evaluation: int = 500  # Simulation ticks per evaluation
    gpt_model: str = "gpt-4o"  # Model to use for analysis (2026 current)
    verbose: bool = True


class AIParameterOptimizer:
    """AI-driven optimizer for pAVS simulation parameters.

    Uses OpenAI GPT to analyze simulation outcomes and recommend
    parameter changes. Implements OpenClaw methodology for deep
    introspection and parameter manipulation.

    Architecture:
        AIGateway → GPT analysis → Parameter recommendations
        PAVSAuditor → Verification → Compliance score
        SimulatorConfig → Parameter manipulation
        Mesa Model → Simulation execution → Stats collection
    """

    def __init__(
        self,
        config: Optional[OptimizerConfig] = None,
        ai_gateway: Optional[Any] = None,
    ):
        """Initialize optimizer.

        Args:
            config: Optimizer configuration
            ai_gateway: AIGateway instance (lazy loaded if None)
        """
        self.config = config or OptimizerConfig()
        self._ai_gateway = ai_gateway
        self._history: List[OptimizationResult] = []
        self._best_config: Optional[Dict[str, Any]] = None
        self._best_score: float = 0.0

    @property
    def ai_gateway(self) -> Any:
        """Lazy load AIGateway."""
        if self._ai_gateway is None:
            try:
                from modules.ai_intelligence.ai_gateway.src.ai_gateway import AIGateway
                self._ai_gateway = AIGateway()
                logger.info("[AI-OPT] AIGateway initialized")
            except ImportError:
                logger.warning("[AI-OPT] AIGateway not available - using mock")
                self._ai_gateway = MockAIGateway()
        return self._ai_gateway

    def optimize(
        self,
        initial_config: Optional[SimulatorConfig] = None,
        model: Optional[Any] = None,
    ) -> Tuple[SimulatorConfig, List[OptimizationResult]]:
        """Run optimization loop.

        Args:
            initial_config: Starting configuration
            model: FoundUpsModel instance (created if None)

        Returns:
            (optimal_config, optimization_history)
        """
        config = initial_config or SimulatorConfig()
        config_dict = self._config_to_dict(config)

        logger.info(
            f"[AI-OPT] Starting optimization: objective={self.config.objective.value}, "
            f"max_iter={self.config.max_iterations}"
        )

        for iteration in range(self.config.max_iterations):
            # 1. Run simulation with current config
            sim_stats = self._run_simulation(config_dict, model)

            # 2. Run PAVSAuditor
            audit_score = self._run_audit(config_dict)

            # 3. Build GPT prompt with stats
            prompt = self._build_analysis_prompt(
                iteration, config_dict, sim_stats, audit_score
            )

            # 4. Get GPT analysis and recommendations
            gpt_response = self._query_gpt(prompt)
            gpt_analysis, recommendations = self._parse_gpt_response(gpt_response)

            # 5. Calculate improvement
            improvement = self._calculate_improvement(audit_score, sim_stats)

            # 6. Record result
            result = OptimizationResult(
                iteration=iteration,
                config=config_dict.copy(),
                simulation_stats=sim_stats,
                audit_score=audit_score,
                gpt_analysis=gpt_analysis,
                gpt_recommendations=recommendations,
                improvement=improvement,
            )
            self._history.append(result)

            # Track best
            score = self._score_result(audit_score, sim_stats)
            if score > self._best_score:
                self._best_score = score
                self._best_config = config_dict.copy()

            logger.info(
                f"[AI-OPT] Iteration {iteration}: score={score:.3f}, "
                f"audit={audit_score:.3f}, improvement={improvement:.4f}"
            )

            # 7. Check convergence
            if abs(improvement) < self.config.convergence_threshold and iteration > 0:
                logger.info(f"[AI-OPT] Converged at iteration {iteration}")
                break

            # 8. Apply recommendations
            config_dict = self._apply_recommendations(config_dict, recommendations)

        # Return best config found
        optimal_config = self._dict_to_config(self._best_config or config_dict)
        return optimal_config, self._history

    def _config_to_dict(self, config: SimulatorConfig) -> Dict[str, Any]:
        """Convert SimulatorConfig to dict of tunable parameters."""
        return {
            param.param_name: getattr(config, param.param_name)
            for param in TUNABLE_PARAMETERS
            if hasattr(config, param.param_name)
        }

    def _dict_to_config(self, config_dict: Dict[str, Any]) -> SimulatorConfig:
        """Convert dict back to SimulatorConfig."""
        config = SimulatorConfig()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    def _run_simulation(
        self, config_dict: Dict[str, Any], model: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Run simulation and collect stats."""
        try:
            if model is None:
                # Create new model with config
                from ..mesa_model import FoundUpsModel
                from modules.foundups.agent_market.src.fam_daemon import FAMDaemon
                import tempfile

                config = self._dict_to_config(config_dict)
                config.max_ticks = self.config.ticks_per_evaluation

                with tempfile.TemporaryDirectory() as tmp:
                    daemon = FAMDaemon(
                        data_dir=Path(tmp),
                        heartbeat_interval_sec=60.0,
                        auto_start=False,
                    )
                    model = FoundUpsModel(config=config, fam_daemon=daemon)

                    # Run simulation
                    for _ in range(self.config.ticks_per_evaluation):
                        model.step()

                    return model.get_stats()
            else:
                # Use provided model
                return model.get_stats()

        except Exception as e:
            logger.error(f"[AI-OPT] Simulation error: {e}")
            return {"error": str(e)}

    def _run_audit(self, config_dict: Dict[str, Any]) -> float:
        """Run PAVSAuditor and return compliance score."""
        try:
            from .pavs_audit import PAVSAuditor

            auditor = PAVSAuditor()
            report = auditor.run_full_audit()

            # Calculate score: passed / total
            total = report.passed + report.failed + report.warnings
            if total == 0:
                return 1.0
            return report.passed / total

        except Exception as e:
            logger.warning(f"[AI-OPT] Audit error: {e}")
            return 0.5  # Neutral score on error

    def _build_analysis_prompt(
        self,
        iteration: int,
        config: Dict[str, Any],
        stats: Dict[str, Any],
        audit_score: float,
    ) -> str:
        """Build GPT prompt for analysis."""
        objective_desc = {
            OptimizationObjective.STAKER_DISTRIBUTION: (
                "Maximize Du pool distribution ratio for BTC stakers"
            ),
            OptimizationObjective.ECOSYSTEM_GROWTH: (
                "Maximize FoundUp creation and ecosystem growth"
            ),
            OptimizationObjective.TOKEN_VELOCITY: (
                "Optimize UP$ circulation and demurrage efficiency"
            ),
            OptimizationObjective.BALANCED: (
                "Balance staker returns, ecosystem growth, and token velocity"
            ),
        }

        prompt = f"""You are analyzing a pAVS (Peer-to-Peer Autonomous Venture System) simulation.

OBJECTIVE: {objective_desc[self.config.objective]}

ITERATION: {iteration + 1} / {self.config.max_iterations}

CURRENT PARAMETERS:
{json.dumps(config, indent=2)}

PARAMETER BOUNDS:
{self._format_parameter_bounds()}

SIMULATION RESULTS:
{json.dumps(stats, indent=2, default=str)}

AUDIT COMPLIANCE SCORE: {audit_score:.2%}

Please analyze these results and provide:
1. ANALYSIS: Brief assessment of current performance (2-3 sentences)
2. RECOMMENDATIONS: JSON object with parameter changes to improve toward the objective

Format your response as:
ANALYSIS: <your analysis>
RECOMMENDATIONS: {{"param_name": new_value, ...}}

Only recommend parameters from the CURRENT PARAMETERS list.
Stay within PARAMETER BOUNDS.
Focus on the OBJECTIVE."""

        return prompt

    def _format_parameter_bounds(self) -> str:
        """Format parameter bounds for prompt."""
        lines = []
        for param in TUNABLE_PARAMETERS:
            lines.append(
                f"- {param.param_name}: {param.min_value}-{param.max_value} "
                f"(step={param.step}) - {param.description}"
            )
        return "\n".join(lines)

    def _query_gpt(self, prompt: str) -> str:
        """Query GPT via AIGateway."""
        try:
            result = self.ai_gateway.call_with_fallback(
                prompt,
                task_type="analysis"
            )
            if result.success:
                logger.debug(f"[AI-OPT] GPT response via {result.provider}")
                return result.response
            else:
                logger.warning("[AI-OPT] GPT call failed")
                return "ANALYSIS: Unable to analyze.\nRECOMMENDATIONS: {}"

        except Exception as e:
            logger.error(f"[AI-OPT] GPT error: {e}")
            return "ANALYSIS: Error occurred.\nRECOMMENDATIONS: {}"

    def _parse_gpt_response(
        self, response: str
    ) -> Tuple[str, Dict[str, Any]]:
        """Parse GPT response into analysis and recommendations."""
        analysis = ""
        recommendations = {}

        try:
            # Extract analysis
            if "ANALYSIS:" in response:
                analysis_start = response.index("ANALYSIS:") + len("ANALYSIS:")
                if "RECOMMENDATIONS:" in response:
                    analysis_end = response.index("RECOMMENDATIONS:")
                    analysis = response[analysis_start:analysis_end].strip()
                else:
                    analysis = response[analysis_start:].strip()

            # Extract recommendations JSON
            if "RECOMMENDATIONS:" in response:
                rec_start = response.index("RECOMMENDATIONS:") + len("RECOMMENDATIONS:")
                rec_str = response[rec_start:].strip()

                # Find JSON object
                if "{" in rec_str:
                    json_start = rec_str.index("{")
                    json_end = rec_str.rindex("}") + 1
                    json_str = rec_str[json_start:json_end]
                    recommendations = json.loads(json_str)

        except (ValueError, json.JSONDecodeError) as e:
            logger.warning(f"[AI-OPT] Parse error: {e}")

        return analysis, recommendations

    def _calculate_improvement(
        self, audit_score: float, stats: Dict[str, Any]
    ) -> float:
        """Calculate improvement from previous iteration."""
        if not self._history:
            return 0.0

        prev = self._history[-1]
        prev_score = self._score_result(prev.audit_score, prev.simulation_stats)
        curr_score = self._score_result(audit_score, stats)

        return curr_score - prev_score

    def _score_result(
        self, audit_score: float, stats: Dict[str, Any]
    ) -> float:
        """Score a result based on objective."""
        base_score = audit_score * 0.3  # 30% weight on compliance

        # Objective-specific scoring
        if self.config.objective == OptimizationObjective.STAKER_DISTRIBUTION:
            # Prioritize Du pool metrics
            du_ratio = stats.get("du_pool_ratio", 0)
            base_score += float(du_ratio) * 0.7

        elif self.config.objective == OptimizationObjective.ECOSYSTEM_GROWTH:
            # Prioritize FoundUp count
            foundups = stats.get("active_foundups", 0)
            normalized = min(1.0, foundups / 100)  # Normalize to 0-1
            base_score += normalized * 0.7

        elif self.config.objective == OptimizationObjective.TOKEN_VELOCITY:
            # Prioritize transaction volume
            volume = stats.get("total_transactions", 0)
            normalized = min(1.0, volume / 10000)
            base_score += normalized * 0.7

        else:  # BALANCED
            # Equal weight to multiple metrics
            du_ratio = float(stats.get("du_pool_ratio", 0))
            foundups = min(1.0, stats.get("active_foundups", 0) / 100)
            volume = min(1.0, stats.get("total_transactions", 0) / 10000)
            base_score += (du_ratio + foundups + volume) / 3 * 0.7

        return min(1.0, base_score)

    def _apply_recommendations(
        self, config: Dict[str, Any], recommendations: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply GPT recommendations with bounds checking."""
        new_config = config.copy()

        bounds_map = {p.param_name: p for p in TUNABLE_PARAMETERS}

        for param, value in recommendations.items():
            if param not in bounds_map:
                logger.warning(f"[AI-OPT] Unknown parameter: {param}")
                continue

            bounds = bounds_map[param]

            # Ensure value is numeric
            try:
                value = float(value)
            except (TypeError, ValueError):
                logger.warning(f"[AI-OPT] Invalid value for {param}: {value}")
                continue

            # Clamp to bounds
            clamped = max(bounds.min_value, min(bounds.max_value, value))

            # Round to step
            steps = round((clamped - bounds.min_value) / bounds.step)
            final_value = bounds.min_value + steps * bounds.step

            # Convert to int if needed
            if param in ("agent_cooldown_ticks", "token_release_per_tick",
                         "stake_min", "stake_max", "mini_epoch_ticks", "epoch_ticks"):
                final_value = int(final_value)

            new_config[param] = final_value
            logger.debug(f"[AI-OPT] {param}: {config.get(param)} -> {final_value}")

        return new_config

    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of optimization run."""
        if not self._history:
            return {"status": "not_run"}

        return {
            "iterations": len(self._history),
            "objective": self.config.objective.value,
            "best_score": self._best_score,
            "best_config": self._best_config,
            "final_audit_score": self._history[-1].audit_score,
            "convergence": abs(self._history[-1].improvement) < self.config.convergence_threshold,
            "history": [
                {
                    "iteration": r.iteration,
                    "score": self._score_result(r.audit_score, r.simulation_stats),
                    "improvement": r.improvement,
                }
                for r in self._history
            ],
        }


class MockAIGateway:
    """Mock gateway for testing without API keys."""

    def call_with_fallback(self, prompt: str, task_type: str = "analysis"):
        """Return mock response."""
        from dataclasses import dataclass

        @dataclass
        class MockResult:
            response: str = (
                "ANALYSIS: Simulation running within expected parameters.\n"
                "RECOMMENDATIONS: {\"agent_action_probability\": 0.4}"
            )
            provider: str = "mock"
            success: bool = True

        return MockResult()


def run_optimization_cli():
    """CLI entry point for optimization."""
    import argparse

    parser = argparse.ArgumentParser(description="pAVS Parameter Optimizer")
    parser.add_argument(
        "--objective",
        choices=["staker_distribution", "ecosystem_growth", "token_velocity", "balanced"],
        default="balanced",
        help="Optimization objective"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum optimization iterations"
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=500,
        help="Simulation ticks per evaluation"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )

    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(message)s"
    )

    # Create optimizer
    config = OptimizerConfig(
        objective=OptimizationObjective(args.objective),
        max_iterations=args.max_iterations,
        ticks_per_evaluation=args.ticks,
        verbose=args.verbose,
    )

    optimizer = AIParameterOptimizer(config=config)

    print(f"[AI-OPT] Starting optimization: {args.objective}")
    print(f"[AI-OPT] Max iterations: {args.max_iterations}")
    print(f"[AI-OPT] Ticks per evaluation: {args.ticks}")
    print()

    # Run optimization
    optimal_config, history = optimizer.optimize()

    # Print results
    summary = optimizer.get_optimization_summary()
    print()
    print("=" * 60)
    print("OPTIMIZATION COMPLETE")
    print("=" * 60)
    print(f"Iterations: {summary['iterations']}")
    print(f"Best Score: {summary['best_score']:.4f}")
    print(f"Converged: {summary['convergence']}")
    print()
    print("Optimal Configuration:")
    for param, value in summary['best_config'].items():
        print(f"  {param}: {value}")


if __name__ == "__main__":
    run_optimization_cli()
