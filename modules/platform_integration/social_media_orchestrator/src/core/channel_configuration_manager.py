"""
Channel Configuration Manager
Handles channel configuration and platform account mapping
Extracted from simple_posting_orchestrator.py for better separation of concerns
"""

import os
import json
import logging
from typing import Dict, Optional, List, Any
from enum import Enum


class LinkedInPage(Enum):
    """LinkedIn company pages"""
    UNDAODU = "165749317"
    FOUNDUPS = "1263645"  # Corrected FoundUps page ID
    GEOZAI = "104834798"  # Corrected GeoZai page ID for Move2Japan


class XAccount(Enum):
    """X/Twitter accounts"""
    MOVE2JAPAN = "Move2Japan"  # @geozeAI
    FOUNDUPS = "FoundUps"      # @Foundups


class ChannelConfigurationManager:
    """Manages channel configuration and platform account mapping"""

    def __init__(self, config_path: str = None):
        """
        Initialize configuration manager

        Args:
            config_path: Optional path to configuration file
        """
        self.logger = logging.getLogger(self.__class__.__name__)

        # Default configuration path
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config', 'channels_config.json'
        )

        # Channel configurations
        self.channel_configs = {}

        # Platform account mappings
        self.linkedin_to_x_mapping = {
            LinkedInPage.UNDAODU.value: XAccount.MOVE2JAPAN,
            LinkedInPage.FOUNDUPS.value: XAccount.FOUNDUPS,
            LinkedInPage.GEOZAI.value: XAccount.MOVE2JAPAN
        }

        # Load configuration
        self._load_channel_configuration()

    def _load_channel_configuration(self) -> None:
        """Load channel configuration from file or use defaults"""
        # Default configuration
        default_config = {
            '@UnDaoDu': {
                'channel_id': 'UCOdP2Gc3n8xqGaHlDXi-Mbg',
                'channel_name': 'UnDaoDu',
                'linkedin_page': LinkedInPage.UNDAODU.value,
                'x_account': XAccount.MOVE2JAPAN.value,
                'use_foundups_x': False,
                'enabled': True
            },
            '@FoundUps': {
                'channel_id': 'UC8NMhWbOE9OVJF0V4DRmNnQ',
                'channel_name': 'FoundUps',
                'linkedin_page': LinkedInPage.FOUNDUPS.value,
                'x_account': XAccount.FOUNDUPS.value,
                'use_foundups_x': True,
                'enabled': True
            },
            'Move 2 Japan': {
                'channel_id': 'UCklMTNnu5POwRmQsg5JJumA',  # Updated to correct Move2Japan channel ID
                'channel_name': 'Move 2 Japan',
                'linkedin_page': LinkedInPage.GEOZAI.value,
                'x_account': XAccount.MOVE2JAPAN.value,
                'use_foundups_x': False,
                'enabled': True
            },
            'FoundUps1934 [TEST]': {
                'channel_id': 'UCROkIz1wOCP3tPk-1j3umyQ',
                'channel_name': 'FoundUps1934 [TEST]',
                'enabled': False
            }
        }

        # Try to load from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    # Start with loaded config, then add any missing defaults
                    self.channel_configs = loaded_config.copy()
                    # Add any default configs that aren't in the loaded file
                    for channel, config in default_config.items():
                        if channel not in self.channel_configs:
                            self.channel_configs[channel] = config
                    self.logger.info(f"[CONFIG] Loaded channel configuration from {self.config_path}")
            except Exception as e:
                self.logger.warning(f"[CONFIG] Could not load config file: {e}, using defaults")
                self.channel_configs = default_config
        else:
            self.logger.info("[CONFIG] Using default channel configuration")
            self.channel_configs = default_config
            # Save defaults to file
            self._save_configuration()

    def _save_configuration(self) -> None:
        """Save current configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding="utf-8") as f:
                json.dump(self.channel_configs, f, indent=2)
            self.logger.info(f"[CONFIG] Saved configuration to {self.config_path}")
        except Exception as e:
            self.logger.error(f"[CONFIG] Failed to save configuration: {e}")

    def get_channel_config(self, channel_identifier: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific channel

        Args:
            channel_identifier: Channel name, handle, or YouTube channel ID

        Returns:
            Channel configuration dictionary or None
        """
        # First check if it's a YouTube channel ID by searching all configs
        if channel_identifier.startswith('UC'):
            # Search for channel ID in all configs
            for config_name, config in self.channel_configs.items():
                if config.get('channel_id') == channel_identifier:
                    self.logger.info(f"[CONFIG] Found config for channel ID {channel_identifier}: {config_name}")
                    self.logger.info(f"[CONFIG] LinkedIn page: {config.get('linkedin_page')} | X account: {config.get('x_account')}")
                    # Validate configuration
                    if config_name == "Move2Japan" and config.get('linkedin_page') != "104834798":
                        self.logger.error(f"[CONFIG ERROR] Move2Japan should use LinkedIn page 104834798 (GeoZai), not {config.get('linkedin_page')}")
                    elif config_name == "@UnDaoDu" and config.get('linkedin_page') != "165749317":
                        self.logger.error(f"[CONFIG ERROR] UnDaoDu should use LinkedIn page 165749317, not {config.get('linkedin_page')}")
                    elif config_name in ["@FoundUps", "FoundUps"] and config.get('linkedin_page') != "1263645":
                        self.logger.error(f"[CONFIG ERROR] FoundUps should use LinkedIn page 1263645, not {config.get('linkedin_page')}")
                    return config.copy()

            # Fallback to hardcoded mapping if not found
            channel_id_mapping = {
                'UCklMTNnu5POwRmQsg5JJumA': 'Move 2 Japan',  # Updated to correct Move2Japan ID
                'UC-LSSlOZwpGIRIYihaz8zCw': '@UnDaoDu',
                'UC8NMhWbOE9OVJF0V4DRmNnQ': '@FoundUps',
                'UCSNTUXjAgpd4sgWYP0xoJgw': 'FoundUps',  # Alternative FoundUps ID
                'UCOdP2Gc3n8xqGaHlDXi-Mbg': '@UnDaoDu',  # UnDaoDu main ID
                'UCMjyY1Sh8TAQCTnSGiLVGnQ': 'Move 2 Japan'  # Alternative Move 2 Japan ID
            }
            channel_name = channel_id_mapping.get(channel_identifier)
            if channel_name and channel_name in self.channel_configs:
                config = self.channel_configs[channel_name]
                self.logger.info(f"[CONFIG] Found config via mapping for {channel_identifier}: {channel_name}")
                self.logger.info(f"[CONFIG] LinkedIn page: {config.get('linkedin_page')} | X account: {config.get('x_account')}")
                return config.copy()

        # Try exact match first
        if channel_identifier in self.channel_configs:
            return self.channel_configs[channel_identifier].copy()

        # Try case-insensitive match
        for key, config in self.channel_configs.items():
            if key.lower() == channel_identifier.lower():
                return config.copy()

        # Try matching by channel_name field
        for config in self.channel_configs.values():
            if config.get('channel_name', '').lower() == channel_identifier.lower():
                return config.copy()

        self.logger.warning(f"[CONFIG] No configuration found for channel: {channel_identifier}")
        return None

    def get_linkedin_page_for_channel(self, channel_name: str) -> Optional[str]:
        """
        Get LinkedIn page ID for a channel

        Args:
            channel_name: Channel name or handle

        Returns:
            LinkedIn page ID or None
        """
        config = self.get_channel_config(channel_name)
        if config:
            return config.get('linkedin_page')
        return None

    def get_x_account_for_channel(self, channel_name: str) -> Optional[str]:
        """
        Get X/Twitter account for a channel

        Args:
            channel_name: Channel name or handle

        Returns:
            X account name or None
        """
        config = self.get_channel_config(channel_name)
        if config:
            return config.get('x_account')
        return None

    def get_x_account_for_linkedin_page(self, linkedin_page: str) -> Optional[str]:
        """
        Get X/Twitter account that corresponds to a LinkedIn page

        Args:
            linkedin_page: LinkedIn page ID

        Returns:
            X account name or None
        """
        x_account = self.linkedin_to_x_mapping.get(linkedin_page)
        if x_account:
            return x_account.value
        return None

    def should_use_foundups_x(self, channel_name: str) -> bool:
        """
        Check if channel should use FoundUps X account

        Args:
            channel_name: Channel name or handle

        Returns:
            True if should use FoundUps X account
        """
        config = self.get_channel_config(channel_name)
        if config:
            return config.get('use_foundups_x', False)
        return False

    def is_channel_enabled(self, channel_name: str) -> bool:
        """
        Check if channel is enabled for posting

        Args:
            channel_name: Channel name or handle

        Returns:
            True if channel is enabled
        """
        config = self.get_channel_config(channel_name)
        if config:
            return config.get('enabled', True)
        return False

    def get_all_channel_names(self) -> List[str]:
        """Get list of all configured channel names"""
        return list(self.channel_configs.keys())

    def get_enabled_channels(self) -> List[str]:
        """Get list of enabled channels"""
        return [
            name for name, config in self.channel_configs.items()
            if config.get('enabled', True)
        ]

    def update_channel_config(self, channel_name: str, updates: Dict[str, Any]) -> bool:
        """
        Update configuration for a channel

        Args:
            channel_name: Channel name or handle
            updates: Dictionary of updates

        Returns:
            True if successful
        """
        if channel_name in self.channel_configs:
            self.channel_configs[channel_name].update(updates)
            self._save_configuration()
            self.logger.info(f"[CONFIG] Updated configuration for {channel_name}")
            return True

        self.logger.warning(f"[CONFIG] Cannot update - channel not found: {channel_name}")
        return False

    def add_channel(self, channel_name: str, config: Dict[str, Any]) -> bool:
        """
        Add a new channel configuration

        Args:
            channel_name: Channel name or handle
            config: Channel configuration

        Returns:
            True if successful
        """
        if channel_name in self.channel_configs:
            self.logger.warning(f"[CONFIG] Channel already exists: {channel_name}")
            return False

        self.channel_configs[channel_name] = config
        self._save_configuration()
        self.logger.info(f"[CONFIG] Added new channel: {channel_name}")
        return True

    def remove_channel(self, channel_name: str) -> bool:
        """
        Remove a channel configuration

        Args:
            channel_name: Channel name or handle

        Returns:
            True if successful
        """
        if channel_name in self.channel_configs:
            del self.channel_configs[channel_name]
            self._save_configuration()
            self.logger.info(f"[CONFIG] Removed channel: {channel_name}")
            return True

        self.logger.warning(f"[CONFIG] Cannot remove - channel not found: {channel_name}")
        return False

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of current configuration"""
        return {
            'total_channels': len(self.channel_configs),
            'enabled_channels': len(self.get_enabled_channels()),
            'channels': {
                name: {
                    'enabled': config.get('enabled', True),
                    'linkedin_page': config.get('linkedin_page'),
                    'x_account': config.get('x_account')
                }
                for name, config in self.channel_configs.items()
            }
        }
