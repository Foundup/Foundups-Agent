"""
Quota Aware Poller
Adjusts polling cadence based on credential set and quota usage

NAVIGATION: Tunes polling cadence using credential awareness.
-> Called by: livechat_core.ChatPoller when credential_set detected
-> Delegates to: youtube_auth credential metadata and throttle manager
-> Related: NAVIGATION.py -> NEED_TO["adjust quota polling"]
-> Quick ref: NAVIGATION.py -> MODULE_GRAPH["core_flows"]["throttling_flow"]
"""

import time
import json
import logging
from typing import Optional, Dict, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class QuotaAwarePoller:
    """Manages polling frequency based on quota and activity."""

    def __init__(self, credential_set: int = 1, oauth_manager=None):
        self.credential_set = credential_set
        self.quota_file = Path("memory/quota_usage.json")
        self.daily_limit = 10000  # YouTube API daily quota
        self.oauth_manager = oauth_manager  # HOLOINDEX IMPROVEMENT: Integration gap fix
        
        # Polling intervals (in seconds) - Conservative to preserve quota
        self.EMERGENCY_INTERVAL = 90  # 90 seconds - quota critical (90%+)
        self.CONSERVATIVE_INTERVAL = 60  # 60 seconds - quota warning (70-90%)
        self.MODERATE_INTERVAL = 20  # 20 seconds - quota caution (50-70%)
        self.NORMAL_INTERVAL = 10  # 10 seconds - quota healthy (<50%)
        self.ACTIVE_INTERVAL = 5  # 5 seconds - very active chat
        
        # Activity tracking
        self.last_message_time = time.time()
        self.message_count = 0
        self.empty_poll_count = 0
        
    def get_current_quota_usage(self) -> Tuple[int, float]:
        """
        Get current quota usage for this credential set.
        
        Returns:
            (units_used, percentage_used)
        """
        try:
            if self.quota_file.exists():
                with open(self.quota_file, 'r') as f:
                    data = json.load(f)
                
                set_data = data.get('sets', {}).get(str(self.credential_set), {})
                units_used = set_data.get('used', 0)
                percentage = units_used / self.daily_limit
                
                return units_used, percentage
        except Exception as e:
            logger.error(f"Error reading quota file: {e}")
        
        return 0, 0.0
    
    def calculate_optimal_interval(self, 
                                  messages_received: int = 0,
                                  stream_active: bool = True) -> float:
        """
        Calculate optimal polling interval based on multiple factors.
        
        Args:
            messages_received: Number of messages in last poll
            stream_active: Whether stream is currently active
            
        Returns:
            Polling interval in seconds
        """
        units_used, quota_percentage = self.get_current_quota_usage()
        
        # Track message activity
        if messages_received > 0:
            self.last_message_time = time.time()
            self.message_count += messages_received
            self.empty_poll_count = 0
        else:
            self.empty_poll_count += 1
        
        # Calculate time since last message
        time_since_message = time.time() - self.last_message_time
        
        # CRITICAL: Over quota or near limit - EMERGENCY SHUTOFF
        if quota_percentage >= 0.98:  # Stop at 98% to prevent death spiral
            logger.critical(f"🚨 QUOTA EXHAUSTED: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")
            logger.critical("🛑 EMERGENCY SHUTOFF - Stopping polling to preserve quota")
            return None  # Stop polling entirely
        
        if quota_percentage >= 0.95:
            logger.error(f"🔴 QUOTA CRITICAL: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")

            # HOLOINDEX IMPROVEMENT: Integration Gap Fix - Rotate OAuth tokens when quota critical
            if self.oauth_manager and hasattr(self.oauth_manager, 'rotate_credentials'):
                logger.warning("🔄 HOLOINDEX FIX: Attempting OAuth token rotation due to quota exhaustion")
                try:
                    rotation_success = self.oauth_manager.rotate_credentials()
                    if rotation_success:
                        logger.info("✅ HOLOINDEX FIX: OAuth token rotation successful - quota reset")
                        # Reset quota tracking for new credential set
                        # Note: Actual quota reset happens on YouTube's side, we just switch credentials
                    else:
                        logger.error("❌ HOLOINDEX FIX: OAuth token rotation failed")
                except Exception as e:
                    logger.error(f"❌ HOLOINDEX FIX: OAuth rotation error: {e}")

            return self.EMERGENCY_INTERVAL
        
        # EMERGENCY: 90-95% quota used
        if quota_percentage >= 0.9:
            logger.warning(f"🟠 QUOTA EMERGENCY: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")
            return self.EMERGENCY_INTERVAL
        
        # WARNING: 70-90% quota used
        if quota_percentage >= 0.7:
            logger.warning(f"🟡 QUOTA WARNING: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")
            # Slow down based on activity
            if time_since_message > 300:  # No messages for 5 minutes
                return self.EMERGENCY_INTERVAL
            elif time_since_message > 120:  # No messages for 2 minutes
                return self.CONSERVATIVE_INTERVAL
            else:
                return self.MODERATE_INTERVAL
        
        # CAUTION: 50-70% quota used
        if quota_percentage >= 0.5:
            logger.info(f"⚠️ QUOTA CAUTION: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")
            # Adaptive based on activity
            if time_since_message > 180:  # No messages for 3 minutes
                return self.CONSERVATIVE_INTERVAL
            elif self.empty_poll_count > 10:  # Many empty polls
                return self.MODERATE_INTERVAL * 1.5
            else:
                return self.MODERATE_INTERVAL
        
        # NORMAL: Under 50% quota
        logger.debug(f"✅ Quota healthy: {units_used}/{self.daily_limit} units ({quota_percentage:.1%})")
        
        # Adjust based on chat activity
        if not stream_active:
            # Stream ended, slow polling
            return self.CONSERVATIVE_INTERVAL
        
        if time_since_message > 300:  # Dead chat (5+ minutes)
            return self.CONSERVATIVE_INTERVAL
        elif time_since_message > 120:  # Quiet chat (2+ minutes)
            return self.MODERATE_INTERVAL
        elif messages_received == 0 and self.empty_poll_count > 5:
            # Multiple empty polls, slow down
            return self.MODERATE_INTERVAL
        elif messages_received > 10:  # Very active chat
            return self.ACTIVE_INTERVAL
        elif messages_received > 5:  # Active chat
            return self.NORMAL_INTERVAL
        else:
            # Default normal polling
            return self.NORMAL_INTERVAL
    
    def should_poll(self) -> Tuple[bool, Optional[float]]:
        """
        Check if we should poll based on quota.
        
        Returns:
            (should_poll, wait_seconds)
        """
        units_used, quota_percentage = self.get_current_quota_usage()
        
        # NEVER poll if over quota
        if quota_percentage >= 1.0:
            logger.critical(f"🚨 POLLING STOPPED: Quota exhausted ({units_used}/{self.daily_limit})")
            return False, None
        
        # Calculate optimal interval
        interval = self.calculate_optimal_interval()
        
        if interval is None:
            return False, None
        
        return True, interval
    
    def get_quota_status(self) -> Dict:
        """Get detailed quota status."""
        units_used, percentage = self.get_current_quota_usage()
        remaining = self.daily_limit - units_used
        
        # Estimate time until limit at current rate
        if self.message_count > 0:
            avg_units_per_poll = 5  # Each poll costs ~5 units
            polls_remaining = remaining / avg_units_per_poll
            current_interval = self.calculate_optimal_interval()
            
            if current_interval:
                hours_remaining = (polls_remaining * current_interval) / 3600
            else:
                hours_remaining = 0
        else:
            hours_remaining = float('inf')
        
        return {
            'credential_set': self.credential_set,
            'units_used': units_used,
            'units_remaining': remaining,
            'percentage_used': percentage,
            'status': self._get_status_label(percentage),
            'hours_until_limit': hours_remaining,
            'current_interval': self.calculate_optimal_interval(),
            'recommendation': self._get_recommendation(percentage)
        }
    
    def _get_status_label(self, percentage: float) -> str:
        """Get status label based on percentage."""
        if percentage >= 1.0:
            return "EXHAUSTED"
        elif percentage >= 0.9:
            return "CRITICAL"
        elif percentage >= 0.7:
            return "WARNING"
        elif percentage >= 0.5:
            return "CAUTION"
        else:
            return "HEALTHY"
    
    def _get_recommendation(self, percentage: float) -> str:
        """Get recommendation based on usage."""
        if percentage >= 1.0:
            return "Stop all operations. Wait for quota reset."
        elif percentage >= 0.9:
            return "Emergency mode. Minimal polling only."
        elif percentage >= 0.7:
            return "Reduce polling frequency. Monitor closely."
        elif percentage >= 0.5:
            return "Use conservative polling. Watch quota."
        else:
            return "Normal operations. Quota healthy."