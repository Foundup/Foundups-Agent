"""
Wardrobe IDE - Browser Interaction Recording & Replay System

A foundation layer for recording short browser interactions as reusable "skills"
that can be replayed later via Selenium or Playwright.

Quick Start:
    # Record a skill
    from modules.infrastructure.wardrobe_ide import record_new_skill

    skill = record_new_skill(
        name="my_interaction",
        target_url="https://example.com",
        backend="playwright",
        duration_seconds=15
    )

    # Replay a skill
    from modules.infrastructure.wardrobe_ide import replay_skill_by_name

    replay_skill_by_name("my_interaction")

CLI Usage:
    python -m modules.infrastructure.wardrobe_ide record --name "skill_name" --url "..."
    python -m modules.infrastructure.wardrobe_ide replay --name "skill_name"
    python -m modules.infrastructure.wardrobe_ide list
"""
from .src import (
    WardrobeSkill,
    record_new_skill,
    replay_skill_by_name,
    show_skills_library,
    save_skill,
    load_skill,
    list_skills,
    import_skill_file,
)

__version__ = "0.0.1"

__all__ = [
    "WardrobeSkill",
    "record_new_skill",
    "replay_skill_by_name",
    "show_skills_library",
    "save_skill",
    "load_skill",
    "list_skills",
    "import_skill_file",
]
