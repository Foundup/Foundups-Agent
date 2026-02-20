"""Central AI Model Registry - Single source of truth for all AI model versions.

UPDATE THIS FILE when providers release new models.
All other modules should import from here, not hardcode model IDs.

Last Updated: 2026-02-15
"""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Dict, Optional


class ModelStatus(Enum):
    """Model lifecycle status."""
    CURRENT = "current"      # Active, recommended
    LEGACY = "legacy"        # Works but newer available
    DEPRECATED = "deprecated"  # Will be removed soon
    SUNSET = "sunset"        # No longer available


@dataclass
class ModelInfo:
    """Model metadata."""
    model_id: str
    provider: str
    status: ModelStatus
    release_date: Optional[date] = None
    sunset_date: Optional[date] = None
    notes: str = ""

    @property
    def is_usable(self) -> bool:
        return self.status in (ModelStatus.CURRENT, ModelStatus.LEGACY)


# =============================================================================
# OPENAI MODELS
# =============================================================================
OPENAI_MODELS: Dict[str, ModelInfo] = {
    # Current (2026)
    "gpt-4o": ModelInfo(
        model_id="gpt-4o",
        provider="openai",
        status=ModelStatus.CURRENT,
        release_date=date(2024, 5, 13),
        notes="Best overall - code, analysis, creative"
    ),
    "gpt-4o-mini": ModelInfo(
        model_id="gpt-4o-mini",
        provider="openai",
        status=ModelStatus.CURRENT,
        release_date=date(2024, 7, 18),
        notes="Fast, cheap, good quality"
    ),
    "o1": ModelInfo(
        model_id="o1",
        provider="openai",
        status=ModelStatus.CURRENT,
        release_date=date(2024, 12, 5),
        notes="Reasoning model - complex problem solving"
    ),
    "o1-mini": ModelInfo(
        model_id="o1-mini",
        provider="openai",
        status=ModelStatus.CURRENT,
        release_date=date(2024, 9, 12),
        notes="Fast reasoning model"
    ),
    "o3-mini": ModelInfo(
        model_id="o3-mini",
        provider="openai",
        status=ModelStatus.CURRENT,
        release_date=date(2025, 1, 31),
        notes="Latest reasoning model"
    ),
    # Legacy
    "gpt-4-turbo": ModelInfo(
        model_id="gpt-4-turbo",
        provider="openai",
        status=ModelStatus.LEGACY,
        release_date=date(2024, 4, 9),
        notes="Superseded by gpt-4o"
    ),
    # Deprecated/Sunset
    "gpt-4": ModelInfo(
        model_id="gpt-4",
        provider="openai",
        status=ModelStatus.DEPRECATED,
        release_date=date(2023, 3, 14),
        sunset_date=date(2025, 6, 1),
        notes="Use gpt-4o instead"
    ),
    "gpt-3.5-turbo": ModelInfo(
        model_id="gpt-3.5-turbo",
        provider="openai",
        status=ModelStatus.DEPRECATED,
        release_date=date(2023, 3, 1),
        notes="Use gpt-4o-mini instead"
    ),
}

# =============================================================================
# ANTHROPIC MODELS
# =============================================================================
ANTHROPIC_MODELS: Dict[str, ModelInfo] = {
    # Current (2026) - Claude 4.x family
    "claude-opus-4-6": ModelInfo(
        model_id="claude-opus-4-6",
        provider="anthropic",
        status=ModelStatus.CURRENT,
        notes="Most capable - complex code, research"
    ),
    "claude-sonnet-4-5-20250929": ModelInfo(
        model_id="claude-sonnet-4-5-20250929",
        provider="anthropic",
        status=ModelStatus.CURRENT,
        release_date=date(2025, 9, 29),
        notes="Balanced - good for most tasks"
    ),
    "claude-haiku-4-5-20251001": ModelInfo(
        model_id="claude-haiku-4-5-20251001",
        provider="anthropic",
        status=ModelStatus.CURRENT,
        release_date=date(2025, 10, 1),
        notes="Fast, cheap - quick tasks"
    ),
    # Deprecated - Claude 3.x family
    "claude-3-opus-20240229": ModelInfo(
        model_id="claude-3-opus-20240229",
        provider="anthropic",
        status=ModelStatus.DEPRECATED,
        release_date=date(2024, 2, 29),
        notes="Use claude-opus-4-6 instead"
    ),
    "claude-3-sonnet-20240229": ModelInfo(
        model_id="claude-3-sonnet-20240229",
        provider="anthropic",
        status=ModelStatus.DEPRECATED,
        release_date=date(2024, 2, 29),
        notes="Use claude-sonnet-4-5 instead"
    ),
    "claude-3-haiku-20240307": ModelInfo(
        model_id="claude-3-haiku-20240307",
        provider="anthropic",
        status=ModelStatus.DEPRECATED,
        release_date=date(2024, 3, 7),
        notes="Use claude-haiku-4-5 instead"
    ),
}

# =============================================================================
# GOOGLE GEMINI MODELS
# =============================================================================
GEMINI_MODELS: Dict[str, ModelInfo] = {
    # Current (2026)
    "gemini-2.5-pro": ModelInfo(
        model_id="gemini-2.5-pro",
        provider="google",
        status=ModelStatus.CURRENT,
        release_date=date(2025, 3, 25),
        notes="Most capable Gemini - thinking model"
    ),
    "gemini-2.5-flash": ModelInfo(
        model_id="gemini-2.5-flash",
        provider="google",
        status=ModelStatus.CURRENT,
        release_date=date(2025, 4, 17),
        notes="Fast thinking model"
    ),
    "gemini-2.0-flash": ModelInfo(
        model_id="gemini-2.0-flash",
        provider="google",
        status=ModelStatus.LEGACY,
        release_date=date(2024, 12, 11),
        notes="Previous gen - use 2.5 series"
    ),
    # Deprecated
    "gemini-pro": ModelInfo(
        model_id="gemini-pro",
        provider="google",
        status=ModelStatus.DEPRECATED,
        release_date=date(2023, 12, 6),
        notes="Use gemini-2.5-pro instead"
    ),
    "gemini-pro-vision": ModelInfo(
        model_id="gemini-pro-vision",
        provider="google",
        status=ModelStatus.DEPRECATED,
        release_date=date(2023, 12, 6),
        notes="Use gemini-2.5-pro (multimodal built-in)"
    ),
}

# =============================================================================
# GROK MODELS (X.AI)
# =============================================================================
GROK_MODELS: Dict[str, ModelInfo] = {
    "grok-3": ModelInfo(
        model_id="grok-3",
        provider="xai",
        status=ModelStatus.CURRENT,
        notes="Current Grok model"
    ),
    "grok-2": ModelInfo(
        model_id="grok-2",
        provider="xai",
        status=ModelStatus.LEGACY,
        notes="Previous generation"
    ),
}

# =============================================================================
# LOCAL MODELS (Ollama/llama.cpp)
# =============================================================================
LOCAL_MODELS: Dict[str, ModelInfo] = {
    "qwen2.5:7b": ModelInfo(
        model_id="qwen2.5:7b",
        provider="ollama",
        status=ModelStatus.CURRENT,
        notes="Strategic planning, code generation"
    ),
    "gemma2:2b": ModelInfo(
        model_id="gemma2:2b",
        provider="ollama",
        status=ModelStatus.CURRENT,
        notes="Fast pattern matching, classification"
    ),
    "llama3.2:3b": ModelInfo(
        model_id="llama3.2:3b",
        provider="ollama",
        status=ModelStatus.CURRENT,
        notes="General purpose local"
    ),
}

# =============================================================================
# COMBINED REGISTRY
# =============================================================================
ALL_MODELS: Dict[str, ModelInfo] = {
    **OPENAI_MODELS,
    **ANTHROPIC_MODELS,
    **GEMINI_MODELS,
    **GROK_MODELS,
    **LOCAL_MODELS,
}

# =============================================================================
# RECOMMENDED MODELS BY TASK
# =============================================================================
RECOMMENDED_MODELS = {
    "code_review": ["claude-opus-4-6", "gpt-4o", "gemini-2.5-pro"],
    "analysis": ["gpt-4o", "claude-sonnet-4-5-20250929", "o1"],
    "creative": ["claude-sonnet-4-5-20250929", "gpt-4o", "gemini-2.5-flash"],
    "quick": ["gpt-4o-mini", "claude-haiku-4-5-20251001", "gemini-2.5-flash"],
    "reasoning": ["o1", "o3-mini", "claude-opus-4-6", "gemini-2.5-pro"],
    "local_fast": ["gemma2:2b", "llama3.2:3b"],
    "local_smart": ["qwen2.5:7b"],
}

# =============================================================================
# MIGRATION MAP (deprecated -> current)
# =============================================================================
MIGRATION_MAP = {
    # OpenAI
    "gpt-4": "gpt-4o",
    "gpt-3.5-turbo": "gpt-4o-mini",
    "gpt-4-turbo": "gpt-4o",
    # Anthropic
    "claude-3-opus-20240229": "claude-opus-4-6",
    "claude-3-sonnet-20240229": "claude-sonnet-4-5-20250929",
    "claude-3-haiku-20240307": "claude-haiku-4-5-20251001",
    # Gemini
    "gemini-pro": "gemini-2.5-pro",
    "gemini-pro-vision": "gemini-2.5-pro",
    "gemini-1.0-pro": "gemini-2.5-pro",
    "gemini-2.0-flash": "gemini-2.5-flash",
    # Grok
    "grok-2": "grok-3",
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_model(model_id: str) -> Optional[ModelInfo]:
    """Get model info by ID."""
    return ALL_MODELS.get(model_id)


def get_current_models(provider: Optional[str] = None) -> Dict[str, ModelInfo]:
    """Get all current (non-deprecated) models."""
    models = {
        k: v for k, v in ALL_MODELS.items()
        if v.status == ModelStatus.CURRENT
    }
    if provider:
        models = {k: v for k, v in models.items() if v.provider == provider}
    return models


def get_deprecated_models() -> Dict[str, ModelInfo]:
    """Get all deprecated models (need migration)."""
    return {
        k: v for k, v in ALL_MODELS.items()
        if v.status in (ModelStatus.DEPRECATED, ModelStatus.SUNSET)
    }


def check_model_status(model_id: str) -> tuple[bool, str]:
    """Check if a model ID is current.

    Returns:
        (is_ok, message)
    """
    model = ALL_MODELS.get(model_id)
    if model is None:
        return False, f"Unknown model: {model_id}"

    if model.status == ModelStatus.CURRENT:
        return True, f"{model_id} is current"
    elif model.status == ModelStatus.LEGACY:
        return True, f"{model_id} works but newer models available"
    elif model.status == ModelStatus.DEPRECATED:
        return False, f"{model_id} is DEPRECATED: {model.notes}"
    else:
        return False, f"{model_id} is SUNSET (no longer available)"


def audit_codebase_models(model_ids: list[str]) -> dict:
    """Audit a list of model IDs for obsolete references.

    Returns dict with current, legacy, deprecated, unknown lists.
    """
    result = {
        "current": [],
        "legacy": [],
        "deprecated": [],
        "unknown": [],
    }

    for model_id in model_ids:
        model = ALL_MODELS.get(model_id)
        if model is None:
            result["unknown"].append(model_id)
        elif model.status == ModelStatus.CURRENT:
            result["current"].append(model_id)
        elif model.status == ModelStatus.LEGACY:
            result["legacy"].append(model_id)
        else:
            result["deprecated"].append(model_id)

    return result


def print_registry_status():
    """Print registry status summary."""
    current = get_current_models()
    deprecated = get_deprecated_models()

    print("=" * 60)
    print("AI MODEL REGISTRY STATUS")
    print("=" * 60)
    print(f"\nCurrent Models ({len(current)}):")
    for model_id, info in sorted(current.items(), key=lambda x: x[1].provider):
        print(f"  [{info.provider:10}] {model_id}")

    print(f"\nDeprecated Models ({len(deprecated)}):")
    for model_id, info in sorted(deprecated.items(), key=lambda x: x[1].provider):
        print(f"  [{info.provider:10}] {model_id} -> {info.notes}")

    print("\nRecommended by Task:")
    for task, models in RECOMMENDED_MODELS.items():
        print(f"  {task}: {models[0]}")


if __name__ == "__main__":
    print_registry_status()
