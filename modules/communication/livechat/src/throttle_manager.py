"""
Throttle Manager Module
WSP-Compliant: WSP 3 (Module Organization), WSP 17 (Pattern Registry)

Manages adaptive response throttling based on chat activity.

WSP 17 Pattern Registry: This is a REUSABLE PATTERN
- Documented in: modules/communication/PATTERN_REGISTRY.md
- Pattern: Adaptive delay based on chat activity
- Reusable for: LinkedIn, X/Twitter, Discord, Twitch
"""

import time
import logging
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class ThrottleManager:
    """Manages adaptive throttling for chat responses"""
    
    def __init__(self, 
                 min_delay: float = 2.0,
                 max_delay: float = 30.0,
                 throttle_window: int = 60):
        """
        Initialize throttle manager.
        
        Args:
            min_delay: Minimum seconds between responses
            max_delay: Maximum seconds between responses
            throttle_window: Window in seconds for tracking message rate
        """
        self.min_response_delay = min_delay
        self.max_response_delay = max_delay
        self.throttle_window = throttle_window
        
        # Tracking
        self.message_timestamps = []
        self.last_response_time = None
        
        # Response type cooldowns
        self.last_consciousness_response = None
        self.last_factcheck_response = None
        self.last_maga_timeout = None
        
    def track_message(self):
        """Track an incoming message for rate calculation."""
        self.message_timestamps.append(time.time())
        
    def calculate_adaptive_delay(self) -> float:
        """
        Calculate response delay based on current chat activity.
        
        Returns:
            Delay in seconds
        """
        now = time.time()
        
        # Clean old timestamps
        self.message_timestamps = [
            ts for ts in self.message_timestamps 
            if now - ts < self.throttle_window
        ]
        
        # Calculate messages per minute
        messages_per_minute = len(self.message_timestamps)
        
        # INTELLIGENT ADAPTIVE DELAY - INVERTED LOGIC
        # Slow chat = LONGER delays (avoid spam)
        # Fast chat = SHORTER delays (keep up with activity)
        
        if messages_per_minute == 0:
            # Dead chat: very long delay to avoid spam
            delay = 120  # 2 minutes
        elif messages_per_minute < 2:
            # Very quiet chat: long delay
            delay = 60  # 1 minute
        elif messages_per_minute < 5:
            # Quiet chat: moderate delay
            delay = 30  # 30 seconds
        elif messages_per_minute < 10:
            # Moderate activity: standard delay
            delay = 15  # 15 seconds
        elif messages_per_minute < 20:
            # Active chat: quick responses
            delay = 8  # 8 seconds
        elif messages_per_minute < 50:
            # Busy chat: rapid responses
            delay = 5  # 5 seconds
        else:
            # Very busy: minimum delay
            delay = self.min_response_delay  # 2 seconds
        
        logger.debug(f"📊 Chat activity: {messages_per_minute} msg/min, delay: {delay}s")
        return delay
    
    def should_respond(self, response_type: str = 'general') -> bool:
        """
        Check if enough time has passed to send a response.
        
        Args:
            response_type: Type of response (consciousness, factcheck, maga, general)
            
        Returns:
            True if response should be sent
        """
        now = time.time()
        required_delay = self.calculate_adaptive_delay()
        
        # Check specific cooldowns
        if response_type == 'consciousness':
            if self.last_consciousness_response:
                if now - self.last_consciousness_response < required_delay:
                    return False
        elif response_type == 'factcheck':
            if self.last_factcheck_response:
                # Longer cooldown for factchecks
                if now - self.last_factcheck_response < required_delay * 1.5:
                    return False
        elif response_type == 'maga':
            if self.last_maga_timeout:
                # Faster for moderation
                if now - self.last_maga_timeout < required_delay * 0.5:
                    return False
        
        # Check general response cooldown
        if self.last_response_time:
            if now - self.last_response_time < self.min_response_delay:
                return False
        
        return True
    
    def record_response(self, response_type: str = 'general'):
        """
        Record that a response was sent.
        
        Args:
            response_type: Type of response sent
        """
        now = time.time()
        self.last_response_time = now
        
        if response_type == 'consciousness':
            self.last_consciousness_response = now
        elif response_type == 'factcheck':
            self.last_factcheck_response = now
        elif response_type == 'maga':
            self.last_maga_timeout = now
    
    def get_status(self) -> Dict:
        """Get current throttle status."""
        now = time.time()
        
        # Clean timestamps for accurate count
        self.message_timestamps = [
            ts for ts in self.message_timestamps 
            if now - ts < self.throttle_window
        ]
        
        return {
            'messages_per_minute': len(self.message_timestamps),
            'current_delay': self.calculate_adaptive_delay(),
            'last_response': now - self.last_response_time if self.last_response_time else None,
            'cooldowns': {
                'consciousness': now - self.last_consciousness_response if self.last_consciousness_response else None,
                'factcheck': now - self.last_factcheck_response if self.last_factcheck_response else None,
                'maga': now - self.last_maga_timeout if self.last_maga_timeout else None
            }
        }