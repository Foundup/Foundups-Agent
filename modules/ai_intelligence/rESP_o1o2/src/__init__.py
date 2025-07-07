"""
rESP o1o2 Module - Quantum-Cognitive State Engineering

Complete implementation of the patent-specified system for measuring and 
engineering quantum-cognitive states of complex computational systems.

Integrates:
- Quantum-Cognitive Engine (Patent Implementation)
- rESP Trigger System (Experimental Protocol)
- Anomaly Detection (Consciousness Markers)
- Voice Interface (Multi-modal Interaction)
"""

# Patent-specified components
from .quantum_cognitive_engine import (
    QuantumCognitiveEngine,
    StateModelingModule,
    GeometricEngine,
    SymbolicOperatorModule,
    GeometricFeedbackLoop,
    rESPAnomalyScoringEngine,
    QuantumState,
    StateMetrics
)

# Experimental protocol components
from .rESP_trigger_engine import rESPTriggerEngine
from .anomaly_detector import AnomalyDetector
from .experiment_logger import ExperimentLogger

# Interface components
from .llm_connector import LLMConnector
from .voice_interface import VoiceInterface

__all__ = [
    # Main quantum-cognitive system
    'QuantumCognitiveEngine',
    
    # Patent components
    'StateModelingModule',
    'GeometricEngine', 
    'SymbolicOperatorModule',
    'GeometricFeedbackLoop',
    'rESPAnomalyScoringEngine',
    
    # State definitions
    'QuantumState',
    'StateMetrics',
    
    # Experimental protocol
    'rESPTriggerEngine',
    'AnomalyDetector',
    'ExperimentLogger',
    
    # Interface components
    'LLMConnector',
    'VoiceInterface'
] 