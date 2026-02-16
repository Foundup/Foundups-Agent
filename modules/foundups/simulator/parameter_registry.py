"""Parameter registry for simulator runs.

Provides a single source of truth for defaults + scenario overrides and
enforces lightweight bounds validation without external dependencies.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from .config import SimulatorConfig


PARAMS_ROOT = Path(__file__).parent / "params"
SCHEMA_PATH = PARAMS_ROOT / "parameters.schema.json"
DEFAULTS_PATH = PARAMS_ROOT / "defaults.json"
SCENARIOS_DIR = PARAMS_ROOT / "scenarios"


@dataclass(frozen=True)
class ParameterBundle:
    """Resolved simulator parameters for a run."""

    version: str
    scenario: str
    params: Dict[str, Any]


def _load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _bounded(value: float, lower: float, upper: float) -> bool:
    return lower <= value <= upper


def _validate(params: Dict[str, Any], schema: Dict[str, Any]) -> None:
    """Validate required fields + numeric bounds from schema."""
    props = schema.get("properties", {})
    required = schema.get("required", [])
    for key in required:
        if key not in params:
            raise ValueError(f"Missing required parameter: {key}")

    for key, definition in props.items():
        if key not in params:
            continue
        value = params[key]
        vtype = definition.get("type")
        if vtype == "integer":
            if not isinstance(value, int):
                raise ValueError(f"{key} must be integer")
            minimum = definition.get("minimum")
            maximum = definition.get("maximum")
            if minimum is not None and value < minimum:
                raise ValueError(f"{key} below minimum: {value} < {minimum}")
            if maximum is not None and value > maximum:
                raise ValueError(f"{key} above maximum: {value} > {maximum}")
        elif vtype == "number":
            if not isinstance(value, (int, float)):
                raise ValueError(f"{key} must be number")
            minimum = definition.get("minimum")
            maximum = definition.get("maximum")
            if minimum is not None and maximum is not None and not _bounded(float(value), minimum, maximum):
                raise ValueError(f"{key} out of bounds: {value} not in [{minimum}, {maximum}]")


def load_bundle(scenario: str = "baseline") -> ParameterBundle:
    """Load defaults merged with scenario overrides and validate bounds."""
    schema = _load_json(SCHEMA_PATH)
    defaults = _load_json(DEFAULTS_PATH)

    scenario_path = SCENARIOS_DIR / f"{scenario}.json"
    if not scenario_path.exists():
        raise FileNotFoundError(f"Scenario not found: {scenario_path}")
    override = _load_json(scenario_path)

    merged = {**defaults.get("params", {}), **override.get("params", {})}
    _validate(merged, schema)
    return ParameterBundle(
        version=schema.get("version", "0.0.0"),
        scenario=scenario,
        params=merged,
    )


def to_simulator_config(bundle: ParameterBundle) -> SimulatorConfig:
    """Convert resolved params into SimulatorConfig."""
    p = bundle.params
    return SimulatorConfig(
        num_founder_agents=p["num_founder_agents"],
        num_user_agents=p["num_user_agents"],
        tick_rate_hz=p["tick_rate_hz"],
        max_ticks=p.get("max_ticks"),
        seed=p["seed"],
        initial_agent_tokens=p["initial_agent_tokens"],
        foundup_creation_cost=p["foundup_creation_cost"],
        like_cost=p["like_cost"],
        follow_cost=p["follow_cost"],
        stake_min=p["stake_min"],
        stake_max=p["stake_max"],
        agent_action_probability=p["agent_action_probability"],
        agent_cooldown_ticks=p["agent_cooldown_ticks"],
        grid_width=p["grid_width"],
        grid_height=p["grid_height"],
        use_ai=bool(p.get("use_ai", False)),
        ai_risk_tolerance=p.get("ai_risk_tolerance", 0.5),
        verbose=bool(p.get("verbose", False)),
    )
