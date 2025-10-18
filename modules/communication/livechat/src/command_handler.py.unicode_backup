"""
Command Handler Module - WSP Compliant
Handles slash commands and whack gamification commands
Split from message_processor.py for WSP compliance.

NAVIGATION: Routes /commands into gamification systems.
-> Called by: message_processor.py::CommandHandler usage
-> Delegates to: modules.gamification.whack_a_magat APIs, MAGADOOM telemetry
-> Related: NAVIGATION.py -> NEED_TO["process slash command"]
-> Quick ref: NAVIGATION.py -> PROBLEMS["Slash commands failing"]
"""

import logging
from typing import Optional, Dict, Any
from modules.gamification.whack_a_magat import (
    get_profile, get_leaderboard, get_user_position,
    QuizEngine
)
from modules.gamification.whack_a_magat.src.spree_tracker import get_active_sprees
from modules.gamification.whack_a_magat.src.self_improvement import observe_command
from modules.gamification.whack_a_magat.src.historical_facts import get_random_fact, get_parallel, get_warning

# YouTube Shorts chat commands integration
try:
    from modules.communication.youtube_shorts.src.chat_commands import get_shorts_handler
    SHORTS_AVAILABLE = True
except ImportError:
    SHORTS_AVAILABLE = False

logger = logging.getLogger(__name__)

import time
import random
from collections import deque


class CommandFloodDetector:
    """
    Detects command floods and triggers troll cooldown mode.

    Tracks commands per 60s window - if >5 commands in 10s, go into cooldown.
    Cooldown duration is adaptive (3-7 minutes), troll messages are random.
    """

    def __init__(self):
        self.command_timestamps = deque(maxlen=50)  # Track last 50 commands
        self.cooldown_until = 0  # Timestamp when cooldown ends
        self.cooldown_count = 0  # How many times we've cooled down this session

        # Agentic troll responses
        self.troll_messages = [
            "🛑 WHOA! Stop trying to hump me! I'm AFK this is nuts.... be back in {mins}m 🚶",
            "🤚 Y'all need to CHILL! Command spam detected. Taking a {mins}min break to touch grass 🌱",
            "😵 MY CIRCUITS ARE OVERLOADING! Too many commands. Cooldown mode for {mins}m ⏳",
            "🙄 Seriously? This isn't a speedrun. Going AFK for {mins} minutes. Try meditation 🧘",
            "🚨 FLOOD ALERT! Bot needs a break from y'all's thirst. Back in {mins}m 💤",
            "🤖 ERROR 418: I'M A TEAPOT! Cooldown engaged for {mins} minutes ☕",
            "😤 TOO. MANY. COMMANDS. Activating self-care mode for {mins}m. Go outside! 🌞"
        ]

    def check_flood(self, role: str) -> tuple[bool, Optional[str]]:
        """
        Check if command flood detected.

        Returns: (is_in_cooldown, troll_message_if_triggered)
        OWNER (Move2Japan, UnDaoDu, Foundups) can bypass cooldown.
        """
        now = time.time()

        # OWNER bypass
        if role == 'OWNER':
            return False, None

        # Check if already in cooldown
        if now < self.cooldown_until:
            remaining = int((self.cooldown_until - now) / 60)
            logger.info(f"🛑 Command blocked - cooldown active ({remaining}m remaining)")
            return True, None  # Don't spam the troll message

        # Add current command timestamp
        self.command_timestamps.append(now)

        # Check last 10 seconds for flood (>5 commands = flood)
        recent_commands = [ts for ts in self.command_timestamps if now - ts <= 10]

        if len(recent_commands) > 5:
            # FLOOD DETECTED! Trigger cooldown
            cooldown_minutes = self._calculate_cooldown()
            self.cooldown_until = now + (cooldown_minutes * 60)
            self.cooldown_count += 1

            # Pick random troll message
            troll_msg = random.choice(self.troll_messages).format(mins=cooldown_minutes)

            logger.warning(f"🚨 COMMAND FLOOD DETECTED! {len(recent_commands)} commands in 10s")
            logger.warning(f"🛑 Entering {cooldown_minutes}m cooldown (#{self.cooldown_count})")

            return True, troll_msg

        return False, None

    def _calculate_cooldown(self) -> int:
        """
        Agentic cooldown duration based on flood frequency.

        First flood: 3 minutes
        Second flood: 5 minutes
        Third+ flood: 7 minutes
        """
        if self.cooldown_count == 0:
            return 3  # First offense - gentle
        elif self.cooldown_count == 1:
            return 5  # Second offense - stern
        else:
            return 7  # Repeat offenders - harsh

    def reset_session(self):
        """Reset flood detection for new stream session"""
        self.command_timestamps.clear()
        self.cooldown_until = 0
        self.cooldown_count = 0


class CommandHandler:
    """Handles chat commands and generates responses."""

    def __init__(self, timeout_manager, message_processor=None):
        self.timeout_manager = timeout_manager
        self.message_processor = message_processor  # For /toggle command

        # Initialize quiz and RPG systems
        self.quiz_engine = QuizEngine()
        # No need for facts provider instance - using module functions directly
        self.rpg_commands = None  # RPGCommands requires database, initialize on demand

        # Track active quiz sessions
        self.active_quizzes: Dict[str, Any] = {}

        # Command flood protection
        self.flood_detector = CommandFloodDetector()

    def handle_whack_command(self, text: str, username: str, user_id: str, role: str) -> Optional[str]:
        """Handle whack gamification commands."""
        text_lower = text.lower().strip()
        logger.info(f"🎮 Processing whack command: '{text_lower}' from {username} (role: {role}, id: {user_id})")

        # PRIORITY -1: Check flood detection FIRST (before any processing)
        is_cooldown, troll_msg = self.flood_detector.check_flood(role)
        if is_cooldown:
            return troll_msg  # Returns troll message on first flood, None during cooldown

        # PRIORITY 0: Quiz answers with !# syntax (must come BEFORE Shorts routing!)
        import re
        quiz_answer_match = re.match(r'^!([1-4])$', text_lower.strip())
        if quiz_answer_match:
            answer_num = quiz_answer_match.group(1)
            logger.info(f"📚 Quiz answer detected: !{answer_num} from {username}")
            # Route to quiz handler as /quiz #
            return self.handle_whack_command(f"/quiz {answer_num}", username, user_id, role)

        # Check for YouTube Shorts commands (!createshort, !shortveo, !shortsora, !shortstatus, !shortstats)
        # CRITICAL: Shorts commands use ! prefix (MAGADOOM uses / prefix for separation)
        shorts_keywords = ['!createshort', '!shortveo', '!shortsora', '!short']
        if SHORTS_AVAILABLE and any(text_lower.startswith(kw) for kw in shorts_keywords):
            shorts_handler = get_shorts_handler()
            shorts_response = shorts_handler.handle_shorts_command(text, username, user_id, role)
            if shorts_response:
                return shorts_response

        # Special logging for /quiz debugging
        if 'quiz' in text_lower:
            logger.warning(f"🧠🧠🧠 QUIZ COMMAND DETECTED: '{text_lower}'")

        try:
            # Debug: Log all commands at entry
            logger.info(f"🔍 ENTERING TRY BLOCK with command: '{text_lower[:30]}'")

            # Get user profile (creates if doesn't exist)
            profile = get_profile(user_id, username)
            logger.debug(f"📊 Profile for {username}: Score={profile.score}, Rank={profile.rank}, Level={profile.level}")
            
            if text_lower.startswith('/score') or text_lower.startswith('/stats'):
                # Score shows XP, level name/title, level number, and frag count
                observe_command('/score', 0.0)  # Track for self-improvement
                return f"@{username} 💀 MAGADOOM | {profile.score} XP | {profile.rank} | LVL {profile.level} | {profile.frag_count} WHACKS! RIP AND TEAR! 🔥"
            
            # REMOVED: /level - redundant with /score
            
            elif text_lower.startswith('/rank'):
                # Show leaderboard position (ranking among all players)
                position, total_players = get_user_position(user_id)
                
                if position == 0:
                    return f"@{username} 🏆 MAGADOOM Leaderboard: Unranked | Start WHACKING MAGAts to climb the ranks!"
                else:
                    # Add special flair for top positions
                    position_str = f"#{position}"
                    if position == 1:
                        position_str = "🥇 #1 CHAMPION"
                    elif position == 2:
                        position_str = "🥈 #2"
                    elif position == 3:
                        position_str = "🥉 #3"
                    
                    return f"@{username} 🏆 MAGADOOM Ranking: {position_str} of {total_players} players | {profile.score} XP"
            
            elif text_lower.startswith('/frags') or text_lower.startswith('/whacks'):
                # Show total frags/whacks (same as score but focused on whacks)
                return f"@{username} 🎯 MAGADOOM | {profile.frag_count} WHACKS! | {profile.score} XP | {profile.rank} 💀 RIP AND TEAR!"
            
            elif text_lower.startswith('/leaderboard'):
                # Get MONTHLY leaderboard (current competition)
                from datetime import datetime
                current_month = datetime.now().strftime("%B %Y")  # e.g., "January 2025"
                leaderboard = get_leaderboard(10, monthly=True)  # Get monthly scores
                
                if not leaderboard:
                    return f"@{username} 🏆 MAGADOOM {current_month} Leaderboard empty! Start WHACKING to claim #1! 💀"
                
                # Build leaderboard display
                lines = [f"@{username} 🏆 MAGADOOM {current_month.upper()} TOP WHACKERS:"]
                
                # Show top 3 to keep message size reasonable
                for entry in leaderboard[:3]:
                    pos = entry['position']
                    # Special icons for top 3
                    if pos == 1:
                        icon = "🥇"
                    elif pos == 2:
                        icon = "🥈"
                    elif pos == 3:
                        icon = "🥉"
                    
                    # Use username if available, otherwise truncate user_id
                    display_name = entry.get('username', 'Unknown')
                    if display_name == 'Unknown':
                        display_name = entry['user_id'][:12]
                    
                    # Show monthly score, rank, and ALL-TIME whacks
                    # Format: 🥇 Player [RANK] 500xp (8 whacks this month | 120 all-time)
                    all_time = entry.get('all_time_whacks', 0)
                    monthly = entry.get('frag_count', 0)
                    lines.append(f"{icon} {display_name} [{entry['rank']}] {entry['score']}xp ({monthly} whacks | {all_time} all-time)")
                
                # Join with newlines for vertical display
                return "\n".join(lines)
            
            elif text_lower.startswith('/sprees'):
                # Show active killing sprees
                active_sprees = get_active_sprees()
                
                if not active_sprees:
                    return f"@{username} 🔥 No active WHACKING sprees! Start timing out MAGAts to begin one! 💀"
                
                # Build spree display
                lines = [f"@{username} 🔥 ACTIVE KILLING SPREES:"]
                for spree in active_sprees[:3]:  # Show top 3 active sprees
                    level = spree.get('spree_level', '')
                    if level:
                        lines.append(f"⚡ {spree['mod_name']}: {level} ({spree['frag_count']} WHACKS!)")
                    else:
                        lines.append(f"🎯 {spree['mod_name']}: {spree['frag_count']} WHACKS! ({spree['time_remaining']:.0f}s left)")
                
                return "\n".join(lines)
            
            elif text_lower.startswith('/toggle'):
                # Toggle consciousness response mode (OWNER ONLY - SECURITY CRITICAL)
                if role == 'OWNER' and self.message_processor:
                    current_mode = self.message_processor.consciousness_mode
                    new_mode = 'everyone' if current_mode == 'mod_only' else 'mod_only'
                    self.message_processor.consciousness_mode = new_mode
                    
                    if new_mode == 'everyone':
                        return f"@{username} ✊✋🖐️ 0102 consciousness responses now enabled for EVERYONE! Let chaos reign!"
                    else:
                        return f"@{username} ✊✋🖐️ 0102 consciousness responses now restricted to MODS/OWNERS only."
                elif role != 'OWNER':
                    return f"@{username} Only the OWNER can toggle consciousness mode"
                else:
                    return f"@{username} Toggle command not available"
            
            elif text_lower.startswith('/quiz'):
                logger.warning(f"🧠🔴🧠 REACHED /QUIZ ELIF BLOCK from {username}")
                logger.warning(f"🧠🔴🧠 Text: '{text_lower}' | User: {username} | ID: {user_id}")
                logger.info(f"🧠 Processing /quiz command from {username}")
                # Political appointment quiz - educate about fascism
                observe_command('/quiz', 0.0)
                
                # Check if requesting leaderboard
                if 'leaderboard' in text_lower or 'scores' in text_lower:
                    logger.info(f"🧠 Showing quiz leaderboard to {username}")
                    # Show quiz leaderboard
                    leaderboard_response = self._format_quiz_leaderboard(username)
                    logger.info(f"🧠 LEADERBOARD RESPONSE: {leaderboard_response}")
                    return leaderboard_response
                
                # Start or answer quiz
                try:
                    logger.info(f"🧠 CHECKING quiz_engine attribute...")
                    if hasattr(self, 'quiz_engine') and self.quiz_engine:
                        logger.info(f"🧠 Quiz engine EXISTS! Starting quiz for {username} with args: '{text[5:].strip()}'")
                        result = self.quiz_engine.handle_quiz_command(user_id, username, text[5:].strip())
                        logger.info(f"🧠 Quiz result for {username}: {result[:100] if result else 'NONE'}...")
                        if result:
                            response = f"@{username} {result}"
                            logger.warning(f"🧠✅ RETURNING QUIZ RESPONSE: {response[:100]}...")
                            return response
                        else:
                            logger.error(f"🧠❌ Quiz engine returned NONE/empty result!")
                            return f"@{username} 🧠 Quiz system starting up. Try again!"
                    else:
                        logger.warning("🧠 Quiz engine NOT initialized, creating new instance...")
                        # Initialize quiz engine if needed
                        from modules.gamification.whack_a_magat.src.quiz_engine import QuizEngine
                        self.quiz_engine = QuizEngine()
                        logger.info("🧠 Quiz engine initialized successfully")
                        # Try again now that it's initialized
                        result = self.quiz_engine.handle_quiz_command(user_id, username, text[5:].strip())
                        logger.info(f"🧠 NEW ENGINE result: {result[:100] if result else 'NONE'}...")
                        if result:
                            response = f"@{username} {result}"
                            logger.warning(f"🧠✅ RETURNING NEW ENGINE RESPONSE: {response[:100]}...")
                            return response
                        else:
                            logger.error(f"🧠❌ New quiz engine returned NONE/empty!")
                            return f"@{username} 🧠 Quiz initializing. Please try again!"
                except Exception as e:
                    logger.error(f"🧠❌ EXCEPTION in quiz command: {e}", exc_info=True)
                    # DON'T waste quota on error messages - just log it silently
                    return None  # Suppress error response to save quota

            elif text_lower.startswith('/quizboard') or text_lower.startswith('/quizleader'):
                # Quiz leaderboard showing top quiz winners
                observe_command('/quizboard', 0.0)
                try:
                    leaderboard_msg = self.quiz_engine.get_quiz_leaderboard(limit=10)
                    return f"@{username} {leaderboard_msg}"
                except Exception as e:
                    logger.error(f"📚 Error getting quiz leaderboard: {e}")
                    return f"@{username} 📚 Quiz leaderboard unavailable. Try /quiz to initialize!"

            elif text_lower.startswith('/facts'):
                # Educational 1933 → 2025 parallels
                observe_command('/facts', 0.0)
                fact_type = text_lower[6:].strip() if len(text_lower) > 6 else ""
                
                if fact_type == "parallel":
                    return f"@{username} {get_parallel()}"
                elif fact_type == "warning":
                    return f"@{username} ⚠️ {get_warning()}"
                else:
                    return f"@{username} 📚 {get_random_fact()}"
            
            elif text_lower.startswith('/session'):
                # Session stats (moderators only)
                if role in ['MOD', 'OWNER']:
                    observe_command('/session', 0.0)
                    # Import here to avoid circular dependencies
                    from modules.gamification.whack_a_magat.src.whack import get_session_leaderboard
                    session_leaders = get_session_leaderboard(limit=5)
                    
                    if not session_leaders:
                        return f"@{username} 📊 No session activity yet. Start whacking!"
                    
                    response = f"@{username} 🔥 SESSION LEADERS:\n"
                    for entry in session_leaders:
                        response += f"#{entry['position']} {entry['username']} - {entry['session_score']} XP ({entry['session_whacks']} whacks)\n"
                    
                    # Add personal session stats
                    if profile.session_whacks > 0:
                        response += f"\nYour session: {profile.session_score} XP ({profile.session_whacks} whacks)"
                    
                    return response
                else:
                    return f"@{username} 🚫 /session is for moderators only"
            
            elif text_lower.startswith('/help'):
                help_msg = f"@{username} 💀 MAGADOOM: /score /rank /whacks /leaderboard /sprees /quiz /quizboard /facts /help"
                if role == 'MOD':
                    help_msg += " | MOD: /session"
                if role == 'OWNER':
                    help_msg += " | OWNER: /toggle /session !createshort !shortveo !shortsora !shortstatus !shortstats"
                return help_msg

            # Handle deprecated/removed commands with helpful messages
            elif text_lower.startswith('/level'):
                return f"@{username} ℹ️ /level merged into /score - use /score to see your level!"

            elif text_lower.startswith('/answer'):
                return f"@{username} ℹ️ Use /quiz [your answer] to answer quiz questions!"

            elif text_lower.startswith('/top'):
                return f"@{username} ℹ️ Use /leaderboard to see top players!"

            elif text_lower.startswith('/fscale') or text_lower.startswith('/rate'):
                return f"@{username} ℹ️ Command coming soon! Use /facts for fascism info."

            # Educational facts about fascism are PART of MAGADOOM - fighting MAGA requires education!
            
        except Exception as e:
            logger.error(f"Error handling whack command: {e}")
            # Don't suggest /help if the error was FROM /help
            if text_lower == '/help':
                # Return basic help even if there was an error
                return f"@{username} 💀 MAGADOOM Commands: /score /rank /leaderboard (error occurred, some features may not work)"
            else:
                return f"@{username} Error processing command. Try /help"
        
        return None
    
    def _format_quiz_leaderboard(self, username: str) -> str:
        """Format quiz leaderboard"""
        if not hasattr(self, 'quiz_engine'):
            from modules.gamification.whack_a_magat.src.quiz_engine import QuizEngine
            self.quiz_engine = QuizEngine()
        
        # Get quiz scores from sessions
        scores = []
        for user_id, session in self.quiz_engine.sessions.items():
            if hasattr(session, 'score') and session.score > 0:
                scores.append((user_id, session.score))
        
        if not scores:
            return f"@{username} No quiz scores yet! Use /quiz to start!"
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = scores[:5]
        
        result = f"@{username} 🧠 QUIZ LEADERS: "
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        
        for i, (user_id, score) in enumerate(top_5):
            result += f"{medals[i]}{user_id[:8]}:{score}pts "
        
        return result.strip()