"""
Banter Engine Singleton

Provides singleton access to BanterEngine to prevent multiple initializations.
Fixes repeated "BanterEngine initialized" logs and reduces LLM connector overhead.

WSP 84: Code Reuse - Singleton pattern for heavy components
WSP 48: Recursive Learning - Reuse pattern memory across instances

Usage:
    from modules.ai_intelligence.banter_engine.src.banter_singleton import get_banter_engine

    banter = get_banter_engine()
    response = banter.generate_response(...)
"""

import logging
from typing import Optional
from .banter_engine import BanterEngine

logger = logging.getLogger(__name__)

# Module-level singleton instance
_banter_instance: Optional[BanterEngine] = None
_initialization_count = 0


def get_banter_engine(banter_file_path=None, emoji_enabled=True) -> BanterEngine:
    """
    Get or create singleton BanterEngine instance.

    First call initializes BanterEngine with LLM connectors.
    Subsequent calls return the same instance (avoiding repeated init).

    Args:
        banter_file_path: Optional path to external banter JSON file
        emoji_enabled: Flag to indicate if emoji usage is preferred

    Returns:
        BanterEngine: Singleton instance
    """
    global _banter_instance, _initialization_count

    if _banter_instance is None:
        _initialization_count += 1
        logger.info(f"[BANTER-SINGLETON] Initializing BanterEngine (first use)")
        _banter_instance = BanterEngine(
            banter_file_path=banter_file_path,
            emoji_enabled=emoji_enabled
        )
        logger.info(f"[BANTER-SINGLETON] BanterEngine singleton created")
    else:
        logger.debug(f"[BANTER-SINGLETON] Reusing existing BanterEngine instance")

    return _banter_instance


def reset_banter_engine():
    """
    Reset the singleton instance (for testing or reconfiguration).

    WARNING: Only use for testing or when configuration changes require reset.
    """
    global _banter_instance, _initialization_count

    if _banter_instance is not None:
        logger.warning("[BANTER-SINGLETON] Resetting BanterEngine singleton")
        _banter_instance = None


def get_initialization_stats() -> dict:
    """
    Get singleton initialization statistics.

    Returns:
        dict: Stats including initialization count and instance state
    """
    return {
        "initialization_count": _initialization_count,
        "instance_active": _banter_instance is not None,
        "llm_enabled": _banter_instance.use_llm if _banter_instance else False
    }
