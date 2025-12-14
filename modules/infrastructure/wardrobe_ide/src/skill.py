"""
Wardrobe Skill - Core skill representation

A WardrobeSkill represents a recorded browser interaction that can be replayed.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


@dataclass
class WardrobeSkill:
    """
    Represents a recorded browser interaction skill.

    Attributes:
        name: Unique skill name (e.g. "yt_like_and_reply")
        backend: Backend used for recording/replay ("playwright" or "selenium")
        steps: List of interaction steps (clicks, types, etc.)
        created_at: Timestamp when skill was created
        meta: Additional metadata (target_url, tags, notes, etc.)
    """
    name: str
    backend: Literal["playwright", "selenium"]
    steps: list[dict[str, Any]]
    created_at: datetime = field(default_factory=datetime.now)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert skill to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "backend": self.backend,
            "steps": self.steps,
            "created_at": self.created_at.isoformat(),
            "meta": self.meta
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "WardrobeSkill":
        """Create skill from dictionary."""
        return cls(
            name=data["name"],
            backend=data["backend"],
            steps=data["steps"],
            created_at=datetime.fromisoformat(data["created_at"]),
            meta=data.get("meta", {})
        )
