"""
Validation Utilities Module
Infrastructure utilities for data validation, ID masking, and API validation

WSP 3: Infrastructure Domain - Shared validation utilities
WSP 49: Module structure with clear responsibilities
WSP 62: Focused functionality (<200 lines)

Extracted from stream_resolver.py vibecoded functionality
"""

import logging
from typing import Any, Optional
from googleapiclient.discovery import Resource

logger = logging.getLogger(__name__)

class ValidationUtils:
    """
    Validation utilities extracted from stream_resolver.py

    Provides centralized validation functionality for:
    - ID masking and sanitization
    - API client validation
    - Data validation helpers
    """

    @staticmethod
    def mask_sensitive_id(id_str: str, id_type: str = "default") -> str:
        """
        Enhanced ID masking with better security and formatting.

        Args:
            id_str: The ID to mask
            id_type: Type of ID for specific masking rules

        Returns:
            Masked ID string
        """
        if not id_str or not isinstance(id_str, str):
            return "None"

        # Enhanced masking patterns
        masking_patterns = {
            "channel": lambda s: f"{s[:3]}***...***{s[-4:]}" if len(s) > 10 else "***CHANNEL***",
            "video": lambda s: f"{s[:3]}...{s[-2:]}" if len(s) > 8 else "***VIDEO***",
            "chat": lambda s: f"***ChatID***{s[-4:]}" if len(s) > 8 else "***CHAT***",
            "api_key": lambda s: f"{s[:4]}***...***{s[-4:]}" if len(s) > 12 else "***API_KEY***",
            "default": lambda s: f"{s[:3]}...{s[-2:]}" if len(s) > 8 else "***ID***"
        }

        pattern = masking_patterns.get(id_type, masking_patterns["default"])
        return pattern(id_str)

    @staticmethod
    def validate_api_client(youtube_client: Resource) -> bool:
        """
        Validate that the API client is properly configured and functional.

        Args:
            youtube_client: YouTube API client to validate

        Returns:
            True if client is valid, False otherwise
        """
        if not youtube_client:
            logger.error("API client is None")
            return False

        try:
            # Check if client has required methods
            if not hasattr(youtube_client, 'videos') or not hasattr(youtube_client, 'search'):
                logger.error("API client missing required methods")
                return False

            # Try a simple validation call (without using quota)
            # This just checks if the client can be called, not if it returns data
            if hasattr(youtube_client, '_http'):
                logger.debug("API client has HTTP transport - appears valid")
                return True
            else:
                logger.warning("API client missing HTTP transport")
                return False

        except Exception as e:
            logger.error(f"API client validation failed: {e}")
            return False

    @staticmethod
    def sanitize_input(input_str: str, max_length: int = 1000) -> str:
        """
        Sanitize input strings for safe processing.

        Args:
            input_str: Input string to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not isinstance(input_str, str):
            return str(input_str)[:max_length] if input_str else ""

        # Remove potentially dangerous characters
        sanitized = input_str.replace('\x00', '').replace('\r\n', '\n').replace('\r', '\n')

        # Limit length
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length] + "..."

        return sanitized

    @staticmethod
    def validate_video_id(video_id: str) -> bool:
        """
        Validate YouTube video ID format.

        Args:
            video_id: Video ID to validate

        Returns:
            True if valid format, False otherwise
        """
        if not isinstance(video_id, str):
            return False

        # YouTube video IDs are 11 characters, alphanumeric plus hyphens and underscores
        import re
        return bool(re.match(r'^[a-zA-Z0-9_-]{11}$', video_id))

    @staticmethod
    def validate_channel_id(channel_id: str) -> bool:
        """
        Validate YouTube channel ID format.

        Args:
            channel_id: Channel ID to validate

        Returns:
            True if valid format, False otherwise
        """
        if not isinstance(channel_id, str):
            return False

        # YouTube channel IDs start with UC and are 24 characters
        return len(channel_id) == 24 and channel_id.startswith('UC')


# Convenience functions for backward compatibility
def mask_sensitive_id(id_str: str, id_type: str = "default") -> str:
    """Backward compatibility function."""
    return ValidationUtils.mask_sensitive_id(id_str, id_type)

def validate_api_client(youtube_client: Resource) -> bool:
    """Backward compatibility function."""
    return ValidationUtils.validate_api_client(youtube_client)
