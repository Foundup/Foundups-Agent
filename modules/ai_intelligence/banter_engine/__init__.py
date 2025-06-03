"""
Module definition for banter_engine.
Exposes the main BanterEngine class.
"""

# Import from the src/ directory
from .src.banter_engine import BanterEngine
from .src.emoji_sequence_map import SEQUENCE_MAP, emoji_string_to_tuple

__all__ = ['BanterEngine', 'SEQUENCE_MAP', 'emoji_string_to_tuple']
