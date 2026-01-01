"""
Consciousness Handler Module
WSP-Compliant: WSP 3 (Module Organization), WSP 27 (DAE Architecture)

Handles all consciousness-related emoji sequence processing and responses.

NAVIGATION: Detects and processes ✊✋🖐 consciousness triggers.
-> Called by: message_processor.py::process_message()
-> Delegates to: llm_integration.py, chat_sender.py
-> Related: NAVIGATION.py -> PROBLEMS["Consciousness trigger not working"]
-> Quick ref: NAVIGATION.py -> NEED_TO["handle consciousness trigger"]
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

        # HoloIndex path (prefer root version)
        self.holoindex_available = False
        try:
            import os
            # Check for HoloIndex in order of preference
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            root_holo = os.path.join(project_root, "holo_index.py")

            if os.path.exists(root_holo):
                self.holoindex_path = root_holo
                self.holoindex_available = True
                logger.info("[OK] HoloIndex integration enabled (using root holo_index.py)")
            elif os.path.exists(r"E:\HoloIndex\enhanced_holo_index.py"):
                self.holoindex_path = r"E:\HoloIndex\enhanced_holo_index.py"
                self.holoindex_available = True
                logger.info("[OK] HoloIndex integration enabled (using E: drive version)")
        except:
            logger.warning("⚠️ HoloIndex not available for chat commands")
        
    def search_with_holoindex(self, query: str, username: str, role: str) -> str:
        """
        Search code using HoloIndex semantic search.

        Args:
            query: Search query
            username: Username requesting search
            role: User role (for permission checks if needed)

        Returns:
            Search results formatted for chat
        """
        if not self.holoindex_available:
            return f"@{username} [SEARCH] HoloIndex not available. Install at E:\\HoloIndex"

        try:
            import subprocess
            import re

            # Run HoloIndex search
            result = subprocess.run(
                ['python', self.holoindex_path, '--search', query, '--no-llm'],  # Fast mode for chat
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=5  # Quick timeout for chat responsiveness
            )

            if result.returncode == 0:
                # Parse top results
                matches = re.findall(r'\[(-?\d+\.?\d*)%\] (.+?)\n\s+-> (.+)', result.stdout)

                if matches and len(matches) > 0:
                    # Format top 3 results for chat
                    top_match = matches[0]
                    confidence = float(top_match[0])

                    if confidence > 50:
                        # High confidence - found it!
                        response = f"@{username} [TARGET] Found: {top_match[1]} ({confidence:.0f}% match) -> {top_match[2][:60]}"
                    else:
                        # Low confidence - show options
                        response = f"@{username} [SEARCH] Possible matches for '{query}': "
                        for match in matches[:2]:
                            response += f"[{match[0]}%] {match[1][:30]}... "

                    return response[:400]  # YouTube comment length limit
                else:
                    return f"@{username} [SEARCH] No code found for '{query}'. Try different keywords?"
            else:
                return f"@{username} [FAIL] Search failed. Try simpler keywords?"

        except subprocess.TimeoutExpired:
            return f"@{username} ⏱️ Search timed out. Try a simpler query?"
        except Exception as e:
            logger.error(f"HoloIndex search error: {e}")
            return f"@{username} [FAIL] Search error. Try again later?"

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
            Command type: 'factcheck', 'rate', 'holoindex', 'targeted', 'creative', or 'basic'
        """
        text_lower = text.lower()

        if "factcheck" in text_lower or " fc" in text_lower or text_lower.endswith(" fc"):
            return 'factcheck'
        elif "rate" in text_lower:
            return 'rate'
        elif "holoindex" in text_lower or "search code" in text_lower or "find code" in text_lower:
            return 'holoindex'
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
        if command_type == 'holoindex':
            # Check role restriction - MOD/OWNER only for security
            if role not in ['MOD', 'OWNER']:
                return f"@{username} [LOCK] HoloIndex search is restricted to mods/owners only"

            # Extract search query from the message
            query = self.extract_creative_request(text)
            if query:
                # Clean up the query
                query = query.replace("holoindex", "").replace("search code", "").replace("find code", "").strip()
                if query:
                    return self.search_with_holoindex(query, username, role)
                else:
                    return f"@{username} [SEARCH] HoloIndex: What code should I search for? Example: ✊✋🖐 holoindex send messages"
            else:
                return f"@{username} [SEARCH] Use: ✊✋🖐 holoindex [what you're looking for]"

        elif command_type == 'factcheck' and self.grok:
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
        
        elif command_type == 'creative':
            if role in ['MOD', 'OWNER']:
                if self.grok:
                    request = self.extract_creative_request(text)
                    return self.grok.creative_response(emoji_sequence, request, username)
                else:
                    return f"@{username} Creative mode requires Grok integration"
            else:
                return f"@{username} Only mods/owners can request creative content"

        # Default to sentiment engine response (basic consciousness)
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