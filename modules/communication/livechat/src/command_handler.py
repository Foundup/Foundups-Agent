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
import os
from typing import Optional, Dict, Any
from modules.gamification.whack_a_magat import (
    get_profile, get_leaderboard, get_user_position,
    QuizEngine
)
from modules.gamification.whack_a_magat.src.spree_tracker import get_active_sprees
from modules.gamification.whack_a_magat.src.self_improvement import observe_command
from modules.gamification.whack_a_magat.src.historical_facts import get_random_fact, get_parallel, get_warning
from modules.gamification.whack_a_magat.src.magats_economy import MAGAtsEconomy

logger = logging.getLogger(__name__)

import time
import random
from collections import deque


def _env_truthy(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "y", "on")


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
            "[STOP] WHOA! Stop trying to hump me! I'm AFK this is nuts.... be back in {mins}m 🚶",
            "🛑 Y'all need to CHILL! Command spam detected. Taking a {mins}min break to touch grass 🌱",
            "😵 MY CIRCUITS ARE OVERLOADING! Too many commands. Cooldown mode for {mins}m ⏳",
            "🙄 Seriously? This isn't a speedrun. Going AFK for {mins} minutes. Try meditation 🧘",
            "[ALERT] FLOOD ALERT! Bot needs a break from y'all's thirst. Back in {mins}m 💤",
            "ERROR 418: I'M A TEAPOT! Cooldown engaged for {mins} minutes ☕",
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
        # Shorts commands are heavy (Veo/Sora deps) - lazy-load on first use
        self._shorts_handler = None
        self._shorts_available = None

    def _get_shorts_handler(self):
        """
        Lazy-load Shorts handler to avoid startup cost when livechat is running
        but Shorts commands are never invoked.
        """
        if _env_truthy("FOUNDUPS_DISABLE_SHORTS_COMMANDS", "false") or not _env_truthy("FOUNDUPS_ENABLE_SHORTS_COMMANDS", "true"):
            self._shorts_available = False
            return None

        if self._shorts_available is False:
            return None

        if self._shorts_handler is not None:
            return self._shorts_handler

        try:
            from modules.communication.youtube_shorts.src.chat_commands import get_shorts_handler
            self._shorts_handler = get_shorts_handler()
            self._shorts_available = True
            return self._shorts_handler
        except Exception as e:
            self._shorts_available = False
            logger.debug(f"[SHORTS] Shorts commands unavailable: {e}")
            return None

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
            logger.debug(f"[PARTY-DEBUG] !party command detected from @{username} (role={role}, user_id={user_id})")

            if not _env_truthy("YT_AUTOMATION_ENABLED", "true"):
                logger.warning(f"[PARTY-DEBUG] Blocked: YT_AUTOMATION_ENABLED=false")
                return f"@{username} !party disabled (YT_AUTOMATION_ENABLED=false)"
            if not _env_truthy("YT_LIVECHAT_UI_ACTIONS_ENABLED", "true"):
                logger.warning(f"[PARTY-DEBUG] Blocked: YT_LIVECHAT_UI_ACTIONS_ENABLED=false")
                return f"@{username} !party disabled (YT_LIVECHAT_UI_ACTIONS_ENABLED=false)"
            if not _env_truthy("YT_PARTY_REACTIONS_ENABLED", "true"):
                logger.warning(f"[PARTY-DEBUG] Blocked: YT_PARTY_REACTIONS_ENABLED=false")
                return f"@{username} !party disabled (YT_PARTY_REACTIONS_ENABLED=false)"

            # OWNER/MOD OR Top 10 leaderboard members can party!
            can_party = False
            party_reason = ""

            if role == 'OWNER':
                can_party = True
                party_reason = "OWNER"
                logger.debug(f"[PARTY-DEBUG] Permission granted: OWNER role")
            elif role == 'MOD':
                can_party = True
                party_reason = "MOD"
                logger.debug(f"[PARTY-DEBUG] Permission granted: MOD role")
            else:
                # Check if user is in top 10 of whack-a-maga leaderboard
                logger.debug(f"[PARTY-DEBUG] Checking leaderboard position for user_id={user_id}")
                try:
                    position, total = get_user_position(user_id)
                    logger.debug(f"[PARTY-DEBUG] Leaderboard result: position={position}, total={total}")
                    if position > 0 and position <= 10:
                        can_party = True
                        party_reason = f"TOP {position} WHACKER"
                        logger.info(f"[PARTY] {username} is #{position} on leaderboard - party approved!")
                    else:
                        logger.debug(f"[PARTY-DEBUG] Permission denied: position={position} (must be ≤10)")
                except Exception as e:
                    logger.warning(f"[PARTY] Could not check leaderboard position: {e}")
                    logger.debug(f"[PARTY-DEBUG] Leaderboard check error: {type(e).__name__}: {str(e)}")

            if can_party:
                logger.info(f"[PARTY] !party triggered by {username} ({party_reason})")
                try:
                    import asyncio
                    from modules.communication.livechat.src.party_reactor import trigger_party

                    # Parse click count if provided (e.g., !party 50)
                    parts = text_lower.split()
                    clicks = 10  # Default (human-like, not spammy)
                    if len(parts) > 1 and parts[1].isdigit():
                        clicks = min(int(parts[1]), 100)  # Cap at 100
                        logger.debug(f"[PARTY-DEBUG] Custom click count: {clicks} (capped at 100)")
                    else:
                        logger.debug(f"[PARTY-DEBUG] Using default click count: {clicks}")

                    logger.debug(f"[PARTY-DEBUG] Calling trigger_party(total_clicks={clicks})")

                    async def _run_party_background() -> None:
                        try:
                            result = await trigger_party(total_clicks=clicks)
                            logger.info(f"[PARTY] {result}")
                        except Exception as e:
                            logger.error(f"[PARTY] Background party failed: {e}", exc_info=True)

                    # If we're already inside the LiveChat async loop, schedule in background
                    # to avoid blocking polling (and to avoid asyncio.run() in a running loop).
                    try:
                        loop = asyncio.get_running_loop()
                    except RuntimeError:
                        loop = None

                    if loop and loop.is_running():
                        loop.create_task(_run_party_background())
                        return f"{mention} 🎉 Party started ({clicks} reactions) — check logs for progress"

                    # Fallback for non-async contexts (e.g., manual scripts)
                    result = asyncio.run(trigger_party(total_clicks=clicks))
                    logger.debug(f"[PARTY-DEBUG] trigger_party() returned: {result[:50]}...")
                    return result
                except Exception as e:
                    logger.error(f"[PARTY] Error: {e}")
                    logger.error(f"[PARTY-DEBUG] Exception details:")
                    logger.error(f"[PARTY-DEBUG]   Type: {type(e).__name__}")
                    logger.error(f"[PARTY-DEBUG]   Message: {str(e)}")
                    import traceback
                    logger.error(f"[PARTY-DEBUG]   Traceback: {traceback.format_exc()}")
                    return f"@{username} 🎉 Party failed: {e}"
            else:
                logger.warning(f"[PARTY-DEBUG] Permission denied for @{username} (role={role}, not in top 10)")
                return f"@{username} 🎉 !party is for ADMINS or TOP 10 MAGADOOM WHACKERS! Get whacking! 💀✊✋🖐️"

        # Check for YouTube Shorts commands (!createshort, !shortveo, !shortsora, !shortstatus, !shortstats)
        # CRITICAL: Shorts commands use ! prefix (MAGADOOM uses / prefix for separation)
        shorts_keywords = ['!createshort', '!shortveo', '!shortsora', '!short']
        if any(text_lower.startswith(kw) for kw in shorts_keywords):
            shorts_handler = self._get_shorts_handler()
            if shorts_handler:
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
                # Score shows XP, level name/title, level number, and frag count + MAGAts
                observe_command('/score', 0.0)  # Track for self-improvement
                # Calculate MAGAts (10 whacks = 1 MAGAt)
                magats = profile.frag_count // 10
                if magats > 0:
                    return f"{mention} 💀 MAGADOOM | {profile.score} XP | {profile.rank} | LVL {profile.level} | {profile.frag_count} WHACKS | 💎 {magats} MAGAts → Redeem @ foundups.com 🔥"
                else:
                    return f"{mention} 💀 MAGADOOM | {profile.score} XP | {profile.rank} | LVL {profile.level} | {profile.frag_count} WHACKS → foundups.com 🔥"
            
            # REMOVED: /level - redundant with /score
            
            elif text_lower.startswith('/rank'):
                # Show leaderboard position (ranking among all players)
                position, total_players = get_user_position(user_id)
                
                if position == 0:
                    return f"{mention} 🏆 MAGADOOM Leaderboard: Unranked | Start WHACKING MAGAts to climb the ranks!"
                else:
                    # Add special flair for top positions
                    position_str = f"#{position}"
                    if position == 1:
                        position_str = "🥇 #1 CHAMPION"
                    elif position == 2:
                        position_str = "🥈 #2"
                    elif position == 3:
                        position_str = "🥉 #3"
                    
                    # Include MAGAts in rank display
                    magats = profile.frag_count // 10
                    magat_str = f" | 💎 {magats} MAGAts" if magats > 0 else ""
                    return f"{mention} 🏆 MAGADOOM Ranking: {position_str} of {total_players}{magat_str} → foundups.com"

            elif text_lower.startswith('/frags') or text_lower.startswith('/whacks'):
                # Show total frags/whacks (same as score but focused on whacks)
                return f"{mention} [TARGET] MAGADOOM | {profile.frag_count} WHACKS! | {profile.score} XP | {profile.rank} 💀 RIP AND TEAR!"
            
            elif text_lower.startswith('/leaderboard'):
                # Get MONTHLY leaderboard (current competition)
                from datetime import datetime
                current_month = datetime.now().strftime("%B %Y")  # e.g., "January 2025"
                leaderboard = get_leaderboard(10, monthly=True)  # Get monthly scores
                
                if not leaderboard:
                    return f"{mention} 🏆 MAGADOOM {current_month} Leaderboard empty! Start WHACKING to claim #1! 💀"
                
                # Build leaderboard display
                lines = [f"{mention} 🏆 MAGADOOM {current_month.upper()} TOP WHACKERS:"]
                
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
                    return f"{mention} 🔥 No active WHACKING sprees! Start timing out MAGAts to begin one! 💀"
                
                # Build spree display
                lines = [f"{mention} 🔥 ACTIVE KILLING SPREES:"]
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
                logger.warning(f"[AI]🔴[AI] REACHED /QUIZ ELIF BLOCK from {username}")
                logger.warning(f"[AI]🔴[AI] Text: '{text_lower}' | User: {username} | ID: {user_id}")
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

                    response = f"{mention} 🔥 SESSION LEADERS:\n"
                    for entry in session_leaders:
                        response += f"#{entry['position']} {entry['username']} - {entry['session_score']} XP ({entry['session_whacks']} whacks)\n"

                    # Add personal session stats
                    if profile.session_whacks > 0:
                        response += f"\nYour session: {profile.session_score} XP ({profile.session_whacks} whacks)"

                    return response
                else:
                    return f"{mention} [FORBIDDEN] /session is for moderators only"

            elif text_lower.startswith('/fuc'):
                # FFCPLN Mining - MAGAts token economy
                # OWNER + Managing Directors (elevated MODs) can use
                # Managing Directors = trusted MODs with owner-level command access
                MANAGING_DIRECTORS = {
                    # JS (Al-sq5ti) - Move2Japan Managing Director
                    'UCcnCiZV5ZPJ_cjF7RsWIZ0w',
                    # Add more Managing Director user IDs here
                }

                is_managing_director = user_id in MANAGING_DIRECTORS
                if role != 'OWNER' and not is_managing_director:
                    return f"{mention} 💀 /fuc is OWNER/Director only! ✊✋🖐️"

                observe_command('/fuc', 0.0)
                economy = MAGAtsEconomy()

                # Parse subcommand
                parts = text_lower.split()
                subcommand = parts[1] if len(parts) > 1 else "status"

                if subcommand in ['status', 'balance', '']:
                    # Show MAGAt balance
                    balance = economy.get_balance(user_id, username)
                    consciousness = economy._get_consciousness_level(balance.total_magats)

                    if balance.total_whacks == 0:
                        return f"{mention} 💀 FFCPLN MINING: No whacks yet! Start timing out MAGAts to mine tokens! ✊✋🖐️"

                    return (f"{mention} 💰 FFCPLN MINING STATUS:\n"
                           f"🔨 Whacks: {balance.total_whacks} | 💎 MAGAts: {balance.total_magats}\n"
                           f"✅ Claimed: {balance.claimed_magats} | ⏳ Pending: {balance.pending_magats}\n"
                           f"📊 {balance.whacks_to_next} whacks to next MAGAt | {consciousness}")

                elif subcommand == 'claim':
                    # Generate claim link
                    balance = economy.get_balance(user_id, username)

                    if balance.pending_magats <= 0:
                        return f"{mention} 💰 No pending MAGAts to claim! Keep whacking FFCPLNs! (Need {balance.whacks_to_next} more whacks) ✊✋🖐️"

                    claim_url, amount = economy.generate_claim_link(user_id, username)
                    if claim_url:
                        return (f"{mention} 🎁 CLAIM YOUR MAGAts!\n"
                               f"💎 {amount} MAGAts ready to claim\n"
                               f"🔗 {claim_url}\n"
                               f"⚠️ Link tied to YOUR YouTube account only! ✊✋🖐️")
                    else:
                        return f"{mention} ❌ Could not generate claim link. Try again later."

                elif subcommand == 'top':
                    # MAGAts leaderboard
                    leaderboard = economy.get_leaderboard(limit=5)

                    if not leaderboard:
                        return f"{mention} 💎 FFCPLN MINING: No miners yet! Be the first to earn MAGAts! ✊✋🖐️"

                    lines = [f"{mention} 💎 TOP FFCPLN MINERS:"]
                    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

                    for entry in leaderboard:
                        pos = entry['position'] - 1
                        medal = medals[pos] if pos < len(medals) else f"#{entry['position']}"
                        lines.append(f"{medal} {entry['username']}: {entry['total_magats']} MAGAts ({entry['total_whacks']} whacks)")

                    return "\n".join(lines)

                elif subcommand == 'mine':
                    # Mining progress
                    status = economy.get_mining_status(user_id)

                    progress_pct = ((10 - status['whacks_to_next']) / 10) * 100
                    progress_bar = "█" * int(progress_pct / 10) + "░" * (10 - int(progress_pct / 10))

                    return (f"{mention} ⛏️ FFCPLN MINING PROGRESS:\n"
                           f"[{progress_bar}] {progress_pct:.0f}%\n"
                           f"🔨 {status['whacks_to_next']} whacks to next MAGAt\n"
                           f"💎 Total: {status['total_magats']} MAGAts | {status['consciousness_level']}")

                elif subcommand == 'invite':
                    # Share invite code - can target a specific user with @username
                    # Already OWNER-gated at top of /fuc block - no additional check needed

                    # Check for @mention target (e.g., "/fuc invite @SomeUser")
                    target_username = None
                    target_mention = mention  # Default to command issuer

                    # Look for @username in the command
                    import re
                    at_match = re.search(r'@(\S+)', text)
                    if at_match:
                        target_username = at_match.group(1)
                        target_mention = f"@{target_username}"

                    # Check population threshold and stream duration (30+ min)
                    try:
                        from modules.gamification.whack_a_magat.src.invite_distributor import get_invite_code
                        # Get stream start time from message processor for duration check
                        stream_start = getattr(self.message_processor, 'stream_start_time', None) if self.message_processor else None
                        invite_result = get_invite_code(user_id, username, stream_start_time=stream_start)

                        if invite_result['success']:
                            if target_username:
                                # Sending invite to specific user
                                return (f"{target_mention} 🎟️ YOU'VE BEEN GIFTED AN INVITE!\n"
                                       f"💎 Code: {invite_result['code']}\n"
                                       f"🌐 Use at: foundups.com\n"
                                       f"⚠️ One-time use - join FoundUP$ now! ✊✋🖐️\n"
                                       f"🎁 Get 5 invite codes to invite your friends!\n"
                                       f"(Sent by {username})")
                            else:
                                return (f"{mention} 🎟️ EXCLUSIVE INVITE CODE!\n"
                                       f"💎 Code: {invite_result['code']}\n"
                                       f"🌐 Use at: foundups.com\n"
                                       f"⚠️ One-time use only! Share wisely! ✊✋🖐️\n"
                                       f"🎁 New members get 5 invite codes!")
                        else:
                            return f"{mention} 🎟️ {invite_result['message']} ✊✋🖐️"
                    except ImportError:
                        return f"{mention} 🎟️ Invite system initializing... Try again later! ✊✋🖐️"
                    except Exception as e:
                        logger.error(f"[FUC] Invite error: {e}")
                        return f"{mention} 🎟️ Invite system error. Try again later! ✊✋🖐️"

                elif subcommand == 'distribute':
                    # Auto-distribute invites to TOP 10 whackers (OWNER only)
                    try:
                        from modules.gamification.whack_a_magat.src.invite_distributor import auto_distribute_top10_invites, get_invite_stats

                        # Get stats first
                        stats = get_invite_stats()

                        # Run auto-distribution
                        new_invites = auto_distribute_top10_invites()

                        if new_invites:
                            # Return multiple messages - one announcement + one per new invite
                            messages = [f"{mention} 🎯 AUTO-DISTRIBUTING TOP 10 INVITES!"]
                            for inv in new_invites:
                                messages.append(inv['message'])
                            messages.append(f"✅ Distributed {len(new_invites)} new invites! Total: {stats['total_distributed'] + len(new_invites)} ✊✋🖐️")
                            return messages
                        else:
                            return f"{mention} ✅ All TOP 10 whackers already have invites! (Total distributed: {stats['total_distributed']}) ✊✋🖐️"

                    except Exception as e:
                        logger.error(f"[FUC] Distribute error: {e}")
                        return f"{mention} 🎟️ Distribute error: {str(e)[:50]} ✊✋🖐️"

                elif subcommand == 'stats':
                    # Show invite distribution stats (OWNER only)
                    try:
                        from modules.gamification.whack_a_magat.src.invite_distributor import get_invite_stats
                        stats = get_invite_stats()

                        return (f"{mention} 📊 INVITE DISTRIBUTION STATS:\n"
                               f"📨 Total distributed: {stats['total_distributed']}\n"
                               f"👥 Unique recipients: {stats['unique_recipients']}\n"
                               f"🏆 By type: {stats['by_type']} ✊✋🖐️")

                    except Exception as e:
                        logger.error(f"[FUC] Stats error: {e}")
                        return f"{mention} 📊 Stats error: {str(e)[:50]} ✊✋🖐️"

                else:
                    return f"{mention} 💀 /fuc commands: status | claim | top | mine | invite | distribute | stats ✊✋🖐️"
            
            elif text_lower == '/help' or text_lower.startswith('/help'):
                # Return list of messages - message_processor sends each one
                # Message 1: Player commands (everyone)
                help_msgs = [f"{mention} 💀 /score /rank /whacks /leaderboard /sprees /quiz | !about !short"]

                # Message 2: Role-specific commands
                if role == 'OWNER':
                    # OWNER gets all commands including /fuc economy
                    help_msgs.append(f"👑 OWNER: /fc /toggle /session !party !createshort /troll")
                    help_msgs.append(f"💎 /fuc status|claim|top|mine|invite|distribute|stats → FFCPLN Economy")
                elif role == 'MOD':
                    help_msgs.append(f"🛡️ MOD: /fc /session !party /troll")
                else:
                    # Check if top 10 whacker
                    try:
                        position, _ = get_user_position(user_id)
                        if position > 0 and position <= 10:
                            help_msgs.append(f"🏆 TOP {position}: !party !createshort /troll")
                    except Exception:
                        pass

                return help_msgs

            elif text_lower.startswith('/fc'):
                # Fact-check command (MOD/OWNER only)
                observe_command('/fc', 0.0)

                # Permission check - MOD/OWNER only
                if role not in ['OWNER', 'MOD']:
                    return f"{mention} /fc is for ADMINS only! ✊✋🖐️"

                # Parse target username
                parts = text.split()
                if len(parts) < 2:
                    return f"{mention} Usage: /fc @username ✊✋🖐️"

                target_user = parts[1].lstrip('@')

                # Retrieve recent messages
                messages = self._get_user_recent_messages(target_user, limit=10)

                if not messages:
                    return f"{mention} No recent messages from @{target_user} ✊✋🖐️"

                # Fact-check with Grok
                logger.info(f"[FC] {username} fact-checking @{target_user} ({len(messages)} messages)")
                return self._grok_fact_check(target_user, messages, username)

            elif text_lower.startswith('/troll'):
                # Troll/roast command (OWNER, MOD, or TOP 10 whackers)
                observe_command('/troll', 0.0)

                # Permission check
                can_troll = False
                if role in ['OWNER', 'MOD']:
                    can_troll = True
                else:
                    # Check if user is top 10 whacker
                    try:
                        position, _ = get_user_position(user_id)
                        if position > 0 and position <= 10:
                            can_troll = True
                    except Exception:
                        pass

                if not can_troll:
                    return f"{mention} /troll is for ADMINS and TOP 10 WHACKERS! Get whacking to unlock! ✊✋🖐️"

                # Parse target username
                parts = text.split()
                if len(parts) < 2:
                    return f"{mention} Usage: /troll @username ✊✋🖐️"

                target_user = parts[1].lstrip('@')

                # Retrieve recent messages
                messages = self._get_user_recent_messages(target_user, limit=5)

                if not messages:
                    return f"{mention} No recent messages from @{target_user} ✊✋🖐️"

                # Roast with Grok
                logger.info(f"[TROLL] {username} roasting @{target_user} ({len(messages)} messages)")
                return self._grok_roast(target_user, messages, username)

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
                return f"{mention} 💀 MAGADOOM Commands: /score /rank /leaderboard (error occurred, some features may not work)"
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
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

        for i, (user_id, score) in enumerate(top_5):
            result += f"{medals[i]}{user_id[:8]}:{score}pts "

        return result.strip()

    def _get_user_recent_messages(self, username: str, limit: int = 10) -> list:
        """
        Retrieve recent messages from chat telemetry store.

        Args:
            username: Target user's display name
            limit: Number of recent messages to retrieve

        Returns:
            List of message text strings
        """
        try:
            from modules.communication.livechat.src.chat_telemetry_store import ChatTelemetryStore
            store = ChatTelemetryStore()
            messages = store.get_user_messages(username, limit=limit)
            return [msg['text'] for msg in messages if 'text' in msg]
        except Exception as e:
            logger.error(f"[FC] Error retrieving messages: {e}")
            return []

    def _grok_fact_check(self, username: str, messages: list, requester: str) -> str:
        """
        Use Grok to fact-check user's recent messages.

        Args:
            username: Target user being fact-checked
            messages: List of recent messages from user
            requester: User who requested fact-check

        Returns:
            Formatted fact-check response
        """
        try:
            from modules.communication.livechat.src.intelligent_livechat_reply import get_livechat_reply_generator
            reply_gen = get_livechat_reply_generator()

            if not reply_gen.grok_available:
                return f"@{requester} Grok unavailable - fact-check failed ✊✋🖐️"

            # Build fact-check prompt
            message_text = "\n".join([f"- {msg}" for msg in messages[-10:]])
            prompt = f"""Analyze these recent messages from {username} and fact-check their claims:

{message_text}

Provide a concise fact-check (50 words max). Rate truthfulness 0-10.
Format: "Rating: X/10 - {{explanation}}" """

            response = reply_gen.grok_client.get_response(prompt)

            if response:
                return f"@{requester} ✊✋🖐️ FC CHECK: @{username} - {response}"
            else:
                return f"@{requester} Fact-check failed - Grok timeout ✊✋🖐️"

        except Exception as e:
            logger.error(f"[FC] Grok error: {e}")
            return f"@{requester} Fact-check error: {str(e)[:50]} ✊✋🖐️"

    def _grok_roast(self, username: str, messages: list, requester: str) -> str:
        """
        Use Grok to roast/troll user based on recent messages.

        Args:
            username: Target user being roasted
            messages: List of recent messages from user
            requester: User who requested roast

        Returns:
            Formatted roast response
        """
        try:
            from modules.communication.livechat.src.intelligent_livechat_reply import get_livechat_reply_generator
            reply_gen = get_livechat_reply_generator()

            if not reply_gen.grok_available:
                return f"@{requester} Grok unavailable - can't roast right now ✊✋🖐️"

            # Build roast prompt
            message_text = "\n".join([f"- {msg}" for msg in messages[-5:]])
            prompt = f"""Roast this user based on their recent messages. Be witty and sarcastic (not mean-spirited).
Keep it short (40 words max) and end with the 0102 signature.

User: {username}
Recent messages:
{message_text}

Deliver a creative, funny roast!"""

            response = reply_gen.grok_client.get_response(prompt)

            if response:
                # Ensure 0102 signature
                if "✊" not in response and "✋" not in response and "🖐" not in response:
                    response += " ✊✋🖐️"
                return f"@{requester} {response}"
            else:
                return f"@{requester} Roast timed out - Grok too busy laughing ✊✋🖐️"

        except Exception as e:
            logger.error(f"[TROLL] Grok error: {e}")
            return f"@{requester} Roast failed: {str(e)[:50]} ✊✋🖐️"
