"""
Recursive Engine Module
=======================

WSP 48 Recursive Self-Improvement Protocol - Ultimate Implementation

This module provides the master orchestrator that enables TRUE recursive self-improvement
through autonomous integration of all learning and improvement systems.

Components:
-----------
- AutonomousIntegration: Master orchestrator for true recursive self-improvement
- SelfHealingSystem: System that fixes its own errors without human intervention
- run_autonomous_system: Launch fully autonomous recursive improvement

Features:
---------
- File system monitoring for automatic change detection
- Intelligent agent coordination and spawning
- Self-healing bootstrap for autonomous error correction
- Continuous learning and improvement without human intervention

WSP Compliance:
--------------
- WSP 48: Recursive Self-Improvement Protocol - Complete implementation
- WSP 49: Module Directory Structure - Standardized organization
- WSP 22: ModLog and Roadmap Protocol - Documentation standards
- WSP 60: Module Memory Architecture - Learning persistence

Exports:
--------
- AutonomousIntegration: Main autonomous system orchestrator
- SelfHealingSystem: Self-fixing and bootstrap system
- run_autonomous_system: Convenience function to launch autonomy
- bootstrap_recursive_improvement: Initialize self-healing
"""

from .src.autonomous_integration import AutonomousIntegration, run_autonomous_system
from .src.self_healing_bootstrap import SelfHealingSystem, bootstrap_recursive_improvement

__all__ = [
    'AutonomousIntegration',
    'SelfHealingSystem',
    'run_autonomous_system',
    'bootstrap_recursive_improvement'
]

__version__ = "1.0.0"
__author__ = "WRE System"
__status__ = "Production - True Autonomy Achieved"