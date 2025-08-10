"""
Agent Learning System Module
============================

WSP 48 & WSP 54 compliant agent learning and knowledge transfer system.

This module enables agents to learn from successful demonstrations and patterns,
implementing the learning aspect of recursive self-improvement.

Exports:
--------
- DemonstrationLearner: Main learning system
- get_demonstration_learner: Global instance accessor  
- record_demonstration: Convenience function for recording actions

WSP Compliance:
--------------
- WSP 48: Recursive Self-Improvement Protocol
- WSP 54: WRE Agent Duties Specification
- WSP 49: Module Directory Structure
- WSP 22: ModLog and Roadmap Protocol
"""

from .src.demonstration_learner import (
    DemonstrationLearner,
    get_demonstration_learner,
    record_demonstration
)

__all__ = [
    'DemonstrationLearner',
    'get_demonstration_learner', 
    'record_demonstration'
]

__version__ = "1.0.0"
__author__ = "WRE System"
__status__ = "Production"