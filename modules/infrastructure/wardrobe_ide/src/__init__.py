"""
Wardrobe IDE - Browser interaction recording and replay system

Core modules for recording, storing, and replaying browser interactions as reusable skills.
"""
from .skill import WardrobeSkill
from .recorder import record_new_skill, replay_skill_by_name, show_skills_library
from .skills_store import save_skill, load_skill, list_skills, import_skill_file

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
