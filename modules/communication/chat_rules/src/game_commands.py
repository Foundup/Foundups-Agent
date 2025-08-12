#!/usr/bin/env python3
"""
Game Command System for Anti-Fascist Educational Chat Games
WSP-Compliant implementation following PoC→Prototype→MVP progression
"""

import json
import random
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import logging

from modules.communication.chat_rules.src.whack_a_magat import (
    WhackAMAGAtSystem, WhackScoringEngine, ActionType
)
from modules.communication.chat_rules.src.database import ChatRulesDB

logger = logging.getLogger(__name__)

# Command prefix
COMMAND_PREFIX = "!"

class CommandType(Enum):
    """Available game commands"""
    WHACK = "whack"      # Whack-a-MAGA game
    QUIZ = "quiz"        # Fascism awareness quiz
    FSCALE = "fscale"    # F-scale authoritarian test
    FACTS = "facts"      # 1933 historical parallels
    SCORE = "score"      # Show leaderboard
    HELP = "help"        # Show available commands
    STATS = "stats"      # Personal statistics

@dataclass
class CommandContext:
    """Context for command execution"""
    user_id: str
    user_name: str
    message: str
    is_moderator: bool = False
    is_member: bool = False
    member_months: int = 0
    room_activity_rate: float = 0.0  # Messages per 5 minutes

class GameCommandSystem:
    """
    Main command system for educational anti-fascist games
    Integrates with existing whack_a_magat scoring system
    """
    
    def __init__(self, db_path: Optional[str] = None):
        self.db = ChatRulesDB(db_path) if db_path else ChatRulesDB()
        self.whack_system = WhackAMAGAtSystem()
        self.scoring_engine = WhackScoringEngine(self.db)
        
        # Command registry
        self.commands = {
            CommandType.WHACK: self._handle_whack,
            CommandType.QUIZ: self._handle_quiz,
            CommandType.FSCALE: self._handle_fscale,
            CommandType.FACTS: self._handle_facts,
            CommandType.SCORE: self._handle_score,
            CommandType.HELP: self._handle_help,
            CommandType.STATS: self._handle_stats,
        }
        
        # Load content databases
        self._load_content_databases()
    
    def _load_content_databases(self):
        """Load quiz questions, facts, and F-scale questions"""
        # PoC: Hardcoded content
        # Prototype: Load from JSON
        # MVP: Dynamic content from Gemini API
        
        self.quiz_questions = [
            {
                "question": "In 1933, the Reichstag Fire was used to suspend civil liberties. What 2001 event had similar effects in the US?",
                "options": ["9/11 attacks", "Dot-com crash", "Enron scandal", "Florida recount"],
                "correct": 0,
                "explanation": "Both events were used to expand government power and restrict civil liberties through emergency measures."
            },
            {
                "question": "The Nazi SA (Brownshirts) used street violence to intimidate opponents. Which modern group uses similar tactics?",
                "options": ["Greenpeace", "Proud Boys", "ACLU", "Sierra Club"],
                "correct": 1,
                "explanation": "The Proud Boys use political violence and intimidation tactics similar to the Nazi SA."
            },
            {
                "question": "Hitler's Beer Hall Putsch failed in 1923 but wasn't properly punished. What similar event happened in 2021?",
                "options": ["GameStop squeeze", "January 6 insurrection", "Texas power crisis", "Suez Canal blockage"],
                "correct": 1,
                "explanation": "Both were failed coup attempts where leaders faced minimal consequences, emboldening future attempts."
            }
        ]
        
        self.historical_facts = [
            "1933: Hitler appointed Chancellor with only 33% support → 2016: Trump won with minority popular vote",
            "1933: Enabling Act gave Hitler dictatorial powers → 2025: Project 2025 seeks similar executive expansion",
            "1933: Jews blamed for Germany's problems → Today: Immigrants scapegoated for economic issues",
            "1933: 'Lügenpresse' (lying press) propaganda → Today: 'Fake news' attacks on media",
            "1933: Book burnings at universities → Today: Book bans in schools and libraries"
        ]
        
        self.fscale_questions = [
            {
                "question": "Obedience and respect for authority are the most important virtues children should learn.",
                "dimension": "authoritarian_submission"
            },
            {
                "question": "Our country desperately needs a mighty leader who will do what has to be done to destroy the radical new ways and sinfulness that are ruining us.",
                "dimension": "authoritarian_aggression"
            },
            {
                "question": "The real keys to the 'good life' are obedience, discipline, and sticking to the straight and narrow.",
                "dimension": "conventionalism"
            }
        ]
    
    def process_message(self, message: str, context: CommandContext) -> Optional[str]:
        """
        Process incoming message for commands
        
        Args:
            message: Raw message text
            context: Command execution context
            
        Returns:
            Response message or None if not a command
        """
        if not message.startswith(COMMAND_PREFIX):
            return None
        
        parts = message[1:].split()
        if not parts:
            return None
        
        command_str = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # Find matching command
        command_type = None
        for cmd_type in CommandType:
            if cmd_type.value == command_str:
                command_type = cmd_type
                break
        
        if not command_type:
            return f"Unknown command: {command_str}. Type !help for available commands."
        
        # Check permissions
        if command_type == CommandType.WHACK and not context.is_moderator:
            return "⚠️ Only moderators can use !whack command"
        
        # Execute command
        handler = self.commands.get(command_type)
        if handler:
            return handler(args, context)
        
        return "Command not implemented yet"
    
    def _handle_whack(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !whack command - timeout a user with scoring
        Format: !whack @username [duration] [reason]
        """
        if len(args) < 1:
            return "Usage: !whack @username [duration_seconds] [reason]"
        
        target = args[0].lstrip('@')
        duration = int(args[1]) if len(args) > 1 and args[1].isdigit() else 60
        reason = ' '.join(args[2:]) if len(args) > 2 else "MAGA behavior detected"
        
        # Record the whack with scoring
        points = self.scoring_engine.process_whack_event(
            mod_id=context.user_id,
            mod_name=context.user_name,
            target_id=f"user_{target}",  # Mock ID for PoC
            target_name=target,
            duration_seconds=duration,
            room_activity_rate=context.room_activity_rate,
            reason=reason
        )
        
        # Build response
        if points > 0:
            response = f"🔨 WHACK! {context.user_name} → {target} ({duration}s timeout)"
            response += f"\n⚡ Points earned: {points}"
            
            # Check for achievements
            leaderboard = self.scoring_engine.generate_leaderboard(limit=3)
            for i, (name, total_points) in enumerate(leaderboard):
                if name == context.user_name:
                    response += f"\n🏆 Rank #{i+1} with {total_points} total points!"
                    break
        else:
            response = f"⚠️ Timeout recorded but no points earned (anti-gaming rules applied)"
        
        return response
    
    def _handle_quiz(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !quiz command - Start a fascism awareness quiz
        """
        # PoC: Return a random quiz question
        question = random.choice(self.quiz_questions)
        
        response = f"📚 **FASCISM AWARENESS QUIZ**\n"
        response += f"Question: {question['question']}\n\n"
        
        for i, option in enumerate(question['options']):
            response += f"{i+1}. {option}\n"
        
        response += f"\nReply with !answer [number] to answer"
        
        # Store question in session for answer verification (not implemented in PoC)
        return response
    
    def _handle_fscale(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !fscale command - F-scale authoritarian personality test
        """
        # PoC: Return first F-scale question
        question = self.fscale_questions[0]
        
        response = f"📊 **F-SCALE AUTHORITARIAN TEST**\n"
        response += f"Rate your agreement (1-5):\n"
        response += f'"{question["question"]}"\n\n'
        response += "1 = Strongly Disagree\n"
        response += "2 = Disagree\n"
        response += "3 = Neutral\n"
        response += "4 = Agree\n"
        response += "5 = Strongly Agree\n\n"
        response += "Reply with !rate [1-5]"
        
        return response
    
    def _handle_facts(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !facts command - Display 1933 historical parallels
        """
        fact = random.choice(self.historical_facts)
        
        response = f"📜 **HISTORICAL PARALLEL**\n"
        response += f"{fact}\n\n"
        response += "Those who don't learn from history are doomed to repeat it."
        
        return response
    
    def _handle_score(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !score command - Show whack-a-MAGA leaderboard
        """
        leaderboard = self.scoring_engine.generate_leaderboard(limit=10)
        
        if not leaderboard:
            return "No scores yet! Moderators can use !whack to start scoring."
        
        response = "🏆 **WHACK-A-MAGA LEADERBOARD** 🏆\n"
        response += "=" * 30 + "\n"
        
        for i, (name, points) in enumerate(leaderboard):
            emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            response += f"{emoji} {name}: {points:,} points\n"
        
        return response
    
    def _handle_help(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !help command - Show available commands
        """
        response = "🎮 **ANTI-FASCIST EDUCATION GAMES** 🎮\n"
        response += "Available commands:\n\n"
        
        if context.is_moderator:
            response += "**Moderator Commands:**\n"
            response += "!whack @user [duration] - Timeout user (earn points)\n\n"
        
        response += "**Educational Commands:**\n"
        response += "!quiz - Fascism awareness quiz\n"
        response += "!fscale - Authoritarian personality test\n"
        response += "!facts - 1933 historical parallels\n"
        response += "!score - Show leaderboard\n"
        response += "!stats - Your personal statistics\n"
        response += "!help - Show this message\n\n"
        
        response += "Learn history. Recognize patterns. Prevent fascism."
        
        return response
    
    def _handle_stats(self, args: List[str], context: CommandContext) -> str:
        """
        Handle !stats command - Show personal statistics
        """
        # Get user stats from whack system
        stats = self.whack_system.get_stats(context.user_id)
        
        if not stats:
            return f"No statistics found for {context.user_name}"
        
        return stats


# PoC Test/Demo
if __name__ == "__main__":
    # Initialize system
    game_system = GameCommandSystem()
    
    # Test context for moderator
    mod_context = CommandContext(
        user_id="mod123",
        user_name="ConsciousMod",
        message="",
        is_moderator=True,
        room_activity_rate=45.0  # Active room
    )
    
    # Test commands
    print("Testing !help command:")
    print(game_system.process_message("!help", mod_context))
    print("\n" + "="*50 + "\n")
    
    print("Testing !whack command:")
    print(game_system.process_message("!whack @MAGATroll 300 Spreading fascist propaganda", mod_context))
    print("\n" + "="*50 + "\n")
    
    print("Testing !quiz command:")
    print(game_system.process_message("!quiz", mod_context))
    print("\n" + "="*50 + "\n")
    
    print("Testing !facts command:")
    print(game_system.process_message("!facts", mod_context))
    print("\n" + "="*50 + "\n")
    
    print("Testing !fscale command:")
    print(game_system.process_message("!fscale", mod_context))
    print("\n" + "="*50 + "\n")
    
    print("Testing !score command:")
    print(game_system.process_message("!score", mod_context))