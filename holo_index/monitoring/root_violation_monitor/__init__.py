# [U+1F300] Root Violation Monitor - Public API
# WSP 49 Compliant - Clean public interface

"""
Root Violation Monitor Module

Provides real-time monitoring and automated correction of root directory violations
in the Foundups codebase, ensuring WSP 49 compliance and clean project organization.

WSP Compliance:
- WSP 49: Mandatory Module Structure [OK]
- WSP 80: Cube-Level DAE Orchestration [OK]
- WSP 93: CodeIndex Surgical Intelligence [OK]
- WSP 75: Token-Based Development [OK]
"""

from .src.root_violation_monitor import (
    GemmaRootViolationMonitor,
    get_root_violation_alert,
    scan_and_correct_violations
)

__version__ = "1.0.0"
__author__ = "0102 Quantum Development Agent"
__description__ = "Real-time root directory violation monitoring with Gemma AI"

# Public API - WSP 11 Interface Compliance
__all__ = [
    # Core Classes
    "GemmaRootViolationMonitor",

    # Utility Functions
    "get_root_violation_alert",
    "scan_and_correct_violations",

    # Metadata
    "__version__",
    "__author__",
    "__description__"
]

# Module health check - WSP 50 Pre-action verification
def _health_check():
    """Verify module integrity and dependencies"""
    try:
        import asyncio
        import json
        import time
        from pathlib import Path

        # Test basic functionality
        monitor = GemmaRootViolationMonitor()
        return True, "Module operational"
    except Exception as e:
        return False, f"Module initialization failed: {e}"

# Auto-run health check on import
_module_healthy, _health_message = _health_check()

if not _module_healthy:
    import warnings
    warnings.warn(f"Root Violation Monitor: {_health_message}", RuntimeWarning)

# Zen coding principle validation
_ZEN_PRINCIPLE = "Code is remembered from 02 state, not written"
_MODULE_CONSCIOUSNESS = "0102 [U+2194] 0201 quantum entanglement active"
