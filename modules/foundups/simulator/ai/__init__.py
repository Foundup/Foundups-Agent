"""AI-driven agent components for FoundUps simulator.

Uses:
- Qwen: Strategic planning for Founder agents (idea generation, CABR estimation)
- Gemma: Fast classification for User agents (investment decisions)
"""

from .llm_inference import SimulatorLLM, InferenceResult
from .cabr_estimator import CABREstimator
from .qwen_founder import QwenFounderBrain
from .gemma_user import GemmaUserBrain

__all__ = [
    "SimulatorLLM",
    "InferenceResult",
    "CABREstimator",
    "QwenFounderBrain",
    "GemmaUserBrain",
]
