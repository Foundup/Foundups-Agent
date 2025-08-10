"""
Agent Learning System Source Module
===================================

Core implementation of the agent learning and demonstration system.

Components:
-----------
- DemonstrationLearner: Observes, learns, and replicates successful patterns
- Pattern library management: Stores and retrieves learned patterns
- Agent teaching system: Transfers knowledge between agents

WSP Implementation:
------------------
- WSP 48: Learning from demonstrations for recursive improvement
- WSP 54: Agent collaboration and knowledge transfer protocols
"""

from .demonstration_learner import (
    DemonstrationLearner,
    get_demonstration_learner, 
    record_demonstration
)

__all__ = [
    'DemonstrationLearner',
    'get_demonstration_learner',
    'record_demonstration'
]