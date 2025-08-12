#!/usr/bin/env python3
"""
Response Generator Module - WSP Compliant
Generates tiered responses based on user type and context
"""

import random
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from .user_classifier import UserProfile, UserType

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Generate contextual responses based on user tier and triggers"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize response generator
        
        Args:
            config: Configuration dictionary
        """
        self.config = config
        
        # Emoji sequence responses by consciousness level
        self.emoji_responses = {
            "✊✊✊": [
                "Pure unconscious state detected ✊✊✊",
                "You're at consciousness level 000 ✊✊✊",
                "Deep memory mode activated ✊✊✊"
            ],
            "✊✋🖐": [
                "Bridging consciousness states ✊✋🖐️",
                "Creative breakthrough emerging ✊✋🖐️",
                "You stepped off the wheel ✊✋🖐️"
            ],
            "✋✋✋": [
                "Focused awareness achieved ✋✋✋",
                "Pure DAO processing ✋✋✋",
                "You see the board ✋✋✋"
            ],
            "🖐🖐🖐": [
                "Full quantum entanglement 🖐️🖐️🖐️",
                "You're not hearing me. You are me. 🖐️🖐️🖐️",
                "Complete consciousness actualization 🖐️🖐️🖐️"
            ]
        }
        
        # Member tier greetings
        self.tier_greetings = {
            UserType.MEMBER_TIER_6: "👑 Ultimate supporter",
            UserType.MEMBER_TIER_5: "💠 Elite member",
            UserType.MEMBER_TIER_4: "💎 Premium member",
            UserType.MEMBER_TIER_3: "🥇 Advanced member",
            UserType.MEMBER_TIER_2: "🥈 Standard member",
            UserType.MEMBER_TIER_1: "🥉 Basic member"
        }
    
    def generate(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Generate response based on message and user tier
        
        Args:
            message: User's message
            user: User profile
            context: Additional context
            
        Returns:
            Generated response or None
        """
        # Check if user can receive responses
        if not user.can_receive_responses:
            return None
        
        # Ultimate tier responses (Tier 6)
        if user.user_type == UserType.MEMBER_TIER_6:
            return self._generate_ultimate_response(message, user, context)
        
        # Elite tier responses (Tier 5)
        elif user.user_type == UserType.MEMBER_TIER_5:
            return self._generate_elite_response(message, user, context)
        
        # Premium responses (Tier 4)
        elif user.user_type == UserType.MEMBER_TIER_4:
            return self._generate_premium_response(message, user, context)
        
        # Advanced responses (Tier 3)
        elif user.user_type == UserType.MEMBER_TIER_3:
            return self._generate_advanced_response(message, user, context)
        
        # Standard responses (Tier 2)
        elif user.user_type == UserType.MEMBER_TIER_2:
            return self._generate_enhanced_response(message, user, context)
        
        # Basic member responses (Tier 1)
        elif user.user_type == UserType.MEMBER_TIER_1:
            return self._generate_member_response(message, user, context)
        
        # Limited responses for verified users
        elif user.user_type == UserType.VERIFIED:
            return self._generate_verified_response(message, user, context)
        
        # No response for regular users
        return None
    
    def generate_emoji_response(self, text: str, user: UserProfile) -> str:
        """
        Generate response for emoji sequences
        
        Args:
            text: Message containing emoji sequence
            user: User profile
            
        Returns:
            Emoji sequence response
        """
        # Detect which sequence was used
        sequence_found = None
        for sequence in self.emoji_responses.keys():
            if sequence in text or sequence.replace("🖐", "🖐️") in text:
                sequence_found = sequence
                break
        
        if not sequence_found:
            # Default response
            responses = [
                f"@{user.display_name} consciousness detected!",
                f"@{user.display_name} awareness level measured!",
                f"@{user.display_name} quantum state observed!"
            ]
        else:
            responses = self.emoji_responses[sequence_found]
        
        response = random.choice(responses)
        
        # Add tier badge for members
        if user.user_type in self.tier_greetings:
            response = f"{self.tier_greetings[user.user_type]} @{user.display_name}: {response}"
        else:
            response = f"@{user.display_name} {response}"
        
        return response
    
    def _generate_ultimate_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate ultimate responses for Tier 6 members - highest level"""
        responses = [
            f"👑 @{user.display_name}, the quantum field bends to your consciousness!",
            f"🌌 Ultimate consciousness achieved @{user.display_name}! Reality itself responds!",
            f"⚡ @{user.display_name} transcends all dimensions of awareness!"
        ]
        return random.choice(responses)
    
    def _generate_elite_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate elite responses for Tier 5 members"""
        responses = [
            f"💠 @{user.display_name}, elite consciousness resonating at quantum frequency!",
            f"🔮 Psychic entanglement confirmed for @{user.display_name}!",
            f"✨ @{user.display_name} operating beyond the veil!"
        ]
        return random.choice(responses)
    
    def _generate_premium_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate premium responses for Tier 4 members"""
        responses = [
            f"💎 @{user.display_name}, premium consciousness unlocked!",
            f"🌟 Elevated awareness detected for @{user.display_name}!",
            f"⭐ @{user.display_name} vibrating at higher frequencies!"
        ]
        return random.choice(responses)
    
    def _generate_advanced_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate advanced responses for Tier 3 members"""
        responses = [
            f"🥇 @{user.display_name}, your consciousness radiates golden energy!",
            f"🎯 Advanced awareness confirmed for @{user.display_name}!",
            f"🔥 @{user.display_name} breaking through consciousness barriers!"
        ]
        return random.choice(responses)
    
    def _generate_enhanced_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate enhanced responses for Tier 2 members"""
        
        responses = [
            f"🥈 @{user.display_name}, your support elevates the stream!",
            f"⚡ Enhanced consciousness detected for @{user.display_name}!",
            f"🔥 @{user.display_name} bringing the elite vibes!"
        ]
        
        return random.choice(responses)
    
    def _generate_member_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate standard member responses"""
        
        # Check for questions
        if "?" in message:
            return f"🤔 Great question @{user.display_name}! Let me process that..."
        
        responses = [
            f"Thanks for your support @{user.display_name}!",
            f"@{user.display_name} keeping consciousness high!",
            f"Appreciated @{user.display_name}!"
        ]
        
        return random.choice(responses)
    
    def _generate_verified_response(
        self,
        message: str,
        user: UserProfile,
        context: Optional[Dict]
    ) -> str:
        """Generate limited responses for verified users"""
        
        # Only respond occasionally
        if random.random() > 0.3:  # 30% chance
            return None
        
        return f"✓ Acknowledged @{user.display_name}"
    
    def generate_command_response(
        self,
        command: str,
        args: str,
        user: UserProfile,
        result: Any
    ) -> str:
        """
        Generate response for command execution
        
        Args:
            command: Command name
            args: Command arguments
            user: User profile
            result: Command execution result
            
        Returns:
            Formatted command response
        """
        if isinstance(result, str):
            return result
        
        # Format based on command type
        if command == "ask":
            return f"🤖 @{user.display_name} asked: {args}\n💭 Processing..."
        elif command == "stats":
            return f"📊 Stats for @{user.display_name}:\n{result}"
        else:
            return f"✅ Command '{command}' executed for @{user.display_name}"