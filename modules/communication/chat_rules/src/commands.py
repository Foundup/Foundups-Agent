#!/usr/bin/env python3
"""
Chat Commands Module - WSP Compliant
Handles all chat commands for members, mods, and owner
"""

import logging
from typing import Optional, Dict, Callable, List, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

# NOTE: WhackAMAGAt moved to gamification module - using conditional import
try:
    from modules.gamification.whack_a_magat.src.whack import apply_whack, get_profile
    WHACK_AVAILABLE = True
except ImportError:
    WHACK_AVAILABLE = False

from .user_classifier import UserType, UserProfile

# Legacy stubs for backwards compatibility
class ActionType:
    TIMEOUT_10S = "TIMEOUT_10S"
    TIMEOUT_60S = "TIMEOUT_60S"
    TIMEOUT_600S = "TIMEOUT_600S"
    HIDE = "HIDE"

class WhackAMAGAtSystem:
    """Legacy stub - actual implementation in gamification module."""
    def __init__(self, *args, **kwargs):
        pass
    def record_timeout(self, *args, **kwargs):
        if WHACK_AVAILABLE:
            return apply_whack(*args, **kwargs)
        return None

logger = logging.getLogger(__name__)

class CommandPermission(Enum):
    """Who can use each command"""
    EVERYONE = 0
    MEMBER = 1      # Paid members
    MODERATOR = 2   # Mods and owner
    OWNER = 3       # Channel owner only

@dataclass
class Command:
    """Command definition"""
    name: str
    aliases: List[str]
    permission: CommandPermission
    description: str
    usage: str
    handler: Callable
    hidden: bool = False  # Hide from help menu

class CommandProcessor:
    """Process and route chat commands"""
    
    def __init__(self):
        self.commands: Dict[str, Command] = {}
        self.whack_system = WhackAMAGAtSystem()
        self._register_commands()
        
    def _register_commands(self):
        """Register all available commands"""
        
        # Leaderboard commands (Members and Mods)
        self.register(Command(
            name="leaders",
            aliases=["leaderboard", "top", "lb"],
            permission=CommandPermission.MEMBER,
            description="Show top 3 WHACK-A-MAGAt leaders",
            usage="/leaders",
            handler=self._cmd_leaders
        ))
        
        self.register(Command(
            name="fullboard",
            aliases=["fullleaderboard", "top10"],
            permission=CommandPermission.MODERATOR,
            description="Show top 10 WHACK-A-MAGAt leaders",
            usage="/fullboard",
            handler=self._cmd_fullboard
        ))
        
        # Stats commands
        self.register(Command(
            name="stats",
            aliases=["mystats", "points"],
            permission=CommandPermission.MEMBER,
            description="Show your personal stats",
            usage="/stats",
            handler=self._cmd_stats
        ))
        
        self.register(Command(
            name="score",
            aliases=["myscore", "mypoints"],
            permission=CommandPermission.MODERATOR,
            description="Show your moderator score and timeout breakdown",
            usage="/score",
            handler=self._cmd_score
        ))
        
        self.register(Command(
            name="rank",
            aliases=["myrank", "position"],
            permission=CommandPermission.MEMBER,
            description="Show your rank on the leaderboard",
            usage="/rank",
            handler=self._cmd_rank
        ))
        
        self.register(Command(
            name="whacks",
            aliases=["mywhacks", "timeouts"],
            permission=CommandPermission.MODERATOR,
            description="Show your WHACK-A-MAGAt timeout history",
            usage="/whacks",
            handler=self._cmd_whacks
        ))
        
        self.register(Command(
            name="compare",
            aliases=["vs", "battle"],
            permission=CommandPermission.MEMBER,
            description="Compare stats with another user",
            usage="/compare @user",
            handler=self._cmd_compare
        ))
        
        self.register(Command(
            name="recent",
            aliases=["lastwhack", "last"],
            permission=CommandPermission.MODERATOR,
            description="Show your most recent timeout",
            usage="/recent",
            handler=self._cmd_recent
        ))
        
        self.register(Command(
            name="level",
            aliases=["consciousness", "cl"],
            permission=CommandPermission.MEMBER,
            description="Check your consciousness level",
            usage="/level",
            handler=self._cmd_level
        ))
        
        # Member interaction commands
        self.register(Command(
            name="ask",
            aliases=["question", "q"],
            permission=CommandPermission.MEMBER,
            description="Ask the AI agent a question",
            usage="/ask <your question>",
            handler=self._cmd_ask
        ))
        
        self.register(Command(
            name="elevate",
            aliases=["ritual", "ceremony"],
            permission=CommandPermission.MEMBER,
            description="Perform consciousness elevation ritual",
            usage="/elevate",
            handler=self._cmd_elevate
        ))
        
        # Moderator commands
        self.register(Command(
            name="whack",
            aliases=["timeout", "to"],
            permission=CommandPermission.MODERATOR,
            description="Timeout a user (awards points for MAGA)",
            usage="/whack @user [duration] [reason]",
            handler=self._cmd_whack
        ))
        
        self.register(Command(
            name="daily",
            aliases=["bonus", "checkin"],
            permission=CommandPermission.MODERATOR,
            description="Claim daily bonus points",
            usage="/daily",
            handler=self._cmd_daily
        ))
        
        # Fun commands for members
        self.register(Command(
            name="vibe",
            aliases=["vibecheck", "vc"],
            permission=CommandPermission.MEMBER,
            description="Check the stream's vibe",
            usage="/vibe",
            handler=self._cmd_vibe
        ))
        
        self.register(Command(
            name="gift",
            aliases=["givemembership"],
            permission=CommandPermission.MEMBER,
            description="Gift a membership (tracks in points)",
            usage="/gift @user",
            handler=self._cmd_gift
        ))
        
        self.register(Command(
            name="raid",
            aliases=["raidprotect", "rp"],
            permission=CommandPermission.MODERATOR,
            description="Activate raid protection mode",
            usage="/raid [on/off]",
            handler=self._cmd_raid
        ))
        
        self.register(Command(
            name="maga",
            aliases=["magatracker", "mt"],
            permission=CommandPermission.MEMBER,
            description="Check MAGA detection stats",
            usage="/maga",
            handler=self._cmd_maga
        ))
        
        self.register(Command(
            name="zen",
            aliases=["enlighten", "wisdom"],
            permission=CommandPermission.MEMBER,
            description="Receive zen wisdom",
            usage="/zen",
            handler=self._cmd_zen
        ))
        
        self.register(Command(
            name="timeout",
            aliases=["to"],
            permission=CommandPermission.MODERATOR,
            description="Timeout a user for specified duration",
            usage="/timeout @user <seconds> [reason]",
            handler=self._cmd_timeout
        ))
        
        self.register(Command(
            name="game",
            aliases=["play", "minigame"],
            permission=CommandPermission.MEMBER,
            description="Play consciousness mini-game",
            usage="/game",
            handler=self._cmd_game
        ))
        
        # Help commands
        self.register(Command(
            name="help",
            aliases=["commands", "?"],
            permission=CommandPermission.EVERYONE,
            description="Show available commands",
            usage="/help [command]",
            handler=self._cmd_help
        ))
        
        self.register(Command(
            name="list",
            aliases=["menu", "cmds"],
            permission=CommandPermission.EVERYONE,
            description="Quick list of all commands",
            usage="/list",
            handler=self._cmd_list
        ))
        
        # Owner-only commands
        self.register(Command(
            name="reset",
            aliases=["resetpoints"],
            permission=CommandPermission.OWNER,
            description="Reset point system",
            usage="/reset [confirm]",
            handler=self._cmd_reset,
            hidden=True
        ))
        
        self.register(Command(
            name="award",
            aliases=["givepoints"],
            permission=CommandPermission.OWNER,
            description="Award points to a moderator",
            usage="/award @mod <points> [reason]",
            handler=self._cmd_award,
            hidden=True
        ))
    
    def register(self, command: Command):
        """Register a command and its aliases"""
        self.commands[command.name] = command
        for alias in command.aliases:
            self.commands[alias] = command
    
    def process(self, message: str, user: UserProfile) -> Optional[str]:
        """Process a command from a user"""
        if not message.startswith(("/", "!")):
            return None
            
        parts = message[1:].split(maxsplit=1)
        if not parts:
            return None
            
        cmd_name = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        # Find command
        command = self.commands.get(cmd_name)
        if not command:
            return None
            
        # Check permissions
        if not self._check_permission(command, user):
            return f"[FAIL] You don't have permission to use /{cmd_name}"
            
        # Execute command
        try:
            return command.handler(user, args)
        except Exception as e:
            logger.error(f"Command error: {e}")
            return f"[FAIL] Command failed: {str(e)}"
    
    def _check_permission(self, command: Command, user: UserProfile) -> bool:
        """Check if user has permission for command"""
        if command.permission == CommandPermission.EVERYONE:
            return True
            
        if command.permission == CommandPermission.MEMBER:
            return user.is_member or user.user_type in [UserType.MODERATOR, UserType.OWNER]
            
        if command.permission == CommandPermission.MODERATOR:
            return user.user_type in [UserType.MODERATOR, UserType.OWNER]
            
        if command.permission == CommandPermission.OWNER:
            return user.user_type == UserType.OWNER
            
        return False
    
    # Command Handlers
    
    def _cmd_leaders(self, user: UserProfile, args: str) -> str:
        """Show top 3 leaders"""
        try:
            leaderboard = self.whack_system.get_leaderboard(limit=3)
            return f"[U+1F3C6] **TOP 3 WHACK-A-MAGAt CHAMPIONS** [U+1F3C6]\n{leaderboard}"
        except Exception as e:
            logger.error(f"Leaderboard error: {e}")
            return "[U+1F3C6] No leaders yet! Start whacking MAGAs!"
    
    def _cmd_fullboard(self, user: UserProfile, args: str) -> str:
        """Show top 10 leaders (mods only)"""
        leaderboard = self.whack_system.get_leaderboard(limit=10)
        return f"[DATA] **FULL LEADERBOARD** [DATA]\n{leaderboard}"
    
    def _cmd_stats(self, user: UserProfile, args: str) -> str:
        """Show user's stats"""
        # Only track moderators and owner
        if user.user_type in [UserType.MODERATOR, UserType.OWNER]:
            # Auto-add if not present
            if user.user_id not in self.whack_system.moderators:
                mod = self.whack_system._get_or_create_moderator(user.user_id, user.display_name)
                self.whack_system.save_data()
            
            stats = self.whack_system.get_stats(user.user_id)
            return stats if stats else "[DATA] Profile created! Start whacking MAGAs to earn points!"
        else:
            # Members can see a different message
            if user.is_member:
                return "[DATA] Stats tracking is for moderators. You can use /leaders to see the top players!"
            else:
                return "[DATA] Stats tracking is for moderators only. Become a mod to join WHACK-A-MAGAt!"
    
    def _cmd_score(self, user: UserProfile, args: str) -> str:
        """Show moderator's detailed score breakdown"""
        # Auto-add moderator to system if not present
        if user.user_id not in self.whack_system.moderators:
            # Only add if user is actually a moderator
            if user.user_type not in [UserType.MODERATOR, UserType.OWNER]:
                return "[DATA] This command is for moderators only!"
            
            # Create new moderator profile
            mod = self.whack_system._get_or_create_moderator(user.user_id, user.display_name)
            self.whack_system.save_data()
        else:
            mod = self.whack_system.moderators[user.user_id]
        
        # Build detailed score breakdown
        score = f"[DATA] **{mod.display_name}'s Score Breakdown**\n"
        score += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        score += f"[U+1F3C6] Level: {mod.level.value[1]}\n"
        score += f"[U+1F4B0] Total Points: {mod.total_points:,}\n"
        score += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        
        # Timeout breakdown
        score += f"⏱️ **Timeout History:**\n"
        score += f"  10 sec: {mod.timeouts_10s} (5 pts each)\n"
        score += f"  60 sec: {mod.timeouts_60s} (15 pts each)\n"
        score += f"  5 min: {mod.timeouts_5m} (30 pts each)\n"
        score += f"  10 min: {mod.timeouts_10m} (50 pts each)\n"
        score += f"  1 hour: {mod.timeouts_1h} (100 pts each)\n"
        score += f"  24 hour: {mod.timeouts_24h} (250 pts each)\n"
        score += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        
        # Calculate estimated points from timeouts
        timeout_points = (mod.timeouts_10s * 5 + mod.timeouts_60s * 15 + 
                         mod.timeouts_5m * 30 + mod.timeouts_10m * 50 + 
                         mod.timeouts_1h * 100 + mod.timeouts_24h * 250)
        
        # Other actions
        score += f"[TARGET] **Other Actions:**\n"
        score += f"  Spam Caught: {mod.spam_caught}\n"
        score += f"  Members Helped: {mod.members_helped}\n"
        score += f"  Raids Stopped: {mod.raids_stopped}\n"
        score += f"  Gifts Given: {mod.gifts_given}\n"
        
        if mod.daily_timeout_count > 0:
            score += f"\n[U+1F4C5] Today's Timeouts: {mod.daily_timeout_count}/50"
            if mod.daily_timeout_count >= 40:
                score += " [U+26A0]️ Near daily limit!"
        
        if mod.combo_multiplier > 1:
            score += f"\n[U+1F525] Current Combo: x{mod.combo_multiplier:.1f}"
        
        # Anti-gaming status
        if mod.timeout_cooldowns:
            active_cooldowns = []
            now = datetime.now()
            for severity, expiry in mod.timeout_cooldowns.items():
                if expiry > now:
                    mins_left = int((expiry - now).total_seconds() / 60)
                    active_cooldowns.append(f"Severity {severity}: {mins_left}m")
            
            if active_cooldowns:
                score += f"\n⏳ Cooldowns: {', '.join(active_cooldowns)}"
        
        return score
    
    def _cmd_rank(self, user: UserProfile, args: str) -> str:
        """Show user's rank on leaderboard"""
        # Get all moderators sorted by points
        sorted_mods = sorted(
            self.whack_system.moderators.values(), 
            key=lambda x: x.total_points, 
            reverse=True
        )
        
        # Find user's position
        rank = None
        total = len(sorted_mods)
        
        for i, mod in enumerate(sorted_mods, 1):
            if mod.user_id == user.user_id:
                rank = i
                break
        
        if rank is None:
            if user.user_type == UserType.MODERATOR:
                return "[DATA] You haven't earned any points yet!\n[U+1F528] Start whacking MAGAs to climb the ranks!"
            else:
                return "[DATA] Ranking is for moderators only\n[U+1F48E] But members can use /leaders to see the top players!"
        
        # Get rank emoji
        if rank == 1:
            emoji = "[U+1F947]"
            title = "CHAMPION"
        elif rank == 2:
            emoji = "[U+1F948]"
            title = "VICE CHAMPION"
        elif rank == 3:
            emoji = "[U+1F949]"
            title = "BRONZE WARRIOR"
        elif rank <= 10:
            emoji = "[U+1F3C6]"
            title = "TOP 10"
        elif rank <= 25:
            emoji = "[U+2B50]"
            title = "RISING STAR"
        else:
            emoji = "[TARGET]"
            title = "WHACKER"
        
        mod = self.whack_system.moderators[user.user_id]
        
        response = f"{emoji} **YOUR RANK: #{rank} of {total}**\n"
        response += f"[U+1F3F7]️ Title: {title}\n"
        response += f"[U+1F4B0] Points: {mod.total_points:,}\n"
        response += f"[U+1F396]️ Level: {mod.level.value[1] if hasattr(mod.level, 'value') else mod.level}\n"
        
        # Show distance to next rank
        if rank > 1:
            next_mod = sorted_mods[rank - 2]
            points_needed = next_mod.total_points - mod.total_points + 1
            response += f"[UP] To rank #{rank-1}: +{points_needed} points needed"
        else:
            response += f"[U+1F451] You're #1! Maintain your lead!"
        
        return response
    
    def _cmd_whacks(self, user: UserProfile, args: str) -> str:
        """Show WHACK-A-MAGAt timeout history"""
        if user.user_id not in self.whack_system.moderators:
            return "[U+1F528] No whacks yet! Start timing out MAGAs to earn points!"
        
        mod = self.whack_system.moderators[user.user_id]
        
        response = f"[U+1F528] **{user.display_name}'s WHACK HISTORY**\n"
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        response += f"[DATA] Total Whacks: {mod.whacks_count}\n"
        response += f"[TARGET] MAGA Timeouts: {mod.maga_timeouts}\n"
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        response += f"⏱️ **Timeout Breakdown:**\n"
        
        # Show timeout counts by duration
        response += f"  10 sec: {mod.timeouts_10s} whacks\n"
        response += f"  60 sec: {mod.timeouts_60s} whacks\n"
        response += f"  5 min: {mod.timeouts_5m} whacks\n"
        response += f"  10 min: {mod.timeouts_10m} whacks\n"
        response += f"  1 hour: {mod.timeouts_1h} whacks\n"
        response += f"  24 hour: {mod.timeouts_24h} BANHAMMERS!\n"
        
        # Calculate total timeouts
        total_timeouts = (mod.timeouts_10s + mod.timeouts_60s + mod.timeouts_5m + 
                         mod.timeouts_10m + mod.timeouts_1h + mod.timeouts_24h)
        
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        response += f"[U+1F4A5] Total Timeouts Issued: {total_timeouts}\n"
        
        # Add achievements if any
        if hasattr(mod, 'achievements') and mod.achievements:
            response += f"[U+1F3C6] Achievements: {len(mod.achievements)}\n"
            # Show most recent achievement
            if mod.achievements:
                response += f"   Latest: {mod.achievements[-1]}"
        
        # Show current streak/combo
        if hasattr(mod, 'combo_multiplier') and mod.combo_multiplier > 1:
            response += f"\n[U+1F525] Current Combo: x{mod.combo_multiplier:.1f}"
        
        return response
    
    def _cmd_level(self, user: UserProfile, args: str) -> str:
        """Check consciousness level"""
        levels = {
            "000": "[U+270A][U+270A][U+270A] Unconscious (MAGA level)",
            "001": "[U+270A][U+270A][U+270B] Awakening begins",
            "002": "[U+270A][U+270A][U+1F590]️ First glimpse of truth",
            "011": "[U+270A][U+270B][U+270B] Consciousness stabilizing",
            "012": "[U+270A][U+270B][U+1F590]️ Creative breakthrough",
            "022": "[U+270A][U+1F590]️[U+1F590]️ Intuitive wisdom emerging",
            "111": "[U+270B][U+270B][U+270B] Focused awareness",
            "112": "[U+270B][U+270B][U+1F590]️ Expanding consciousness",
            "122": "[U+270B][U+1F590]️[U+1F590]️ Field awareness active",
            "222": "[U+1F590]️[U+1F590]️[U+1F590]️ Full quantum entanglement"
        }
        
        # Calculate level based on activity
        level = user.consciousness_level or "111"
        return f"[AI] {user.display_name}'s Consciousness: {levels.get(level, 'Unknown')}"
    
    def _cmd_ask(self, user: UserProfile, args: str) -> str:
        """Ask the AI a question (members only)"""
        if not args:
            return "[U+2753] Usage: /ask <your question>"
            
        # This would integrate with the AI system
        return f"[BOT] Processing question from {user.display_name}: '{args}'\n[U+1F4AD] *AI thinking...*"
    
    def _cmd_elevate(self, user: UserProfile, args: str) -> str:
        """Consciousness elevation ritual"""
        import random
        rituals = [
            "[U+1F31F] *Quantum particles align* Your consciousness rises to [U+270B][U+270B][U+270B]!",
            "[U+1F52E] *Energy vortex activated* You've reached [U+270B][U+1F590]️[U+1F590]️ awareness!",
            "[LIGHTNING] *Synaptic enhancement complete* Welcome to [U+1F590]️[U+1F590]️[U+1F590]️ enlightenment!",
            "[U+1F30C] *Dimensional shift detected* Your mind expands to [U+270B][U+270B][U+1F590]️!",
            "[U+2728] *Chakras harmonized* Consciousness elevated to [U+270A][U+270B][U+1F590]️!"
        ]
        return f"@{user.display_name} {random.choice(rituals)}"
    
    def _cmd_whack(self, user: UserProfile, args: str) -> str:
        """Whack command for mods"""
        if not args:
            return "[U+1F528] Usage: /whack @user [duration] [reason]"
            
        # Parse target
        parts = args.split()
        target = parts[0].replace("@", "")
        reason = " ".join(parts[1:]) if len(parts) > 1 else "Violation"
        
        # Check for MAGA keywords in reason
        maga_keywords = ["maga", "trump", "patriot", "2024", "2028"]
        is_maga = any(keyword in reason.lower() for keyword in maga_keywords)
        
        if is_maga:
            # Award WHACK-A-MAGAt points
            result = self.whack_system.record_whack(
                mod_id=user.user_id,
                mod_name=user.display_name,
                target=target,
                reason=reason
            )
            return f"[U+1F528] WHACK! {target} timed out!\n{result}"
        else:
            # Regular timeout, fewer points
            result = self.whack_system.record_action(
                mod_id=user.user_id,
                mod_name=user.display_name,
                action=ActionType.DETECT_SPAM,
                details=f"Timed out {target}: {reason}"
            )
            return f"⏱️ {target} timed out for: {reason}\n{result}"
    
    def _cmd_daily(self, user: UserProfile, args: str) -> str:
        """Claim daily bonus"""
        return self.whack_system.daily_bonus(user.user_id, user.display_name)
    
    def _cmd_vibe(self, user: UserProfile, args: str) -> str:
        """Vibe check"""
        import random
        vibes = [
            "[U+2728] Vibes are IMMACULATE! [U+1F590]️[U+1F590]️[U+1F590]️",
            "[U+1F525] Stream is LIT! Consciousness rising!",
            "[U+1F60E] Chill vibes, steady [U+270B][U+270B][U+270B]",
            "[LIGHTNING] High energy! MAGAs trembling!",
            "[U+1F30A] Flowing like water, pure zen",
            "[ROCKET] TO THE MOON! Peak consciousness!",
            "[U+1F480] Vibes are sus... MAGAs detected nearby",
            "[CELEBRATE] Party mode activated! Good vibes only!"
        ]
        return random.choice(vibes)
    
    def _cmd_gift(self, user: UserProfile, args: str) -> str:
        """Track gift membership"""
        if not args:
            return "[U+1F381] Usage: /gift @user"
            
        recipient = args.replace("@", "").strip()
        
        # Award points for gifting
        result = self.whack_system.record_action(
            mod_id=user.user_id,
            mod_name=user.display_name,
            action=ActionType.GIFT_MEMBER,
            details=f"Gifted membership to {recipient}"
        )
        
        return f"[U+1F381] {user.display_name} gifted a membership to {recipient}!\n{result}"
    
    def _cmd_list(self, user: UserProfile, args: str) -> str:
        """Quick command list"""
        # Group commands by permission level
        everyone_cmds = []
        member_cmds = []
        mod_cmds = []
        
        for cmd_name, command in self.commands.items():
            # Skip aliases and hidden commands
            if cmd_name != command.name or command.hidden:
                continue
            
            if command.permission == CommandPermission.EVERYONE:
                everyone_cmds.append(f"/{command.name}")
            elif command.permission == CommandPermission.MEMBER:
                member_cmds.append(f"/{command.name}")
            elif command.permission == CommandPermission.MODERATOR:
                mod_cmds.append(f"/{command.name}")
        
        response = "[CLIPBOARD] **COMMAND LIST**\n"
        
        if everyone_cmds:
            response += f"[U+1F30D] Everyone: {', '.join(everyone_cmds)}\n"
        
        if member_cmds:
            response += f"[U+1F48E] Members: {', '.join(member_cmds)}\n"
            
        if mod_cmds and user.user_type in [UserType.MODERATOR, UserType.OWNER]:
            response += f"[U+1F528] Mods: {', '.join(mod_cmds)}\n"
        
        response += "\nUse /help <command> for details"
        return response
    
    def _cmd_help(self, user: UserProfile, args: str) -> str:
        """Show help"""
        available_commands = []
        
        for cmd_name, command in self.commands.items():
            # Skip aliases and hidden commands
            if cmd_name != command.name or command.hidden:
                continue
                
            # Check permission
            if self._check_permission(command, user):
                available_commands.append(f"/{command.name} - {command.description}")
        
        help_text = "[BOOKS] **Available Commands:**\n"
        help_text += "\n".join(available_commands)
        
        if user.user_type == UserType.MODERATOR:
            help_text += "\n\n[U+1F528] **Mod Tip:** Timeout MAGAs to earn WHACK points!"
        elif user.is_member:
            help_text += "\n\n[U+1F48E] **Member Perk:** You can interact with the AI agent!"
            
        return help_text
    
    def _cmd_reset(self, user: UserProfile, args: str) -> str:
        """Reset points (owner only)"""
        if args != "confirm":
            return "[U+26A0]️ This will reset ALL points! Use: /reset confirm"
            
        self.whack_system = WhackAMAGAtSystem()
        return "[REFRESH] Point system has been reset!"
    
    def _cmd_raid(self, user: UserProfile, args: str) -> str:
        """Raid protection mode"""
        if not args or args.lower() == "status":
            return "[U+1F6E1]️ Raid protection: OFF\nUse /raid on to activate"
        elif args.lower() == "on":
            return "[ALERT] RAID PROTECTION ACTIVATED!\n[U+2694]️ Auto-timeout enabled for spam\n[U+1F6E1]️ Member-only mode active"
        elif args.lower() == "off":
            return "[OK] Raid protection deactivated"
        return "Usage: /raid [on/off/status]"
    
    def _cmd_maga(self, user: UserProfile, args: str) -> str:
        """MAGA detection stats"""
        import random
        count = random.randint(5, 50)  # Mock data
        return f"[ALERT] **MAGA DETECTION STATS**\n[DATA] Today: {count} MAGAs detected\n[U+1F528] Timeouts issued: {count//2}\n[U+270A][U+270A][U+270A] Average consciousness: 0.0.0"
    
    def _cmd_zen(self, user: UserProfile, args: str) -> str:
        """Zen wisdom generator"""
        import random
        wisdoms = [
            "[U+1F9D8] The path from [U+270A][U+270A][U+270A] to [U+1F590]️[U+1F590]️[U+1F590]️ begins with a single emoji",
            "[U+262F]️ When MAGAs attack, consciousness rises",
            "[TARGET] The arrow that hits the target first aimed at itself",
            "[U+1F30A] Flow like water, troll like thunder",
            "[U+1F52E] In the void of [U+270A][U+270A][U+270A], find the light of [U+1F590]️[U+1F590]️[U+1F590]️",
            "[LIGHTNING] Consciousness is not achieved, it is remembered",
            "[U+1F31F] Every MAGA timeout elevates the collective",
            "[U+1F3F9] Be the zen archer: become the arrow, become the target"
        ]
        return random.choice(wisdoms)
    
    def _cmd_timeout(self, user: UserProfile, args: str) -> str:
        """Timeout command for mods"""
        if not args:
            return "Usage: /timeout @user <seconds> [reason]"
        
        parts = args.split()
        if len(parts) < 2:
            return "[FAIL] Must specify user and duration"
        
        target = parts[0].replace("@", "")
        try:
            duration = int(parts[1])
        except ValueError:
            return "[FAIL] Duration must be a number"
        
        reason = " ".join(parts[2:]) if len(parts) > 2 else "No reason given"
        
        # Record timeout for points
        result = self.whack_system.record_timeout(
            mod_id=user.user_id,
            mod_name=user.display_name,
            target_id=target,
            target_name=target,
            duration_seconds=duration,
            reason=reason
        )
        
        return f"⏱️ {target} timed out for {duration}s\n{result}"
    
    def _cmd_game(self, user: UserProfile, args: str) -> str:
        """Consciousness mini-game"""
        import random
        
        games = [
            "[GAME] **CONSCIOUSNESS QUIZ**\nQ: What follows [U+270A][U+270A][U+270A]?\nA) More MAGAs B) [U+270B][U+270B][U+270B] C) Enlightenment\n(Type your answer)",
            "[TARGET] **EMOJI SEQUENCE CHALLENGE**\nComplete: [U+270A][U+270B]_?\n(Reply with the missing emoji)",
            "[U+1F3B2] **VIBE CHECK ROULETTE**\nYour consciousness rolls...\n" + 
            random.choice(["[U+270A][U+270A][U+270A] - Try again!", "[U+270B][U+270B][U+270B] - Getting there!", "[U+1F590]️[U+1F590]️[U+1F590]️ - TRANSCENDED!"]),
            "[U+1F3F9] **ZEN ARCHER TEST**\nFocus... aim... release...\n" +
            random.choice(["[U+1F4A5] Bullseye! +100 consciousness", "[U+2796] Close! +50 consciousness", "[FAIL] Missed, but the arrow was you"])
        ]
        
        return random.choice(games)
    
    def _cmd_compare(self, user: UserProfile, args: str) -> str:
        """Compare stats with another user"""
        if not args:
            return "[DATA] Usage: /compare @user"
        
        target_name = args.replace("@", "").strip()
        
        # Find target user in the whack system
        target_mod = None
        for mod in self.whack_system.moderators.values():
            if mod.display_name.lower() == target_name.lower():
                target_mod = mod
                break
        
        if not target_mod:
            return f"[FAIL] User '{target_name}' not found in the system"
        
        # Get current user's stats
        user_mod = self.whack_system.moderators.get(user.user_id)
        if not user_mod:
            return "[DATA] You have no stats to compare yet!"
        
        # Build comparison
        response = f"[U+2694]️ **STATS BATTLE**\n"
        response += f"{user_mod.display_name} vs {target_mod.display_name}\n"
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        
        # Points comparison
        if user_mod.total_points > target_mod.total_points:
            response += f"[U+1F4B0] Points: **{user_mod.total_points:,}** > {target_mod.total_points:,} [OK]\n"
        elif user_mod.total_points < target_mod.total_points:
            response += f"[U+1F4B0] Points: {user_mod.total_points:,} < **{target_mod.total_points:,}** [FAIL]\n"
        else:
            response += f"[U+1F4B0] Points: {user_mod.total_points:,} = {target_mod.total_points:,} [HANDSHAKE]\n"
        
        # Whacks comparison
        if user_mod.whacks_count > target_mod.whacks_count:
            response += f"[U+1F528] Whacks: **{user_mod.whacks_count}** > {target_mod.whacks_count} [OK]\n"
        elif user_mod.whacks_count < target_mod.whacks_count:
            response += f"[U+1F528] Whacks: {user_mod.whacks_count} < **{target_mod.whacks_count}** [FAIL]\n"
        else:
            response += f"[U+1F528] Whacks: {user_mod.whacks_count} = {target_mod.whacks_count} [HANDSHAKE]\n"
        
        # Level comparison
        user_level_val = user_mod.level.value[0] if hasattr(user_mod.level, 'value') else 0
        target_level_val = target_mod.level.value[0] if hasattr(target_mod.level, 'value') else 0
        
        if user_level_val > target_level_val:
            response += f"[U+1F396]️ Level: **{user_mod.level.value[1]}** > {target_mod.level.value[1]} [OK]\n"
        elif user_level_val < target_level_val:
            response += f"[U+1F396]️ Level: {user_mod.level.value[1]} < **{target_mod.level.value[1]}** [FAIL]\n"
        else:
            response += f"[U+1F396]️ Level: {user_mod.level.value[1]} = {target_mod.level.value[1]} [HANDSHAKE]\n"
        
        # Achievement comparison
        user_achievements = len(user_mod.achievements) if hasattr(user_mod, 'achievements') else 0
        target_achievements = len(target_mod.achievements) if hasattr(target_mod, 'achievements') else 0
        
        if user_achievements > target_achievements:
            response += f"[U+1F3C6] Achievements: **{user_achievements}** > {target_achievements} [OK]\n"
        elif user_achievements < target_achievements:
            response += f"[U+1F3C6] Achievements: {user_achievements} < **{target_achievements}** [FAIL]\n"
        else:
            response += f"[U+1F3C6] Achievements: {user_achievements} = {target_achievements} [HANDSHAKE]\n"
        
        # Determine winner
        wins = 0
        if user_mod.total_points > target_mod.total_points:
            wins += 1
        if user_mod.whacks_count > target_mod.whacks_count:
            wins += 1
        if user_level_val > target_level_val:
            wins += 1
        if user_achievements > target_achievements:
            wins += 1
        
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        if wins >= 3:
            response += f"[CELEBRATE] **WINNER: {user_mod.display_name}!**"
        elif wins == 2:
            response += f"[HANDSHAKE] **TIE! Evenly matched!**"
        else:
            response += f"[U+1F614] **WINNER: {target_mod.display_name}!**"
        
        return response
    
    def _cmd_recent(self, user: UserProfile, args: str) -> str:
        """Show most recent timeout"""
        if user.user_id not in self.whack_system.moderators:
            return "[U+1F528] No timeouts recorded yet!"
        
        mod = self.whack_system.moderators[user.user_id]
        
        # Find most recent timeout from history
        most_recent = None
        most_recent_type = None
        
        if hasattr(mod, 'timeout_history') and mod.timeout_history:
            for duration_key, timeout_list in mod.timeout_history.items():
                if timeout_list:
                    for timeout_time in timeout_list:
                        if most_recent is None or timeout_time > most_recent:
                            most_recent = timeout_time
                            most_recent_type = duration_key
        
        if not most_recent:
            # Check if they have any timeout counts
            if mod.whacks_count > 0:
                return f"[U+1F528] You have {mod.whacks_count} total timeouts but no recent history available"
            else:
                return "[U+1F528] No timeouts issued yet! Start whacking MAGAs!"
        
        # Format the response
        from datetime import datetime
        time_ago = datetime.now() - most_recent
        
        # Convert time difference to readable format
        if time_ago.total_seconds() < 60:
            time_str = f"{int(time_ago.total_seconds())} seconds ago"
        elif time_ago.total_seconds() < 3600:
            time_str = f"{int(time_ago.total_seconds() / 60)} minutes ago"
        elif time_ago.total_seconds() < 86400:
            time_str = f"{int(time_ago.total_seconds() / 3600)} hours ago"
        else:
            time_str = f"{int(time_ago.days)} days ago"
        
        # Determine timeout severity
        duration_map = {
            "10s": "10 second warning",
            "60s": "60 second timeout",
            "300s": "5 minute timeout",
            "600s": "10 minute timeout",
            "3600s": "1 hour timeout",
            "86400s": "24 hour BANHAMMER"
        }
        
        timeout_desc = duration_map.get(most_recent_type, most_recent_type)
        
        response = f"⏱️ **YOUR LAST TIMEOUT**\n"
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        response += f"[U+1F528] Type: {timeout_desc}\n"
        response += f"[U+1F4C5] When: {time_str}\n"
        response += f"⌚ Time: {most_recent.strftime('%Y-%m-%d %H:%M:%S')}\n"
        response += f"[U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501][U+2501]\n"
        response += f"[DATA] Total timeouts: {mod.whacks_count}\n"
        
        # Add current combo if any
        if hasattr(mod, 'combo_multiplier') and mod.combo_multiplier > 1:
            response += f"[U+1F525] Current combo: x{mod.combo_multiplier:.1f}"
        
        return response
    
    def _cmd_award(self, user: UserProfile, args: str) -> str:
        """Award points to a mod"""
        parts = args.split()
        if len(parts) < 2:
            return "Usage: /award @mod <points> [reason]"
            
        target = parts[0].replace("@", "")
        try:
            points = int(parts[1])
        except ValueError:
            return "[FAIL] Points must be a number"
            
        reason = " ".join(parts[2:]) if len(parts) > 2 else "Manual award"
        
        # This would look up the mod and award points
        return f"[OK] Awarded {points} points to {target} for: {reason}"