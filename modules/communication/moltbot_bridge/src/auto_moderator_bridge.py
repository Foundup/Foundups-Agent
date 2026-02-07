#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AutoModeratorBridge - Conversational Control Plane for YouTube Automation

Connects OpenClawDAE (conversational interface) to AutoModeratorDAE (automation).
Enables 012 to query, command, and monitor the automation system via Discord.

WSP 73: Partner-Principal-Associate Architecture
WSP 27: DAE Interface Standards
"""

import logging
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("auto_moderator_bridge")

# Cache for lazy-loaded instances
_scheduler_tracker_cache = None
_channel_registry_cache = None


def _get_scheduler_tracker():
    """Lazy-load schedule tracker for shorts scheduling queries."""
    global _scheduler_tracker_cache
    if _scheduler_tracker_cache is None:
        try:
            from modules.platform_integration.youtube_shorts_scheduler.src.schedule_tracker import ScheduleTracker
            _scheduler_tracker_cache = ScheduleTracker
        except ImportError:
            logger.warning("ScheduleTracker not available")
            _scheduler_tracker_cache = False
    return _scheduler_tracker_cache if _scheduler_tracker_cache else None


def _get_channel_registry():
    """Lazy-load channel registry for channel info."""
    global _channel_registry_cache
    if _channel_registry_cache is None:
        try:
            from modules.infrastructure.shared_utilities.youtube_channel_registry import (
                get_channel_by_key, get_rotation_order, group_channels_by_browser
            )
            _channel_registry_cache = {
                "get_channel_by_key": get_channel_by_key,
                "get_rotation_order": get_rotation_order,
                "group_channels_by_browser": group_channels_by_browser,
            }
        except ImportError:
            logger.warning("Channel registry not available")
            _channel_registry_cache = {}
    return _channel_registry_cache


class AutoModeratorBridge:
    """
    Conversational interface to AutoModeratorDAE.
    
    Provides query/command/monitor capabilities via natural language
    routed from OpenClawDAE.
    """
    
    def __init__(self):
        self._skip_channels: Dict[str, datetime] = {}  # channel -> skip_until
        self._alert_history: List[Dict[str, Any]] = []
        
    # -------------------------------------------------------------------------
    # Query Methods (read-only)
    # -------------------------------------------------------------------------
    
    def query_status(self) -> str:
        """
        Get comprehensive system status.
        
        Returns human-readable status for Discord response.
        """
        lines = ["**📊 Automation System Status**", ""]
        
        # Channel registry
        registry = _get_channel_registry()
        if registry:
            try:
                browser_groups = registry["group_channels_by_browser"]()
                lines.append("**🖥️ Browser Channels:**")
                for browser, channels in browser_groups.items():
                    channel_names = [c.get("name", c.get("key", "?")) for c in channels]
                    lines.append(f"  • {browser.upper()}: {', '.join(channel_names)}")
                lines.append("")
            except Exception as e:
                logger.warning(f"Failed to get browser groups: {e}")
        
        # Scheduler status
        lines.extend(self._get_scheduler_summary())
        
        # Skip status
        active_skips = self._get_active_skips()
        if active_skips:
            lines.append("**⏸️ Skipped Channels:**")
            for channel, until in active_skips.items():
                remaining = (until - datetime.now()).total_seconds() / 60
                lines.append(f"  • {channel}: skipped for {int(remaining)} more minutes")
            lines.append("")
        
        # Recent alerts
        if self._alert_history:
            lines.append("**🚨 Recent Alerts:**")
            for alert in self._alert_history[-3:]:
                lines.append(f"  • {alert['time']}: {alert['message'][:50]}...")
            lines.append("")
        
        lines.append(f"_Updated: {datetime.now().strftime('%H:%M:%S')}_")
        return "\n".join(lines)
    
    def get_scheduler_report(self, channel: Optional[str] = None) -> str:
        """
        Get detailed scheduler report.
        
        Args:
            channel: Optional channel name to filter by
            
        Returns:
            Formatted scheduler statistics
        """
        TrackerClass = _get_scheduler_tracker()
        if not TrackerClass:
            return "❌ Scheduler not available"
        
        lines = ["**📅 Shorts Scheduler Report**", ""]
        
        registry = _get_channel_registry()
        if not registry:
            return "❌ Channel registry not available"
        
        try:
            browser_groups = registry["group_channels_by_browser"]()
            total_scheduled = 0
            
            for browser, channels in browser_groups.items():
                for ch in channels:
                    ch_key = ch.get("key", "")
                    ch_name = ch.get("name", ch_key)
                    ch_id = ch.get("id", "")
                    
                    if channel and channel.lower() not in ch_name.lower():
                        continue
                    
                    try:
                        tracker = TrackerClass(ch_id)
                        stats = tracker.get_statistics()
                        total = stats.get("total_scheduled", 0)
                        total_scheduled += total
                        
                        if total > 0:
                            lines.append(f"**{ch_name}:**")
                            lines.append(f"  • Total scheduled: {total}")
                            lines.append(f"  • Full days: {stats.get('full_days', 0)}")
                            if stats.get("date_range"):
                                lines.append(f"  • Range: {stats['date_range'][0]} → {stats['date_range'][1]}")
                            lines.append("")
                    except Exception as e:
                        logger.debug(f"No tracker for {ch_name}: {e}")
            
            if total_scheduled == 0:
                lines.append("No scheduled shorts found.")
            else:
                lines.append(f"**Total across all channels: {total_scheduled} shorts**")
                
        except Exception as e:
            logger.error(f"Scheduler report error: {e}")
            lines.append(f"Error generating report: {e}")
        
        return "\n".join(lines)
    
    def get_oops_pages(self) -> str:
        """
        Check for any channels with OOPS page errors.
        
        Returns:
            List of channels with recent OOPS errors
        """
        # Check alert history for OOPS mentions
        oops_alerts = [
            a for a in self._alert_history
            if "oops" in a.get("message", "").lower()
        ]
        
        if not oops_alerts:
            return "✅ No OOPS page errors detected recently."
        
        lines = ["**🚨 OOPS Page Errors:**", ""]
        for alert in oops_alerts[-5:]:
            lines.append(f"• {alert['time']}: {alert['message']}")
        
        return "\n".join(lines)
    
    # -------------------------------------------------------------------------
    # Command Methods (write/control)
    # -------------------------------------------------------------------------
    
    def skip_channel(self, channel: str, hours: float = 1.0) -> str:
        """
        Skip a channel for a specified duration.
        
        Args:
            channel: Channel name to skip
            hours: Duration in hours
            
        Returns:
            Confirmation message
        """
        skip_until = datetime.now() + timedelta(hours=hours)
        self._skip_channels[channel.lower()] = skip_until
        
        logger.info(f"[BRIDGE] Skipping {channel} until {skip_until}")
        return f"⏸️ Skipping **{channel}** for {hours} hour(s) (until {skip_until.strftime('%H:%M')})"
    
    def resume_channel(self, channel: str) -> str:
        """
        Resume a skipped channel.
        
        Args:
            channel: Channel name to resume
            
        Returns:
            Confirmation message
        """
        if channel.lower() in self._skip_channels:
            del self._skip_channels[channel.lower()]
            logger.info(f"[BRIDGE] Resumed {channel}")
            return f"▶️ Resumed **{channel}**"
        return f"ℹ️ **{channel}** was not skipped"
    
    def is_channel_skipped(self, channel: str) -> bool:
        """Check if a channel is currently skipped."""
        channel_lower = channel.lower()
        if channel_lower not in self._skip_channels:
            return False
        
        skip_until = self._skip_channels[channel_lower]
        if datetime.now() >= skip_until:
            del self._skip_channels[channel_lower]
            return False
        return True
    
    # -------------------------------------------------------------------------
    # Alert Methods (outbound)
    # -------------------------------------------------------------------------
    
    def record_alert(self, message: str, severity: str = "info"):
        """
        Record an alert from the automation system.
        
        Args:
            message: Alert message
            severity: Alert severity (info, warning, error)
        """
        alert = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message,
            "severity": severity,
        }
        self._alert_history.append(alert)
        
        # Keep only last 50 alerts
        if len(self._alert_history) > 50:
            self._alert_history = self._alert_history[-50:]
        
        logger.info(f"[BRIDGE-ALERT] [{severity.upper()}] {message}")
    
    def record_oops_page(self, channel: str, fallback: Optional[str] = None):
        """Record an OOPS page detection."""
        msg = f"OOPS page on {channel}"
        if fallback:
            msg += f" (fallback: {fallback})"
        self.record_alert(msg, "warning")
    
    # -------------------------------------------------------------------------
    # Private Helpers
    # -------------------------------------------------------------------------
    
    def _get_scheduler_summary(self) -> List[str]:
        """Get brief scheduler summary lines."""
        lines = []
        TrackerClass = _get_scheduler_tracker()
        
        if TrackerClass:
            lines.append("**📅 Scheduler:** Active")
        else:
            lines.append("**📅 Scheduler:** Not loaded")
        
        return lines
    
    def _get_active_skips(self) -> Dict[str, datetime]:
        """Get currently active channel skips."""
        now = datetime.now()
        active = {}
        expired = []
        
        for channel, until in self._skip_channels.items():
            if now < until:
                active[channel] = until
            else:
                expired.append(channel)
        
        # Clean up expired
        for channel in expired:
            del self._skip_channels[channel]
        
        return active


# Singleton instance
_bridge_instance: Optional[AutoModeratorBridge] = None


def get_bridge() -> AutoModeratorBridge:
    """Get or create the singleton AutoModeratorBridge instance."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = AutoModeratorBridge()
    return _bridge_instance


# -------------------------------------------------------------------------
# Intent Router Integration
# -------------------------------------------------------------------------

def handle_automation_intent(message: str, sender: str) -> str:
    """
    Handle automation-related intents from OpenClawDAE.
    
    Args:
        message: User message
        sender: Sender identifier
        
    Returns:
        Response text for Discord
    """
    bridge = get_bridge()
    msg_lower = message.lower()
    
    # Query: Status
    if any(kw in msg_lower for kw in ["status", "how is", "what's running", "system"]):
        return bridge.query_status()
    
    # Query: Scheduler
    if any(kw in msg_lower for kw in ["scheduler", "scheduled", "shorts", "how many"]):
        # Extract channel name if mentioned
        channel = None
        for ch in ["move2japan", "undaodu", "foundups", "ravingantifa"]:
            if ch in msg_lower:
                channel = ch
                break
        return bridge.get_scheduler_report(channel)
    
    # Query: OOPS pages
    if any(kw in msg_lower for kw in ["oops", "error", "problem", "issue"]):
        return bridge.get_oops_pages()
    
    # Command: Skip channel
    if "skip" in msg_lower:
        for ch in ["move2japan", "undaodu", "foundups", "ravingantifa"]:
            if ch in msg_lower:
                hours = 1.0
                if "2 hour" in msg_lower:
                    hours = 2.0
                elif "30 min" in msg_lower:
                    hours = 0.5
                return bridge.skip_channel(ch, hours)
        return "❓ Which channel should I skip? (Move2Japan, UnDaoDu, FoundUps, RavingANTIFA)"
    
    # Command: Resume channel
    if "resume" in msg_lower:
        for ch in ["move2japan", "undaodu", "foundups", "ravingantifa"]:
            if ch in msg_lower:
                return bridge.resume_channel(ch)
        return "❓ Which channel should I resume?"
    
    # Default: Status
    return bridge.query_status()


if __name__ == "__main__":
    # Test the bridge
    bridge = get_bridge()
    print(bridge.query_status())
    print("\n---\n")
    print(bridge.get_scheduler_report())
