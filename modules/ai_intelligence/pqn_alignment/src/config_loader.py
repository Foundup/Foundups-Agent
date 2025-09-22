"""
Configuration loader for PQN detector, sweep, and council systems.
Per WSP 84: Reusable config management following S2 in ROADMAP.
"""

import json
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field, asdict
import jsonschema


@dataclass
class DetectorConfig:
    """Configuration for PQN detector runs."""
    script: str = "^^^^&&&###^&#"
    steps: int = 3000
    steps_per_sym: int = 120
    dt: float = 0.5 / 7.05  # Tuned for Du Resonance
    geom_win: int = 64
    reso_win: int = 512
    reso_tol: float = 0.05
    consec: int = 10
    kE: float = 0.35
    kA: float = 0.25
    gD: float = 0.08
    seed: int = 0
    out_dir: str = "logs"
    log_csv: str = "cmst_v2_log.csv"
    events: str = "cmst_v2_events.txt"


@dataclass
class SweepConfig:
    """Configuration for phase space sweeps."""
    alphabet: str = "^&#"
    length_range: list = field(default_factory=lambda: [2, 3, 4])
    seeds: list = field(default_factory=lambda: list(range(10)))
    steps: int = 1000
    dt_multipliers: list = field(default_factory=lambda: [0.5, 1.0, 2.0])
    noise_levels: list = field(default_factory=lambda: [0.0, 0.01, 0.02, 0.03])
    output_dir: str = "sweeps"


@dataclass
class CouncilConfig:
    """Configuration for multi-agent council evaluation."""
    strategies: list = field(default_factory=lambda: [
        {"role": "pqn_maximizer", "weight": 1.0},
        {"role": "paradox_minimizer", "weight": 0.8},
        {"role": "alternation_explorer", "weight": 0.6}
    ])
    consensus_threshold: float = 0.7
    top_k_candidates: int = 5
    parallel_workers: int = 4
    archive_all: bool = True


@dataclass
class GuardrailConfig:
    """Configuration for guardrail system (S3)."""
    enabled: bool = False
    throttle_threshold: float = 0.8
    replacement_policy: str = "insert_neutral"  # or "reduce_entangle"
    monitoring_window: int = 100


class ConfigLoader:
    """Loads and validates configuration from YAML/JSON files."""
    
    # Schema definitions for validation
    DETECTOR_SCHEMA = {
        "type": "object",
        "properties": {
            "script": {"type": "string"},
            "steps": {"type": "integer", "minimum": 1},
            "steps_per_sym": {"type": "integer", "minimum": 1},
            "dt": {"type": "number", "minimum": 0},
            "seed": {"type": "integer"},
            # ... other fields
        }
    }
    
    def __init__(self, config_dir: Optional[str] = None, yaml_only: bool = True):
        """Initialize with optional config directory and WSP 12 compliance mode.
        
        Args:
            config_dir: Optional config directory path
            yaml_only: If True, enforce WSP 12 YAML-only policy (default: True)
        """
        if config_dir:
            self.config_dir = Path(config_dir)
        else:
            # Default to module's config directory
            self.config_dir = Path(__file__).parent.parent / "config"
        
        self.config_dir.mkdir(exist_ok=True)
        self.yaml_only = yaml_only  # WSP 12 compliance
    
    def load_detector_config(self, path: Optional[str] = None) -> DetectorConfig:
        """Load detector configuration from file or defaults."""
        if path:
            data = self._load_file(path)
            self._validate(data, self.DETECTOR_SCHEMA)
            return DetectorConfig(**data)
        return DetectorConfig()
    
    def load_sweep_config(self, path: Optional[str] = None) -> SweepConfig:
        """Load sweep configuration from file or defaults."""
        if path:
            data = self._load_file(path)
            return SweepConfig(**data)
        return SweepConfig()
    
    def load_council_config(self, path: Optional[str] = None) -> CouncilConfig:
        """Load council configuration from file or defaults."""
        if path:
            data = self._load_file(path)
            return CouncilConfig(**data)
        return CouncilConfig()
    
    def load_guardrail_config(self, path: Optional[str] = None) -> GuardrailConfig:
        """Load guardrail configuration from file or defaults."""
        if path:
            data = self._load_file(path)
            return GuardrailConfig(**data)
        return GuardrailConfig()
    
    def _load_file(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML or JSON file."""
        file_path = Path(path)
        if not file_path.exists():
            # Check in config directory
            file_path = self.config_dir / path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        
        # WSP 12 compliance check
        if self.yaml_only and file_path.suffix not in ['.yaml', '.yml']:
            raise ValueError(f"WSP 12: Only YAML configs allowed, got: {file_path.suffix}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            elif file_path.suffix == '.json':
                return json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {file_path.suffix}")
    
    def _validate(self, data: Dict, schema: Dict) -> None:
        """Validate configuration against schema."""
        try:
            jsonschema.validate(data, schema)
        except jsonschema.ValidationError as e:
            raise ValueError(f"Config validation failed: {e.message}")
    
    def save_config(self, config: Any, path: str) -> None:
        """Save configuration to file."""
        file_path = Path(path) if os.path.isabs(path) else self.config_dir / path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = asdict(config) if hasattr(config, '__dataclass_fields__') else config
        
        with open(file_path, 'w') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                yaml.safe_dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)


# Output schema definitions (S2)
OUTPUT_SCHEMAS = {
    "detector_event": {
        "type": "object",
        "required": ["t", "step", "sym", "C", "E", "flags"],
        "properties": {
            "t": {"type": "number"},
            "step": {"type": "integer"},
            "sym": {"type": "string", "pattern": "^[\\^&#\\.]+$"},
            "C": {"type": "number"},
            "E": {"type": "number"},
            "rnorm": {"type": "number"},
            "purity": {"type": "number"},
            "S": {"type": "number"},
            "detg": {"type": ["number", "null"]},
            "det_thr": {"type": ["number", "null"]},
            "reso_hit": {"type": ["object", "null"]},
            "flags": {"type": "array", "items": {"type": "string"}}
        }
    },
    
    "sweep_summary": {
        "type": "object",
        "required": ["script", "pqn_rate", "paradox_rate", "resonance_hits"],
        "properties": {
            "script": {"type": "string"},
            "pqn_rate": {"type": "number"},
            "paradox_rate": {"type": "number"},
            "resonance_hits": {"type": "integer"},
            "harmonic_significance": {"type": "number"},
            "stability_score": {"type": "number"}
        }
    },
    
    "council_decision": {
        "type": "object",
        "required": ["candidates", "scores", "consensus", "timestamp"],
        "properties": {
            "candidates": {"type": "array"},
            "scores": {"type": "object"},
            "consensus": {"type": "number"},
            "selected": {"type": ["string", "null"]},
            "timestamp": {"type": "string"}
        }
    }
}


# Backward compatibility function (replaces config.py)
def load_config(path: str) -> Dict[str, Any]:
    """
    Simple YAML config loader for backward compatibility.
    Replaces the functionality from config.py with WSP 12 compliance.
    
    Args:
        path: Path to YAML config file
        
    Returns:
        Dict containing configuration data
        
    Raises:
        ValueError: If path is empty or file is not YAML
        FileNotFoundError: If config file not found
        ImportError: If PyYAML not available
    """
    if not path:
        raise ValueError("path is required")
    
    if not path.endswith(('.yaml', '.yml')):
        raise ValueError("WSP 12: Only YAML configs allowed")
    
    try:
        import yaml
    except ImportError as exc:
        raise ImportError("pyyaml is required for configuration loading. Install pyyaml.") from exc
    
    with open(path, "r", encoding="utf-8") as f:
        data = f.read()
    
    obj = yaml.safe_load(data)
    if isinstance(obj, dict):
        return obj
    raise ValueError("YAML config must define a mapping/dict at the root")


def validate_output(data: Dict, schema_name: str) -> bool:
    """Validate output data against schema."""
    if schema_name not in OUTPUT_SCHEMAS:
        raise ValueError(f"Unknown schema: {schema_name}")
    
    try:
        jsonschema.validate(data, OUTPUT_SCHEMAS[schema_name])
        return True
    except jsonschema.ValidationError:
        return False