"""
Orchestrator Migration Bridge
Provides backward compatibility while transitioning to refactored modules
Maps old simple_posting_orchestrator API to new core components
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import logging
from typing import Dict, Any, Optional

# Import the new refactored orchestrator
from .refactored_posting_orchestrator import (
    RefactoredPostingOrchestrator,
    get_orchestrator
)

# Import old types for compatibility
from .simple_posting_orchestrator import PostResponse, PostResult, Platform


logger = logging.getLogger(__name__)


class MigrationBridge:
    """
    Bridge class that provides backward compatibility
    Maps old API calls to new refactored components
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.new_orchestrator = get_orchestrator()
        self.logger.info("[U+1F309] Migration bridge initialized - using refactored modules")

    def handle_stream_detected(
        self,
        video_id: str,
        title: str,
        url: str,
        channel_name: str
    ) -> Dict[str, Any]:
        """
        Handle stream detection using new orchestrator
        Maintains exact same API as simple_posting_orchestrator

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            channel_name: Channel name/handle

        Returns:
            Results dictionary (same format as before)
        """
        self.logger.info("[REFRESH] Routing through migration bridge to refactored modules")
        return self.new_orchestrator.handle_stream_detected(
            video_id=video_id,
            title=title,
            url=url,
            channel_name=channel_name
        )

    def check_if_already_posted(self, video_id: str) -> Dict[str, Any]:
        """
        Check if video was already posted
        Maps to new DuplicatePreventionManager

        Args:
            video_id: YouTube video ID

        Returns:
            Dictionary with already_posted flag and platforms
        """
        return self.new_orchestrator.duplicate_manager.check_if_already_posted(video_id)

    def mark_as_posted(
        self,
        video_id: str,
        title: str,
        url: str,
        platforms: list
    ) -> bool:
        """
        Mark video as posted
        Maps to new DuplicatePreventionManager

        Args:
            video_id: YouTube video ID
            title: Stream title
            url: Stream URL
            platforms: List of platforms posted to

        Returns:
            Success flag
        """
        return self.new_orchestrator.duplicate_manager.mark_as_posted(
            video_id=video_id,
            title=title,
            url=url,
            platforms=platforms
        )

    def get_posting_stats(self) -> Dict[str, Any]:
        """
        Get posting statistics
        Maps to new orchestrator stats

        Returns:
            Statistics dictionary
        """
        return self.new_orchestrator.get_posting_stats()


# Global instance for backward compatibility
_migration_bridge = None


def get_migration_bridge() -> MigrationBridge:
    """
    Get singleton migration bridge instance

    Returns:
        MigrationBridge instance
    """
    global _migration_bridge
    if _migration_bridge is None:
        _migration_bridge = MigrationBridge()
    return _migration_bridge


# Drop-in replacement functions for simple_posting_orchestrator.py
def handle_stream_detected(video_id: str, title: str, url: str, channel_name: str) -> Dict[str, Any]:
    """
    Drop-in replacement for simple_posting_orchestrator.handle_stream_detected
    Routes to new refactored modules

    Args:
        video_id: YouTube video ID
        title: Stream title
        url: Stream URL
        channel_name: Channel name/handle

    Returns:
        Results dictionary
    """
    bridge = get_migration_bridge()
    return bridge.handle_stream_detected(video_id, title, url, channel_name)


def check_if_already_posted(video_id: str) -> Dict[str, Any]:
    """
    Drop-in replacement for simple_posting_orchestrator.check_if_already_posted
    Routes to new DuplicatePreventionManager

    Args:
        video_id: YouTube video ID

    Returns:
        Dictionary with already_posted flag
    """
    bridge = get_migration_bridge()
    return bridge.check_if_already_posted(video_id)


# Migration instructions
MIGRATION_INSTRUCTIONS = """
=================================================================
SOCIAL MEDIA ORCHESTRATOR - MIGRATION GUIDE
=================================================================

The simple_posting_orchestrator.py (996 lines) has been refactored
into modular components for better maintainability.

NEW ARCHITECTURE:
-----------------
1. DuplicatePreventionManager (291 lines) - Handles duplicate detection
2. LiveStatusVerifier (232 lines) - Verifies stream status
3. ChannelConfigurationManager (283 lines) - Manages channel config
4. PlatformPostingService (400 lines) - Handles platform posting
5. RefactoredPostingOrchestrator (300 lines) - Clean coordinator

MIGRATION OPTIONS:
------------------

Option 1: Use Migration Bridge (Recommended for gradual migration)
------------------------------------------------------------------
# In stream_resolver.py or any calling code:
from modules.platform_integration.social_media_orchestrator.src.orchestrator_migration import (
    handle_stream_detected
)

# Use exactly the same as before - no code changes needed!
result = handle_stream_detected(video_id, title, url, channel_name)


Option 2: Use New Refactored Orchestrator Directly
---------------------------------------------------
# For new code or full refactor:
from modules.platform_integration.social_media_orchestrator.src.refactored_posting_orchestrator import (
    get_orchestrator
)

orchestrator = get_orchestrator()
result = orchestrator.handle_stream_detected(video_id, title, url, channel_name)


Option 3: Use Individual Core Components
-----------------------------------------
# For fine-grained control:
from modules.platform_integration.social_media_orchestrator.src.core import (
    DuplicatePreventionManager,
    LiveStatusVerifier,
    ChannelConfigurationManager,
    PlatformPostingService
)

# Use components independently as needed
duplicate_mgr = DuplicatePreventionManager()
if not duplicate_mgr.check_if_already_posted(video_id)['already_posted']:
    # Post to platforms...


BENEFITS OF REFACTORING:
------------------------
[OK] Single Responsibility - Each module does one thing well
[OK] Testability - Easy to write unit tests for each component
[OK] Maintainability - Changes isolated to specific modules
[OK] Reusability - Components can be used independently
[OK] Clarity - 996 lines split into 5 focused modules
[OK] Performance - Same functionality, better organized

NEXT STEPS:
-----------
1. Test with migration bridge first
2. Gradually update imports to use refactored modules
3. Remove simple_posting_orchestrator.py once migration complete
4. Update documentation and tests

=================================================================
"""


def print_migration_guide():
    """Print migration instructions"""
    print(MIGRATION_INSTRUCTIONS)


if __name__ == "__main__":
    print_migration_guide()