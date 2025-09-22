"""
Idle Automation Module
WSP 3: Infrastructure Domain - System Automation
Provides autonomous background task execution during idle periods.
"""

from .src.idle_automation_dae import IdleAutomationDAE, run_idle_automation

__all__ = [
    'IdleAutomationDAE',
    'run_idle_automation'
]

__version__ = "1.0.0"
__wsp_compliance__ = "WSP 3, 27, 35, 48, 60, 70"
