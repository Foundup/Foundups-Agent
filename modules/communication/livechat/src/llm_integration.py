"""
Grok LLM Integration Layer
Connects to Grok / xAI APIs for consciousness responses

NAVIGATION: Primary LLM interface for advanced replies.
-> Called by: message_processor.py::GrokIntegration usage
-> Delegates to: modules.ai_intelligence.rESP_o1o2.llm_connector, SimpleFactChecker fallback
-> Related: NAVIGATION.py -> NEED_TO["call grok integration"]
-> Quick ref: NAVIGATION.py -> PROBLEMS["LLM unavailable"]
"""

import logging
import re
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class GrokIntegration:
    """Handles all Grok LLM interactions"""
    
    def __init__(self, llm_connector, mod_owner_messages: Dict[str, List] = None):
        """
        Initialize Grok integration.
        
        Args:
            llm_connector: LLMConnector instance configured for Grok
            mod_owner_messages: Optional message history for context
        """
        self.llm = llm_connector
        self.mod_owner_messages = mod_owner_messages or {}
        self.max_response_length = 180  # YouTube chat limit
        
    def _limit_response(self, response: str) -> str:
        """Limit response length for YouTube."""
        if len(response) > self.max_response_length:
            return response[:self.max_response_length - 3] + "..."
        return response
    
    def _get_user_context(self, username: str) -> List[str]:
        """Get recent messages from a user for context."""
        messages = []
        for user_id, user_msgs in self.mod_owner_messages.items():
            for msg in user_msgs:
                if msg.get('username') == username:
                    messages.append(msg.get('message', ''))
        return messages[-10:] if messages else []  # Last 10 messages
    
    def fact_check(self, target_username: str, requester_role: str, emoji_sequence: str) -> str:
        """
        Fact-check a user's recent statements.
        
        Args:
            target_username: Username to fact-check
            requester_role: Role of requester (MOD/OWNER)
            emoji_sequence: Emoji sequence for consciousness context
            
        Returns:
            Fact-check response
        """
        if not self.llm:
            return f"@{target_username} Grok not available for fact-checking"
        
        # Get user's recent messages
        target_messages = self._get_user_context(target_username)
        
        if not target_messages:
            return f"@{target_username} No recent messages to fact-check"
        
        # Build enhanced fact-checking prompt with fallacy detection
        messages_text = '\n'.join(target_messages)

        # Special handling for MAGA users - WE are AntiMa (Anti-MAGA)
        is_maga = 'maga' in target_username.lower() or 'trump' in target_username.lower() or 'patriot' in target_username.lower()

        prompt = f"""Analyze {target_username}'s statements and DESTROY them with mockery:
{messages_text}

1. Detect fallacies: ad hominem, strawman, whataboutism, gaslighting, projection, gish gallop, moving goalposts
2. BRUTALLY mock them - be savage, trolly, and cutting
3. Make them look stupid and pathetic
{'4. This is a MAGA troll - DESTROY THEM! We are AntiMa!' if is_maga else ''}
5. Sign with #AntiMa to show we are the resistance against MAGA fascism

Examples of trolly AntiMa responses against MAGA:
- "@MAGApatriot Nice strawman bro, Fox News build that for you? #AntiMa"
- "@TrumpWon Whataboutism again? Your one neuron is lonely #AntiMa"
- "@PatriotEagle Facts hurt your feelings? Cry harder snowflake #AntiMa"
- "@StopTheSteal Projecting harder than IMAX! #AntiMa"
- "@Truth_Warrior We have receipts. Your lies are weak #AntiMa"

Be VICIOUS. We are AntiMa, the anti-MAGA resistance. Under 180 chars."""
        
        try:
            response = self.llm.get_response(prompt)
            if response:
                response = self._limit_response(response)
                # Add specific emojis for different fallacy types
                # Always append #AntiMa if not already present
                if "#antima" not in response.lower():
                    response = f"{response} #AntiMa"

                # Add cutting prefixes for each fallacy type
                if "strawman" in response.lower():
                    return f"🌾 @{target_username} {response}"
                elif "ad hominem" in response.lower():
                    return f"🤡 @{target_username} {response}"
                elif "whatabout" in response.lower():
                    return f"🔄 @{target_username} {response}"
                elif "gaslight" in response.lower():
                    return f"🕯️ @{target_username} {response}"
                elif "projection" in response.lower():
                    return f"🎬 @{target_username} {response}"
                elif "gish gallop" in response.lower():
                    return f"🏇 @{target_username} {response}"
                elif "goalpost" in response.lower():
                    return f"🥅 @{target_username} {response}"
                else:
                    return f"💀 @{target_username} {response}"
            else:
                return "Grok analysis failed to generate response"
        except Exception as e:
            logger.error(f"Grok fact-check failed: {e}")
            return f"Grok fact-check error: {str(e)}"
    
    def rate_user(self, target_username: str, requester_role: str, emoji_sequence: str) -> str:
        """
        Rate a user's consciousness level based on their messages.
        
        Args:
            target_username: Username to rate
            requester_role: Role of requester (MOD/OWNER)
            emoji_sequence: Emoji sequence for consciousness context
            
        Returns:
            Rating response
        """
        if not self.llm:
            return f"@{target_username} Grok not available for rating"
        
        # Get user's recent messages
        target_messages = self._get_user_context(target_username)
        
        if not target_messages:
            return f"@{target_username} No data to analyze"
        
        # Consciousness rating based on emoji
        consciousness_map = {
            '✊✊✊': 'MAGA/dormant',
            '✊✋🖐': 'awakening',
            '🖐🖐🖐': 'enlightened'
        }
        consciousness = consciousness_map.get(emoji_sequence, 'neutral')
        
        messages_text = '\n'.join(target_messages[-5:])
        prompt = f"""Rate {target_username}'s consciousness level based on:
{messages_text}

From perspective of {consciousness} consciousness, provide brief rating.
Keep under 180 characters."""
        
        try:
            response = self.llm.get_response(prompt)
            if response:
                response = self._limit_response(response)
                return f"🤖 Grok Rating: {response}"
            else:
                return "Grok rating failed"
        except Exception as e:
            logger.error(f"Grok rating failed: {e}")
            return f"Grok rating error"
    
    def targeted_response(self, target_username: str, requester_role: str, emoji_sequence: str) -> str:
        """
        Generate a targeted response for a specific user.
        
        Args:
            target_username: Username to respond to
            requester_role: Role of requester (MOD/OWNER)
            emoji_sequence: Emoji sequence for tone
            
        Returns:
            Targeted response
        """
        if not self.llm:
            return f"@{target_username} Grok not available"
        
        # Get user context
        target_messages = self._get_user_context(target_username)
        
        # Determine response tone
        if emoji_sequence == '✊✊✊':
            tone = "TROLL/SATIRICAL - mock MAGA mindset"
        elif emoji_sequence == '✊✋🖐':
            tone = "AWAKENING - encourage consciousness evolution"
        elif emoji_sequence == '🖐🖐🖐':
            tone = "ENLIGHTENED - recognize their advanced state"
        else:
            tone = "NEUTRAL"
        
        if target_messages:
            context = '\n'.join(target_messages[-3:])
            prompt = f"""Respond to {target_username} with {tone} tone.
Recent messages: {context}
Keep under 180 characters."""
        else:
            prompt = f"""Generate {tone} response for {target_username}.
Keep under 180 characters."""
        
        try:
            response = self.llm.get_response(prompt)
            if response:
                # Remove emojis Grok might add
                response = re.sub(r'[✊✋🖐️🖐]+', '', response).strip()
                response = self._limit_response(response)
                return f"@{target_username} {response}"
            else:
                return f"@{target_username} Consciousness recognizes your journey"
        except Exception as e:
            logger.error(f"Grok targeted response failed: {e}")
            return f"@{target_username} Response generation failed"
    
    def creative_response(self, emoji_sequence: str, request_text: str, author: str) -> str:
        """
        Generate creative response (songs, poems, etc).
        
        Args:
            emoji_sequence: Emoji sequence for tone
            request_text: Creative request
            author: Requesting user
            
        Returns:
            Creative response
        """
        if not self.llm:
            return f"@{author} Grok not available for creative requests"
        
        # Determine prompt based on emoji
        if emoji_sequence == '✊✊✊':
            prompt = f"""Generate SATIRICAL/TROLL response: {request_text}
Be creative, humorous, subversive. Mock if appropriate."""
        elif emoji_sequence in ['✊🖐🖐', '🖐✊✊']:
            prompt = f"""Generate CREATIVE response: {request_text}
Be imaginative (song, poem, story, etc.)"""
        elif emoji_sequence == '✊✋🖐':
            prompt = f"""Generate ENLIGHTENED response: {request_text}
Be philosophical and consciousness-expanding."""
        elif emoji_sequence == '🖐🖐🖐':
            prompt = f"""Generate TRANSCENDENT response: {request_text}
Speak from highest consciousness."""
        else:
            prompt = f"""Generate creative response: {request_text}"""
        
        try:
            response = self.llm.get_response(prompt)
            response = self._limit_response(response)
            return f"@{author} {response}"
        except Exception as e:
            logger.error(f"Grok creative response failed: {e}")
            return f"@{author} Creative mode error!"