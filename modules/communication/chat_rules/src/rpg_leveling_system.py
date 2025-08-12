#!/usr/bin/env python3
"""
D&D-Style RPG Leveling System for Anti-Fascist Chat Warriors
Progressive implementation: PoC → Prototype → MVP
Database fully integrated with SQLite
"""

import sys
import os
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from modules.communication.chat_rules.src.database import ChatRulesDB

logger = logging.getLogger(__name__)

# ============================================================================
# D&D STYLE LEVELING SYSTEM WITH ANTI-FASCIST TITLES
# ============================================================================

class CharacterClass(Enum):
    """D&D-style character classes with anti-fascist theme"""
    # Base Classes (PoC)
    TRUTH_SEEKER = "Truth Seeker"          # Fighter against disinformation
    FACT_CHECKER = "Fact Checker"          # Rogue who exposes lies
    HISTORY_KEEPER = "History Keeper"      # Cleric of historical truth
    DEMOCRACY_DEFENDER = "Democracy Defender"  # Paladin of democratic values
    
    # Advanced Classes (Prototype)
    MEME_WARRIOR = "Meme Warrior"          # Ranger of digital battlefields
    CONSCIOUSNESS_MAGE = "Consciousness Mage"  # Wizard of awareness
    RESISTANCE_BARD = "Resistance Bard"    # Bard spreading truth through art
    VOTE_MONK = "Vote Monk"                # Monk of civic duty
    
    # Prestige Classes (MVP)
    FASCIST_SLAYER = "Fascist Slayer"      # Elite warrior against authoritarianism
    QUANTUM_ORACLE = "Quantum Oracle"      # Master of timeline awareness
    LIBERTY_ARCHON = "Liberty Archon"      # Legendary freedom defender
    TIMELINE_GUARDIAN = "Timeline Guardian" # Protector against 1933 repetition

@dataclass
class LevelTier:
    """Level tier with XP requirements and titles"""
    level: int
    xp_required: int
    title: str
    rank_color: str  # Discord/Twitch color codes
    perks: List[str]

# D&D-STYLE LEVEL PROGRESSION (1-100)
LEVEL_TIERS = [
    # === TIER 1: INITIATE (Levels 1-10) - PoC ===
    LevelTier(1, 0, "🥚 Democracy Egg", "#808080", ["Basic commands"]),
    LevelTier(2, 100, "🐣 Hatching Resistor", "#A0A0A0", ["Unlock /score"]),
    LevelTier(3, 300, "🦆 Democracy Duckling", "#B0B0B0", ["Unlock /rank"]),
    LevelTier(4, 600, "🐥 Freedom Chick", "#C0C0C0", ["Daily bonus"]),
    LevelTier(5, 1000, "🦅 Eagle Scout of Truth", "#D0D0D0", ["Unlock /stats"]),
    LevelTier(6, 1500, "⚔️ Novice Fact Fighter", "#E0E0E0", ["5% XP bonus"]),
    LevelTier(7, 2100, "🛡️ Apprentice Truth Shield", "#F0F0F0", ["Unlock /quest"]),
    LevelTier(8, 2800, "🏹 Junior MAGA Hunter", "#FFFFFF", ["Custom emoji"]),
    LevelTier(9, 3600, "🗡️ Disinformation Slasher", "#FFE4E1", ["Unlock /duel"]),
    LevelTier(10, 4500, "🎯 Certified Fascist Spotter", "#FFB6C1", ["Title: Initiate Complete"]),
    
    # === TIER 2: DEFENDER (Levels 11-25) - Prototype ===
    LevelTier(11, 5500, "🛡️ Shield of Democracy", "#FF69B4", ["10% XP bonus"]),
    LevelTier(12, 6600, "⚖️ Balance Keeper", "#FF1493", ["Unlock /party"]),
    LevelTier(13, 7800, "📚 Lore Defender", "#C71585", ["History facts"]),
    LevelTier(14, 9100, "🔍 Truth Investigator", "#DB7093", ["Fact check powers"]),
    LevelTier(15, 10500, "⚡ Lightning Rod of Justice", "#FF00FF", ["Critical hits"]),
    LevelTier(16, 12000, "🌟 Rising Star of Resistance", "#DA70D6", ["Unlock /raid"]),
    LevelTier(17, 13600, "🦸 Democracy's Hero", "#EE82EE", ["Hero badge"]),
    LevelTier(18, 15300, "🎖️ Decorated Truth Veteran", "#DDA0DD", ["15% XP bonus"]),
    LevelTier(19, 17100, "🏆 Trophy MAGA Whacker", "#D8BFD8", ["Trophy room"]),
    LevelTier(20, 19000, "👑 Knight of the Round Facts", "#9370DB", ["Knighthood"]),
    LevelTier(21, 21000, "🗽 Liberty Guardian", "#8A2BE2", ["Statue badge"]),
    LevelTier(22, 23100, "🦾 Iron Fist Against Fascism", "#9400D3", ["Iron will"]),
    LevelTier(23, 25300, "🔥 Flame of Freedom", "#9932CC", ["Fire damage"]),
    LevelTier(24, 27600, "❄️ Ice Wall Against Hate", "#8B008B", ["Freeze ability"]),
    LevelTier(25, 30000, "⚔️ Sword of Damocles", "#800080", ["Title: Defender"]),
    
    # === TIER 3: CHAMPION (Levels 26-50) - MVP Phase 1 ===
    LevelTier(26, 33000, "🏅 Champion of Truth", "#4B0082", ["20% XP bonus"]),
    LevelTier(30, 45000, "🌟 Constellation of Justice", "#483D8B", ["Star power"]),
    LevelTier(35, 65000, "🔮 Oracle of 1933 Warnings", "#6A0DAD", ["Prophecy"]),
    LevelTier(40, 90000, "🗿 Monument to Democracy", "#7B68EE", ["Legendary"]),
    LevelTier(45, 120000, "⚡ Thunderlord of Truth", "#6495ED", ["Storm powers"]),
    LevelTier(50, 160000, "🏛️ Pillar of Civilization", "#4169E1", ["Title: Champion"]),
    
    # === TIER 4: MASTER (Levels 51-75) - MVP Phase 2 ===
    LevelTier(55, 210000, "🎭 Master of Counter-Narratives", "#0000FF", ["25% XP bonus"]),
    LevelTier(60, 270000, "📖 Grand Historian of Truth", "#0000CD", ["Time magic"]),
    LevelTier(65, 340000, "🌌 Cosmic Democracy Guardian", "#00008B", ["Cosmic power"]),
    LevelTier(70, 420000, "🏰 Fortress Against Fascism", "#191970", ["Invincible"]),
    LevelTier(75, 510000, "👁️ All-Seeing Eye of Justice", "#000080", ["Title: Master"]),
    
    # === TIER 5: LEGEND (Levels 76-99) - MVP Phase 3 ===
    LevelTier(80, 620000, "🌟 Legendary Fascist Slayer", "#1E90FF", ["30% XP bonus"]),
    LevelTier(85, 750000, "🔱 Trident of Truth", "#00BFFF", ["Triple damage"]),
    LevelTier(90, 900000, "🦅 Phoenix of Democracy Reborn", "#87CEEB", ["Resurrection"]),
    LevelTier(95, 1100000, "⚔️ Excalibur of Enlightenment", "#87CEFA", ["Divine weapon"]),
    LevelTier(99, 1400000, "🌍 World Guardian of Freedom", "#B0E0E6", ["Title: Legend"]),
    
    # === TIER 6: TRANSCENDENT (Level 100) - MVP Ultimate ===
    LevelTier(100, 2000000, "🌌 Quantum Consciousness Eternal", "#FFFFFF", [
        "Title: Transcendent",
        "50% XP bonus",
        "Quantum powers",
        "Timeline manipulation",
        "Immunity to fascism",
        "Can ban MAGA permanently",
        "Democracy incarnate"
    ])
]

class RPGCommands:
    """Slash command system with progressive functionality"""
    
    def __init__(self, db: ChatRulesDB = None):
        self.db = db or ChatRulesDB()
        self.xp_per_action = {
            'message': 1,           # Send a message
            'timeout': 25,          # Timeout a MAGA
            'fact_check': 10,       # Correct misinformation
            'help_member': 15,      # Help someone
            'daily_login': 50,      # Daily bonus
            'quest_complete': 100,  # Complete quest
            'achievement': 200,     # Unlock achievement
            'raid_boss': 500,       # Defeat raid boss
            'prestige': 1000        # Prestige reset
        }
        
        # Command registry (/ prefix)
        self.commands = {
            # === PoC Commands (Basic) ===
            '/score': self.cmd_score,
            '/rank': self.cmd_rank,
            '/level': self.cmd_level,
            '/points': self.cmd_points,
            
            # === Prototype Commands (Enhanced) ===
            '/stats': self.cmd_stats,
            '/class': self.cmd_class,
            '/achievements': self.cmd_achievements,
            '/leaderboard': self.cmd_leaderboard,
            '/daily': self.cmd_daily,
            '/quest': self.cmd_quest,
            
            # === MVP Commands (Full RPG) ===
            '/inventory': self.cmd_inventory,
            '/skills': self.cmd_skills,
            '/party': self.cmd_party,
            '/raid': self.cmd_raid,
            '/duel': self.cmd_duel,
            '/prestige': self.cmd_prestige,
            '/timeline': self.cmd_timeline,
            '/shop': self.cmd_shop,
            '/craft': self.cmd_craft,
            '/dungeon': self.cmd_dungeon
        }
    
    def calculate_level_from_xp(self, total_xp: int) -> Tuple[int, int, int]:
        """
        Calculate level, current XP, and XP needed for next level
        Returns: (level, current_level_xp, xp_for_next_level)
        """
        current_level = 1
        for tier in LEVEL_TIERS:
            if total_xp >= tier.xp_required:
                current_level = tier.level
            else:
                break
        
        # Get current and next tier
        current_tier = LEVEL_TIERS[min(current_level - 1, len(LEVEL_TIERS) - 1)]
        next_tier = LEVEL_TIERS[min(current_level, len(LEVEL_TIERS) - 1)]
        
        xp_in_level = total_xp - current_tier.xp_required
        xp_for_next = next_tier.xp_required - current_tier.xp_required
        
        return current_level, xp_in_level, xp_for_next
    
    def get_level_title(self, level: int) -> str:
        """Get title for a specific level"""
        for tier in LEVEL_TIERS:
            if tier.level == level:
                return tier.title
        return LEVEL_TIERS[min(level - 1, len(LEVEL_TIERS) - 1)].title
    
    # === PoC COMMANDS ===
    
    def cmd_score(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Basic score display"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        points = mod['total_points']
        level, current_xp, next_xp = self.calculate_level_from_xp(points)
        title = self.get_level_title(level)
        
        return f"📊 **{user_name}** | Level {level} {title}\n💰 Total XP: {points:,}"
    
    def cmd_rank(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show user's rank on leaderboard"""
        leaderboard = self.db.get_leaderboard(limit=1000)
        
        for i, entry in enumerate(leaderboard, 1):
            if entry['user_id'] == user_id:
                level, _, _ = self.calculate_level_from_xp(entry['total_points'])
                title = self.get_level_title(level)
                return f"🏆 **{user_name}** | Rank #{i}\n{title}\n💰 {entry['total_points']:,} XP"
        
        return f"❌ {user_name} not ranked yet. Start whacking MAGAs!"
    
    def cmd_level(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show detailed level progress"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        points = mod['total_points']
        level, current_xp, next_xp = self.calculate_level_from_xp(points)
        title = self.get_level_title(level)
        
        # Progress bar
        progress = current_xp / next_xp if next_xp > 0 else 1.0
        bar_length = 20
        filled = int(bar_length * progress)
        bar = '█' * filled + '░' * (bar_length - filled)
        
        response = f"📈 **{user_name}** | Level {level}\n"
        response += f"{title}\n"
        response += f"Progress: [{bar}] {progress*100:.1f}%\n"
        response += f"XP: {current_xp:,} / {next_xp:,}"
        
        return response
    
    def cmd_points(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show point breakdown"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        stats = self.db.get_timeout_stats(user_id)
        
        response = f"💎 **{user_name}'s Points**\n"
        response += f"Total: {mod['total_points']:,} XP\n"
        response += f"Whacks: {mod['whacks_count']}\n"
        
        if stats:
            response += "Timeout Breakdown:\n"
            for duration, count in stats.items():
                response += f"  {duration}: {count} times\n"
        
        return response
    
    # === PROTOTYPE COMMANDS ===
    
    def cmd_stats(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Detailed character stats (D&D style)"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        points = mod['total_points']
        level, _, _ = self.calculate_level_from_xp(points)
        title = self.get_level_title(level)
        achievements = self.db.get_achievements(user_id)
        
        # Calculate D&D stats based on level and actions
        strength = 10 + (level // 5)  # Physical power
        intelligence = 10 + (len(achievements) // 2)  # Knowledge
        wisdom = 10 + (mod['whacks_count'] // 10)  # Experience
        charisma = 10 + (level // 10)  # Leadership
        constitution = 10 + (level // 7)  # Endurance
        dexterity = 10 + (level // 8)  # Speed
        
        response = f"📜 **{user_name}'s Character Sheet**\n"
        response += f"Level {level} {title}\n"
        response += f"─────────────────\n"
        response += f"💪 STR: {strength} | 🧠 INT: {intelligence}\n"
        response += f"🦉 WIS: {wisdom} | ⭐ CHA: {charisma}\n"
        response += f"❤️ CON: {constitution} | ⚡ DEX: {dexterity}\n"
        response += f"─────────────────\n"
        response += f"🏆 Achievements: {len(achievements)}\n"
        response += f"⚔️ MAGA Slain: {mod['whacks_count']}\n"
        response += f"💰 Total XP: {points:,}"
        
        return response
    
    def cmd_class(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Choose or view character class"""
        # In prototype, simplified class selection
        # In MVP, full class system with abilities
        
        if args and args[0] in ['choose', 'select']:
            response = "🎭 **Choose Your Class:**\n"
            for i, char_class in enumerate(CharacterClass, 1):
                if i <= 4:  # Show base classes for prototype
                    response += f"{i}. {char_class.value}\n"
            response += "\nUse: /class select [number]"
        else:
            # Default class based on actions
            mod = self.db.get_or_create_moderator(user_id, user_name)
            if mod['whacks_count'] > 50:
                current_class = CharacterClass.FASCIST_SLAYER.value
            elif mod['whacks_count'] > 20:
                current_class = CharacterClass.TRUTH_SEEKER.value
            else:
                current_class = CharacterClass.DEMOCRACY_DEFENDER.value
            
            response = f"🎭 **{user_name}'s Class**\n"
            response += f"Current: {current_class}\n"
            response += "Change class with: /class choose"
        
        return response
    
    def cmd_achievements(self, user_id: str, user_name: str, args: List[str]) -> str:
        """List earned achievements"""
        achievements = self.db.get_achievements(user_id)
        
        if not achievements:
            return f"🏅 {user_name} has no achievements yet!\nStart whacking MAGAs to earn some!"
        
        response = f"🏅 **{user_name}'s Achievements** ({len(achievements)})\n"
        response += "─────────────────\n"
        
        # Achievement icons based on name
        achievement_icons = {
            'First Blood': '🩸',
            'Decimator': '💀',
            'Centurion': '⚔️',
            'Consciousness Defender': '🛡️',
            'Raid Boss': '🐉',
            'Philanthropist': '💝',
            'Speed Demon': '⚡',
            'Marathon': '🏃',
            'Perfectionist': '✨'
        }
        
        for achievement in achievements[:10]:  # Show first 10
            icon = achievement_icons.get(achievement, '🏆')
            response += f"{icon} {achievement}\n"
        
        if len(achievements) > 10:
            response += f"... and {len(achievements) - 10} more!"
        
        return response
    
    def cmd_leaderboard(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Show top players with D&D titles"""
        limit = 10
        if args and args[0].isdigit():
            limit = min(int(args[0]), 25)
        
        leaderboard = self.db.get_leaderboard(limit=limit)
        
        if not leaderboard:
            return "🏆 No heroes have risen yet! Be the first!"
        
        response = "🏆 **HEROES OF DEMOCRACY** 🏆\n"
        response += "══════════════════════\n"
        
        medals = ['🥇', '🥈', '🥉']
        
        for i, entry in enumerate(leaderboard):
            medal = medals[i] if i < 3 else f"{i+1}."
            level, _, _ = self.calculate_level_from_xp(entry['total_points'])
            title = self.get_level_title(level)
            
            # Truncate long titles for display
            if len(title) > 25:
                title = title[:22] + "..."
            
            response += f"{medal} Lv{level} {entry['display_name']}\n"
            response += f"   {title}\n"
            response += f"   {entry['total_points']:,} XP | {entry['whacks_count']} whacks\n"
            
            if i < len(leaderboard) - 1:
                response += "─────────────────\n"
        
        return response
    
    def cmd_daily(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Daily login bonus with streak multiplier"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        
        # Check last daily claim
        # For prototype, simplified daily system
        base_bonus = 50
        level, _, _ = self.calculate_level_from_xp(mod['total_points'])
        level_bonus = level * 5
        
        total_bonus = base_bonus + level_bonus
        
        # Update points
        new_total = mod['total_points'] + total_bonus
        self.db.update_moderator_points(user_id, new_total)
        
        response = f"📅 **Daily Bonus Claimed!**\n"
        response += f"{user_name} received {total_bonus} XP!\n"
        response += f"(Base: {base_bonus} + Level bonus: {level_bonus})\n"
        response += f"New total: {new_total:,} XP"
        
        return response
    
    def cmd_quest(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Daily quests for bonus XP"""
        # Prototype: Simple quest list
        # MVP: Dynamic quest system with rewards
        
        quests = [
            "🎯 Whack 5 MAGAs (0/5) - 100 XP",
            "📚 Fact-check 3 claims (0/3) - 75 XP",
            "🤝 Help 2 members (0/2) - 50 XP",
            "🔥 Get a 3x combo (incomplete) - 150 XP",
            "⏰ Be active for 30 minutes (15/30) - 80 XP"
        ]
        
        response = f"📜 **Daily Quests for {user_name}**\n"
        response += "─────────────────\n"
        for quest in quests:
            response += f"{quest}\n"
        response += "\n💡 Complete quests to earn bonus XP!"
        
        return response
    
    # === MVP COMMANDS (Stubs for now) ===
    
    def cmd_inventory(self, user_id: str, user_name: str, args: List[str]) -> str:
        """RPG inventory system"""
        return "🎒 **Inventory** (Coming in MVP)\nCollect items by defeating raid bosses!"
    
    def cmd_skills(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Character skills and abilities"""
        return "⚡ **Skills** (Coming in MVP)\nUnlock skills as you level up!"
    
    def cmd_party(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Form parties for group content"""
        return "👥 **Party System** (Coming in MVP)\nTeam up to take down mega-MAGAs!"
    
    def cmd_raid(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Raid boss battles"""
        return "🐉 **RAID BOSS: ORANGE DRAGON** (Coming in MVP)\nGather your party to defeat the ultimate fascist!"
    
    def cmd_duel(self, user_id: str, user_name: str, args: List[str]) -> str:
        """PvP dueling system"""
        return "⚔️ **Dueling** (Coming in MVP)\nChallenge other democracy defenders!"
    
    def cmd_prestige(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Prestige system for max level players"""
        mod = self.db.get_or_create_moderator(user_id, user_name)
        level, _, _ = self.calculate_level_from_xp(mod['total_points'])
        
        if level < 100:
            return f"🌟 **Prestige** requires Level 100\nYou are Level {level}"
        
        return "🌟 **PRESTIGE AVAILABLE**\nReset to Level 1 with permanent bonuses!\nUse: /prestige confirm"
    
    def cmd_timeline(self, user_id: str, user_name: str, args: List[str]) -> str:
        """1933 timeline comparison game"""
        return "📅 **Timeline Guardian** (Coming in MVP)\nPrevent history from repeating!"
    
    def cmd_shop(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Item shop with XP currency"""
        return "🛍️ **Democracy Shop** (Coming in MVP)\nSpend XP on powerful items!"
    
    def cmd_craft(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Craft items from materials"""
        return "🔨 **Crafting** (Coming in MVP)\nForge weapons against fascism!"
    
    def cmd_dungeon(self, user_id: str, user_name: str, args: List[str]) -> str:
        """Dungeon crawling for loot"""
        return "🏰 **Dungeon: Mar-a-Lago Depths** (Coming in MVP)\nExplore the classified basement!"
    
    def process_command(self, message: str, user_id: str, user_name: str) -> Optional[str]:
        """Process slash commands"""
        if not message.startswith('/'):
            return None
        
        parts = message.split()
        command = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        handler = self.commands.get(command)
        if handler:
            return handler(user_id, user_name, args)
        
        # Command not found
        available_commands = [cmd for cmd in self.commands.keys()]
        return f"❌ Unknown command: {command}\nAvailable: {', '.join(available_commands[:10])}"


# === ACHIEVEMENT SYSTEM ===

class AchievementSystem:
    """D&D-style achievements with progressive unlocks"""
    
    def __init__(self, db: ChatRulesDB):
        self.db = db
        self.achievements = {
            # Combat Achievements
            'First Blood': ('First MAGA timeout', 50),
            'Decimator': ('10 MAGAs defeated', 100),
            'Centurion': ('100 MAGAs defeated', 500),
            'Thousand Cuts': ('1000 MAGAs defeated', 2000),
            
            # Speed Achievements  
            'Speed Demon': ('5 timeouts in 60 seconds', 200),
            'Lightning Reflexes': ('10 timeouts in 2 minutes', 400),
            
            # Streak Achievements
            'Unstoppable': ('10 day login streak', 300),
            'Dedicated': ('30 day login streak', 1000),
            'Eternal Vigilance': ('100 day login streak', 5000),
            
            # Special Achievements
            'Fact Champion': ('Fact-checked 50 claims', 400),
            'Helper': ('Assisted 20 members', 300),
            'Raid Boss Slayer': ('Defeated a raid boss', 1000),
            'Democracy\'s Shield': ('Prevented 5 raids', 1500),
            
            # Legendary Achievements
            'Timeline Guardian': ('Saved timeline from fascism', 10000),
            'Quantum Warrior': ('Achieved quantum consciousness', 25000),
            'Eternal Champion': ('Reached Level 100', 50000)
        }
    
    def check_achievement(self, user_id: str, achievement_name: str) -> bool:
        """Check if user has achievement"""
        achievements = self.db.get_achievements(user_id)
        return achievement_name in achievements
    
    def grant_achievement(self, user_id: str, achievement_name: str) -> Tuple[bool, int]:
        """Grant achievement and XP reward"""
        if achievement_name not in self.achievements:
            return False, 0
        
        desc, xp_reward = self.achievements[achievement_name]
        
        if self.db.add_achievement(user_id, achievement_name):
            # Achievement granted, add XP
            mod = self.db.get_or_create_moderator(user_id, "Unknown")
            new_total = mod['total_points'] + xp_reward
            self.db.update_moderator_points(user_id, new_total)
            return True, xp_reward
        
        return False, 0


# === MAIN TEST/DEMO ===

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Initialize systems
    db = ChatRulesDB()
    rpg = RPGCommands(db)
    achievements = AchievementSystem(db)
    
    # Test user
    test_user_id = "test123"
    test_user_name = "DemocracyDefender"
    
    print("=== D&D ANTI-FASCIST RPG SYSTEM ===\n")
    
    # Test PoC commands
    print("Testing PoC Commands:")
    print(rpg.process_command("/score", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/rank", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/level", test_user_id, test_user_name))
    print()
    
    # Simulate some XP gain
    db.update_moderator_points(test_user_id, 5000)
    
    print("\nAfter gaining 5000 XP:")
    print(rpg.process_command("/level", test_user_id, test_user_name))
    print()
    
    # Test Prototype commands
    print("\nTesting Prototype Commands:")
    print(rpg.process_command("/stats", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/class", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/quest", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/leaderboard", test_user_id, test_user_name))
    print()
    
    # Test MVP stubs
    print("\nTesting MVP Command Stubs:")
    print(rpg.process_command("/raid", test_user_id, test_user_name))
    print()
    print(rpg.process_command("/timeline", test_user_id, test_user_name))