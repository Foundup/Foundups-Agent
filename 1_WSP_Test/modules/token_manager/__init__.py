"""
Token Manager Module for Windsurf Project
Exports the singleton instance and the class.
"""

# Import the singleton instance and the class from the src file
from .src.token_manager import token_manager, TokenManager

__all__ = ['token_manager', 'TokenManager']
