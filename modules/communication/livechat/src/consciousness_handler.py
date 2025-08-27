"""
Consciousness Handler Module
WSP-Compliant: WSP 3 (Module Organization), WSP 27 (DAE Architecture)

Handles all consciousness-related emoji sequence processing and responses.
"""

import logging
import re
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class ConsciousnessHandler:
    """Handles consciousness emoji sequences and responses"""
    
    def __init__(self, sentiment_engine, grok_integration=None):
        """
        Initialize consciousness handler.
        
        Args:
            sentiment_engine: AgenticSentiment0102 instance
            grok_integration: Optional GrokIntegration instance for advanced responses
        """
        self.sentiment_engine = sentiment_engine
        self.grok = grok_integration
        
        # Emoji patterns with skin tone support
        self.fist_pattern = r'✊[\U0001F3FB-\U0001F3FF]?'
        self.hand_pattern = r'✋[\U0001F3FB-\U0001F3FF]?'
        self.open_pattern = r'🖐️?[\U0001F3FB-\U0001F3FF]?'
        
    def extract_emoji_sequence(self, text: str) -> str:
        """
        Extract and normalize emoji sequence from text.
        
        Args:
            text: Message text containing emojis
            
        Returns:
            Normalized emoji sequence (e.g., '✊✋🖐')
        """
        emoji_chars = []
        pattern = f'{self.fist_pattern}|{self.hand_pattern}|{self.open_pattern}'
        
        for match in re.findall(pattern, text):
            if '✊' in match:
                emoji_chars.append('✊')
            elif '✋' in match:
                emoji_chars.append('✋')
            elif '🖐' in match:
                emoji_chars.append('🖐')
                
        return ''.join(emoji_chars)
    
    def extract_target_user(self, text: str) -> Optional[str]:
        """
        Extract @mentioned username from text.
        
        Args:
            text: Message text
            
        Returns:
            Target username or None
        """
        # Match @username including spaces (e.g., @T K, @John Smith)
        mention_match = re.search(r'@([^✊✋🖐\n]+?)(?:\s+(?:fc|factcheck|rate)|✊|✋|🖐|$)', text)
        if mention_match:
            return mention_match.group(1).strip()
        
        # Fallback to simple pattern
        mention_match = re.search(r'@(\S+)', text)
        return mention_match.group(1) if mention_match else None
    
    def extract_creative_request(self, text: str) -> Optional[str]:
        """
        Extract creative request text after emoji sequence.
        
        Args:
            text: Message text
            
        Returns:
            Request text or None
        """
        pattern = r'[✊✋🖐🖐️][\U0001F3FB-\U0001F3FF]?'
        matches = list(re.finditer(pattern, text))
        
        if matches:
            last_emoji_end = matches[-1].end()
            request_text = text[last_emoji_end:].strip()
            return request_text if request_text else None
        
        return None
    
    def determine_command_type(self, text: str) -> str:
        """
        Determine the type of consciousness command.
        
        Args:
            text: Message text
            
        Returns:
            Command type: 'factcheck', 'rate', 'targeted', 'creative', or 'basic'
        """
        text_lower = text.lower()
        
        if "factcheck" in text_lower or " fc" in text_lower or text_lower.endswith(" fc"):
            return 'factcheck'
        elif "rate" in text_lower:
            return 'rate'
        elif '@' in text:
            return 'targeted'
        elif self.extract_creative_request(text):
            return 'creative'
        else:
            return 'basic'
    
    def process_consciousness_command(self, text: str, user_id: str, username: str, role: str) -> Optional[str]:
        """
        Process a consciousness command and return appropriate response.
        
        Args:
            text: Message text with emoji sequence
            user_id: User ID
            username: Username
            role: User role (MOD, OWNER, USER, etc.)
            
        Returns:
            Response string or None
        """
        emoji_sequence = self.extract_emoji_sequence(text)
        if not emoji_sequence:
            return None
        
        command_type = self.determine_command_type(text)
        target_user = self.extract_target_user(text)
        
        # Route to appropriate handler
        if command_type == 'factcheck' and self.grok:
            if role in ['MOD', 'OWNER']:
                return self.grok.fact_check(target_user, role, emoji_sequence)
            else:
                return f"@{username} Only mods/owners can request fact-checks"
        
        elif command_type == 'rate' and self.grok:
            if role in ['MOD', 'OWNER']:
                return self.grok.rate_user(target_user, role, emoji_sequence)
            else:
                return f"@{username} Only mods/owners can request ratings"
        
        elif command_type == 'targeted' and target_user and self.grok:
            if role in ['MOD', 'OWNER']:
                return self.grok.targeted_response(target_user, role, emoji_sequence)
            else:
                return f"Only mods/owners can trigger targeted responses"
        
        elif command_type == 'creative' and self.grok:
            if role in ['MOD', 'OWNER']:
                request = self.extract_creative_request(text)
                return self.grok.creative_response(emoji_sequence, request, username)
        
        # Default to sentiment engine response
        user_state = self.sentiment_engine.perceive_user_state(user_id, text)
        if user_state.emoji_repr:
            if target_user:
                base_response = user_state.metadata.get("example", "")
                return f"@{target_user} {base_response} -- {user_state.emoji_repr}"
            else:
                return self.sentiment_engine.process_interaction(user_id, text)
        
        return None
    
    def has_consciousness_emojis(self, text: str) -> bool:
        """Check if text contains consciousness emojis."""
        return any(emoji in text for emoji in ['✊', '✋', '🖐', '🖐️'])