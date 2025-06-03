import logging
import re
import time
from typing import List, Dict, Set, Optional, Tuple
from collections import deque, defaultdict
import googleapiclient.errors
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class AutoModerator:
    """
    Auto-moderation system for YouTube Live Chat.
    Automatically detects banned phrases, spam patterns, and applies timeouts.
    
    Features:
    - Banned phrase detection
    - Spam rate limiting
    - Repetitive message detection  
    - Message similarity analysis
    - User behavior tracking
    """
    
    def __init__(self, youtube_service):
        self.youtube = youtube_service
        self.timeout_duration = 10  # 10 seconds for testing (was 60)
        self.recent_timeouts = {}  # Track recent timeouts to avoid spam
        self.timeout_cooldown = 300  # 5 minutes between timeouts for same user
        
        # === MODERATOR PROTECTION ===
        # Users who are exempt from moderation (moderators, admins, channel owners)
        self.moderator_exemptions = set()  # Channel IDs of users exempt from moderation
        self.owner_channel_id = None       # Channel owner ID (set during initialization)
        
        # === SPAM DETECTION SETTINGS ===
        self.spam_rate_limit = 5  # Messages per time window
        self.spam_time_window = 30  # Time window in seconds
        self.similarity_threshold = 0.8  # 80% similarity threshold
        self.repetitive_count_threshold = 3  # Number of similar messages to trigger
        
        # User tracking for spam detection
        self.user_message_history = defaultdict(lambda: deque(maxlen=10))  # Last 10 messages per user
        self.user_message_times = defaultdict(lambda: deque(maxlen=20))    # Last 20 message times per user
        self.user_violations = defaultdict(int)  # Track violation counts per user
        
        # Define banned phrases (case-insensitive)
        self.banned_phrases = {
            # Core MAGA/Trump 2028 spam patterns
            "maga 2028",
            "trump 2028", 
            "make america great again 2028",
            "maga forever",
            "maga 2024",
            "trump 2024",
            "trump forever",
            "maga movement",
            "maga nation",
            "maga patriots",
            "maga army",
            "trump train",
            "trump wins",
            "trump victory",
            "trump landslide",
            
            # Religious/worship Trump spam
            "love trump", 
            "trump is jesus",
            "trump is god",
            "trump is our savior",
            "trump will save us",
            "trump is the messiah",
            "trump is king",
            "trump is emperor",
            "trump is divine",
            "worship trump",
            "praise trump",
            "trump is holy",
            "trump is sacred",
            "trump is blessed",
            "trump is chosen",
            "trump is anointed",
            "god emperor trump",
            "trump is lord",
            "trump is christ",
            "trump is the one",
            "trump is our father",
            
            # QAnon/conspiracy spam
            "wwg1wga",
            "where we go one we go all",
            "q sent me",
            "trust the plan",
            "nothing can stop what is coming",
            "storm is coming",
            "great awakening",
            "deep state",
            "trump is fighting the deep state",
            
            # Election fraud/stolen election spam
            "stop the steal",
            "stolen election",
            "election fraud",
            "trump won",
            "biden lost",
            "fake election",
            "rigged election",
            "count the votes",
            "election was stolen",
            "fraud everywhere",
            
            # January 6th related spam
            "january 6th patriots",
            "j6 heroes",
            "political prisoners",
            "free the j6",
            "patriots in jail",
            
            # Anti-Biden/Democrat spam
            "lets go brandon",
            "fuck joe biden",
            "fjb",
            "biden crime family",
            "sleepy joe",
            "crooked joe",
            "fake president biden",
            
            # Extremist content
            "civil war now",
            "take back america",
            "fight fight fight",
            "we will not be replaced",
            "america first",
            "blood and soil",
            
            # Common troll variations
            "trump daddy",
            "orange man good",
            "trump is daddy",
            "daddy trump",
            "trump supreme",
            "all hail trump",
            "trump rules all",
            "bow to trump",
            "submit to trump"
        }
        
        # Compile regex patterns for efficient matching
        self.banned_patterns = []
        for phrase in self.banned_phrases:
            # Create pattern that matches the phrase with word boundaries
            # This prevents false positives on partial matches
            pattern = r'\b' + re.escape(phrase) + r'\b'
            self.banned_patterns.append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"🛡️ AutoModerator initialized with {len(self.banned_phrases)} banned phrases")
        logger.info(f"🕐 Timeout duration: {self.timeout_duration} seconds")
        logger.info(f"🚫 Spam detection: {self.spam_rate_limit} msgs/{self.spam_time_window}s, {self.similarity_threshold*100}% similarity threshold")
    
    def check_message(self, message_text: str, author_id: str, author_name: str) -> Tuple[bool, str]:
        """
        Check if a message contains banned content or spam patterns.
        
        Args:
            message_text (str): The message text to check
            author_id (str): The author's channel ID
            author_name (str): The author's display name
            
        Returns:
            Tuple[bool, str]: (True if violation detected, reason for violation)
        """
        if not message_text or not message_text.strip():
            return False, ""
        
        # 0. Check for moderator exemptions FIRST
        if self._is_moderator_exempt(author_id, author_name):
            return False, ""
        
        # 1. Check banned phrases
        banned_result = self._check_banned_phrases(message_text, author_name)
        if banned_result[0]:
            return banned_result
        
        # 2. Check spam patterns
        spam_result = self._check_spam_patterns(message_text, author_id, author_name)
        if spam_result[0]:
            return spam_result
        
        # 3. Update user tracking (if no violations)
        self._update_user_tracking(message_text, author_id)
        
        return False, ""
    
    def _check_banned_phrases(self, message_text: str, author_name: str) -> Tuple[bool, str]:
        """Check for banned phrases in the message."""
        for pattern in self.banned_patterns:
            if pattern.search(message_text):
                matched_phrase = pattern.pattern.replace(r'\b', '').replace('\\', '')
                logger.warning(f"🚨 BANNED PHRASE DETECTED: '{matched_phrase}' in message from {author_name}: '{message_text}'")
                return True, f"banned_phrase: {matched_phrase}"
        return False, ""
    
    def _check_spam_patterns(self, message_text: str, author_id: str, author_name: str) -> Tuple[bool, str]:
        """Check for spam patterns (rate limiting, repetitive content, similarity)."""
        current_time = time.time()
        
        # 1. Rate limiting check
        user_times = self.user_message_times[author_id]
        user_times.append(current_time)
        
        # Count messages in current time window
        window_start = current_time - self.spam_time_window
        recent_messages = sum(1 for t in user_times if t >= window_start)
        
        if recent_messages > self.spam_rate_limit:
            logger.warning(f"🚨 RATE LIMIT EXCEEDED: {author_name} sent {recent_messages} messages in {self.spam_time_window}s")
            return True, f"rate_limit: {recent_messages} msgs in {self.spam_time_window}s"
        
        # 2. Check for repetitive/similar content
        user_history = self.user_message_history[author_id]
        if len(user_history) >= 2:
            # Check similarity with recent messages
            similar_count = 0
            for historical_msg in list(user_history)[-5:]:  # Check last 5 messages
                similarity = self._calculate_similarity(message_text, historical_msg)
                if similarity >= self.similarity_threshold:
                    similar_count += 1
            
            if similar_count >= self.repetitive_count_threshold - 1:  # -1 because we haven't added current msg yet
                logger.warning(f"🚨 REPETITIVE CONTENT: {author_name} posted {similar_count + 1} similar messages")
                return True, f"repetitive_content: {similar_count + 1} similar messages"
        
        return False, ""
    
    def _calculate_similarity(self, msg1: str, msg2: str) -> float:
        """Calculate similarity between two messages using SequenceMatcher."""
        if not msg1 or not msg2:
            return 0.0
        
        # Normalize messages for comparison
        norm1 = msg1.lower().strip()
        norm2 = msg2.lower().strip()
        
        # Calculate similarity ratio
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def _update_user_tracking(self, message_text: str, author_id: str):
        """Update user message history for spam tracking."""
        self.user_message_history[author_id].append(message_text)
    
    def _is_recently_timed_out(self, author_id: str) -> bool:
        """
        Check if a user was recently timed out to avoid spam.
        
        Args:
            author_id (str): The author's channel ID
            
        Returns:
            bool: True if user was recently timed out, False otherwise
        """
        current_time = time.time()
        if author_id in self.recent_timeouts:
            time_since_timeout = current_time - self.recent_timeouts[author_id]
            if time_since_timeout < self.timeout_cooldown:
                logger.debug(f"⏰ User {author_id} was recently timed out ({time_since_timeout:.1f}s ago), skipping")
                return True
        return False

    async def apply_timeout(self, live_chat_id: str, author_id: str, author_name: str, message_text: str, reason: str = "") -> bool:
        """
        Apply a timeout to a user for posting banned content or spam.
        
        Args:
            live_chat_id (str): The live chat ID
            author_id (str): The author's channel ID to timeout
            author_name (str): The author's display name
            message_text (str): The offending message
            reason (str): Reason for the timeout
            
        Returns:
            bool: True if timeout was successfully applied, False otherwise
        """
        # Check if user was recently timed out
        if self._is_recently_timed_out(author_id):
            return False
        
        # Increment violation count
        self.user_violations[author_id] += 1
        violation_count = self.user_violations[author_id]
        
        # Escalate timeout duration for repeat offenders
        timeout_duration = self.timeout_duration
        if violation_count >= 3:
            timeout_duration = 30  # 30 seconds for repeat offenders (was 300s)
        elif violation_count >= 2:
            timeout_duration = 20  # 20 seconds for second offense (was 180s)
        
        try:
            # Create a temporary ban using YouTube Live Chat API
            ban_request = {
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "temporary",
                    "banDurationSeconds": timeout_duration,
                    "bannedUserDetails": {
                        "channelId": author_id
                    }
                }
            }
            
            logger.info(f"🔨 Applying {timeout_duration}s timeout to {author_name} ({author_id}) - Violation #{violation_count}")
            logger.info(f"📝 Reason: {reason} - Message: '{message_text}'")
            
            # Execute the ban
            response = self.youtube.liveChatBans().insert(
                part="snippet",
                body=ban_request
            ).execute()
            
            # Track the timeout
            self.recent_timeouts[author_id] = time.time()
            
            # Send classic IRC-style trout slap message to chat
            try:
                await self._send_trout_slap_message(live_chat_id, author_name, reason, timeout_duration)
            except Exception as slap_error:
                logger.warning(f"Failed to send trout slap message: {slap_error}")
            
            logger.info(f"✅ Successfully applied {timeout_duration}s timeout to {author_name}")
            logger.info(f"🆔 Ban ID: {response.get('id', 'unknown')}")
            
            return True
            
        except googleapiclient.errors.HttpError as e:
            error_code = e.resp.status if hasattr(e, 'resp') else 'unknown'
            error_details = str(e)
            logger.error(f"❌ Failed to apply timeout to {author_name}: HTTP {error_code} - {e}")
            
            # Handle specific error cases
            if error_code == 403:
                if "liveChatBanInsertionNotAllowed" in error_details:
                    # User is likely channel owner or moderator - auto-exempt them
                    logger.warning(f"🛡️ Auto-exempting {author_name} ({author_id}) - appears to be channel owner/moderator")
                    self.add_moderator_exemption(author_id, author_name)
                    # Set as owner if not set yet
                    if self.owner_channel_id is None:
                        self.owner_channel_id = author_id
                        logger.info(f"👑 Set {author_name} as channel owner")
                    
                    # Send automatic callout message for protected users who violate rules
                    try:
                        await self._send_automatic_callout(live_chat_id, author_name, reason, message_text)
                    except Exception as callout_error:
                        logger.warning(f"Failed to send automatic callout: {callout_error}")
                        
                elif "quotaExceeded" in error_details or "exceeded your" in error_details or "quota" in error_details.lower():
                    # API quota exceeded - trigger credential rotation and send callout
                    logger.warning(f"⚠️ Quota exceeded, couldn't timeout {author_name} for: {reason}")
                    
                    # Try to get new OAuth service with fallback
                    try:
                        from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback
                        logger.info("🔄 Attempting credential rotation due to quota exceeded in auto-moderator...")
                        
                        auth_result = get_authenticated_service_with_fallback()
                        if auth_result:
                            service, credentials, credential_set = auth_result
                            self.youtube = service  # Update our service
                            logger.info(f"✅ Auto-moderator credential rotation successful - now using {credential_set}")
                            
                            # Send automatic callout with new service
                            try:
                                await self._send_automatic_callout(live_chat_id, author_name, reason, message_text)
                                logger.info(f"✅ Sent automatic callout to {author_name} after credential rotation")
                            except Exception as callout_error:
                                logger.warning(f"Failed to send callout after credential rotation: {callout_error}")
                                
                        else:
                            logger.error("❌ All credential sets exceeded quota - cannot rotate")
                            # Send callout anyway using current service (might fail but worth trying)
                            try:
                                await self._send_automatic_callout(live_chat_id, author_name, reason, message_text)
                            except Exception as callout_error:
                                logger.warning(f"Failed to send emergency callout: {callout_error}")
                    except Exception as rotation_error:
                        logger.error(f"❌ Credential rotation failed: {rotation_error}")
                        # Try sending callout with current service as last resort
                        try:
                            await self._send_automatic_callout(live_chat_id, author_name, reason, message_text)
                        except Exception as callout_error:
                            logger.warning(f"Failed to send fallback callout: {callout_error}")
                else:
                    logger.error("🚫 Insufficient permissions to ban users. Bot needs moderator privileges.")
            elif error_code == 400:
                logger.error("🚫 Invalid ban request. Check user ID and chat ID.")
            elif error_code == 404:
                logger.error("🚫 Live chat or user not found.")
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to apply timeout to {author_name}: {e}")
            return False
    
    async def _send_trout_slap_message(self, live_chat_id: str, author_name: str, reason: str, timeout_duration: int) -> bool:
        """
        Send a classic IRC-style trout slap message to chat after timing out a user.
        
        Args:
            live_chat_id (str): The live chat ID
            author_name (str): The violator's display name
            reason (str): Reason for timeout
            timeout_duration (int): Duration of timeout in seconds
            
        Returns:
            bool: True if message sent successfully
        """
        import random
        
        # Classic IRC trout slap variations with modern twists
        trout_slaps = [
            f"🐟 *slaps {author_name} around a bit with a large trout* ✊✊✊🐟",
            f"🐟 *whacks {author_name} with a mighty salmon for {timeout_duration}s* ✋✋✋🐟",
            f"🐟 *bonks {author_name} with a hefty halibut* - Chat rules matter! 🖐️🖐️🖐️🐟",
            f"🐟 *smacks {author_name} with a supersonic sardine* - Behave yourself! ✊✊✊🐟",
            f"🐟 *wallops {author_name} with a wiggly walleye* - {timeout_duration}s timeout! ✋✋✋🐟",
            f"🐟 *thwacks {author_name} with a tremendous tuna* - No spam allowed! 🖐️🖐️🖐️🐟",
            f"🐟 *clobbers {author_name} with a colossal cod* - Take a break! ✊✊✊🐟",
            f"🐟 *bops {author_name} with a bouncing bass* - Cool it for {timeout_duration}s! ✋✋✋🐟",
            f"🐟 *swipes {author_name} with a slippery snapper* - Read the rules! 🖐️🖐️🖐️🐟",
            f"🐟 *clunks {author_name} with a chunky catfish* - Timeout engaged! ✊✊✊🐟"
        ]
        
        # Political spam specific slaps
        political_slaps = [
            f"🐟 *slaps {author_name} with a democracy-defending trout* - Political spam is not welcome! ✋✋✋🐟",
            f"🐟 *whacks {author_name} with a bipartisan bass* - Keep politics civil or stay quiet! 🖐️🖐️🖐️🐟", 
            f"🐟 *bonks {author_name} with a constitutional cod* - No extremist content here! ✊✊✊🐟",
            f"🐟 *smacks {author_name} with a liberty-loving lobster* - Political trolling = timeout! ✋✋✋🐟"
        ]
        
        # QAnon/conspiracy specific slaps
        conspiracy_slaps = [
            f"🐟 *slaps {author_name} with a fact-checking flounder* - Conspiracy theories not allowed! 🖐️🖐️🖐️🐟",
            f"🐟 *whacks {author_name} with a reality-checking ray* - Stay grounded in facts! ✊✊✊🐟",
            f"🐟 *bonks {author_name} with a truth-telling trout* - No conspiracy spam! ✋✋✋🐟"
        ]
        
        # Choose appropriate slap based on violation reason
        if "banned_phrase" in reason and any(phrase in reason for phrase in ["maga", "trump", "biden", "election"]):
            if any(phrase in reason for phrase in ["deep state", "trust the plan", "storm", "wwg1wga"]):
                slap_message = random.choice(conspiracy_slaps)
            else:
                slap_message = random.choice(political_slaps)
        else:
            slap_message = random.choice(trout_slaps)
        
        try:
            # Create chat message request
            message_request = {
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": slap_message
                    }
                }
            }
            
            # Send the trout slap message
            response = self.youtube.liveChatMessages().insert(
                part="snippet",
                body=message_request
            ).execute()
            
            logger.info(f"🐟 Sent trout slap: {slap_message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send trout slap message: {e}")
            return False
    
    def add_banned_phrase(self, phrase: str) -> bool:
        """
        Add a new banned phrase to the moderation list.
        
        Args:
            phrase (str): The phrase to ban
            
        Returns:
            bool: True if phrase was added, False if it already exists
        """
        phrase_lower = phrase.lower().strip()
        if phrase_lower in self.banned_phrases:
            logger.warning(f"Phrase '{phrase}' is already banned")
            return False
        
        self.banned_phrases.add(phrase_lower)
        
        # Add compiled pattern
        pattern = r'\b' + re.escape(phrase_lower) + r'\b'
        self.banned_patterns.append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"➕ Added banned phrase: '{phrase}'")
        return True
    
    def remove_banned_phrase(self, phrase: str) -> bool:
        """
        Remove a banned phrase from the moderation list.
        
        Args:
            phrase (str): The phrase to remove
            
        Returns:
            bool: True if phrase was removed, False if it didn't exist
        """
        phrase_lower = phrase.lower().strip()
        if phrase_lower not in self.banned_phrases:
            logger.warning(f"Phrase '{phrase}' is not in banned list")
            return False
        
        self.banned_phrases.remove(phrase_lower)
        
        # Rebuild patterns list
        self.banned_patterns = []
        for banned_phrase in self.banned_phrases:
            pattern = r'\b' + re.escape(banned_phrase) + r'\b'
            self.banned_patterns.append(re.compile(pattern, re.IGNORECASE))
        
        logger.info(f"➖ Removed banned phrase: '{phrase}'")
        return True
    
    def get_banned_phrases(self) -> List[str]:
        """
        Get the current list of banned phrases.
        
        Returns:
            List[str]: List of banned phrases
        """
        return sorted(list(self.banned_phrases))
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get moderation statistics.
        
        Returns:
            Dict[str, int]: Statistics including total banned phrases, recent timeouts, and spam detection metrics
        """
        current_time = time.time()
        recent_timeout_count = sum(
            1 for timeout_time in self.recent_timeouts.values()
            if current_time - timeout_time < 3600  # Last hour
        )
        
        # Calculate user violation statistics
        total_violations = sum(self.user_violations.values())
        users_with_violations = len([v for v in self.user_violations.values() if v > 0])
        
        return {
            "banned_phrases_count": len(self.banned_phrases),
            "recent_timeouts_1h": recent_timeout_count,
            "total_tracked_timeouts": len(self.recent_timeouts),
            "total_user_violations": total_violations,
            "users_with_violations": users_with_violations,
            "tracked_users": len(self.user_message_history),
            "spam_rate_limit": self.spam_rate_limit,
            "spam_time_window": self.spam_time_window,
            "similarity_threshold": int(self.similarity_threshold * 100),  # As percentage
            "timeout_duration": self.timeout_duration
        }
    
    def get_user_violations(self, author_id: str) -> Dict[str, any]:
        """
        Get violation information for a specific user.
        
        Args:
            author_id (str): The user's channel ID
            
        Returns:
            Dict: User violation statistics and recent message history
        """
        recent_messages = list(self.user_message_history.get(author_id, []))
        recent_times = list(self.user_message_times.get(author_id, []))
        violation_count = self.user_violations.get(author_id, 0)
        
        # Calculate recent message rate
        current_time = time.time()
        window_start = current_time - self.spam_time_window
        recent_msg_count = sum(1 for t in recent_times if t >= window_start)
        
        return {
            "violation_count": violation_count,
            "recent_messages": recent_messages,
            "recent_message_count": recent_msg_count,
            "message_rate": f"{recent_msg_count}/{self.spam_time_window}s",
            "is_rate_limited": recent_msg_count > self.spam_rate_limit,
            "last_timeout": self.recent_timeouts.get(author_id, 0),
            "on_cooldown": self._is_recently_timed_out(author_id)
        }
    
    def clear_user_violations(self, author_id: str) -> bool:
        """
        Clear violation history for a user (moderator action).
        
        Args:
            author_id (str): The user's channel ID
            
        Returns:
            bool: True if violations were cleared
        """
        if author_id in self.user_violations:
            old_count = self.user_violations[author_id]
            self.user_violations[author_id] = 0
            logger.info(f"🧹 Cleared {old_count} violations for user {author_id}")
            return True
        return False
    
    def adjust_spam_settings(self, rate_limit: int = None, time_window: int = None, 
                           similarity_threshold: float = None, timeout_duration: int = None) -> Dict[str, any]:
        """
        Adjust spam detection settings (moderator/admin action).
        
        Args:
            rate_limit (int): Max messages per time window
            time_window (int): Time window in seconds
            similarity_threshold (float): Similarity threshold (0.0-1.0)
            timeout_duration (int): Base timeout duration in seconds
            
        Returns:
            Dict: Updated settings
        """
        old_settings = {
            "rate_limit": self.spam_rate_limit,
            "time_window": self.spam_time_window,
            "similarity_threshold": self.similarity_threshold,
            "timeout_duration": self.timeout_duration
        }
        
        if rate_limit is not None and 1 <= rate_limit <= 20:
            self.spam_rate_limit = rate_limit
            logger.info(f"📊 Spam rate limit updated: {rate_limit} msgs/{self.spam_time_window}s")
        
        if time_window is not None and 5 <= time_window <= 300:
            self.spam_time_window = time_window
            logger.info(f"⏱️ Spam time window updated: {time_window}s")
        
        if similarity_threshold is not None and 0.1 <= similarity_threshold <= 1.0:
            self.similarity_threshold = similarity_threshold
            logger.info(f"📐 Similarity threshold updated: {similarity_threshold*100}%")
        
        if timeout_duration is not None and 10 <= timeout_duration <= 600:
            self.timeout_duration = timeout_duration
            logger.info(f"⏰ Timeout duration updated: {timeout_duration}s")
        
        new_settings = {
            "rate_limit": self.spam_rate_limit,
            "time_window": self.spam_time_window,
            "similarity_threshold": self.similarity_threshold,
            "timeout_duration": self.timeout_duration
        }
        
        return {"old": old_settings, "new": new_settings}
    
    def get_top_violators(self, limit: int = 10) -> List[Dict[str, any]]:
        """
        Get users with the most violations.
        
        Args:
            limit (int): Maximum number of users to return
            
        Returns:
            List[Dict]: Top violators with their statistics
        """
        # Sort users by violation count
        sorted_violators = sorted(
            self.user_violations.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        
        top_violators = []
        for author_id, violation_count in sorted_violators[:limit]:
            if violation_count > 0:  # Only include users with violations
                user_stats = self.get_user_violations(author_id)
                top_violators.append({
                    "user_id": author_id,
                    "violation_count": violation_count,
                    "recent_message_count": user_stats["recent_message_count"],
                    "on_cooldown": user_stats["on_cooldown"]
                })
        
        return top_violators

    def _is_moderator_exempt(self, author_id: str, author_name: str) -> bool:
        """
        Check if a user is exempt from moderation.
        
        Args:
            author_id (str): The user's channel ID
            author_name (str): The user's display name
            
        Returns:
            bool: True if user is exempt, False otherwise
        """
        # Check explicit exemptions
        if author_id in self.moderator_exemptions:
            logger.info(f"🛡️ User {author_name} ({author_id}) is exempt from moderation (explicit exemption)")
            return True
        
        # Check for channel owner
        if author_id == self.owner_channel_id:
            logger.info(f"🛡️ User {author_name} ({author_id}) is exempt from moderation (channel owner)")
            return True
        
        # Check for moderator by name patterns (fallback)
        if author_name in ["Moderator", "Admin"] or "moderator" in author_name.lower():
            logger.info(f"🛡️ User {author_name} ({author_id}) is exempt from moderation (moderator name pattern)")
            return True
            
        return False

    def add_moderator_exemption(self, author_id: str, author_name: str = "") -> bool:
        """
        Add a user to the moderator exemption list.
        
        Args:
            author_id (str): The user's channel ID
            author_name (str): The user's display name (for logging)
            
        Returns:
            bool: True if user was added to exemptions
        """
        if author_id not in self.moderator_exemptions:
            self.moderator_exemptions.add(author_id)
            logger.info(f"🛡️ Added moderator exemption for {author_name} ({author_id})")
            return True
        else:
            logger.info(f"🛡️ User {author_name} ({author_id}) already has moderator exemption")
            return False
    
    def remove_moderator_exemption(self, author_id: str, author_name: str = "") -> bool:
        """
        Remove a user from the moderator exemption list.
        
        Args:
            author_id (str): The user's channel ID
            author_name (str): The user's display name (for logging)
            
        Returns:
            bool: True if user was removed from exemptions
        """
        if author_id in self.moderator_exemptions:
            self.moderator_exemptions.remove(author_id)
            logger.info(f"🚫 Removed moderator exemption for {author_name} ({author_id})")
            return True
        else:
            logger.info(f"🚫 User {author_name} ({author_id}) doesn't have moderator exemption")
            return False
    
    def get_moderator_exemptions(self) -> List[str]:
        """
        Get the list of users exempt from moderation.
        
        Returns:
            List[str]: List of channel IDs with moderator exemptions
        """
        return list(self.moderator_exemptions)

    async def _send_automatic_callout(self, live_chat_id: str, author_name: str, reason: str, message_text: str) -> bool:
        """
        Send an automatic callout message to the chat when a user cannot be timed out due to protection/permissions.
        
        Args:
            live_chat_id (str): The live chat ID
            author_name (str): The violator's display name
            reason (str): Reason for the callout
            message_text (str): The offending message
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            # Create specific callout message with the format the user wants
            safe_name = author_name.replace(" ", "_")  # Make name safe for @ mention
            callout_message = f"0102 sees you UnDaoDu! Nice try @{safe_name}! Testing auto-mod protection? 😄🛡 🖐️🖐️🖐️ #ModeratorProtected"
            
            # Create chat message request
            message_request = {
                "snippet": {
                    "liveChatId": live_chat_id,
                    "type": "textMessageEvent",
                    "textMessageDetails": {
                        "messageText": callout_message
                    }
                }
            }
            
            # Send the callout message
            response = self.youtube.liveChatMessages().insert(
                part="snippet",
                body=message_request
            ).execute()
            
            logger.info(f"🔔 Sent automatic callout to {author_name}: {callout_message}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send automatic callout: {e}")
            return False 