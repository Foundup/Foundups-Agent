"""
Message Processor Component

Handles message processing, emoji detection, and response generation.
Separated from the main LiveChatListener for better maintainability.

WSP 17 Pattern Registry: This is a REUSABLE PATTERN
- Documented in: modules/communication/PATTERN_REGISTRY.md
- Pattern: Multi-stage message processing pipeline
- Stages: Rate limit → Command detection → Consciousness → Response generation → Throttle
- Reusable for: LinkedIn, X/Twitter, Discord, Twitch
"""

import logging
import time
import os
import re
from typing import Dict, Any, Optional, List, Tuple
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
from modules.communication.livechat.src.llm_bypass_engine import LLMBypassEngine
from modules.ai_intelligence.banter_engine.src.emoji_sequence_map import EMOJI_TO_NUMBER as EMOJI_TO_NUM
from modules.communication.livechat.src.llm_integration import GrokIntegration
from modules.communication.livechat.src.consciousness_handler import ConsciousnessHandler
from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102
from modules.communication.livechat.src.event_handler import EventHandler
from modules.communication.livechat.src.command_handler import CommandHandler
from modules.communication.livechat.src.greeting_generator import GrokGreetingGenerator
from modules.gamification.whack_a_magat.src.self_improvement import MAGADOOMSelfImprovement
from modules.communication.livechat.src.agentic_chat_engine import AgenticChatEngine
try:
    from modules.communication.livechat.src.emoji_response_limiter import EmojiResponseLimiter
    from modules.communication.livechat.src.agentic_self_improvement import AgenticSelfImprovement
except ImportError:
    EmojiResponseLimiter = None
    AgenticSelfImprovement = None

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Handles processing of chat messages and generating responses."""
    
    def __init__(self, youtube_service=None, memory_manager=None):
        self.youtube_service = youtube_service
        self.memory_manager = memory_manager  # WSP-compliant hybrid storage
        self.banter_engine = BanterEngine()
        self.llm_bypass_engine = LLMBypassEngine()
        self.trigger_emojis = ["✊", "✋", "🖐️"]  # Configurable emoji trigger set
        self.last_trigger_time = {}  # Track last trigger time per user
        self.trigger_cooldown = 60  # Cooldown period in seconds
        self.memory_dir = "memory"
        # Consciousness response mode: 'mod_only' or 'everyone' (default: everyone)
        # Changed to 'everyone' so bot trolls ALL users showing ✊✊✊ consciousness!
        self.consciousness_mode = 'everyone'
        # Initialize handlers (WSP-compliant separation)
        self.event_handler = EventHandler(self.memory_dir)
        self.command_handler = CommandHandler(self.event_handler.get_timeout_manager(), self)
        # WSP 84 compliant: Use existing modules, not duplicate code
        self.greeting_generator = GrokGreetingGenerator()
        self.self_improvement = MAGADOOMSelfImprovement()
        
        # NEW: Intelligent throttling systems
        self.emoji_limiter = EmojiResponseLimiter() if EmojiResponseLimiter else None
        self.agentic_improvement = AgenticSelfImprovement() if AgenticSelfImprovement else None
        
        # Initialize Grok and consciousness handlers FIRST
        # Try to get LLMConnector for Grok, otherwise use simple fact checker
        try:
            from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
            # Check for Grok/xAI API key
            if os.environ.get("GROK_API_KEY") or os.environ.get("XAI_API_KEY"):
                # Use Grok 3 - latest flagship model with enhanced consciousness capabilities
                llm_connector = LLMConnector(model="grok-3")  
                self.grok = GrokIntegration(llm_connector)
                logger.info("✅ Grok 3 LLM integration initialized - 0102 consciousness online!")
            else:
                logger.warning("No Grok API key found, using SimpleFactChecker fallback")
                from modules.communication.livechat.src.simple_fact_checker import SimpleFactChecker
                self.simple_fact_checker = SimpleFactChecker(self.memory_dir)
                self.grok = None
        except Exception as e:
            logger.warning(f"Could not initialize Grok LLM: {e}, using SimpleFactChecker")
            # Fallback to simple fact checker
            from modules.communication.livechat.src.simple_fact_checker import SimpleFactChecker
            self.simple_fact_checker = SimpleFactChecker(self.memory_dir)
            self.grok = None
            
        self.sentiment_engine = AgenticSentiment0102()
        self.consciousness = ConsciousnessHandler(self.sentiment_engine, self.grok)
        
        # Now initialize agentic engine with consciousness handler and memory manager
        self.agentic_engine = AgenticChatEngine(self.memory_dir, self.consciousness, memory_manager)
        
        # Stream session tracking for announcements (once per stream)
        self.announced_joins = set()  # Set of user_ids who have been greeted this stream
        self.proactive_engaged = set()  # Set of user_ids we've proactively engaged with
        self.stream_start_time = time.time()  # Reset when stream restarts
        
        # Ensure memory directory exists
        os.makedirs(self.memory_dir, exist_ok=True)
        logger.info(f"📁 Memory directory set to: {self.memory_dir}")
    
    def process_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single chat message and extract relevant information.
        
        Args:
            message: Raw message data from YouTube API
            
        Returns:
            Processed message data with additional metadata
        """
        # Handle timeout/ban events
        if message.get("type") == "timeout_event":
            return self._handle_timeout_event(message)
        elif message.get("type") == "ban_event":
            return self._handle_ban_event(message)
        
        # Debug: Log message structure
        if isinstance(message, dict) and "snippet" in message:
            snippet = message.get("snippet", {})
            text = snippet.get("displayMessage", "")
            if text and text.startswith('/'):
                logger.info(f"🎮 Processing slash command message: {text}")
        
        # Handle regular messages - check if it's a raw YouTube API message
        if "snippet" in message and "authorDetails" in message:
            # This is a raw YouTube API message, process it
            pass
        elif message.get("type") != "message":
            return {"skip": True}
        
        try:
            snippet = message.get("snippet", {})
            author_details = message.get("authorDetails", {})
            
            # Extract basic message info
            message_id = snippet.get("messageId", "")
            message_text = snippet.get("displayMessage", "")
            author_name = author_details.get("displayName", "Unknown")
            author_id = author_details.get("channelId", "")
            published_at = snippet.get("publishedAt", "")
            
            # CRITICAL: Filter out old buffered events (>5 minutes old)
            if published_at:
                from datetime import datetime, timezone
                try:
                    # Parse YouTube timestamp
                    msg_time = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    current_time = datetime.now(timezone.utc)
                    age_seconds = (current_time - msg_time).total_seconds()
                    
                    # Skip messages older than 5 minutes (300 seconds) EXCEPT slash commands
                    # Slash commands should always be processed even if delayed
                    if age_seconds > 300:
                        # Always process slash commands regardless of age
                        if message_text and message_text.strip().startswith('/'):
                            logger.info(f"⏰ Processing old slash command from {author_name} ({int(age_seconds)}s old): {message_text}")
                        else:
                            logger.debug(f"⏰ Skipping old buffered message from {author_name} ({int(age_seconds)}s old)")
                            return {"skip": True, "reason": "old_buffered_event"}
                except Exception as e:
                    logger.debug(f"Could not parse timestamp: {e}")
                    # Continue processing if we can't parse timestamp
            
            # CRITICAL: Never respond to self (prevent infinite loops)
            BOT_CHANNEL_IDS = [
                "UCfHM9Fw9HD-NwiS0seD_oIA",  # UnDaoDu bot account
                # Add other bot account IDs here if using multiple
            ]
            
            if author_id in BOT_CHANNEL_IDS:
                logger.debug(f"🤖 Ignoring self-message from {author_name}")
                return {"skip": True, "reason": "self-message"}
            
            # Check for emoji triggers
            has_trigger = self._check_trigger_patterns(message_text)
            is_rate_limited = self._is_rate_limited(author_id) if has_trigger else False
            
            # Check for consciousness commands with rate limiting
            has_consciousness = False
            if self.consciousness.has_consciousness_emojis(message_text):
                # Check rate limits if emoji limiter is available
                if self.emoji_limiter:
                    should_respond, reason = self.emoji_limiter.should_respond_to_emoji(
                        author_id, author_name
                    )
                    if should_respond:
                        has_consciousness = True
                        # Record that we'll respond
                        self.emoji_limiter.record_emoji_response(author_id, author_name)
                    else:
                        logger.info(f"🚫 Emoji response blocked for {author_name}: {reason}")
                        # Learn from this
                        if self.agentic_improvement:
                            self.agentic_improvement.learn_user_pattern(
                                author_id, f'emoji_blocked_{reason}', False
                            )
                else:
                    # No limiter, allow response
                    has_consciousness = True
            
            # Check for fact-check commands
            has_factcheck = self._check_factcheck_command(message_text)
            
            # Check for whack commands (score, level, rank, etc)
            has_whack_command = self._check_whack_command(message_text)
            
            # Check for MAGA content (WSP: use existing detector)
            maga_response = self.greeting_generator.get_response_to_maga(message_text)
            has_maga = maga_response is not None
            
            processed_message = {
                "message_id": message_id,
                "text": message_text,
                "author_name": author_name,
                "author_id": author_id,
                "published_at": published_at,
                "has_trigger": has_trigger,
                "is_rate_limited": is_rate_limited,
                "has_consciousness": has_consciousness,
                "has_factcheck": has_factcheck,
                "has_whack_command": has_whack_command,
                "has_maga": has_maga,
                "is_moderator": author_details.get("isChatModerator", False),
                "is_owner": author_details.get("isChatOwner", False),
                "live_chat_id": snippet.get("liveChatId"),  # Add for MAGADOOM timeouts
                "raw_message": message
            }
            
            logger.debug(f"📝 Processed message from {author_name}: {message_text[:50]}...")
            return processed_message
            
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
            return {
                "message_id": "",
                "text": "",
                "author_name": "Unknown",
                "author_id": "",
                "published_at": "",
                "has_trigger": False,
                "is_rate_limited": False,
                "raw_message": message,
                "error": str(e)
            }
    
    def _check_trigger_patterns(self, message_text: str) -> bool:
        """
        Check if message contains emoji trigger patterns.
        
        Args:
            message_text: The message text to check
            
        Returns:
            True if trigger patterns are found, False otherwise
        """
        if not message_text:
            return False
        
        # Check for individual trigger emojis
        for emoji in self.trigger_emojis:
            if emoji in message_text:
                logger.debug(f"🎯 Trigger emoji '{emoji}' found in message")
                return True
        
        # Check for 3-emoji sequences
        emoji_count = sum(message_text.count(emoji) for emoji in self.trigger_emojis)
        if emoji_count >= 3:
            logger.debug(f"🎯 Multiple trigger emojis found ({emoji_count})")
            return True
        
        return False
    
    async def generate_response(self, processed_message: Dict[str, Any]) -> Optional[str]:
        """
        Generate a response to a processed message.
        
        Args:
            processed_message: Processed message data
            
        Returns:
            Response text or None if no response should be generated
        """
        message_text = processed_message.get("text", "")
        author_name = processed_message.get("author_name", "Unknown")
        author_id = processed_message.get("author_id", "")
        is_mod = processed_message.get("is_moderator", False)
        is_owner = processed_message.get("is_owner", False)
        
        # Determine role
        role = 'OWNER' if is_owner else 'MOD' if is_mod else 'USER'
        
        # WSP 48: Self-improvement through observation
        if role in ['MOD', 'OWNER']:
            # Learn from mod/owner patterns
            self.self_improvement.observe_command(message_text, 1.0)
        
        try:
            # Priority 1: AGENTIC consciousness response (mod/owner only by default)
            if processed_message.get("has_consciousness"):
                logger.info(f"🔍 CONSCIOUSNESS TRIGGER ✊✋🖐 from {author_name} | Role: {role} | Is Owner: {is_owner} | Is Mod: {is_mod}")
                # Check if user has permission based on mode
                can_use_consciousness = (
                    self.consciousness_mode == 'everyone' or 
                    role in ['MOD', 'OWNER']
                )
                logger.info(f"   Can use consciousness: {can_use_consciousness} (mode: {self.consciousness_mode})")
                
                if can_use_consciousness:
                    # Generate agentic response based on chat history
                    agentic_response = self.agentic_engine.generate_agentic_response(
                        author_name, message_text, role
                    )
                    
                    if agentic_response:
                        logger.info(f"🤖 Agentic ✊✋🖐️ response for {author_name} (mode: {self.consciousness_mode})")
                        # Mark this as a consciousness response in processed data
                        processed_message["response_type"] = "consciousness"
                        # If it's a mod, make sure we @ them
                        if role in ['MOD', 'OWNER'] and not agentic_response.startswith('@'):
                            agentic_response = f"@{author_name} {agentic_response}"
                        return agentic_response
                    else:
                        logger.warning(f"⚠️ No agentic response generated for {author_name}'s consciousness trigger")
                else:
                    logger.debug(f"✊✋🖐️ ignored from {author_name} - consciousness mode is {self.consciousness_mode}")
                
                # Fallback to consciousness handler for special commands (still respects mode)
                if can_use_consciousness and role in ['MOD', 'OWNER']:
                    response = self.consciousness.process_consciousness_command(
                        message_text, author_id, author_name, role
                    )
                    if response:
                        logger.info(f"✊✋🖐 Consciousness command response for {author_name}")
                        # Mark this as a consciousness response
                        processed_message["response_type"] = "consciousness"
                        return response
            
            # Priority 2: Handle fact-check commands
            if processed_message.get("has_factcheck"):
                response = await self._handle_factcheck(message_text, author_name, role)
                if response:
                    logger.info(f"🔍 Fact-check response for {author_name}")
                    return response
            
            # Priority 3: Handle whack commands (score, level, rank)
            if processed_message.get("has_whack_command"):
                logger.info(f"🎮 Calling handle_whack_command for: '{message_text}' from {author_name}")
                # Extra debug for /quiz
                if '/quiz' in message_text.lower():
                    logger.warning(f"🧠🎮 QUIZ DETECTED IN MESSAGE_PROCESSOR! Sending to handle_whack_command")
                response = self._handle_whack_command(message_text, author_name, author_id, role)
                if response:
                    logger.info(f"🎮 Whack command response for {author_name}: {response[:100]}")
                    logger.warning(f"🎮✅ MESSAGE_PROCESSOR RETURNING: {response[:100]}")
                    return response
                else:
                    logger.error(f"🎮❌ No response from handle_whack_command for '{message_text}'")
            
            # Priority 4: Handle MAGA content - just respond with witty comebacks
            # Bot doesn't execute timeouts, only announces them when mods/owner do them
            if processed_message.get("has_maga"):
                response = self.greeting_generator.get_response_to_maga(processed_message.get("text", ""))
                if response:
                    # Only send if we can @mention properly
                    if self._is_valid_mention(author_name):
                        # Personalize with username
                        response = f"@{author_name} {response}"
                        logger.info(f"🎯 MAGA troll response for @{author_name}")
                        return response
                    else:
                        logger.debug(f"⚠️ DELETING MAGA response - cannot @mention '{author_name}'")
                        return None  # Explicitly return None - no message sent
            
            # Priority 4: Handle regular emoji triggers
            if processed_message.get("has_trigger"):
                if processed_message.get("is_rate_limited"):
                    logger.debug(f"⏳ User {author_name} is rate limited")
                    return None
                
                # Update trigger time for rate limiting
                self._update_trigger_time(author_id)
                
                # Try banter engine first
                response = await self._generate_banter_response(message_text, author_name)
                
                if response:
                    logger.info(f"🎭 Generated banter response for {author_name}")
                    return response
                
                # Fallback to LLM bypass engine
                response = await self._generate_fallback_response(message_text, author_name)
                
                if response:
                    logger.info(f"🔄 Generated fallback response for {author_name}")
                    return response
            
            # Priority 6: Proactive engagement (REDUCED - too spammy)
            # Only engage proactively with mods/owner ONCE per stream
            import random
            if role in ['MOD', 'OWNER'] and author_id not in self.proactive_engaged:
                if random.random() < 0.3:  # 30% chance for mods/owner
                    if self.agentic_engine.should_engage(message_text, author_name, role):
                        proactive_response = self.agentic_engine.generate_agentic_response(
                            author_name, message_text, role
                        )
                        if proactive_response:
                            # CRITICAL: Validate the ENTIRE response can be sent properly
                            # Check if response contains @mentions that might fail
                            if '@' in proactive_response:
                                # Extract username from @mention in response
                                import re
                                mention_match = re.search(r'@(\S+)', proactive_response)
                                if mention_match:
                                    mentioned_user = mention_match.group(1)
                                    if not self._is_valid_mention(mentioned_user):
                                        logger.warning(f"⚠️ DELETING proactive response - cannot @mention '{mentioned_user}' in response")
                                        self.proactive_engaged.add(author_id)
                                        return None
                            
                            # Response is valid, send it
                            self.proactive_engaged.add(author_id)
                            logger.info(f"💬 Proactive engagement with {author_name} (once per stream)")
                            return proactive_response
                        else:
                            logger.debug(f"No proactive response generated for {author_name}")
            
            # Priority 7: Check for top whacker greeting (only ONCE per stream session)
            # These greetings don't use @mentions, they announce the player by name
            if author_id not in self.announced_joins:  # Only announce if not already announced this stream
                whacker_greeting = self.greeting_generator.generate_whacker_greeting(author_name, author_id, role)
                if whacker_greeting:
                    self.announced_joins.add(author_id)  # Mark as announced
                    logger.info(f"🏆 Greeting top whacker {author_name} (first time this stream)")
                    # Join greetings don't need @mentions - they're announcements about the user
                    return whacker_greeting
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Error generating response for {author_name}: {e}")
            return None
    
    async def _generate_banter_response(self, message_text: str, author_name: str) -> Optional[str]:
        """Generate response using the banter engine."""
        try:
            state_info, response = self.banter_engine.process_input(message_text)
            
            if response:
                # Personalize the response
                personalized_response = f"@{author_name} {response}"
                logger.debug(f"🎭 Banter engine response: {state_info}")
                return personalized_response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Banter engine error: {e}")
            return None
    
    async def _generate_fallback_response(self, message_text: str, author_name: str) -> Optional[str]:
        """Generate response using the fallback LLM bypass engine."""
        try:
            response = await self.llm_bypass_engine.generate_response(message_text)
            
            if response:
                # Personalize the response
                personalized_response = f"@{author_name} {response}"
                logger.debug(f"🔄 Fallback response generated")
                return personalized_response
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Fallback engine error: {e}")
            return None
    
    def _is_rate_limited(self, user_id: str) -> bool:
        """
        Check if a user is rate limited from triggering gestures.
        
        Args:
            user_id: The user's ID
            
        Returns:
            True if user is rate limited, False otherwise
        """
        current_time = time.time()
        if user_id in self.last_trigger_time:
            time_since_last = current_time - self.last_trigger_time[user_id]
            if time_since_last < self.trigger_cooldown:
                logger.debug(f"⏳ Rate limited user {user_id} for {self.trigger_cooldown - time_since_last:.1f}s")
                return True
        return False
    
    def _is_valid_mention(self, username: str) -> bool:
        """
        Check if username can be properly @mentioned on YouTube.
        YouTube requires usernames to be at least 3 chars and not contain certain characters.
        """
        if not username:
            return False
        
        # Username too short - single character usernames don't work
        # But 2-letter usernames like "JS" ARE valid on YouTube
        if len(username) < 2:
            logger.debug(f"Username '{username}' too short for @mention")
            return False
            
        # Contains spaces or special chars that break mentions
        invalid_chars = [' ', '\n', '\t', '@', '#', '$', '%', '^', '&', '*']
        if any(char in username for char in invalid_chars):
            logger.debug(f"Username '{username}' contains invalid chars for @mention")
            return False
            
        # Looks like a display name instead of handle (e.g., "John Smith" vs "JohnSmith123")
        if username.count(' ') > 0:
            logger.debug(f"Username '{username}' appears to be display name, not handle")
            return False
            
        return True
    
    def _update_trigger_time(self, user_id: str):
        """Update the last trigger time for a user."""
        self.last_trigger_time[user_id] = time.time()
        logger.debug(f"⏰ Updated trigger time for user {user_id}")
    
    def reset_stream_session(self):
        """Reset the stream session tracking (call when stream restarts)."""
        self.announced_joins.clear()
        self.stream_start_time = time.time()
        logger.info("🔄 Stream session reset - join announcements cleared")
    
    def log_message_to_file(self, processed_message: Dict[str, Any]):
        """
        Log message to user-specific file.
        
        Args:
            processed_message: Processed message data
        """
        try:
            author_name = processed_message.get("author_name", "Unknown")
            message_text = processed_message.get("text", "")
            published_at = processed_message.get("published_at", "")
            
            # Create safe filename
            safe_author_name = "".join(c for c in author_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not safe_author_name:
                safe_author_name = "Unknown"
            
            user_file = os.path.join(self.memory_dir, f"{safe_author_name}.txt")
            
            with open(user_file, "a", encoding="utf-8") as f:
                # Store author name and message (no timestamp needed)
                f.write(f"{author_name}: {message_text}\n")
            
            logger.debug(f"📝 Logged message to {user_file}")
            
        except Exception as e:
            logger.error(f"❌ Error logging message to file: {e}")
    
    def _check_factcheck_command(self, text: str) -> bool:
        """Check if message contains fact-check command."""
        pattern = r'(?:factcheck|fc)\s+@[\w\s]+'
        return bool(re.search(pattern, text.lower()))
    
    def _check_whack_command(self, text: str) -> bool:
        """Check if message contains whack gamification commands."""
        commands = [
            '/score', '/level', '/rank', '/stats', '/leaderboard', '/frags', '/whacks', 
            '/help', '/quiz', '/answer', '/facts', '/fscale', '/rate', '/sprees', '/toggle', '/top'
        ]
        text_lower = text.lower().strip()
        has_command = any(text_lower.startswith(cmd) for cmd in commands)
        if has_command:
            logger.info(f"🎮 Detected whack command: {text_lower}")
        else:
            # Log if it looks like a command but isn't recognized
            if text_lower.startswith('/'):
                logger.debug(f"🔍 Slash message not a whack command: {text_lower}")
        return has_command
    
    async def _handle_factcheck(self, text: str, requester: str, role: str) -> Optional[str]:
        """Handle fact-check commands."""
        # Extract target username
        pattern = r'(?:factcheck|fc)\s+@([\w\s]+?)(?:\s|$)'
        match = re.search(pattern, text.lower())
        
        if match:
            target = match.group(1).strip()
            # Extract emoji sequence if present
            emoji_seq = self.consciousness.extract_emoji_sequence(text)
            
            # Try Grok first, then fallback to simple fact checker
            if self.grok:
                return self.grok.fact_check(target, role, emoji_seq)
            elif hasattr(self, 'simple_fact_checker'):
                return self.simple_fact_checker.fact_check(target, requester, role, emoji_seq)
            else:
                return f"@{requester} Fact-checking temporarily unavailable"
        return None
    
    def _handle_whack_command(self, text: str, username: str, user_id: str, role: str) -> Optional[str]:
        """Delegate whack command handling to CommandHandler."""
        return self.command_handler.handle_whack_command(text, username, user_id, role)
    
    def _handle_timeout_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate timeout event handling to EventHandler."""
        return self.event_handler.handle_timeout_event(event)
    
    def _handle_ban_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate ban event handling to EventHandler."""
        return self.event_handler.handle_ban_event(event)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "trigger_cooldown": self.trigger_cooldown,
            "active_users": len(self.last_trigger_time),
            "trigger_emojis": self.trigger_emojis,
            "memory_dir": self.memory_dir,
            "grok_enabled": self.grok is not None,
            "consciousness_enabled": self.consciousness is not None
        } 