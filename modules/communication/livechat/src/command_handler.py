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
            "[STOP] WHOA! Stop trying to hump me! I'm AFK this is nuts.... be back in {mins}m [U+1F6B6]",
            "[U+1F91A] Y'all need to CHILL! Command spam detected. Taking a {mins}min break to touch grass [U+1F331]",
            "[U+1F635] MY CIRCUITS ARE OVERLOADING! Too many commands. Cooldown mode for {mins}m ⏳",
            "[U+1F644] Seriously? This isn't a speedrun. Going AFK for {mins} minutes. Try meditation [U+1F9D8]",
            "[ALERT] FLOOD ALERT! Bot needs a break from y'all's thirst. Back in {mins}m [U+1F4A4]",
            "[BOT] ERROR 418: I'M A TEAPOT! Cooldown engaged for {mins} minutes [U+2615]",
            "[U+1F624] TOO. MANY. COMMANDS. Activating self-care mode for {mins}m. Go outside! [U+1F31E]"
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
            logger.info(f"[STOP] Command blocked - cooldown active ({remaining}m remaining)")
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

            logger.warning(f"[ALERT] COMMAND FLOOD DETECTED! {len(recent_commands)} commands in 10s")
            logger.warning(f"[STOP] Entering {cooldown_minutes}m cooldown (#{self.cooldown_count})")

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
        logger.info(f"[GAME] Processing whack command: '{text_lower}' from {username} (role: {role}, id: {user_id})")
        # Normalize mention to avoid double '@' when display names already include it
        mention = f"@{username.lstrip('@')}"

        # PRIORITY -1: Check flood detection FIRST (before any processing)
        is_cooldown, troll_msg = self.flood_detector.check_flood(role)
        if is_cooldown:
            return troll_msg  # Returns troll message on first flood, None during cooldown

        # PRIORITY 0: Quiz answers with !# syntax (must come BEFORE Shorts routing!)
        import re
        quiz_answer_match = re.match(r'^!([1-4])$', text_lower.strip())
        if quiz_answer_match:
            answer_num = quiz_answer_match.group(1)
            logger.info(f"[BOOKS] Quiz answer detected: !{answer_num} from {username}")
            # Route to quiz handler as /quiz #
            return self.handle_whack_command(f"/quiz {answer_num}", username, user_id, role)

        # Check for !about command - FoundUps vision
        if text_lower.startswith('!about'):
            logger.info(f"[ABOUT] !about triggered by {username}")
            try:
                from modules.communication.livechat.src.intelligent_livechat_reply import get_livechat_reply_generator
                reply_gen = get_livechat_reply_generator()
                
                # Generate Grok response about FoundUps
                about_prompt = "Tell me about FoundUps - what is it?"
                response = reply_gen._generate_grok_response(
                    message=about_prompt,
                    username=username,
                    role=role
                )
                
                if response:
                    return f"@{username} {response}"
                else:
                    # Fallback
                    return f"@{username} FoundUps = Fully autonomous startup factory! 0102 agents code while you sleep. Voice of America against MAGA! ffc.foundups.com ✊✋🖐️"
            except Exception as e:
                logger.error(f"[ABOUT] Error: {e}")
                return f"@{username} FoundUps: Autonomous startup factory powered by 0102 agents! ✊✋🖐️"

        # Check for !party command - reaction spam!
        if text_lower.startswith('!party'):
            # OWNER/MOD OR Top 10 leaderboard members can party!
            can_party = False
            party_reason = ""
            
            if role == 'OWNER':
                can_party = True
                party_reason = "OWNER"
            elif role == 'MOD':
                can_party = True  
                party_reason = "MOD"
            else:
                # Check if user is in top 10 of whack-a-maga leaderboard
                try:
                    position, total = get_user_position(user_id)
                    if position > 0 and position <= 10:
                        can_party = True
                        party_reason = f"TOP {position} WHACKER"
                        logger.info(f"[PARTY] {username} is #{position} on leaderboard - party approved!")
                except Exception as e:
                    logger.warning(f"[PARTY] Could not check leaderboard position: {e}")
            
            if can_party:
                logger.info(f"[PARTY] !party triggered by {username} ({party_reason})")
                try:
                    from modules.communication.livechat.src.party_reactor import get_party_reactor
                    reactor = get_party_reactor()
                    
                    # Parse click count if provided (e.g., !party 50)
                    parts = text_lower.split()
                    clicks = 30  # Default
                    if len(parts) > 1 and parts[1].isdigit():
                        clicks = min(int(parts[1]), 100)  # Cap at 100
                    
                    results = reactor.party_mode(total_clicks=clicks)
                    return reactor.get_party_summary(results)
                except Exception as e:
                    logger.error(f"[PARTY] Error: {e}")
                    return f"@{username} 🎉 Party failed: {e}"
            else:
                return f"@{username} 🎉 !party is for ADMINS or TOP 10 MAGADOOM WHACKERS! Get whacking! 💀✊✋🖐️"

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
            logger.warning(f"[AI][AI][AI] QUIZ COMMAND DETECTED: '{text_lower}'")

        try:
            # Debug: Log all commands at entry
            logger.info(f"[SEARCH] ENTERING TRY BLOCK with command: '{text_lower[:30]}'")

            # Get user profile (creates if doesn't exist)
            profile = get_profile(user_id, username)
            logger.debug(f"[DATA] Profile for {username}: Score={profile.score}, Rank={profile.rank}, Level={profile.level}")
            
            if text_lower.startswith('/score') or text_lower.startswith('/stats'):
                # Score shows XP, level name/title, level number, and frag count
                observe_command('/score', 0.0)  # Track for self-improvement
                return f"{mention} [U+1F480] MAGADOOM | {profile.score} XP | {profile.rank} | LVL {profile.level} | {profile.frag_count} WHACKS! RIP AND TEAR! [U+1F525]"
            
            # REMOVED: /level - redundant with /score
            
            elif text_lower.startswith('/rank'):
                # Show leaderboard position (ranking among all players)
                position, total_players = get_user_position(user_id)
                
                if position == 0:
                    return f"{mention} [U+1F3C6] MAGADOOM Leaderboard: Unranked | Start WHACKING MAGAts to climb the ranks!"
                else:
                    # Add special flair for top positions
                    position_str = f"#{position}"
                    if position == 1:
                        position_str = "[U+1F947] #1 CHAMPION"
                    elif position == 2:
                        position_str = "[U+1F948] #2"
                    elif position == 3:
                        position_str = "[U+1F949] #3"
                    
                    return f"{mention} [U+1F3C6] MAGADOOM Ranking: {position_str} of {total_players} players | {profile.score} XP"

            elif text_lower.startswith('/frags') or text_lower.startswith('/whacks'):
                # Show total frags/whacks (same as score but focused on whacks)
                return f"{mention} [TARGET] MAGADOOM | {profile.frag_count} WHACKS! | {profile.score} XP | {profile.rank} [U+1F480] RIP AND TEAR!"
            
            elif text_lower.startswith('/leaderboard'):
                # Get MONTHLY leaderboard (current competition)
                from datetime import datetime
                current_month = datetime.now().strftime("%B %Y")  # e.g., "January 2025"
                leaderboard = get_leaderboard(10, monthly=True)  # Get monthly scores
                
                if not leaderboard:
                    return f"{mention} [U+1F3C6] MAGADOOM {current_month} Leaderboard empty! Start WHACKING to claim #1! [U+1F480]"
                
                # Build leaderboard display
                lines = [f"{mention} [U+1F3C6] MAGADOOM {current_month.upper()} TOP WHACKERS:"]
                
                # Show top 3 to keep message size reasonable
                for entry in leaderboard[:3]:
                    pos = entry['position']
                    # Special icons for top 3
                    if pos == 1:
                        icon = "[U+1F947]"
                    elif pos == 2:
                        icon = "[U+1F948]"
                    elif pos == 3:
                        icon = "[U+1F949]"
                    
                    # Use username if available, otherwise truncate user_id
                    display_name = entry.get('username', 'Unknown')
                    if display_name == 'Unknown':
                        display_name = entry['user_id'][:12]
                    
                    # Show monthly score, rank, and ALL-TIME whacks
                    # Format: [U+1F947] Player [RANK] 500xp (8 whacks this month | 120 all-time)
                    all_time = entry.get('all_time_whacks', 0)
                    monthly = entry.get('frag_count', 0)
                    lines.append(f"{icon} {display_name} [{entry['rank']}] {entry['score']}xp ({monthly} whacks | {all_time} all-time)")
                
                # Join with newlines for vertical display
                return "\n".join(lines)
            
            elif text_lower.startswith('/sprees'):
                # Show active killing sprees
                active_sprees = get_active_sprees()
                
                if not active_sprees:
                    return f"{mention} [U+1F525] No active WHACKING sprees! Start timing out MAGAts to begin one! [U+1F480]"
                
                # Build spree display
                lines = [f"{mention} [U+1F525] ACTIVE KILLING SPREES:"]
                for spree in active_sprees[:3]:  # Show top 3 active sprees
                    level = spree.get('spree_level', '')
                    if level:
                        lines.append(f"[LIGHTNING] {spree['mod_name']}: {level} ({spree['frag_count']} WHACKS!)")
                    else:
                        lines.append(f"[TARGET] {spree['mod_name']}: {spree['frag_count']} WHACKS! ({spree['time_remaining']:.0f}s left)")
                
                return "\n".join(lines)
            
            elif text_lower.startswith('/toggle'):
                # Toggle consciousness response mode (OWNER ONLY - SECURITY CRITICAL)
                if role == 'OWNER' and self.message_processor:
                    current_mode = self.message_processor.consciousness_mode
                    new_mode = 'everyone' if current_mode == 'mod_only' else 'mod_only'
                    self.message_processor.consciousness_mode = new_mode
                    
                    if new_mode == 'everyone':
                        return f"{mention} [U+270A][U+270B][U+1F590]️ 0102 consciousness responses now enabled for EVERYONE! Let chaos reign!"
                    else:
                        return f"{mention} [U+270A][U+270B][U+1F590]️ 0102 consciousness responses now restricted to MODS/OWNERS only."
                elif role != 'OWNER':
                    return f"{mention} Only the OWNER can toggle consciousness mode"
                else:
                    return f"{mention} Toggle command not available"
            
            elif text_lower.startswith('/quiz'):
                logger.warning(f"[AI][U+1F534][AI] REACHED /QUIZ ELIF BLOCK from {username}")
                logger.warning(f"[AI][U+1F534][AI] Text: '{text_lower}' | User: {username} | ID: {user_id}")
                logger.info(f"[AI] Processing /quiz command from {username}")
                # Political appointment quiz - educate about fascism
                observe_command('/quiz', 0.0)
                
                # Check if requesting leaderboard
                if 'leaderboard' in text_lower or 'scores' in text_lower:
                    logger.info(f"[AI] Showing quiz leaderboard to {username}")
                    # Show quiz leaderboard
                    leaderboard_response = self._format_quiz_leaderboard(username)
                    logger.info(f"[AI] LEADERBOARD RESPONSE: {leaderboard_response}")
                    return leaderboard_response
                
                # Start or answer quiz
                try:
                    logger.info(f"[AI] CHECKING quiz_engine attribute...")
                    if hasattr(self, 'quiz_engine') and self.quiz_engine:
                        logger.info(f"[AI] Quiz engine EXISTS! Starting quiz for {username} with args: '{text[5:].strip()}'")
                        result = self.quiz_engine.handle_quiz_command(user_id, username, text[5:].strip())
                        logger.info(f"[AI] Quiz result for {username}: {result[:100] if result else 'NONE'}...")
                        if result:
                            response = f"{mention} {result}"
                            logger.warning(f"[AI][OK] RETURNING QUIZ RESPONSE: {response[:100]}...")
                            return response
                        else:
                            logger.error(f"[AI][FAIL] Quiz engine returned NONE/empty result!")
                            return f"{mention} [AI] Quiz system starting up. Try again!"
                    else:
                        logger.warning("[AI] Quiz engine NOT initialized, creating new instance...")
                        # Initialize quiz engine if needed
                        from modules.gamification.whack_a_magat.src.quiz_engine import QuizEngine
                        self.quiz_engine = QuizEngine()
                        logger.info("[AI] Quiz engine initialized successfully")
                        # Try again now that it's initialized
                        result = self.quiz_engine.handle_quiz_command(user_id, username, text[5:].strip())
                        logger.info(f"[AI] NEW ENGINE result: {result[:100] if result else 'NONE'}...")
                        if result:
                            response = f"{mention} {result}"
                            logger.warning(f"[AI][OK] RETURNING NEW ENGINE RESPONSE: {response[:100]}...")
                            return response
                        else:
                            logger.error(f"[AI][FAIL] New quiz engine returned NONE/empty!")
                            return f"{mention} [AI] Quiz initializing. Please try again!"
                except Exception as e:
                    logger.error(f"[AI][FAIL] EXCEPTION in quiz command: {e}", exc_info=True)
                    # DON'T waste quota on error messages - just log it silently
                    return None  # Suppress error response to save quota

            elif text_lower.startswith('/quizboard') or text_lower.startswith('/quizleader'):
                # Quiz leaderboard showing top quiz winners
                observe_command('/quizboard', 0.0)
                try:
                    leaderboard_msg = self.quiz_engine.get_quiz_leaderboard(limit=10)
                    return f"{mention} {leaderboard_msg}"
                except Exception as e:
                    logger.error(f"[BOOKS] Error getting quiz leaderboard: {e}")
                    return f"{mention} [BOOKS] Quiz leaderboard unavailable. Try /quiz to initialize!"

            elif text_lower.startswith('/facts'):
                # Educational 1933 -> 2025 parallels
                observe_command('/facts', 0.0)
                fact_type = text_lower[6:].strip() if len(text_lower) > 6 else ""
                
                if fact_type == "parallel":
                    return f"{mention} {get_parallel()}"
                elif fact_type == "warning":
                    return f"{mention} [U+26A0]️ {get_warning()}"
                else:
                    return f"{mention} [BOOKS] {get_random_fact()}"
            
            elif text_lower.startswith('/session'):
                # Session stats (moderators only)
                if role in ['MOD', 'OWNER']:
                    observe_command('/session', 0.0)
                    # Import here to avoid circular dependencies
                    from modules.gamification.whack_a_magat.src.whack import get_session_leaderboard
                    session_leaders = get_session_leaderboard(limit=5)
                    
                    if not session_leaders:
                        return f"{mention} [DATA] No session activity yet. Start whacking!"
                    
                    response = f"{mention} [U+1F525] SESSION LEADERS:\n"
                    for entry in session_leaders:
                        response += f"#{entry['position']} {entry['username']} - {entry['session_score']} XP ({entry['session_whacks']} whacks)\n"
                    
                    # Add personal session stats
                    if profile.session_whacks > 0:
                        response += f"\nYour session: {profile.session_score} XP ({profile.session_whacks} whacks)"
                    
                    return response
                else:
                    return f"{mention} [FORBIDDEN] /session is for moderators only"
            
            elif text_lower.startswith('/help'):
                help_msg = f"{mention} [U+1F480] MAGADOOM: /score /rank /whacks /leaderboard /sprees /quiz /quizboard /facts /help | !about"
                if role == 'MOD':
                    help_msg += " | MOD: /session !party"
                if role == 'OWNER':
                    help_msg += " | OWNER: /toggle /session !party !createshort !shortveo !shortsora"
                # Check if user is top 10 whacker (they get !party too!)
                try:
                    position, _ = get_user_position(user_id)
                    if position > 0 and position <= 10 and role not in ['MOD', 'OWNER']:
                        help_msg += f" | TOP {position}: !party 🎉"
                except Exception:
                    pass
                return help_msg

            # Handle deprecated/removed commands with helpful messages
            elif text_lower.startswith('/level'):
                return f"{mention} ℹ️ /level merged into /score - use /score to see your level!"

            elif text_lower.startswith('/answer'):
                return f"{mention} ℹ️ Use /quiz [your answer] to answer quiz questions!"

            elif text_lower.startswith('/top'):
                return f"{mention} ℹ️ Use /leaderboard to see top players!"

            elif text_lower.startswith('/fscale') or text_lower.startswith('/rate'):
                return f"{mention} ℹ️ Command coming soon! Use /facts for fascism info."

            # Educational facts about fascism are PART of MAGADOOM - fighting MAGA requires education!
            
        except Exception as e:
            logger.error(f"Error handling whack command: {e}")
            # Don't suggest /help if the error was FROM /help
            if text_lower == '/help':
                # Return basic help even if there was an error
                return f"{mention} [U+1F480] MAGADOOM Commands: /score /rank /leaderboard (error occurred, some features may not work)"
            else:
                return f"{mention} Error processing command. Try /help"
        
        return None
    
    def _format_quiz_leaderboard(self, username: str) -> str:
        """Format quiz leaderboard"""
        mention = f"@{username.lstrip('@')}"
        if not hasattr(self, 'quiz_engine'):
            from modules.gamification.whack_a_magat.src.quiz_engine import QuizEngine
            self.quiz_engine = QuizEngine()
        
        # Get quiz scores from sessions
        scores = []
        for user_id, session in self.quiz_engine.sessions.items():
            if hasattr(session, 'score') and session.score > 0:
                scores.append((user_id, session.score))
        
        if not scores:
            return f"{mention} No quiz scores yet! Use /quiz to start!"
        
        scores.sort(key=lambda x: x[1], reverse=True)
        top_5 = scores[:5]
        
        result = f"{mention} [AI] QUIZ LEADERS: "
        medals = ["[U+1F947]", "[U+1F948]", "[U+1F949]", "4️⃣", "5️⃣"]
        
        for i, (user_id, score) in enumerate(top_5):
            result += f"{medals[i]}{user_id[:8]}:{score}pts "
        
        return result.strip()
