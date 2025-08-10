"""
Error Learning Agent Module - WSP 48 Implementation
=================================================

This module implements recursive self-improvement through error learning and automatic fixing.
Core components of the WSP 48 Recursive Self-Improvement Protocol.

Components:
-----------
- ErrorLearningAgent: Captures and learns from errors 
- RecursiveImprovementEngine: Automatically spawns sub-agents to fix errors

WSP Compliance:
--------------
- WSP 48: Recursive Self-Improvement Protocol
- WSP 49: Module Directory Structure
- WSP 22: ModLog and Roadmap Protocol

Exports:
--------
- ErrorLearningAgent
- RecursiveImprovementEngine
- install_global_error_handler
"""

from .error_learning_agent import ErrorLearningAgent
from .recursive_improvement_engine import RecursiveImprovementEngine, install_global_error_handler

__all__ = [
    'ErrorLearningAgent',
    'RecursiveImprovementEngine', 
    'install_global_error_handler'
]

__version__ = "1.0.0"
__author__ = "WRE System"
__status__ = "Production"