"""
Channel Routing Configuration
Maps YouTube channels to social media accounts per WSP 3 functional distribution.

This module centralizes channel → social media routing logic that was previously
scattered across stream_resolver and social_media_orchestrator.

WSP 3: Functional Distribution - Routing is social media concern, not stream resolution
WSP 62: Large File Refactoring - Extracted from stream_resolver.py
WSP 84: Code Memory - Surgical refactoring documented in docs/session_backups/
"""

from typing import Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ChannelRouting:
    """Complete routing configuration for a YouTube channel"""
    channel_id: str
    channel_name: str
    linkedin_page_id: str
    x_account: str
    enabled: bool = True

    def __str__(self) -> str:
        return f"{self.channel_name} → LinkedIn:{self.linkedin_page_id}, X:@{self.x_account}"


class SocialMediaRouter:
    """
    Centralized routing for YouTube channels → social media accounts.

    Replaces inline routing logic from:
    - stream_resolver.py:_get_linkedin_page_for_channel()
    - stream_resolver.py:_get_channel_display_name()
    - PlatformPostingService page mappings

    Benefits:
    - Single source of truth for channel routing
    - Testable routing logic
    - Easy to add new channels
    - Clean separation of concerns
    """

    # Channel routing mappings (single source of truth)
    CHANNEL_MAPPINGS = {
        'UCSNTUXjAgpd4sgWYP0xoJgw': ChannelRouting(
            channel_id='UCSNTUXjAgpd4sgWYP0xoJgw',
            channel_name='UnDaoDu',
            linkedin_page_id='165749317',
            x_account='undaodu',
            enabled=True
        ),
        'UC-LSSlOZwpGIRIYihaz8zCw': ChannelRouting(
            channel_id='UC-LSSlOZwpGIRIYihaz8zCw',
            channel_name='FoundUps',
            linkedin_page_id='1263645',
            x_account='foundups',
            enabled=True
        ),
        'UCklMTNnu5POwRmQsg5JJumA': ChannelRouting(
            channel_id='UCklMTNnu5POwRmQsg5JJumA',
            channel_name='Move2Japan',
            linkedin_page_id='104834798',  # GeoZai page
            x_account='geozai',
            enabled=True
        )
    }

    # Display names with visual indicators (from stream_resolver)
    DISPLAY_NAMES = {
        'UCSNTUXjAgpd4sgWYP0xoJgw': 'UnDaoDu [MINDFUL]',
        'UC-LSSlOZwpGIRIYihaz8zCw': 'FoundUps [LOYAL]',
        'UCklMTNnu5POwRmQsg5JJumA': 'Move2Japan [JAPAN]'
    }

    @classmethod
    def get_routing(cls, channel_id: str) -> Optional[ChannelRouting]:
        """
        Get complete routing configuration for a YouTube channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            ChannelRouting object or None if channel not configured
        """
        routing = cls.CHANNEL_MAPPINGS.get(channel_id)
        if routing:
            logger.debug(f"[ROUTING] Found config for {channel_id}: {routing}")
        else:
            logger.warning(f"[ROUTING] No configuration for channel {channel_id}")
        return routing

    @classmethod
    def get_linkedin_page(cls, channel_id: str) -> str:
        """
        Get LinkedIn page ID for a YouTube channel.
        Backward compatible with stream_resolver._get_linkedin_page_for_channel()

        Args:
            channel_id: YouTube channel ID

        Returns:
            LinkedIn page ID (defaults to FoundUps if channel not found)
        """
        routing = cls.get_routing(channel_id)
        if routing and routing.enabled:
            logger.info(f"[ROUTING] {channel_id} → LinkedIn page: {routing.linkedin_page_id} ({routing.channel_name})")
            return routing.linkedin_page_id

        # Fallback to FoundUps (default)
        logger.info(f"[ROUTING] Unknown channel {channel_id}, using default LinkedIn: 1263645 (FoundUps)")
        return '1263645'

    @classmethod
    def get_x_account(cls, channel_id: str) -> str:
        """
        Get X/Twitter account for a YouTube channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            X account name (defaults to 'foundups' if channel not found)
        """
        routing = cls.get_routing(channel_id)
        if routing and routing.enabled:
            return routing.x_account
        return 'foundups'  # Default

    @classmethod
    def get_display_name(cls, channel_id: str) -> str:
        """
        Get human-readable channel name with visual indicator.
        Replaces stream_resolver._get_channel_display_name()

        Args:
            channel_id: YouTube channel ID

        Returns:
            Display name (e.g., "UnDaoDu [MINDFUL]")
        """
        display = cls.DISPLAY_NAMES.get(channel_id)
        if display:
            return display

        # Fallback to channel config name or truncated ID
        routing = cls.get_routing(channel_id)
        if routing:
            return routing.channel_name

        return f"Channel-{channel_id[:8]}"

    @classmethod
    def is_posting_enabled(cls, channel_id: str) -> bool:
        """
        Check if social media posting is enabled for a channel.

        Args:
            channel_id: YouTube channel ID

        Returns:
            True if posting enabled, False otherwise
        """
        routing = cls.get_routing(channel_id)
        if routing:
            return routing.enabled
        return False  # Unknown channels disabled by default

    @classmethod
    def get_all_channels(cls) -> list[str]:
        """
        Get list of all configured channel IDs.

        Returns:
            List of YouTube channel IDs
        """
        return list(cls.CHANNEL_MAPPINGS.keys())

    @classmethod
    def validate_linkedin_page(cls, linkedin_page_id: str) -> bool:
        """
        Validate that a LinkedIn page ID is configured.
        Used by PlatformPostingService for validation.

        Args:
            linkedin_page_id: LinkedIn page ID to validate

        Returns:
            True if page ID is valid, False otherwise
        """
        valid_pages = {r.linkedin_page_id for r in cls.CHANNEL_MAPPINGS.values()}
        return linkedin_page_id in valid_pages


# Convenience functions for backward compatibility
def get_linkedin_page_for_channel(channel_id: str) -> str:
    """Backward compatible wrapper for stream_resolver"""
    return SocialMediaRouter.get_linkedin_page(channel_id)


def get_channel_display_name(channel_id: str) -> str:
    """Backward compatible wrapper for stream_resolver"""
    return SocialMediaRouter.get_display_name(channel_id)
