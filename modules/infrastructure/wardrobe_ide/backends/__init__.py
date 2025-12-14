"""
Wardrobe IDE Backends - Backend interface and resolver

Backends handle recording and replaying browser interactions.
"""
from abc import ABC, abstractmethod
from typing import Any

from ..src.skill import WardrobeSkill


class WardrobeBackendBase(ABC):
    """
    Abstract base class for Wardrobe IDE backends.

    Backends are responsible for:
    1. Recording browser interactions as a list of steps
    2. Replaying recorded skills in a browser
    """

    @abstractmethod
    def record_session(
        self,
        target_url: str,
        duration_seconds: int = 15
    ) -> list[dict[str, Any]]:
        """
        Record a browser interaction session.

        Args:
            target_url: URL to navigate to for recording
            duration_seconds: How long to record (default 15s)

        Returns:
            List of recorded steps, each step is a dict with:
            - action: "click" | "type" | "navigate" | etc.
            - selector: CSS selector for the element
            - value/text: For type actions
            - timestamp: Relative timestamp from session start
        """
        pass

    @abstractmethod
    def replay_skill(self, skill: WardrobeSkill) -> None:
        """
        Replay a recorded skill.

        Args:
            skill: The WardrobeSkill to replay

        Note:
            Should navigate to skill.meta["target_url"] if present,
            then execute each step in skill.steps sequentially.
        """
        pass


def get_backend(name: str) -> WardrobeBackendBase:
    """
    Get a backend instance by name.

    Args:
        name: Backend name ("playwright" or "selenium")

    Returns:
        Backend instance

    TODO: Plug in 0102-based backend selection here
          (e.g. choose best backend per domain/skill using AI/LLM)
    """
    if name == "playwright":
        from .playwright_backend import PlaywrightBackend
        return PlaywrightBackend()
    elif name == "selenium":
        from .selenium_backend import SeleniumBackend
        return SeleniumBackend()
    elif name == "tars":
        from .tars_backend import TarsBackend
        return TarsBackend()
    else:
        raise ValueError(f"Unknown backend: {name}. Use 'playwright', 'selenium', or 'tars'.")


__all__ = ["WardrobeBackendBase", "get_backend"]
