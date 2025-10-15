#!/usr/bin/env python3
"""
Configuration for Stream Resolver Module
WSP 70: Externalized configuration for maintainability
"""

import os
from typing import Dict, Any

class StreamResolverConfig:
    """Configuration management for stream resolver components."""

    # Default configuration values
    DEFAULT_CONFIG = {
        # Timeouts and delays
        'request_timeout': 30,
        'retry_delay_base': 1.0,
        'max_retry_delay': 60.0,
        'backoff_multiplier': 2.0,

        # Rate limiting
        'max_requests_per_minute': 60,
        'burst_limit': 10,

        # Messages and strings (externalized for i18n/localization)
        'live_verifier_unavailable_msg': "LiveStatusVerifier not available - will use scraping for verification",
        'stream_checker_description': "Check YouTube stream status without using API quota",
        'quota_exceeded_msg': "Quota exceeded, switching to backup method",
        'verification_success_msg': "Stream verification completed successfully",

        # Logging
        'log_level': 'INFO',
        'log_format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',

        # Database settings
        'db_connection_timeout': 10,
        'db_max_connections': 5,

        # Circuit breaker
        'circuit_breaker_threshold': 5,
        'circuit_breaker_timeout': 300,  # 5 minutes
    }

    def __init__(self, config_file: str = None):
        """Initialize configuration with optional override file."""
        self.config = self.DEFAULT_CONFIG.copy()

        # Load from environment variables
        self._load_from_env()

        # Load from file if specified
        if config_file and os.path.exists(config_file):
            self._load_from_file(config_file)

    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'STREAM_RESOLVER_TIMEOUT': ('request_timeout', int),
            'STREAM_RESOLVER_MAX_REQUESTS': ('max_requests_per_minute', int),
            'STREAM_RESOLVER_LOG_LEVEL': ('log_level', str),
        }

        for env_var, (config_key, type_func) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                try:
                    self.config[config_key] = type_func(value)
                except (ValueError, TypeError):
                    # Invalid value, keep default
                    pass

    def _load_from_file(self, config_file: str):
        """Load configuration from JSON file."""
        import json
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                self.config.update(file_config)
        except (json.JSONDecodeError, IOError):
            # Invalid file, keep current config
            pass

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value

    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values."""
        return self.config.copy()

# Global configuration instance
config = StreamResolverConfig()

# Convenience functions for backward compatibility
def get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value (backward compatibility)."""
    return config.get(key, default)

def get_request_timeout() -> int:
    """Get request timeout."""
    return config.get('request_timeout', 30)

def get_live_verifier_message() -> str:
    """Get LiveStatusVerifier unavailable message."""
    return config.get('live_verifier_unavailable_msg')

def get_stream_checker_description() -> str:
    """Get stream checker description."""
    return config.get('stream_checker_description')
