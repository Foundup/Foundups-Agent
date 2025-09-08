"""
LiveChat Activity Switches - Bridge to Universal Activity Controller

Provides LiveChat-specific interface to the centralized activity control system.
All switches are managed by modules.infrastructure.activity_control but this
module provides convenient LiveChat-focused functions.

Usage in LiveChat modules:
- from .activity_switches import is_enabled
- if is_enabled('magadoom.announcements'): announce_whack()
- if is_enabled('consciousness.emoji_triggers'): process_emoji()
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))

try:
    from modules.infrastructure.activity_control.src.activity_control import (
        controller,
        is_enabled as _is_enabled,
        set_enabled as _set_enabled,
        apply_preset as _apply_preset,
        emergency_silence as _emergency_silence
    )
except ImportError:
    # Fallback for testing - create minimal implementation
    def _is_enabled(activity): return True
    def _set_enabled(activity, enabled): pass
    def _apply_preset(preset): pass
    def _emergency_silence(): pass
    controller = None
import logging

logger = logging.getLogger(__name__)


# LiveChat-specific convenience functions
def is_enabled(activity: str) -> bool:
    """
    Check if LiveChat activity is enabled.
    Automatically prefixes 'livechat.' to activity path.
    
    Args:
        activity: LiveChat activity like 'magadoom.announcements'
    
    Returns:
        bool: True if enabled
    """
    return _is_enabled(f"livechat.{activity}")


def set_enabled(activity: str, enabled: bool):
    """Enable/disable LiveChat activity"""
    _set_enabled(f"livechat.{activity}", enabled)
    status = "ENABLED" if enabled else "DISABLED"
    logger.info(f"🎛️ LiveChat {activity} {status}")


def apply_preset(preset_name: str):
    """Apply universal preset"""
    _apply_preset(preset_name)


def emergency_silence():
    """Emergency silence all activities"""
    _emergency_silence()


def get_status():
    """Get LiveChat-specific activity status"""
    return {
        "magadoom": {
            "announcements": is_enabled("magadoom.announcements"),
            "level_notifications": is_enabled("magadoom.level_notifications"),
            "spree_announcements": is_enabled("magadoom.spree_announcements"),
            "rank_promotions": is_enabled("magadoom.rank_promotions")
        },
        "consciousness": {
            "emoji_triggers": is_enabled("consciousness.emoji_triggers"),
            "auto_responses": is_enabled("consciousness.automatic_responses"),
            "pattern_recognition": is_enabled("consciousness.pattern_recognition")
        },
        "chat": {
            "command_processing": is_enabled("chat.command_processing"),
            "status_announcements": is_enabled("chat.status_announcements"),
            "greeting_generation": is_enabled("chat.greeting_generation"),
            "automatic_moderation": is_enabled("chat.automatic_moderation")
        }
    }


# Quick testing functions
def silence_magadoom():
    """Quickly disable all MagaDoom activities"""
    set_enabled("magadoom.announcements", False)
    set_enabled("magadoom.level_notifications", False)
    set_enabled("magadoom.spree_announcements", False)
    logger.info("🔇 MagaDoom activities silenced")


def silence_consciousness():
    """Quickly disable 0102 consciousness activities"""
    set_enabled("consciousness.emoji_triggers", False)
    set_enabled("consciousness.automatic_responses", False)
    logger.info("🔇 Consciousness activities silenced")


def enable_testing_mode():
    """Enable testing mode - minimal noise"""
    apply_preset("silent_testing")
    logger.info("🧪 Testing mode enabled - system silenced")


def restore_normal():
    """Restore normal operation"""
    from modules.infrastructure.activity_control.src.activity_control import restore_normal
    restore_normal()
    logger.info("🔄 Normal operation restored")


# Command-line interface functions for easy manual control
def print_status():
    """Print current LiveChat activity status"""
    status = get_status()
    print("🎛️ LiveChat Activity Status:")
    print(f"  MagaDoom Announcements: {'✅' if status['magadoom']['announcements'] else '❌'}")
    print(f"  Level Notifications: {'✅' if status['magadoom']['level_notifications'] else '❌'}")
    print(f"  Consciousness Triggers: {'✅' if status['consciousness']['emoji_triggers'] else '❌'}")
    print(f"  Auto Responses: {'✅' if status['consciousness']['auto_responses'] else '❌'}")
    print(f"  Status Announcements: {'✅' if status['chat']['status_announcements'] else '❌'}")


if __name__ == "__main__":
    # Command-line interface for quick testing
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            print_status()
        elif command == "silence":
            emergency_silence()
            print("🚨 Emergency silence activated")
        elif command == "magadoom_off":
            silence_magadoom()
        elif command == "consciousness_off":  
            silence_consciousness()
        elif command == "testing":
            enable_testing_mode()
        elif command == "normal":
            restore_normal()
        else:
            print("Usage: python activity_switches.py [status|silence|magadoom_off|consciousness_off|testing|normal]")
    else:
        print_status()