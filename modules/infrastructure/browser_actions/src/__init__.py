"""
Browser Actions - Platform Action Router

Routes browser automation actions to the optimal driver (Selenium or UI-TARS).

Public API:
    - ActionRouter: Intelligent driver routing
    - DriverType: Driver type enum (SELENIUM, VISION, AUTO)
    - RoutingResult: Result of routed action
    - YouTubeActions: YouTube automation
    - LinkedInActions: LinkedIn automation (coming soon)
    - XActions: X/Twitter automation (coming soon)
    - create_action_router: Factory function

WSP Compliance:
    - WSP 3: Infrastructure domain placement
    - WSP 11: Public API exports
    - WSP 77: AI Overseer integration
"""

__all__ = [
    "ActionRouter",
    "DriverType",
    "RoutingResult",
    "YouTubeActions",
    "LinkedInActions",
    "XActions",
    "FoundUpActions",
    "create_action_router",
    "BrowserActionsCoordinator",
    "get_coordinator",
    "TelemetryDashboard",
    "get_dashboard",
]

# Lazy imports to avoid startup cost
def __getattr__(name):
    if name == "ActionRouter":
        from .action_router import ActionRouter
        return ActionRouter
    elif name == "DriverType":
        from .action_router import DriverType
        return DriverType
    elif name == "RoutingResult":
        from .action_router import RoutingResult
        return RoutingResult
    elif name == "YouTubeActions":
        from .youtube_actions import YouTubeActions
        return YouTubeActions
    elif name == "LinkedInActions":
        from .linkedin_actions import LinkedInActions
        return LinkedInActions
    elif name == "XActions":
        from .x_actions import XActions
        return XActions
    elif name == "FoundUpActions":
        from .foundups_actions import FoundUpActions
        return FoundUpActions
    elif name == "create_action_router":
        from .action_router import create_action_router
        return create_action_router
    elif name == "BrowserActionsCoordinator":
        from .ai_overseer_integration import BrowserActionsCoordinator
        return BrowserActionsCoordinator
    elif name == "get_coordinator":
        from .ai_overseer_integration import get_coordinator
        return get_coordinator
    elif name == "TelemetryDashboard":
        from .telemetry_dashboard import TelemetryDashboard
        return TelemetryDashboard
    elif name == "get_dashboard":
        from .telemetry_dashboard import get_dashboard
        return get_dashboard
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

