"""
Moderation Statistics Tracker - WSP Compliant Module
Tracks moderation events, violations, and provides analytics
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)

class ModerationStats:
    """
    Tracks moderation statistics and violations.
    Separated from LiveChatListener for WSP compliance.
    """
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.stats_file = os.path.join(memory_dir, "moderation_stats.json")
        self.violations = defaultdict(list)  # user_id -> list of violations
        self.banned_phrases = set()
        self.total_messages = 0
        self.total_violations = 0
        self.total_timeouts = 0
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing stats if available
        self.load_stats()
        logger.info("ModerationStats initialized")
    
    def load_stats(self):
        """Load stats from persistent storage."""
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.violations = defaultdict(list, data.get("violations", {}))
                    self.banned_phrases = set(data.get("banned_phrases", []))
                    self.total_messages = data.get("total_messages", 0)
                    self.total_violations = data.get("total_violations", 0)
                    self.total_timeouts = data.get("total_timeouts", 0)
                    logger.info(f"Loaded stats: {self.total_violations} violations, {self.total_timeouts} timeouts")
            except Exception as e:
                logger.error(f"Error loading stats: {e}")
    
    def save_stats(self):
        """Save stats to persistent storage."""
        try:
            data = {
                "violations": dict(self.violations),
                "banned_phrases": list(self.banned_phrases),
                "total_messages": self.total_messages,
                "total_violations": self.total_violations,
                "total_timeouts": self.total_timeouts,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            logger.debug("Stats saved to disk")
        except Exception as e:
            logger.error(f"Error saving stats: {e}")
    
    def record_message(self):
        """Record that a message was processed."""
        self.total_messages += 1
    
    def record_violation(self, user_id: str, username: str, violation_type: str, details: str = ""):
        """
        Record a violation by a user.
        
        Args:
            user_id: The user's ID
            username: The user's display name
            violation_type: Type of violation (e.g., "spam", "hate_speech", "maga_support")
            details: Additional details about the violation
        """
        violation = {
            "timestamp": datetime.now().isoformat(),
            "username": username,
            "type": violation_type,
            "details": details
        }
        self.violations[user_id].append(violation)
        self.total_violations += 1
        logger.info(f"Recorded violation for {username}: {violation_type}")
        self.save_stats()
    
    def record_timeout(self, user_id: str, username: str, duration: int, reason: str):
        """
        Record that a user was timed out.
        
        Args:
            user_id: The user's ID
            username: The user's display name
            duration: Timeout duration in seconds
            reason: Reason for the timeout
        """
        self.record_violation(user_id, username, "timeout", f"Duration: {duration}s, Reason: {reason}")
        self.total_timeouts += 1
        self.save_stats()
    
    def get_moderation_stats(self) -> Dict[str, Any]:
        """
        Get overall moderation statistics.
        
        Returns:
            Dictionary containing moderation stats
        """
        return {
            "total_messages": self.total_messages,
            "total_violations": self.total_violations,
            "total_timeouts": self.total_timeouts,
            "unique_violators": len(self.violations),
            "banned_phrases_count": len(self.banned_phrases),
            "violation_rate": f"{(self.total_violations / max(self.total_messages, 1)) * 100:.2f}%"
        }
    
    def get_user_violations(self, user_id: str) -> Dict[str, Any]:
        """
        Get violations for a specific user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            Dictionary containing user's violation history
        """
        user_violations = self.violations.get(user_id, [])
        return {
            "user_id": user_id,
            "total_violations": len(user_violations),
            "violations": user_violations[-10:],  # Last 10 violations
            "first_violation": user_violations[0]["timestamp"] if user_violations else None,
            "last_violation": user_violations[-1]["timestamp"] if user_violations else None
        }
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the top violators by violation count.
        
        Args:
            limit: Maximum number of violators to return
            
        Returns:
            List of top violators with their stats
        """
        violator_stats = []
        for user_id, violations in self.violations.items():
            if violations:
                latest_violation = violations[-1]
                violator_stats.append({
                    "user_id": user_id,
                    "username": latest_violation.get("username", "Unknown"),
                    "violation_count": len(violations),
                    "last_violation": latest_violation["timestamp"],
                    "violation_types": list(set(v["type"] for v in violations))
                })
        
        # Sort by violation count
        violator_stats.sort(key=lambda x: x["violation_count"], reverse=True)
        return violator_stats[:limit]
    
    def clear_user_violations(self, user_id: str) -> bool:
        """
        Clear violations for a specific user.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if violations were cleared, False if user had no violations
        """
        if user_id in self.violations:
            del self.violations[user_id]
            self.save_stats()
            logger.info(f"Cleared violations for user {user_id}")
            return True
        return False
    
    def add_banned_phrase(self, phrase: str) -> bool:
        """
        Add a phrase to the banned list.
        
        Args:
            phrase: The phrase to ban
            
        Returns:
            True if added, False if already banned
        """
        phrase_lower = phrase.lower().strip()
        if phrase_lower not in self.banned_phrases:
            self.banned_phrases.add(phrase_lower)
            self.save_stats()
            logger.info(f"Added banned phrase: {phrase}")
            return True
        return False
    
    def remove_banned_phrase(self, phrase: str) -> bool:
        """
        Remove a phrase from the banned list.
        
        Args:
            phrase: The phrase to unban
            
        Returns:
            True if removed, False if not in list
        """
        phrase_lower = phrase.lower().strip()
        if phrase_lower in self.banned_phrases:
            self.banned_phrases.remove(phrase_lower)
            self.save_stats()
            logger.info(f"Removed banned phrase: {phrase}")
            return True
        return False
    
    def get_banned_phrases(self) -> List[str]:
        """Get the list of banned phrases."""
        return sorted(list(self.banned_phrases))
    
    def check_banned_phrase(self, text: str) -> Optional[str]:
        """
        Check if text contains a banned phrase.
        
        Args:
            text: Text to check
            
        Returns:
            The banned phrase found, or None
        """
        text_lower = text.lower()
        for phrase in self.banned_phrases:
            if phrase in text_lower:
                return phrase
        return None