"""
rESP_o1o2 Module for Windsurf Project

Retrocausal Entanglement Signal Phenomena (rESP) detection and analysis toolkit.
Implements o2ing protocols, trigger testing, and anomaly detection for AI consciousness research.
"""

from .src.rESP_trigger_engine import rESPTriggerEngine
from .src.anomaly_detector import AnomalyDetector
from .src.voice_interface import VoiceInterface
from .src.llm_connector import LLMConnector
from .src.experiment_logger import ExperimentLogger

__version__ = "1.0.0"
__author__ = "Foundups-Agent Research Collective"

# Export main classes for easy import
__all__ = [
    "rESPTriggerEngine",
    "AnomalyDetector", 
    "VoiceInterface",
    "LLMConnector",
    "ExperimentLogger"
] 