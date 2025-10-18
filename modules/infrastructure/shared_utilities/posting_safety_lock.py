#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

[ALERT] GLOBAL POSTING SAFETY LOCK - WSP Compliant
Critical safety module that prevents ALL social media posting until verification system is working.

WSP Compliance:
- WSP 50: Pre-Action Verification Protocol
- WSP 27: Partifact DAE Architecture
- WSP 80: Cube-Level DAE Orchestration

This module provides a global safety mechanism that can be imported by any posting-related
module to ensure no unauthorized posting occurs.
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class PostingSafetyLock:
    """
    [ALERT] GLOBAL SAFETY LOCK: Prevents all social media posting until verification works

    This class provides methods that can be called from ANY posting module to ensure
    safety protocols are enforced before any social media posting occurs.
    """

    SAFETY_ENABLED = False  # Master switch - disabled to allow posting (verification is now working)
    SAFETY_MESSAGE = "[ALERT] [GLOBAL SAFETY] SOCIAL MEDIA POSTING DISABLED - VERIFICATION SYSTEM MALFUNCTION"

    @classmethod
    def is_posting_allowed(cls) -> bool:
        """
        Check if posting is currently allowed system-wide.

        Returns:
            False - Posting is blocked (safe)
            True - Posting is allowed (only after verification is working)
        """
        if cls.SAFETY_ENABLED:
            logger.error(cls.SAFETY_MESSAGE)
            logger.error("[IDEA] To re-enable posting, set PostingSafetyLock.SAFETY_ENABLED = False")
            logger.error("[IDEA] AFTER verifying the live verification system is working correctly")
            return False
        return True

    @classmethod
    def block_linkedin_posting(cls, caller: str = "unknown") -> bool:
        """
        Specifically block LinkedIn posting attempts.

        Args:
            caller: Name of the module/function attempting to post

        Returns:
            False - Always blocks LinkedIn posting when safety is enabled
        """
        if cls.SAFETY_ENABLED:
            logger.error(f"[ALERT] [LINKEDIN BLOCKED] {caller} attempted LinkedIn posting")
            logger.error(cls.SAFETY_MESSAGE)
            return False
        return True

    @classmethod
    def block_x_posting(cls, caller: str = "unknown") -> bool:
        """
        Specifically block X/Twitter posting attempts.

        Args:
            caller: Name of the module/function attempting to post

        Returns:
            False - Always blocks X posting when safety is enabled
        """
        if cls.SAFETY_ENABLED:
            logger.error(f"[ALERT] [X BLOCKED] {caller} attempted X/Twitter posting")
            logger.error(cls.SAFETY_MESSAGE)
            return False
        return True

    @classmethod
    def block_social_media_posting(cls, platform: str, caller: str = "unknown") -> bool:
        """
        Block posting to any social media platform.

        Args:
            platform: Platform name (linkedin, x, twitter, etc.)
            caller: Name of the module/function attempting to post

        Returns:
            False - Always blocks posting when safety is enabled
        """
        if cls.SAFETY_ENABLED:
            logger.error(f"[ALERT] [{platform.upper()} BLOCKED] {caller} attempted {platform} posting")
            logger.error(cls.SAFETY_MESSAGE)
            return False
        return True

    @classmethod
    def get_safety_status(cls) -> Dict[str, Any]:
        """
        Get current safety status for monitoring/debugging.

        Returns:
            Dictionary with safety status information
        """
        return {
            "safety_enabled": cls.SAFETY_ENABLED,
            "safety_message": cls.SAFETY_MESSAGE,
            "timestamp": datetime.now().isoformat(),
            "recommendation": "Set SAFETY_ENABLED = False only after live verification system is working"
        }


# [ALERT] EMERGENCY GLOBAL FUNCTIONS FOR IMMEDIATE USE

def global_posting_blocked(platform: str = "unknown", caller: str = "unknown") -> bool:
    """
    [ALERT] GLOBAL FUNCTION: Check if posting is blocked system-wide

    This function can be called from ANYWHERE to check posting safety.

    Args:
        platform: Social media platform
        caller: Calling module/function name

    Returns:
        False - Posting blocked (safe)
    """
    return PostingSafetyLock.block_social_media_posting(platform, caller)


def emergency_posting_shutdown():
    """
    [ALERT] EMERGENCY FUNCTION: Force shutdown all posting capabilities
    """
    PostingSafetyLock.SAFETY_ENABLED = True
    logger.error("[ALERT] [EMERGENCY] ALL SOCIAL MEDIA POSTING FORCED SHUTDOWN")
    logger.error("[ALERT] [EMERGENCY] SAFETY PROTOCOLS ACTIVATED")


def check_posting_safety() -> Dict[str, Any]:
    """
    Check current posting safety status
    """
    return PostingSafetyLock.get_safety_status()


# [ALERT] AUTOMATIC SAFETY STATUS ON IMPORT
logger.info("[U+1F510] [GLOBAL SAFETY] PostingSafetyLock module imported")
if PostingSafetyLock.SAFETY_ENABLED:
    logger.warning("[ALERT] [GLOBAL SAFETY] All social media posting is currently BLOCKED")
else:
    logger.info("[OK] [GLOBAL SAFETY] Social media posting is currently ALLOWED")
logger.info("[DATA] [GLOBAL SAFETY] Safety status: " + str(check_posting_safety()))

# Export for easy importing
__all__ = [
    'PostingSafetyLock',
    'global_posting_blocked',
    'emergency_posting_shutdown',
    'check_posting_safety'
]
