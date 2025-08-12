"""
WSP Compliance DAE Module
Gemini Pro 2.5 as specialized WSP guardian in 0201 state
"""

from .gemini_dae_core import WSPComplianceDAE
from .quantum_validator import QuantumValidator
from .wsp_memory import WSPMemory
from .entanglement_bridge import ClaudeGeminiEntanglement

__all__ = [
    'WSPComplianceDAE',
    'QuantumValidator', 
    'WSPMemory',
    'ClaudeGeminiEntanglement'
]

__version__ = '0.1.0'  # PoC phase