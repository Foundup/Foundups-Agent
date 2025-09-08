"""
Centralized Activity Control System

Universal throttling and switch system for ALL automated activities across
the entire Foundups Agent system. Provides granular control over:

- LiveChat activities (MagaDoom, 0102 triggers, chat responses)
- AI Intelligence activities (banter engine, learning, pattern recognition)  
- Platform Integration activities (YouTube, social media, API calls)
- Background processes (monitoring, cleanup, health checks)
- Infrastructure activities (WRE, DAE operations, system tasks)

Essential for testing, debugging, and noise reduction across all modules.

🧪 EMBEDDED MODULE DOCUMENTATION (WSP 22)
═══════════════════════════════════════════════════════════════

📖 README.md Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Module: activity_control | Domain: infrastructure | Phase: PoC
Purpose: Universal switch system for all automated activities (testing/debugging)
Status: ACTIVE - Critical for system-wide noise reduction and testing
Dependencies: json, pathlib, typing | WSP Compliance: WSP 22, WSP 49, WSP 85

📊 ModLog.md Key Milestones:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PoC Implementation - Universal switch architecture
🚧 LiveChat integration - MagaDoom, consciousness, API controls
🚧 AI Intelligence integration - Banter, learning, pattern controls  
🚧 Platform integration - Social media, YouTube, monitoring controls

🧪 TestModLog.md Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Coverage: 0% (new module) | Tests: TBD | Performance: <1s config load
Evolution: Foundation for system-wide activity control

🎯 Integration Points (0102 Agents):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Used by: ALL modules with automated activities
• WSP Compliance: WSP 22 (embedded docs), WSP 49 (structure), WSP 85 (placement)
• Usage: from modules.infrastructure.activity_control import is_enabled
• Config: JSON-based with runtime modification and preset support

═══════════════════════════════════════════════════════════════
END EMBEDDED DOCUMENTATION - See separate files for full details
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List, Set
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class UniversalActivityController:
    """
    Centralized controller for ALL automated activities across the entire system.
    
    Provides hierarchical control over:
    - Module-level switches (entire modules on/off)
    - Category-level switches (types of activities)  
    - Activity-level switches (specific features)
    
    Usage Examples:
    - is_enabled('livechat.magadoom.announcements')
    - set_enabled('ai.banter_engine.auto_responses', False)
    - apply_preset('silent_testing')
    - emergency_silence()
    """
    
    _instance = None
    _config: Dict[str, Any] = {}
    _config_file = "modules/infrastructure/activity_control/config/universal_switches.json"
    _activity_registry: Set[str] = set()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize universal activity control system"""
        self._load_config()
        self._notification_callback = None  # Callback for stream notifications
        logger.info("🎛️ Universal Activity Controller initialized")
    
    def _load_config(self):
        """Load configuration from file or create defaults"""
        try:
            config_path = Path(self._config_file)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
                logger.info(f"📖 Loaded universal activity config from {self._config_file}")
            else:
                self._config = self._get_default_config()
                self._save_config()
                logger.info("🔧 Created default universal activity configuration")
        except Exception as e:
            logger.error(f"❌ Failed to load universal activity config: {e}")
            self._config = self._get_default_config()
    
    def _save_config(self):
        """Save current configuration to file"""
        try:
            config_path = Path(self._config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Add metadata
            config_with_meta = {
                **self._config,
                "_metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0.0",
                    "registered_activities": sorted(list(self._activity_registry))
                }
            }
            
            with open(config_path, 'w') as f:
                json.dump(config_with_meta, f, indent=2)
            logger.debug("💾 Saved universal activity configuration")
        except Exception as e:
            logger.error(f"❌ Failed to save universal activity config: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get comprehensive default configuration for all system modules"""
        return {
            # Global System Controls
            "global": {
                "enabled": True,
                "testing_mode": False,
                "debug_mode": False,
                "emergency_silence": False
            },
            
            # LiveChat Module Controls
            "livechat": {
                "enabled": True,
                
                # MagaDoom Gamification
                "magadoom": {
                    "enabled": True,
                    "announcements": True,
                    "level_notifications": True,
                    "leaderboard_updates": True,
                    "spree_announcements": True,
                    "rank_promotions": True,
                    "achievement_notifications": True
                },
                
                # 0102 Consciousness
                "consciousness": {
                    "enabled": True,
                    "emoji_triggers": True,
                    "automatic_responses": True,
                    "pattern_recognition": True,
                    "learning_updates": True
                },
                
                # Chat Activities
                "chat": {
                    "enabled": True,
                    "command_processing": True,
                    "greeting_generation": True,
                    "status_announcements": True,
                    "automatic_moderation": True
                }
            },
            
            # AI Intelligence Module Controls
            "ai": {
                "enabled": True,
                
                # Banter Engine
                "banter_engine": {
                    "enabled": True,
                    "auto_responses": True,
                    "pattern_learning": True,
                    "emoji_processing": True
                },
                
                # Learning Systems
                "learning": {
                    "enabled": True,
                    "pattern_updates": True,
                    "model_training": True,
                    "feedback_processing": True
                }
            },
            
            # Platform Integration Controls
            "platform": {
                "enabled": True,
                
                # API Activities
                "api": {
                    "enabled": True,
                    "youtube_polling": True,
                    "youtube_posting": True,
                    "social_media_posting": True,
                    "stream_monitoring": True,
                    "quota_monitoring": True
                },
                
                # OAuth Management
                "oauth": {
                    "enabled": True,
                    "credential_rotation": True,
                    "quota_management": True,
                    "health_checks": True
                }
            },
            
            # Infrastructure Controls
            "infrastructure": {
                "enabled": True,
                
                # Background Processes
                "background": {
                    "enabled": True,
                    "cleanup_tasks": True,
                    "monitoring": True,
                    "health_checks": True,
                    "log_rotation": True
                },
                
                # WRE Operations
                "wre": {
                    "enabled": True,
                    "recursive_improvement": True,
                    "pattern_optimization": True,
                    "memory_management": True
                }
            },
            
            # Gamification Controls (All Games)
            "gamification": {
                "enabled": True,
                "whack_a_magat": {
                    "enabled": True,
                    "announcements": True,
                    "scoring": True,
                    "leaderboards": True
                }
            },
            
            # Testing and Debug Presets
            "presets": {
                "silent_testing": {
                    "description": "Complete silence - all automated activities disabled",
                    "overrides": {
                        "livechat.magadoom.announcements": False,
                        "livechat.magadoom.level_notifications": False,
                        "livechat.consciousness.automatic_responses": False,
                        "livechat.chat.status_announcements": False,
                        "platform.api.social_media_posting": False,
                        "ai.banter_engine.auto_responses": False,
                        "gamification.whack_a_magat.announcements": False
                    }
                },
                
                "api_testing": {
                    "description": "API testing only - no chat or announcement noise",
                    "overrides": {
                        "livechat.magadoom.enabled": False,
                        "livechat.consciousness.automatic_responses": False,
                        "livechat.chat.status_announcements": False,
                        "ai.banter_engine.auto_responses": False
                    }
                },
                
                "magadoom_off": {
                    "description": "Disable all MagaDoom gamification activities",
                    "overrides": {
                        "livechat.magadoom.enabled": False,
                        "gamification.whack_a_magat.enabled": False
                    }
                },
                
                "consciousness_off": {
                    "description": "Disable 0102 consciousness triggers and responses",
                    "overrides": {
                        "livechat.consciousness.enabled": False,
                        "ai.banter_engine.auto_responses": False
                    }
                },
                
                "emergency_silence": {
                    "description": "Emergency preset - disable all noisy activities immediately",
                    "overrides": {
                        "livechat.magadoom.announcements": False,
                        "livechat.consciousness.automatic_responses": False,
                        "livechat.chat.status_announcements": False,
                        "platform.api.social_media_posting": False,
                        "ai.banter_engine.auto_responses": False,
                        "infrastructure.background.monitoring": False
                    }
                }
            }
        }
    
    def register_activity(self, activity_path: str):
        """Register an activity with the controller for tracking"""
        self._activity_registry.add(activity_path)
        logger.debug(f"📝 Registered activity: {activity_path}")
    
    def is_enabled(self, activity_path: str) -> bool:
        """
        Check if a specific activity is enabled.
        
        Args:
            activity_path: Hierarchical path like 'livechat.magadoom.announcements'
        
        Returns:
            bool: True if activity is enabled, False otherwise
        """
        # Register activity for tracking
        self.register_activity(activity_path)
        
        # Check global enabled state first
        if not self._config.get("global", {}).get("enabled", True):
            return False
        
        # Check emergency silence
        if self._config.get("global", {}).get("emergency_silence", False):
            return False
        
        # Parse the activity path
        parts = activity_path.split('.')
        current = self._config
        
        try:
            # Navigate through the configuration tree
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    # Path not found, check parent categories
                    if len(parts) > 1:
                        parent_path = '.'.join(parts[:-1])
                        return self.is_enabled(parent_path)
                    return True  # Default to enabled if not specified
            
            return bool(current) if isinstance(current, bool) else True
            
        except Exception as e:
            logger.error(f"❌ Error checking activity '{activity_path}': {e}")
            return True  # Default to enabled on error
    
    def set_enabled(self, activity_path: str, enabled: bool):
        """
        Enable or disable a specific activity.
        
        Args:
            activity_path: Hierarchical path like 'livechat.magadoom.announcements'
            enabled: True to enable, False to disable
        """
        self.register_activity(activity_path)
        parts = activity_path.split('.')
        current = self._config
        
        try:
            # Navigate to parent and set value
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            current[parts[-1]] = enabled
            self._save_config()
            
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            logger.info(f"🎛️ Activity '{activity_path}' {status}")
            
        except Exception as e:
            logger.error(f"❌ Failed to set activity '{activity_path}': {e}")
    
    def set_notification_callback(self, callback):
        """Register callback for stream notifications"""
        self._notification_callback = callback
        logger.info("📢 Stream notification callback registered")
    
    def _send_notification(self, message: str):
        """Send notification to stream if callback is registered"""
        if self._notification_callback:
            try:
                self._notification_callback(message)
            except Exception as e:
                logger.error(f"❌ Failed to send stream notification: {e}")
    
    def apply_preset(self, preset_name: str):
        """
        Apply a predefined configuration preset.
        
        Args:
            preset_name: Name of preset ('silent_testing', 'api_testing', etc.)
        """
        presets = self._config.get("presets", {})
        if preset_name not in presets:
            logger.error(f"❌ Unknown preset: {preset_name}")
            available = list(presets.keys())
            logger.info(f"📋 Available presets: {', '.join(available)}")
            return
        
        preset = presets[preset_name]
        overrides = preset.get("overrides", {})
        
        logger.info(f"🎛️ Applying preset '{preset_name}': {preset.get('description', '')}")
        
        # Send stream notifications for specific presets
        if preset_name == "magadoom_off":
            self._send_notification("⚡ MagaDoom OFF")
        elif preset_name == "consciousness_off":
            self._send_notification("⚡ 0102 OFF")
        elif preset_name == "silent_testing":
            self._send_notification("⚡ Silent Mode ON")
        
        for activity_path, enabled in overrides.items():
            self.set_enabled(activity_path, enabled)
    
    def emergency_silence(self):
        """Emergency function to disable all noisy activities immediately"""
        logger.warning("🚨 EMERGENCY SILENCE - Disabling all noisy activities across entire system")
        
        self._config["global"]["emergency_silence"] = True
        self.apply_preset("emergency_silence")
    
    def restore_normal(self):
        """Restore all activities to normal operation"""
        logger.info("🔄 RESTORE NORMAL - Enabling all activities across entire system")
        
        # Send stream notification for restore
        self._send_notification("⚡ Normal Mode ON")
        
        # Reset emergency silence
        self._config["global"]["emergency_silence"] = False
        
        # Reset to default config
        self._config = self._get_default_config()
        self._save_config()
    
    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status of all activity switches"""
        return {
            "global": {
                "enabled": self._config.get("global", {}).get("enabled", True),
                "testing_mode": self._config.get("global", {}).get("testing_mode", False),
                "emergency_silence": self._config.get("global", {}).get("emergency_silence", False)
            },
            "modules": {
                "livechat": {
                    "magadoom_announcements": self.is_enabled("livechat.magadoom.announcements"),
                    "consciousness_triggers": self.is_enabled("livechat.consciousness.emoji_triggers"),
                    "auto_responses": self.is_enabled("livechat.consciousness.automatic_responses")
                },
                "platform": {
                    "youtube_posting": self.is_enabled("platform.api.youtube_posting"),
                    "social_media_posting": self.is_enabled("platform.api.social_media_posting"),
                    "stream_monitoring": self.is_enabled("platform.api.stream_monitoring")
                },
                "ai": {
                    "banter_responses": self.is_enabled("ai.banter_engine.auto_responses"),
                    "pattern_learning": self.is_enabled("ai.learning.pattern_updates")
                }
            },
            "registered_activities": sorted(list(self._activity_registry)),
            "available_presets": list(self._config.get("presets", {}).keys())
        }
    
    def list_presets(self) -> Dict[str, str]:
        """Get available presets with descriptions"""
        presets = self._config.get("presets", {})
        return {
            name: preset.get("description", "No description")
            for name, preset in presets.items()
        }


# Global singleton instance
controller = UniversalActivityController()


# Convenience functions for common usage patterns
def is_enabled(activity_path: str) -> bool:
    """Check if activity is enabled. Usage: is_enabled('livechat.magadoom.announcements')"""
    return controller.is_enabled(activity_path)


def set_enabled(activity_path: str, enabled: bool):
    """Enable/disable activity. Usage: set_enabled('livechat.magadoom.announcements', False)"""
    controller.set_enabled(activity_path, enabled)


def emergency_silence():
    """Emergency silence ALL noisy activities across entire system"""
    controller.emergency_silence()


def restore_normal():
    """Restore all activities to normal across entire system"""
    controller.restore_normal()


def apply_preset(preset_name: str):
    """Apply configuration preset. Usage: apply_preset('silent_testing')"""
    controller.apply_preset(preset_name)


def get_status() -> Dict[str, Any]:
    """Get comprehensive system status"""
    return controller.get_status()


def list_presets() -> Dict[str, str]:
    """List available presets with descriptions"""
    return controller.list_presets()