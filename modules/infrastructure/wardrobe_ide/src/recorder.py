"""
Recorder - Orchestration layer for Wardrobe Skills recording and replay

Provides Python API and CLI for recording and replaying browser interactions.
"""
from datetime import datetime
from typing import Optional

from .skill import WardrobeSkill
from .skills_store import save_skill, load_skill, list_skills
from ..backends import get_backend
from .config import DEFAULT_BACKEND, DEFAULT_RECORD_DURATION


def record_new_skill(
    name: str,
    target_url: str,
    backend: str = DEFAULT_BACKEND,
    duration_seconds: int = DEFAULT_RECORD_DURATION,
    tags: Optional[list[str]] = None,
    notes: Optional[str] = None
) -> WardrobeSkill:
    """
    Record a new Wardrobe Skill.

    Opens a browser, navigates to target_url, records interactions for
    the specified duration, then saves the skill to the library.

    Args:
        name: Skill name (e.g. "yt_like_and_reply")
        target_url: URL to navigate to for recording
        backend: Backend to use ("playwright" or "selenium")
        duration_seconds: How long to record (default from config)
        tags: Optional tags for categorization
        notes: Optional notes about the skill

    Returns:
        The created WardrobeSkill

    Example:
        >>> skill = record_new_skill(
        ...     name="YouTube Like",
        ...     target_url="https://studio.youtube.com/...",
        ...     backend="playwright",
        ...     duration_seconds=20,
        ...     tags=["youtube", "engagement"]
        ... )
    """
    print(f"[RECORDER] Recording new skill: '{name}'")
    print(f"[RECORDER] Backend: {backend}")
    print(f"[RECORDER] Target URL: {target_url}")
    print(f"[RECORDER] Duration: {duration_seconds}s")

    # Get backend instance
    backend_instance = get_backend(backend)

    # Record session
    steps = backend_instance.record_session(
        target_url=target_url,
        duration_seconds=duration_seconds
    )

    # Create skill object
    skill = WardrobeSkill(
        name=name,
        backend=backend,
        steps=steps,
        created_at=datetime.now(),
        meta={
            "target_url": target_url,
            "tags": tags or [],
            "notes": notes or "",
            "step_count": len(steps)
        }
    )

    # Save to library
    save_skill(skill)

    print(f"[RECORDER] Skill '{name}' recorded successfully!")
    print(f"[RECORDER] {len(steps)} steps captured")

    return skill


def replay_skill_by_name(
    name: str,
    backend: Optional[str] = None
) -> None:
    """
    Replay a skill from the library by name.

    Args:
        name: Skill name
        backend: Optional backend override (uses skill's recorded backend if None)

    Example:
        >>> replay_skill_by_name("YouTube Like")
        >>> replay_skill_by_name("YouTube Like", backend="selenium")
    """
    print(f"[RECORDER] Loading skill: '{name}'")

    # Load skill
    skill = load_skill(name, backend=backend)

    if not skill:
        print(f"[RECORDER] Failed to load skill '{name}'")
        return

    # Determine backend to use
    replay_backend = backend or skill.backend
    print(f"[RECORDER] Replaying with backend: {replay_backend}")

    # Get backend instance
    backend_instance = get_backend(replay_backend)

    # Replay
    backend_instance.replay_skill(skill)

    print(f"[RECORDER] Replay complete")


def show_skills_library(backend_filter: Optional[str] = None) -> None:
    """
    Display all skills in the library.

    Args:
        backend_filter: Optional backend filter
    """
    print("[RECORDER] Skills Library")
    print("=" * 80)

    skills = list_skills(filter_backend=backend_filter)

    if not skills:
        print("No skills found.")
        print("\nCreate a skill with:")
        print("  python -m modules.infrastructure.wardrobe_ide record ...")
        return

    for i, skill in enumerate(skills, 1):
        print(f"\n{i}. {skill.name}")
        print(f"   Backend: {skill.backend}")
        print(f"   Created: {skill.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Steps: {len(skill.steps)}")
        if skill.meta.get("tags"):
            print(f"   Tags: {', '.join(skill.meta['tags'])}")
        if skill.meta.get("notes"):
            print(f"   Notes: {skill.meta['notes']}")
        print(f"   URL: {skill.meta.get('target_url', 'N/A')}")

    print(f"\n{'-' * 80}")
    print(f"Total skills: {len(skills)}")


# TODO: Future enhancements
# - Accept tasks triggered remotely by 0102
#   (e.g. "run skill yt_like_and_reply on host PC")
# - Add validation/verification after replay
# - Support skill composition (chain multiple skills)
# - Add screenshot capture during record/replay
# - Integration with Chrome extension / desktop popup UI
