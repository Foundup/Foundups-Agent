"""LinkedIn Engagement WRE Skill — bridges WRE execute_skill() to linkedin_social_adapter."""
from .executor import execute, get_skill_info  # noqa: F401

__all__ = ["execute", "get_skill_info"]
