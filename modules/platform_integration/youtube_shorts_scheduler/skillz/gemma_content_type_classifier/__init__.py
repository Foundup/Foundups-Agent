"""
Gemma Content Type Classifier Skill

AI-driven content classification for YouTube Shorts scheduling.
Replaces static description_template with dynamic classification.

WSP 95: SKILLz Wardrobe Protocol
"""

from .executor import classify_content, get_pattern_fidelity, ContentType

__all__ = ["classify_content", "get_pattern_fidelity", "ContentType"]
