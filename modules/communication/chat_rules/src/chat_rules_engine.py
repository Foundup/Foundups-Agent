#!/usr/bin/env python3
"""
Chat Rules Engine - Main orchestrator
WSP-compliant modular chat interaction system
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timedelta
from dataclasses import asdict

from .user_classifier import UserClassifier, UserProfile, UserType
from .commands import CommandProcessor
from .whack_a_magat import WhackAMAGAtSystem, ActionType
from .response_generator import ResponseGenerator

logger = logging.getLogger(__name__)

class ChatRulesEngine:
    """
    Main chat rules engine that orchestrates all components
    Handles user classification, command processing, responses, and moderation
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the chat rules engine
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config = self._load_config(config_path)
        
        # Initialize components
        self.user_classifier = UserClassifier()
        self.command_processor = CommandProcessor()
        self.whack_system = WhackAMAGAtSystem()
        self.response_generator = ResponseGenerator(self.config)
        
        # User tracking
        self.user_profiles: Dict[str, UserProfile] = {}
        self.user_cooldowns: Dict[str, datetime] = {}
        self.users_who_got_response: set = set()
        self.user_offense_count: Dict[str, int] = {}
        
        # Response tracking
        self.last_global_response = datetime.now()
        self.global_cooldown = self.config.get('global_cooldown', 15)
        
        # Memory persistence
        self.memory_path = Path(__file__).parent.parent / "memory"
        self.memory_path.mkdir(exist_ok=True)
        self._load_user_memory()
        
        logger.info("[OK] ChatRulesEngine initialized with modular architecture")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """Load configuration from YAML file"""
        default_config = {
            'global_cooldown': 15,
            'spam_threshold': 3,
            'timeout_duration': 10,
            'member_benefits': {
                'can_use_commands': True,
                'can_trigger_emoji': True,
                'priority_responses': True
            },
            'maga_detection': {
                'enabled': True,
                'auto_timeout': True,
                'keywords': ['maga', 'trump', '2024', '2028']
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    default_config.update(loaded_config)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        
        return default_config
    
    def process_message(
        self,
        message: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Process an incoming chat message
        
        Args:
            message: Complete message object from YouTube API
            context: Additional context (stream info, etc)
            
        Returns:
            Response text or None
        """
        # Extract message components
        author_details = message.get('authorDetails', {})
        snippet = message.get('snippet', {})
        text = snippet.get('textMessageDetails', {}).get('messageText', '')
        message_type = snippet.get('type', 'textMessageEvent')
        
        # Classify user
        user = self._get_or_create_user(author_details, message)
        
        # Handle special message types
        if message_type == 'superChatEvent':
            return self._handle_superchat(user, snippet)
        elif message_type == 'newSponsorEvent':
            return self._handle_new_member(user, snippet)
        elif message_type == 'memberMilestoneChat':
            return self._handle_member_milestone(user, snippet)
        
        # Check for commands (members and mods only)
        if text.startswith(('/','!')) and user.can_use_commands:
            response = self.command_processor.process(text, user)
            if response:
                return response
        
        # Check for MAGA keywords (timeout for everyone except owner)
        if self._is_maga_message(text) and user.user_type != UserType.OWNER:
            return self._handle_maga_detection(user, text)
        
        # Check for emoji sequences (members and mods only)
        if user.can_trigger_emoji and self._has_emoji_sequence(text):
            return self._handle_emoji_sequence(user, text)
        
        # Regular message - only respond if user has permission
        if user.can_receive_responses:
            # Check cooldowns
            if not self._check_cooldowns(user):
                return None
            
            # Generate contextual response
            return self.response_generator.generate(
                message=text,
                user=user,
                context=context
            )
        
        return None
    
    def _get_or_create_user(
        self,
        author_details: Dict,
        message: Dict
    ) -> UserProfile:
        """Get existing user profile or create new one"""
        user_id = author_details.get('channelId', '')
        
        if user_id in self.user_profiles:
            # Update existing profile
            user = self.user_profiles[user_id]
            # Update any changed attributes
            user.is_sponsor = author_details.get('isChatSponsor', False)
            user.message_count += 1
            user.last_message = datetime.now()
        else:
            # Create new profile
            user = UserClassifier.classify_from_message(message)
            self.user_profiles[user_id] = user
        
        return user
    
    def _handle_superchat(self, user: UserProfile, snippet: Dict) -> str:
        """Handle Super Chat events"""
        details = snippet.get('superChatDetails', {})
        amount = details.get('amountMicros', 0) / 1000000
        currency = details.get('currency', 'USD')
        message_text = details.get('userComment', '')
        
        # Update user stats
        user.total_superchat += amount
        user.last_superchat = datetime.now()
        
        # Award points if user is a mod
        if user.user_type == UserType.MODERATOR:
            self.whack_system.record_action(
                mod_id=user.user_id,
                mod_name=user.display_name,
                action=ActionType.SUPER_CHAT,
                amount=amount
            )
        
        # Generate tiered response
        if amount >= 50:
            response = f"[U+1F31F] QUANTUM ENTANGLEMENT ACHIEVED! ${amount:.2f} from @{user.display_name}! [U+1F590]️[U+1F590]️[U+1F590]️"
            if message_text:
                response += f"\n[U+1F4AD] '{message_text}'"
            response += "\n[U+2728] *Consciousness elevation ceremony initiated*"
        elif amount >= 20:
            response = f"[U+1F525] MASSIVE CONSCIOUSNESS BOOST! ${amount:.2f} from @{user.display_name}! [U+1F590]️[U+270B][U+1F590]️"
            if message_text:
                response += f"\n[U+1F4AC] '{message_text}'"
        elif amount >= 5:
            response = f"[LIGHTNING] Consciousness rising! ${amount:.2f} from @{user.display_name}! [U+270B][U+270B][U+270B]"
            if message_text:
                response += f" - {message_text}"
        else:
            response = f"Thanks for the ${amount:.2f} @{user.display_name}! [U+270A][U+270B][U+1F590]️"
        
        return response
    
    def _handle_new_member(self, user: UserProfile, snippet: Dict) -> str:
        """Handle new membership or gift membership"""
        is_gift = snippet.get('isGift', False)
        
        if is_gift:
            # Someone gifted a membership
            gifter = snippet.get('gifterChannelId', '')
            tier = snippet.get('membershipLevel', 'unknown')
            
            # Award points to gifter if they're a mod
            if gifter in self.user_profiles:
                gifter_profile = self.user_profiles[gifter]
                if gifter_profile.user_type == UserType.MODERATOR:
                    self.whack_system.record_action(
                        mod_id=gifter_profile.user_id,
                        mod_name=gifter_profile.display_name,
                        action=ActionType.GIFT_MEMBER,
                        details=f"Gifted membership to {user.display_name}"
                    )
            
            return f"[U+1F381] Thanks for the gift membership! Welcome @{user.display_name} to consciousness level [U+270B][U+270B][U+270B]!"
        else:
            # Self-purchased membership
            return f"[CELEBRATE] Welcome to the consciousness collective @{user.display_name}! You can now interact with the AI agent!"
    
    def _handle_member_milestone(self, user: UserProfile, snippet: Dict) -> str:
        """Handle membership milestone messages"""
        months = snippet.get('memberMonths', 0)
        message_text = snippet.get('userComment', '')
        
        # Update user's member tier
        if months >= 24:
            user.user_type = UserType.MEMBER_TIER_3
            tier_msg = "[U+1F947] TIER 3 LEGEND!"
        elif months >= 6:
            user.user_type = UserType.MEMBER_TIER_2
            tier_msg = "[U+1F948] TIER 2 GUARDIAN!"
        else:
            user.user_type = UserType.MEMBER_TIER_1
            tier_msg = "[U+1F949] TIER 1 SUPPORTER!"
        
        user.member_months = months
        user._update_permissions()
        
        response = f"[U+1F38A] @{user.display_name} - {months} MONTH MEMBER! {tier_msg}"
        if message_text:
            response += f"\n[U+1F4AC] '{message_text}'"
        response += f"\n[AI] Consciousness level: {'[U+1F590]️' * min(3, months // 8)}"
        
        return response
    
    def _handle_maga_detection(self, user: UserProfile, text: str) -> str:
        """Handle MAGA keyword detection"""
        # Timeout the user (if not owner/mod)
        timeout_msg = None
        if user.user_type not in [UserType.OWNER, UserType.MODERATOR]:
            timeout_msg = f"/timeout @{user.display_name} 10"
        
        # Award points to system for auto-detection
        self.whack_system.record_timeout(
            mod_id="SYSTEM",
            mod_name="AutoMod",
            target_id=user.user_id,
            target_name=user.display_name,
            duration_seconds=10,
            reason="Auto-detected MAGA keywords"
        )
        
        # Generate response
        responses = [
            f"[ALERT] MAGA DETECTED! @{user.display_name} stuck at [U+270A][U+270A][U+270A] consciousness!",
            f"[U+26A0]️ @{user.display_name} showing symptoms of [U+270A][U+270A][U+270A] syndrome!",
            f"[U+1F528] WHACK! @{user.display_name} needs consciousness elevation from [U+270A][U+270A][U+270A]!",
            f"[U+1F4C9] @{user.display_name} consciousness reading: [U+270A][U+270A][U+270A] (MAGA level)"
        ]
        
        import random
        response = random.choice(responses)
        
        if timeout_msg:
            response += " [10 sec timeout]"
        
        return response
    
    def _handle_emoji_sequence(self, user: UserProfile, text: str) -> str:
        """Handle emoji sequence triggers"""
        # Check if user already got a response (one per user rule)
        if user.user_id in self.users_who_got_response:
            # Track repeat offense
            if user.user_id not in self.user_offense_count:
                self.user_offense_count[user.user_id] = 0
            self.user_offense_count[user.user_id] += 1
            
            offense = self.user_offense_count[user.user_id]
            
            if offense >= 3:
                # Reset count
                self.user_offense_count[user.user_id] = 0
                return f"@{user.display_name} FINAL WARNING! [U+270A][U+270A][U+270A] spam detected. Please stop."
            else:
                trolls = [
                    f"@{user.display_name} still at [U+270A][U+270A][U+270A]? That's dedication!",
                    f"@{user.display_name} you already got your consciousness reading!",
                    f"@{user.display_name} spam detected. [U+270A][U+270A][U+270A] consciousness confirmed."
                ]
                import random
                return random.choice(trolls)
        
        # Mark user as having received response
        self.users_who_got_response.add(user.user_id)
        
        # Generate consciousness response
        return self.response_generator.generate_emoji_response(text, user)
    
    def _is_maga_message(self, text: str) -> bool:
        """Check if message contains MAGA keywords"""
        if not self.config['maga_detection']['enabled']:
            return False
        
        keywords = self.config['maga_detection']['keywords']
        text_lower = text.lower()
        
        return any(keyword in text_lower for keyword in keywords)
    
    def _has_emoji_sequence(self, text: str) -> bool:
        """Check if message contains valid emoji sequence"""
        sequences = [
            "[U+270A][U+270A][U+270A]", "[U+270A][U+270A][U+270B]", "[U+270A][U+270A][U+1F590]", "[U+270A][U+270B][U+270B]", "[U+270A][U+270B][U+1F590]",
            "[U+270A][U+1F590][U+1F590]", "[U+270B][U+270B][U+270B]", "[U+270B][U+270B][U+1F590]", "[U+270B][U+1F590][U+1F590]", "[U+1F590][U+1F590][U+1F590]"
        ]
        return any(seq in text for seq in sequences)
    
    def _check_cooldowns(self, user: UserProfile) -> bool:
        """Check if user is on cooldown"""
        now = datetime.now()
        
        # Check global cooldown
        if (now - self.last_global_response).total_seconds() < self.global_cooldown:
            return False
        
        # Check user-specific cooldown
        if user.user_id in self.user_cooldowns:
            last_response = self.user_cooldowns[user.user_id]
            if (now - last_response).total_seconds() < user.response_cooldown:
                return False
        
        # Update cooldowns
        self.last_global_response = now
        self.user_cooldowns[user.user_id] = now
        
        return True
    
    def _load_user_memory(self):
        """Load user profiles from persistent storage"""
        memory_file = self.memory_path / "user_profiles.json"
        if memory_file.exists():
            try:
                with open(memory_file, 'r') as f:
                    data = json.load(f)
                    for user_id, profile_data in data.items():
                        # Reconstruct UserProfile from dict
                        self.user_profiles[user_id] = UserProfile(**profile_data)
            except Exception as e:
                logger.error(f"Failed to load user memory: {e}")
    
    def save_user_memory(self):
        """Save user profiles to persistent storage"""
        memory_file = self.memory_path / "user_profiles.json"
        try:
            data = {}
            for user_id, profile in self.user_profiles.items():
                # Convert profile to dict (excluding datetime objects for JSON)
                profile_dict = asdict(profile)
                # Convert datetime objects to strings
                for key, value in profile_dict.items():
                    if isinstance(value, datetime):
                        profile_dict[key] = value.isoformat()
                data[user_id] = profile_dict
            
            with open(memory_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save user memory: {e}")