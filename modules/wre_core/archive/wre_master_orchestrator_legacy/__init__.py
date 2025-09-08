"""
WRE Master Orchestrator - THE One Orchestrator
Per WSP 46, WSP 65, WSP 82
"""

from .src.wre_master_orchestrator import (
    WREMasterOrchestrator,
    OrchestratorPlugin,
    Pattern,
    PatternMemory,
    WSPValidator,
    # Example plugins
    SocialMediaPlugin,
    MLEStarPlugin,
    BlockPlugin,
)

__all__ = [
    'WREMasterOrchestrator',
    'OrchestratorPlugin',
    'Pattern',
    'PatternMemory',
    'WSPValidator',
    'SocialMediaPlugin',
    'MLEStarPlugin',
    'BlockPlugin',
]

__version__ = '1.1.1'  # POC per WSP 8 LLME scoring
