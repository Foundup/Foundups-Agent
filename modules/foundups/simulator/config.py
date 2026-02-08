"""Simulator configuration knobs.

All simulation parameters in one place for easy tuning.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SimulatorConfig:
    """Configuration for FoundUps simulator."""

    # Agent counts
    num_founder_agents: int = 3
    num_user_agents: int = 10

    # Timing
    tick_rate_hz: float = 2.0  # Ticks per second
    max_ticks: Optional[int] = None  # None = run forever

    # Randomness
    seed: int = 42  # Deterministic seed for reproducibility

    # Token economics
    initial_agent_tokens: int = 1000
    foundup_creation_cost: int = 100
    like_cost: int = 1
    follow_cost: int = 5
    stake_min: int = 10
    stake_max: int = 100

    # FoundUp parameters
    max_token_supply: int = 21_000_000
    token_release_per_tick: int = 100

    # Agent behavior
    agent_action_probability: float = 0.3  # Chance to act each tick
    agent_cooldown_ticks: int = 5  # Ticks between actions

    # Viewport
    grid_width: int = 10
    grid_height: int = 6
    event_log_lines: int = 10

    # Render mode
    render_mode: str = "terminal"  # "terminal" or "pygame"

    # Debug
    verbose: bool = False
    show_debug_panel: bool = True

    # AI agents (Qwen founders, Gemma users)
    use_ai: bool = False  # Enable AI-driven agents
    ai_risk_tolerance: float = 0.5  # User agent risk tolerance (0-1)


# Default config instance
DEFAULT_CONFIG = SimulatorConfig()
