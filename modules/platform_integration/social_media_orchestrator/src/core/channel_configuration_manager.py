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
    FOUNDUPS = "105793707"
    GEOZAI = "106064089"


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
                'channel_id': 'UCMjyY1Sh8TAQCTnSGiLVGnQ',
                'channel_name': 'Move 2 Japan',
                'linkedin_page': LinkedInPage.GEOZAI.value,
                'x_account': XAccount.MOVE2JAPAN.value,
                'use_foundups_x': False,
                'enabled': True
            }
        }

        # Try to load from file
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    for channel, config in default_config.items():
                        if channel in loaded_config:
                            config.update(loaded_config[channel])
                    self.channel_configs = default_config
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
            with open(self.config_path, 'w') as f:
                json.dump(self.channel_configs, f, indent=2)
            self.logger.info(f"[CONFIG] Saved configuration to {self.config_path}")
        except Exception as e:
            self.logger.error(f"[CONFIG] Failed to save configuration: {e}")

    def get_channel_config(self, channel_name: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific channel

        Args:
            channel_name: Channel name or handle

        Returns:
            Channel configuration dictionary or None
        """
        # Try exact match first
        if channel_name in self.channel_configs:
            return self.channel_configs[channel_name].copy()

        # Try case-insensitive match
        for key, config in self.channel_configs.items():
            if key.lower() == channel_name.lower():
                return config.copy()

        # Try matching by channel_name field
        for config in self.channel_configs.values():
            if config.get('channel_name', '').lower() == channel_name.lower():
                return config.copy()

        self.logger.warning(f"[CONFIG] No configuration found for channel: {channel_name}")
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