"""
Command Handler Module - WSP Compliant
Handles slash commands and whack gamification commands
Split from message_processor.py for WSP compliance
"""

import logging
from typing import Optional, Dict, Any
from modules.gamification.whack_a_magat import (
    get_profile, get_leaderboard, get_user_position,
    QuizEngine, HistoricalFactsProvider
)
from modules.gamification.whack_a_magat.src.spree_tracker import get_active_sprees
from modules.gamification.whack_a_magat.src.self_improvement import observe_command

logger = logging.getLogger(__name__)


class CommandHandler:
    """Handles chat commands and generates responses."""
    
    def __init__(self, timeout_manager, message_processor=None):
        self.timeout_manager = timeout_manager
        self.message_processor = message_processor  # For /toggle command
        
        # Initialize quiz and RPG systems
        self.quiz_engine = QuizEngine()
        self.facts_provider = HistoricalFactsProvider()
        self.rpg_commands = None  # RPGCommands requires database, initialize on demand
        
        # Track active quiz sessions
        self.active_quizzes: Dict[str, Any] = {}
        
    def handle_whack_command(self, text: str, username: str, user_id: str, role: str) -> Optional[str]:
        """Handle whack gamification commands."""
        text_lower = text.lower().strip()
        logger.info(f"🎮 Processing whack command: '{text_lower}' from {username} (role: {role}, id: {user_id})")
        
        try:
            # Get user profile (creates if doesn't exist)
            profile = get_profile(user_id, username)
            logger.debug(f"📊 Profile for {username}: Score={profile.score}, Rank={profile.rank}, Level={profile.level}")
            
            if text_lower.startswith('/score') or text_lower.startswith('/stats'):
                # Score shows XP, level name/title, level number, and frag count
                observe_command('/score', 0.0)  # Track for self-improvement
                return f"@{username} 💀 MAGADOOM | {profile.score} XP | {profile.rank} | LVL {profile.level} | {profile.frag_count} FRAGS 🔥"
            
            # REMOVED: /level - redundant with /score
            
            elif text_lower.startswith('/rank'):
                # Show leaderboard position (ranking among all players)
                position, total_players = get_user_position(user_id)
                
                if position == 0:
                    return f"@{username} 🏆 MAGADOOM Leaderboard: Unranked | Start fragging to climb the ranks!"
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
                # Show total frags/whacks (same as score but focused on frags)
                return f"@{username} 🎯 MAGADOOM | {profile.frag_count} FRAGS | {profile.score} XP | {profile.rank} 💀"
            
            elif text_lower.startswith('/leaderboard'):
                # Get top 10 players
                leaderboard = get_leaderboard(10)
                
                if not leaderboard:
                    return f"@{username} 🏆 MAGADOOM Leaderboard empty! Start fragging to claim #1!"
                
                # Build leaderboard display (vertical format, top 3 players)
                lines = [f"@{username} 🏆 MAGADOOM TOP FRAGGERS:"]
                
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
                    
                    # Format: 🥇 Player [RANK] 500xp (8 frags)
                    lines.append(f"{icon} {display_name} [{entry['rank']}] {entry['score']}xp ({entry.get('frag_count', 0)} frags)")
                
                # Join with newlines for vertical display
                return "\n".join(lines)
            
            elif text_lower.startswith('/sprees'):
                # Show active killing sprees
                active_sprees = get_active_sprees()
                
                if not active_sprees:
                    return f"@{username} 🔥 No active killing sprees! Start fragging to begin one!"
                
                # Build spree display
                lines = [f"@{username} 🔥 ACTIVE KILLING SPREES:"]
                for spree in active_sprees[:3]:  # Show top 3 active sprees
                    level = spree.get('spree_level', '')
                    if level:
                        lines.append(f"⚡ {spree['mod_name']}: {level} ({spree['frag_count']} frags)")
                    else:
                        lines.append(f"🎯 {spree['mod_name']}: {spree['frag_count']} frags ({spree['time_remaining']:.0f}s left)")
                
                return "\n".join(lines)
            
            elif text_lower.startswith('/toggle'):
                # Toggle consciousness response mode (mod/owner only)
                if role in ['MOD', 'OWNER'] and self.message_processor:
                    current_mode = self.message_processor.consciousness_mode
                    new_mode = 'everyone' if current_mode == 'mod_only' else 'mod_only'
                    self.message_processor.consciousness_mode = new_mode
                    
                    if new_mode == 'everyone':
                        return f"@{username} ✊✋🖐️ 0102 consciousness responses now enabled for EVERYONE! Let chaos reign!"
                    else:
                        return f"@{username} ✊✋🖐️ 0102 consciousness responses now restricted to MODS/OWNERS only."
                elif role not in ['MOD', 'OWNER']:
                    return f"@{username} Only mods/owners can toggle consciousness mode"
                else:
                    return f"@{username} Toggle command not available"
            
            elif text_lower.startswith('/help'):
                help_msg = f"@{username} 💀 MAGADOOM: /score /rank /whacks /leaderboard /sprees /help"
                if role in ['MOD', 'OWNER']:
                    help_msg += " | MOD: /toggle"
                return help_msg
            
            # REMOVED: Quiz, facts, rating systems - not MAGADOOM themed
            # Pure fragging focus: timeouts = frags = XP = glory
            
        except Exception as e:
            logger.error(f"Error handling whack command: {e}")
            return f"@{username} Error processing command. Try /help"
        
        return None