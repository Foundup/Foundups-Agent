"""
Stream Session Logger - Wrapper for ChatMemoryManager session logging.
This module provides backward compatibility for session logging functionality.
"""

from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager

# Global instance for session logging
_session_logger = None

def get_session_logger():
    """
    Get or create a singleton session logger instance.
    Returns a ChatMemoryManager instance for session logging.
    """
    global _session_logger
    if _session_logger is None:
        _session_logger = ChatMemoryManager()
    return _session_logger

# For direct import compatibility
SessionLogger = ChatMemoryManager