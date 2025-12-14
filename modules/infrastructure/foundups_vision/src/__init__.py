"""
FoundUps Vision - UI-TARS Integration for Vision-Based Browser Automation

Provides 0102's "eyes" for complex browser tasks that require visual understanding.

Public API:
    - UITarsBridge: Connection to UI-TARS Desktop
    - VisionExecutor: Multi-step workflow executor
    - ActionResult: Result of a vision action
    - ActionStep: Single step in a workflow
    - WorkflowResult: Result of a multi-step workflow
    - create_ui_tars_bridge: Factory function

WSP Compliance:
    - WSP 3: Infrastructure domain placement
    - WSP 11: Public API exports
    - WSP 77: AI Overseer integration
"""

__all__ = [
    "UITarsBridge",
    "VisionExecutor",
    "ActionResult",
    "ActionStep",
    "WorkflowResult",
    "create_ui_tars_bridge",
    "ActionPatternLearner",
    "get_learner",
]

# Lazy imports to avoid startup cost
def __getattr__(name):
    if name == "UITarsBridge":
        from .ui_tars_bridge import UITarsBridge
        return UITarsBridge
    elif name == "VisionExecutor":
        from .vision_executor import VisionExecutor
        return VisionExecutor
    elif name == "ActionResult":
        from .ui_tars_bridge import ActionResult
        return ActionResult
    elif name == "ActionStep":
        from .vision_executor import ActionStep
        return ActionStep
    elif name == "WorkflowResult":
        from .vision_executor import WorkflowResult
        return WorkflowResult
    elif name == "create_ui_tars_bridge":
        from .ui_tars_bridge import create_ui_tars_bridge
        return create_ui_tars_bridge
    elif name == "ActionPatternLearner":
        from .action_pattern_learner import ActionPatternLearner
        return ActionPatternLearner
    elif name == "get_learner":
        from .action_pattern_learner import get_learner
        return get_learner
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

