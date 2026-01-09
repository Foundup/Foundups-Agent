"""
FoundUps Selenium - Browser Automation Infrastructure

Provides browser automation capabilities with anti-detection, telemetry, and session management.

Public API:
    - FoundUpsDriver: Enhanced Selenium WebDriver with telemetry
    - BrowserManager: Singleton browser session manager
    - get_browser_manager: Factory function for BrowserManager
    - TelemetryStore: Browser action telemetry storage

WSP Compliance:
    - WSP 3: Infrastructure domain placement
    - WSP 11: Public API exports
    - WSP 77: AI Overseer telemetry integration
"""

from .foundups_driver import FoundUpsDriver
from .browser_manager import BrowserManager, get_browser_manager
from .telemetry_store import TelemetryStore
from .foundup_typer import FoundupsTyper, get_typer
from .human_behavior import HumanBehavior, get_human_behavior

__all__ = [
    "FoundUpsDriver",
    "BrowserManager",
    "get_browser_manager",
    "TelemetryStore",
    "FoundupsTyper",
    "get_typer",
    "HumanBehavior",
    "get_human_behavior",
]

__version__ = "1.0.0"
