"""LiveChat Module for YouTube DAE Cube.

Keep this package import lightweight.
Importing `modules.communication.livechat` should NOT eagerly import the full
YouTube DAE stack (which pulls in Selenium, network clients, and optional
dependencies).
"""

from __future__ import annotations

from typing import Any

__all__ = ["LiveChatCore", "AutoModeratorDAE"]


def __getattr__(name: str) -> Any:
    if name == "LiveChatCore":
        from .src.livechat_core import LiveChatCore

        return LiveChatCore
    if name == "AutoModeratorDAE":
        from .src.auto_moderator_dae import AutoModeratorDAE

        return AutoModeratorDAE
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
