"""
Moderation Statistics Tracker - WSP 84 Enhanced with MAGADOOM Gaming
WSP 84 Compliant: Absorbs MAGADOOM gaming functionality into existing module
Tracks moderation events, violations, gaming stats, and provides analytics

Enhanced to include:
- Gaming commands (/whacks, /leaderboard, /quiz, /session)
- Activity control (/magadoom_off, /magadoom_on) 
- Gaming profile integration
- Quiz engine integration
"""

import logging
import json
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

# Initialize logger first
logger = logging.getLogger(__name__)

# WSP 84 Enhancement: Import gaming functionality to absorb
try:
    from modules.gamification.whack_a_magat import (
        get_profile, get_leaderboard, get_user_position,
        QuizEngine
    )
    from modules.gamification.whack_a_magat.src.spree_tracker import get_active_sprees
    from modules.gamification.whack_a_magat.src.self_improvement import observe_command
    from modules.gamification.whack_a_magat.src.historical_facts import get_random_fact, get_parallel, get_warning
    from modules.gamification.whack_a_magat.src.whack import get_session_leaderboard
    GAMING_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Gaming modules not available: {e}")
    GAMING_AVAILABLE = False

# Activity control integration - fix import path
try:
    sys.path.append(os.path.join(os.path.dirname(__file__), '../../../../'))
    from modules.infrastructure.activity_control.src.activity_control import controller
    ACTIVITY_CONTROL_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Activity control not available: {e}")
    ACTIVITY_CONTROL_AVAILABLE = False

class ModerationStats:
    """
    WSP 84 Enhanced: Moderation Statistics + MAGADOOM Gaming Integration
    
    Tracks moderation statistics, violations, and gaming functionality.
    Absorbs MAGADOOM commands from command_handler.py per WSP 84 principles.
    """
    
    def __init__(self, memory_dir: str = "memory"):
        self.memory_dir = memory_dir
        self.stats_file = os.path.join(memory_dir, "moderation_stats.json")
        self.violations = defaultdict(list)  # user_id -> list of violations
        self.banned_phrases = set()
        self.total_messages = 0
        self.total_violations = 0
        self.total_timeouts = 0
        
        # Duke Nukem/Quake announcer for timeouts (existing gaming infrastructure)
        self.kill_streaks = {}  # mod_id -> streak count
        self.last_kill_time = {}  # mod_id -> timestamp
        self.streak_window = 15  # seconds to maintain streak
        
        # WSP 84 Enhancement: MAGADOOM Gaming Integration
        self.quiz_engine = None  # Lazy initialization
        self.gaming_enabled = GAMING_AVAILABLE
        self.activity_control_enabled = ACTIVITY_CONTROL_AVAILABLE
        
        # Ensure memory directory exists
        os.makedirs(memory_dir, exist_ok=True)
        
        # Load existing stats if available
        self.load_stats()
        logger.info("ModerationStats initialized with MAGADOOM gaming integration")
    
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
    
    def record_timeout(self, user_id: str, username: str, duration: int, reason: str, mod_id: str = None, mod_name: str = None) -> Optional[str]:
        """
        Record that a user was timed out and generate Duke Nukem announcement.
        
        Args:
            user_id: The user's ID
            username: The user's display name
            duration: Timeout duration in seconds
            reason: Reason for the timeout
            mod_id: Moderator's ID (for streak tracking)
            mod_name: Moderator's name (for announcements)
            
        Returns:
            Duke Nukem/Quake style announcement if streak achieved
        """
        self.record_violation(user_id, username, "timeout", f"Duration: {duration}s, Reason: {reason}")
        self.total_timeouts += 1
        self.save_stats()
        
        # Generate Duke Nukem announcement if mod info provided
        if mod_id and mod_name:
            return self._get_timeout_announcement(mod_id, mod_name, username)
        return None
    
    def _get_timeout_announcement(self, mod_id: str, mod_name: str, target_name: str) -> Optional[str]:
        """Generate Duke Nukem/Quake style timeout announcement."""
        import time
        current_time = time.time()
        
        # Check if streak is still active
        if mod_id in self.last_kill_time:
            if current_time - self.last_kill_time[mod_id] > self.streak_window:
                # Streak expired, reset
                self.kill_streaks[mod_id] = 0
        
        # Increment streak
        self.kill_streaks[mod_id] = self.kill_streaks.get(mod_id, 0) + 1
        self.last_kill_time[mod_id] = current_time
        
        streak = self.kill_streaks[mod_id]
        
        # Streak announcements
        streak_messages = {
            2: f"💀 {mod_name} DOUBLE KILL! {target_name} terminated!",
            3: f"🔥 {mod_name} TRIPLE KILL! {target_name} fragged!",
            4: f"⚡ {mod_name} DOMINATING! {target_name} destroyed!",
            5: f"💥 {mod_name} RAMPAGE! {target_name} obliterated!",
            6: f"🌟 {mod_name} UNSTOPPABLE! {target_name} annihilated!",
            7: f"⭐ {mod_name} GODLIKE! {target_name} vaporized!",
            8: f"🎯 {mod_name} WICKED SICK! {target_name} eviscerated!",
            10: f"☠️ {mod_name} HOLY SH*T! {target_name} decimated!",
            15: f"🏆 {mod_name} FLAWLESS VICTORY! {target_name} eliminated!"
        }
        
        # Get announcement for current streak
        if streak in streak_messages:
            return streak_messages[streak]
        elif streak > 15:
            return f"🎮 {mod_name} LEGENDARY {streak} KILL STREAK! {target_name} deleted!"
        
        # First kill (no streak yet)
        if streak == 1:
            import random
            first_kill = [
                f"🎯 {mod_name} scores first blood! {target_name} timed out!",
                f"💥 {mod_name} opens the frag fest! {target_name} eliminated!",
                f"⚔️ {mod_name} draws first blood! {target_name} pwned!"
            ]
            return random.choice(first_kill)
        
        return None
    
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
    
    # WSP 84 Enhancement: MAGADOOM Gaming Command Integration
    # Absorbs gaming functionality from command_handler.py
    
    def handle_gaming_command(self, text: str, username: str, user_id: str, role: str) -> Optional[str]:
        """
        WSP 84 Enhancement: Handle MAGADOOM gaming commands.
        Absorbed from command_handler.py per WSP 84 principles.
        
        Args:
            text: Command text
            username: User's display name
            user_id: User's ID  
            role: User's role (USER/MOD/OWNER)
            
        Returns:
            Gaming command response or None if not a gaming command
        """
        if not self.gaming_enabled:
            return None
            
        text_lower = text.lower().strip()
        logger.info(f"🎮 Processing MAGADOOM command: '{text_lower}' from {username} (role: {role})")
        
        try:
            # Get user profile for gaming commands
            profile = get_profile(user_id, username)
            
            if text_lower.startswith('/score') or text_lower.startswith('/rank'):
                # Show user's score and rank
                return f"@{username} 💀 MAGADOOM | {profile.rank} | {profile.score} XP | {profile.frag_count} FRAGS | RIP AND TEAR!"
            
            elif text_lower.startswith('/frags') or text_lower.startswith('/whacks'):
                # Show total frags/whacks (same as score but focused on whacks)
                return f"@{username} 🎯 MAGADOOM | {profile.frag_count} WHACKS! | {profile.score} XP | {profile.rank} 💀 RIP AND TEAR!"
            
            elif text_lower.startswith('/leaderboard'):
                # Show leaderboard with enhanced formatting
                leaderboard = get_leaderboard(limit=5)
                if not leaderboard:
                    return f"@{username} 📊 Leaderboard empty. Be the first to score!"
                
                response = f"@{username} 🏆 MAGADOOM LEADERBOARD:\n"
                rank_icons = {1: "🥇", 2: "🥈", 3: "🥉"}
                
                for i, entry in enumerate(leaderboard, 1):
                    icon = rank_icons.get(i, f"#{i}")
                    display_name = entry.get('username', 'Unknown')[:15]
                    
                    # Show monthly score, rank, and ALL-TIME whacks
                    all_time = entry.get('all_time_whacks', 0)
                    monthly = entry.get('frag_count', 0)
                    response += f"{icon} {display_name} [{entry['rank']}] {entry['score']}xp ({monthly} whacks | {all_time} all-time)\n"
                
                return response.rstrip()
            
            elif text_lower.startswith('/sprees'):
                # Show active sprees
                sprees = get_active_sprees()
                if not sprees:
                    return f"@{username} ⚡ No active sprees. Start a rampage!"
                
                response = f"@{username} 🔥 ACTIVE SPREES:\n"
                for spree in sprees[:5]:
                    response += f"🌟 {spree['username']}: {spree['type']} ({spree['count']} streak)\n"
                return response.rstrip()
            
            elif text_lower.startswith('/quiz'):
                # Handle quiz functionality
                return self._handle_quiz_command(username, user_id, role)
            
            elif text_lower.startswith('/facts'):
                # Educational facts about fascism
                fact = get_random_fact()
                return f"@{username} 📚 ANTI-FASCIST FACT: {fact}"
            
            elif text_lower.startswith('/session') and role in ['MOD', 'OWNER']:
                # Show session leaderboard
                session_leaders = get_session_leaderboard(limit=5)
                if not session_leaders:
                    return f"@{username} 📊 No session activity yet. Start whacking!"
                
                response = f"@{username} 🔥 SESSION LEADERS:\n"
                for entry in session_leaders:
                    response += f"#{entry['position']} {entry['username']} - {entry['session_score']} XP ({entry['session_whacks']} whacks)\n"
                
                # Add personal session stats
                if profile.session_whacks > 0:
                    response += f"\nYour session: {profile.session_score} XP ({profile.session_whacks} whacks)"
                
                return response.rstrip()
            
            # Activity Control Commands (MOD/OWNER only)
            elif text_lower.startswith('/magadoom_off') and role in ['MOD', 'OWNER']:
                if self.activity_control_enabled:
                    apply_preset('magadoom_off')
                    logger.info(f"🔇 {username} turned off MagaDoom activities")
                    return f"@{username} ⚡ MagaDoom activities disabled (announcements, levels)"
                else:
                    return f"@{username} ⚡ Activity control not available"
            
            elif text_lower.startswith('/magadoom_on') and role in ['MOD', 'OWNER']:
                if self.activity_control_enabled:
                    restore_normal()
                    logger.info(f"🔊 {username} restored MagaDoom activities")
                    return f"@{username} ⚡ MagaDoom activities enabled"
                else:
                    return f"@{username} ⚡ Activity control not available"
            
            elif text_lower.startswith('/activity_status') and role in ['MOD', 'OWNER']:
                if self.activity_control_enabled:
                    controller = ActivityController()
                    status = controller.get_status()
                    magadoom = "✅" if status['modules']['livechat']['magadoom_announcements'] else "❌"
                    consciousness = "✅" if status['modules']['livechat']['consciousness_triggers'] else "❌"
                    return f"@{username} ⚡ Status: MagaDoom {magadoom} | 0102 {consciousness}"
                else:
                    return f"@{username} ⚡ Activity control not available"
            
            elif text_lower.startswith('/help'):
                # MAGADOOM help
                help_msg = f"@{username} 💀 MAGADOOM: /score /rank /whacks /leaderboard /sprees /quiz /facts /help"
                if role in ['MOD', 'OWNER']:
                    help_msg += " | MOD: /session /magadoom_off /magadoom_on /activity_status"
                return help_msg
            
        except Exception as e:
            logger.error(f"Error handling MAGADOOM command: {e}")
            if text_lower != '/help':
                return f"@{username} ⚠️ Gaming system error. Try /help for commands."
        
        return None  # Not a gaming command or error occurred
    
    def _handle_quiz_command(self, username: str, user_id: str, role: str) -> Optional[str]:
        """Handle quiz command functionality."""
        try:
            # Initialize quiz engine if needed
            if not self.quiz_engine:
                self.quiz_engine = QuizEngine()
                logger.info("🧠 Quiz engine initialized in ModerationStats")
            
            question_data = self.quiz_engine.get_question()
            if not question_data:
                return f"@{username} 🧠 Quiz system unavailable. Try again later."
            
            # Format question for chat (remove markdown for YouTube compatibility)
            question = question_data['question'].replace('**', '').replace('*', '')
            options = question_data['options']
            
            # Create formatted response
            response = f"@{username} 🧠 QUIZ: {question}\n"
            for i, option in enumerate(options, 1):
                clean_option = option.replace('**', '').replace('*', '')
                response += f"{i}. {clean_option}\n"
            
            response += "Reply with the number (1-4)"
            logger.info(f"🧠 Generated quiz for {username}: {question[:50]}...")
            return response.rstrip()
            
        except Exception as e:
            logger.error(f"Quiz generation error: {e}")
            return f"@{username} 🧠 Quiz system error. Educational content temporarily unavailable."
    
    def is_gaming_command(self, text: str) -> bool:
        """
        Check if text is a MAGADOOM gaming command.
        
        Args:
            text: Text to check
            
        Returns:
            True if it's a gaming command
        """
        if not self.gaming_enabled:
            return False
            
        gaming_commands = [
            '/score', '/rank', '/frags', '/whacks', '/leaderboard', 
            '/sprees', '/quiz', '/facts', '/session', '/help',
            '/magadoom_off', '/magadoom_on', '/activity_status'
        ]
        
        text_lower = text.lower().strip()
        return any(text_lower.startswith(cmd) for cmd in gaming_commands)