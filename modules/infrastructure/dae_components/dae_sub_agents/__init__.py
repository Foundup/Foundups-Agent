"""
DAE Sub-Agent Enhancement System
WSP-Compliant sub-agents that enhance DAE pattern memory operations

This module provides sub-agent layers that ensure complete WSP framework
compliance while maintaining the efficiency of the DAE architecture.

Sub-Agent Types:
- Verification: WSP 50 pre-action verification
- Compliance: WSP 64 violation prevention
- Improvement: WSP 48 recursive enhancement
- Enhancement: WSP 74 Ultra_think processing
- Quantum: WSP 76 coherence maintenance
"""

from .base.sub_agent_base import SubAgentBase, SubAgentContext
from .verification.wsp50_verifier import WSP50VerificationSubAgent
from .compliance.wsp64_preventer import WSP64ViolationPreventionSubAgent
from .improvement.wsp48_improver import WSP48RecursiveImprovementSubAgent
from .enhancement.wsp74_enhancer import WSP74AgenticEnhancementSubAgent
from .quantum.wsp76_coherence import WSP76QuantumCoherenceSubAgent

__all__ = [
    'SubAgentBase',
    'SubAgentContext',
    'WSP50VerificationSubAgent',
    'WSP64ViolationPreventionSubAgent',
    'WSP48RecursiveImprovementSubAgent',
    'WSP74AgenticEnhancementSubAgent',
    'WSP76QuantumCoherenceSubAgent'
]

# Version info following WSP 22
__version__ = "1.0.0"
__wsp_compliance__ = ["WSP 50", "WSP 64", "WSP 48", "WSP 74", "WSP 76"]