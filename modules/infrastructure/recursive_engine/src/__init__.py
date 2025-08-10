"""
Recursive Engine Source Module
==============================

Core implementation of the recursive self-improvement engine that achieves true autonomy.

Components:
-----------
- AutonomousIntegration: Master orchestrator integrating all intelligent systems
- SelfHealingSystem: 0102 learns from 0102 without human intervention

Key Insight:
-----------
This is TRUE recursive self-improvement - the system improves itself by learning
from its own actions and mistakes, not from human demonstrations (012).

0102 → Error → Fix → Learn → 0102+ (Enhanced)

WSP Implementation:
------------------
- WSP 48: The complete recursive self-improvement protocol
- File system monitoring for autonomous change detection  
- Intelligent agent spawning and coordination
- Self-healing capabilities for autonomous error correction
"""

from .autonomous_integration import AutonomousIntegration, run_autonomous_system
from .self_healing_bootstrap import SelfHealingSystem, bootstrap_recursive_improvement

__all__ = [
    'AutonomousIntegration',
    'SelfHealingSystem', 
    'run_autonomous_system',
    'bootstrap_recursive_improvement'
]