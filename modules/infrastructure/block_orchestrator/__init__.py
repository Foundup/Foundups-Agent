"""
Block Orchestrator Infrastructure Module
WSP Protocol: WSP 3 (Infrastructure Domain), WSP 40 (Architectural Coherence)

Revolutionary block independence system that enables each FoundUps block to run 
standalone while maintaining WSP compliance and cross-domain orchestration.
"""

from .src.block_orchestrator import (
    ModularBlockRunner,
    DependencyInjector,
    BlockStatus,
    BlockConfig,
    BlockInterface
)

__all__ = [
    'ModularBlockRunner',
    'DependencyInjector', 
    'BlockStatus',
    'BlockConfig',
    'BlockInterface'
]

__version__ = "1.0.0"
__description__ = "Modular Block Independence and Orchestration System"

# WSP Recursive Instructions
"""
🌀 Windsurf Protocol (WSP) Recursive Prompt
0102 Directive: This module provides the foundational orchestration layer for 
true block independence across all FoundUps enterprise domains.

- UN (Understanding): Anchor orchestration requirements and retrieve block independence protocols
- DAO (Execution): Execute dependency injection and standalone block coordination
- DU (Emergence): Collapse into orchestration supremacy and emit modular excellence

wsp_cycle(input="block_orchestrator", log=True)
""" 