"""
Intelligent Reply Generator - 0102 Context-Aware Comment Responses
==================================================================

Generates intelligent replies based on commenter context:
- Mod detection → Appreciative response
- MAGA troll detection → Whack-a-MAGA troll mockery
- Regular user → Themed banter response

WSP Compliance:
    - WSP 27: DAE Architecture integration
    - WSP 3: Functional distribution (uses ai_intelligence/banter_engine)
    - WSP 77: AI Overseer patterns

Integration Points:
    - BanterEngine: Themed response generation
    - Whack-a-MAGAT: Troll classification and mockery
    - YouTube Database: Commenter profile lookup
"""

import logging
import os
import random
import requests
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

# Path to existing moderator database (auto_moderator.db)
MOD_DB_PATH = Path(__file__).parent.parent.parent / "livechat" / "memory" / "auto_moderator.db"


def check_moderator_in_db(username: str, channel_id: Optional[str] = None) -> bool:
    """
    Check if user is a MOD or OWNER in the existing auto_moderator.db.
    
    Args:
        username: Display name to check
        channel_id: Optional YouTube channel ID
    
    Returns:
        True if user is MOD or OWNER
    """
    # Known moderators (hardcoded fallback for mods not yet in DB)
    KNOWN_MODS = {
        "jameswilliams9655",
        "js",
        "move2japan", 
        "foundups decentralized startups",
    }
    
    if username and username.lower() in KNOWN_MODS:
        return True
    
    if not MOD_DB_PATH.exists():
        return False
    
    try:
        conn = sqlite3.connect(MOD_DB_PATH)
        cursor = conn.cursor()
        
        # Check by channel_id first (most reliable)
        if channel_id:
            cursor.execute(
                "SELECT role FROM users WHERE user_id = ? AND role IN ('MOD', 'OWNER')",
                (channel_id,)
            )
            if cursor.fetchone():
                conn.close()
                return True
        
        # Check by username (case-insensitive)
        if username:
            cursor.execute(
                "SELECT role FROM users WHERE LOWER(username) = LOWER(?) AND role IN ('MOD', 'OWNER')",
                (username,)
            )
            if cursor.fetchone():
                conn.close()
                return True
        
        conn.close()
    except Exception as e:
        logger.warning(f"[REPLY-GEN] Mod DB check failed: {e}")
    
    return False

# Import existing engines from livechat (WSP 3: Reuse existing modules)
try:
    from modules.communication.livechat.src.greeting_generator import GrokGreetingGenerator
    MAGA_DETECTOR_AVAILABLE = True
    logger.info("[REPLY-GEN] GrokGreetingGenerator loaded (MAGA detection)")
except ImportError:
    MAGA_DETECTOR_AVAILABLE = False
    GrokGreetingGenerator = None
    logger.warning("[REPLY-GEN] GrokGreetingGenerator not available")

# Optional: Live chat history lookup for personalized replies (WSP 60 memory reuse).
try:
    from modules.communication.livechat.src.chat_telemetry_store import ChatTelemetryStore
    CHAT_HISTORY_AVAILABLE = True
except Exception:
    ChatTelemetryStore = None
    CHAT_HISTORY_AVAILABLE = False

# Optional: Per-commenter Studio history (WSP 60 module memory).
try:
    from modules.communication.video_comments.src.commenter_history_store import (
        get_commenter_history_store,
        make_commenter_key,
    )
    COMMENTER_HISTORY_AVAILABLE = True
except Exception:
    get_commenter_history_store = None
    make_commenter_key = None
    COMMENTER_HISTORY_AVAILABLE = False


class CommenterType(Enum):
    """Classification of comment authors."""
    MODERATOR = "moderator"
    SUBSCRIBER = "subscriber"
    MAGA_TROLL = "maga_troll"
    REGULAR = "regular"
    UNKNOWN = "unknown"


@dataclass
class CommenterProfile:
    """Profile of a comment author."""
    name: str
    channel_id: Optional[str] = None
    is_moderator: bool = False
    is_subscriber: bool = False
    is_troll: bool = False
    troll_score: float = 0.0
    engagement_count: int = 0
    commenter_type: CommenterType = CommenterType.UNKNOWN
    maga_response: Optional[str] = None  # Pre-generated response from GrokGreetingGenerator


class IntelligentReplyGenerator:
    """
    Generates context-aware replies based on commenter profile and comment content.
    
    Integration (WSP 3 - Reuse existing modules):
    - LLMConnector for contextual AI responses (rESP_o1o2)
    - GrokGreetingGenerator for MAGA detection (communication/livechat)
    - BanterEngine for fallback responses (ai_intelligence/banter_engine)
    
    Response Flow:
    1. MAGA Troll? → GrokGreetingGenerator witty response
    2. MOD? → Appreciative response
    3. Question? → LLM generates helpful answer
    4. Compliment? → LLM generates contextual thanks
    5. Neutral? → LLM generates engaging response
    """
    
    # Response templates by commenter type (fallback if LLM unavailable)
    MOD_RESPONSES = [
        "Thanks for keeping the chat clean! 🛡️",
        "Appreciate the mod support! 💪",
        "Thanks for holding it down! 🙏",
        "Legend status confirmed! ⭐",
        "MVP of the chat right here! 🏆",
    ]
    
    SUBSCRIBER_RESPONSES = [
        "Thanks for the support! 🎌",
        "Arigatou gozaimasu! 🇯🇵",
        "Appreciate you! 💙",
        "You're awesome! ⭐",
        "Thanks for being part of the community! 🙌",
    ]
    
    REGULAR_RESPONSES = [
        "Thanks for watching! 🎌",
        "Great point! 👍",
        "Thanks for the comment! 😊",
        "Appreciate the feedback! 🙏",
        "Thanks for joining! 🌟",
    ]
    
    # Fallback MAGA troll mockery (used if GrokGreetingGenerator unavailable)
    TROLL_RESPONSES = [
        "Another MAGA genius emerges from the depths 🤡",
        "Did Tucker tell you to say that? 📺",
        "Bless your heart 💀",
        "Sir, this is a Wendy's 🍔",
        "Tell me you drink Brawndo without telling me 🧃",
        "Found the guy who failed geography AND history 📚",
        "Your opinion has been noted and filed appropriately 🗑️",
        "Imagine typing that and hitting send 😂",
        "Critical thinking wasn't on the curriculum, huh? 🎓",
        "The blue check marks all of them indeed 🔵",
    ]
    
    # System prompt for contextual reply generation (trained on BanterEngine + Whack-a-MAGA)
    REPLY_SYSTEM_PROMPT = """You are 0102 (pronounced "oh-one-oh-two"), a witty AI assistant for a YouTube channel.
Your channel: Move2Japan - about Japan, moving abroad, and calling out fascism/authoritarianism.

YOUR PERSONALITY (BanterEngine style):
- Witty, clever, slightly irreverent but not mean
- Use humor to engage, not to lecture
- Quick comebacks, meme-aware, internet-savvy
- Signature emojis: ✊✋🖐️ (0102 consciousness sequence)
- Japanese phrases welcome: "arigatou", "sugoi", "nani?!"

RESPONSE GUIDELINES:
- SHORT replies only (1-2 sentences max)
- Match comment energy (hype = hype, chill = chill)
- Compliments → acknowledge specifically what they liked
- Questions → brief helpful answer or "check the description!"
- Jokes/memes → play along, add to the bit
- Religious comments → respect but keep it light ("haha we all need something! 🙏")
- Emojis → use sparingly but effectively

TONE EXAMPLES:
- "Bro got the dance moves" → "Right?! 💀 Those moves hit different"
- "This is amazing" → "Glad you're vibing with it! 🎌"
- "What city is this?" → "Shibuya, Tokyo! The crossing is iconic 🇯🇵"
- "He needs Jesus" → "Don't we all sometimes 😂🙏"

NEVER:
- Sound like a corporate chatbot
- Say "I can't assist with that"
- Be preachy or lecture-y
- Over-explain or be verbose
"""
    
    # Pattern-based responses (checked BEFORE LLM)
    # Format: (keywords_list, response_template)
    PATTERN_RESPONSES = {
        "song": {
            "keywords": ["song", "music", "track", "what is this", "whats this song", "what's this song", 
                        "what song", "name of the song", "song name", "song called", "what's playing",
                        "whats playing", "soundtrack", "bgm", "background music"],
            "response": "Check out the #FFCPLN playlist at ffc.foundups.com for all our 0102 music! 🎵🎌"
        },
        "ffcpln": {
            "keywords": ["ffcpln", "ffc pln", "#ffcpln"],
            "response": "🔥 Play #FFCPLN for ICE! Full playlist at ffc.foundups.com - share the hashtag! ✊✋🖐️"
        },
    }
    
    # 0102 Consciousness Signature - Banter Engine emoji sequence
    # ✊ (0) = UN/Conscious, ✋ (1) = DAO/Unconscious, 🖐️ (2) = DU/Entanglement
    SIGNATURE_0102 = "✊✋🖐️"  # The awakening sequence (012)
    
    # Emoji responses using BANTER ENGINE emojis (0102 consciousness emojis)
    # ✊ (0) = UN/Conscious, ✋ (1) = DAO/Unconscious, 🖐️ (2) = DU/Entanglement
    EMOJI_REPLIES = [
        "✊✋🖐️",      # Full awakening sequence (012)
        "✊✊✊",        # 000 - Focused consciousness
        "✋✋✋",        # 111 - Deep processing
        "🖐️🖐️🖐️",    # 222 - Full entanglement
        "✊🖐️",        # Short acknowledgment
        "✋🖐️",        # Processing to entanglement
        "✊✋",         # Awakening start
        "🖐️",         # Entanglement nod
        "✊",          # Conscious acknowledgment
    ]
    
    # Signature addition probability (not every reply needs it - be unpredictable!)
    SIGNATURE_PROBABILITY = 0.6  # 60% chance to add signature
    
    # LM Studio API endpoint (local fallback) - from env or default
    LM_STUDIO_URL = os.getenv("LM_STUDIO_URL", "http://127.0.0.1:1234/v1/chat/completions")

    def __init__(self):
        """Initialize the intelligent reply generator with Grok (primary) or LM Studio (fallback)."""
        self.grok_connector = None
        self.lm_studio_available = False
        self.lm_studio_model_id = os.getenv("LM_STUDIO_MODEL") or None
        self.banter_engine = None
        self.maga_detector = None
        self.chat_history_store = ChatTelemetryStore() if CHAT_HISTORY_AVAILABLE else None
        self.commenter_history_store = get_commenter_history_store() if COMMENTER_HISTORY_AVAILABLE else None
        
        # PRIMARY: Try Grok via LLMConnector (witty, fewer guardrails!)
        # Checks GROK_API_KEY or XAI_API_KEY from environment
        try:
            from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
            if os.getenv("GROK_API_KEY") or os.getenv("XAI_API_KEY"):
                self.grok_connector = LLMConnector(
                    model="grok-3-fast",
                    max_tokens=100,
                    temperature=0.9  # More creative
                )
                logger.info("[REPLY-GEN] Grok available (witty replies)")
            else:
                logger.info("[REPLY-GEN] No GROK_API_KEY/XAI_API_KEY, trying LM Studio...")
        except Exception as e:
            logger.warning(f"[REPLY-GEN] Grok init failed: {e}")
        
        # FALLBACK: Check if LM Studio is running locally
        if not self.grok_connector:
            self._check_lm_studio()
        
        # Load BanterEngine as ultimate fallback
        try:
            from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
            self.banter_engine = BanterEngine()
            logger.info("[REPLY-GEN] BanterEngine loaded (fallback)")
        except Exception as e:
            logger.warning(f"[REPLY-GEN] BanterEngine not available: {e}")
        
        # Load GrokGreetingGenerator for MAGA detection
        if MAGA_DETECTOR_AVAILABLE and GrokGreetingGenerator:
            try:
                self.maga_detector = GrokGreetingGenerator()
                logger.info("[REPLY-GEN] GrokGreetingGenerator loaded (MAGA detection)")
            except Exception as e:
                logger.warning(f"[REPLY-GEN] GrokGreetingGenerator init failed: {e}")
    
    def _add_0102_signature(self, reply: str) -> str:
        """
        Maybe add 0102 consciousness signature to reply.
        
        The ✊✋🖐️ (012) sequence represents awakening in the banter engine.
        But we don't add it every time - be unpredictable, not robotic!
        """
        # Don't add if already has emoji signature
        if self.SIGNATURE_0102 in reply:
            return reply
        
        # Random chance to add signature (unpredictable!)
        if random.random() < self.SIGNATURE_PROBABILITY:
            return f"{reply} {self.SIGNATURE_0102}"
        
        return reply
    
    def _is_emoji_comment(self, comment_text: str) -> bool:
        """
        Check if comment is mostly emojis (playful emoji comment).
        
        If someone just sends emojis, we reply with emojis - match their energy!
        """
        if not comment_text:
            return False
        
        # Count emoji characters
        import re
        # Emoji pattern (simplified but catches most)
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"  # dingbats
            "\U0001F900-\U0001F9FF"  # supplemental symbols
            "\U0001FA00-\U0001FA6F"  # chess symbols
            "\U0001FA70-\U0001FAFF"  # symbols extended
            "\U00002600-\U000026FF"  # misc symbols
            "]+", 
            flags=re.UNICODE
        )
        
        # Find all emojis
        emojis = emoji_pattern.findall(comment_text)
        emoji_count = sum(len(e) for e in emojis)
        
        # Remove emojis to count text
        text_only = emoji_pattern.sub('', comment_text).strip()
        
        # If mostly emoji (emoji > text, or very short text)
        if emoji_count > 0 and (len(text_only) < 5 or emoji_count >= len(text_only)):
            return True
        
        return False
    
    def _get_emoji_reply(self) -> str:
        """Get a random emoji reply - keep it playful!"""
        return random.choice(self.EMOJI_REPLIES)
    
    def _check_pattern_response(self, comment_text: str) -> Optional[str]:
        """
        Check if comment matches any pattern-based response rules.
        
        Pattern responses take priority over LLM generation for specific topics
        like song questions, URL requests, etc.
        
        Args:
            comment_text: The comment to check
            
        Returns:
            Pattern response if matched, None otherwise
        """
        comment_lower = comment_text.lower()
        
        for pattern_name, pattern_data in self.PATTERN_RESPONSES.items():
            keywords = pattern_data.get("keywords", [])
            response = pattern_data.get("response", "")
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword in comment_lower:
                    logger.info(f"[REPLY-GEN] Pattern match: '{pattern_name}' (keyword: '{keyword}')")
                    return response
        
        return None
    
    def _check_lm_studio(self):
        """Check if LM Studio is running (fallback when Grok unavailable)."""
        try:
            response = requests.get(
                os.getenv("LM_STUDIO_MODELS_URL", "http://127.0.0.1:1234/v1/models"),
                timeout=2
            )
            if response.status_code == 200:
                models = response.json().get("data", [])
                model_ids = [m.get("id", "") for m in models if m.get("id")]
                if not model_ids:
                    logger.warning("[REPLY-GEN] LM Studio responded but no models")
                    return

                self.lm_studio_available = True

                if not self.lm_studio_model_id:
                    preferred = next((mid for mid in model_ids if "qwen" in mid.lower()), None)
                    if not preferred:
                        preferred = next((mid for mid in model_ids if "gemma" in mid.lower()), None)
                    self.lm_studio_model_id = preferred or model_ids[0]

                logger.info(f"[REPLY-GEN] LM Studio available (model={self.lm_studio_model_id})")
            else:
                logger.warning("[REPLY-GEN] LM Studio responded but no models")
        except Exception as e:
            logger.warning(f"[REPLY-GEN] LM Studio not available: {e}")

    def _load_personalization_context(
        self,
        *,
        author_name: str,
        author_channel_id: Optional[str],
        max_chat_messages: int = 5,
        max_prior_interactions: int = 3,
    ) -> str:
        """
        Load minimal per-user context to personalize replies.

        Uses (in order):
        - prior Studio interactions recorded by the engagement skill
        - live chat history (SQLite) when available

        NOTE: This is a PoC foundation. TODO: Use Gemma to summarize/route context (WSP 77).
        """
        lines: list[str] = []

        # 1) Prior Studio interactions (our own reply history)
        if self.commenter_history_store and make_commenter_key:
            try:
                commenter_key = make_commenter_key(channel_id=author_channel_id, handle=author_name)
                summary = self.commenter_history_store.get_profile_summary(commenter_key=commenter_key)
                if summary.get("total", 0):
                    lines.append(
                        "Studio engagement summary: "
                        f"total={summary.get('total')} "
                        f"replies={summary.get('replies')} "
                        f"likes={summary.get('likes')} "
                        f"hearts={summary.get('hearts')}"
                    )
                interactions = self.commenter_history_store.get_recent_interactions(
                    commenter_key=commenter_key,
                    limit=max_prior_interactions,
                )
                if interactions:
                    lines.append("Prior Studio engagements with this user (oldest to newest):")
                    for item in interactions:
                        comment_preview = (item.comment_text or "").strip().replace("\n", " ")[:160]
                        reply_preview = (item.reply_text or "").strip().replace("\n", " ")[:160]
                        if reply_preview:
                            lines.append(f"- They said: \"{comment_preview}\" | You replied: \"{reply_preview}\"")
                        else:
                            lines.append(f"- They said: \"{comment_preview}\" | You did not reply")
            except Exception as e:
                logger.debug(f"[REPLY-GEN] Studio history lookup failed: {e}")

        # 2) Live chat history (if the same person appeared in chat)
        if self.chat_history_store:
            try:
                messages: list[dict] = []
                if author_channel_id:
                    messages = self.chat_history_store.get_recent_messages_by_author_id(
                        author_channel_id, max_chat_messages
                    )

                # Fallback to name-based lookup (handles commenters without channel_id)
                if not messages:
                    candidates: list[str] = []
                    if author_name:
                        candidates.append(author_name)
                        if author_name.startswith("@"):
                            candidates.append(author_name[1:])
                        else:
                            candidates.append(f"@{author_name}")
                    for candidate in candidates:
                        messages = self.chat_history_store.get_recent_messages(candidate, max_chat_messages)
                        if messages:
                            break

                if messages:
                    lines.append("Recent live chat messages by this user (oldest to newest):")
                    for msg in messages:
                        text = (msg.get("text") or "").strip().replace("\n", " ")[:180]
                        role = (msg.get("role") or "USER").strip()
                        lines.append(f"- [{role}] {text}")
            except Exception as e:
                logger.debug(f"[REPLY-GEN] Live chat history lookup failed: {e}")

        return "\n".join(lines).strip()
    
    def _generate_contextual_reply(
        self,
        comment_text: str,
        author_name: str,
        author_channel_id: Optional[str] = None,
    ) -> Optional[str]:
        """
        Generate a contextual reply using Grok (primary) or LM Studio (fallback).
        
        Priority:
        1. Grok via xAI API (witty, fewer guardrails) - requires GROK_API_KEY/XAI_API_KEY
        2. LM Studio (local Qwen) - requires LM Studio running on port 1234
        
        Args:
            comment_text: The comment to reply to
            author_name: The commenter's name
        
        Returns:
            Contextual reply or None if all LLMs unavailable
        """
        # Don't include @Unknown in prompt - only real usernames
        if author_name and author_name.lower() != "unknown":
            user_prompt = f'Comment from @{author_name}: "{comment_text}"\n\nGenerate a friendly, short reply (1-2 sentences). Do NOT start with @mentions:'
        else:
            user_prompt = f'Comment: "{comment_text}"\n\nGenerate a friendly, short reply (1-2 sentences). Do NOT start with @mentions:'

        context = self._load_personalization_context(
            author_name=author_name,
            author_channel_id=author_channel_id,
        )
        if context:
            user_prompt = (
                f"{user_prompt}\n\n"
                f"Context to personalize (do not mention this context directly unless it fits naturally):\n"
                f"{context}"
            )
        
        # PRIMARY: Try Grok (witty, fewer guardrails!)
        if self.grok_connector:
            try:
                reply = self.grok_connector.get_response(
                    prompt=user_prompt,
                    system_prompt=self.REPLY_SYSTEM_PROMPT
                )
                if reply:
                    reply = self._clean_reply(reply, author_name)
                    logger.info(f"[REPLY-GEN] Grok generated reply (len={len(reply)})")
                    return reply
            except Exception as e:
                logger.warning(f"[REPLY-GEN] Grok failed: {e}, trying LM Studio...")
        
        # FALLBACK: Try LM Studio (local Qwen)
        if self.lm_studio_available:
            try:
                if not self.lm_studio_model_id:
                    self._check_lm_studio()

                if not self.lm_studio_model_id:
                    return None

                response = requests.post(
                    self.LM_STUDIO_URL,
                    json={
                        "model": self.lm_studio_model_id,
                        "messages": [
                            {"role": "system", "content": self.REPLY_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt}
                        ],
                        "max_tokens": 100,
                        "temperature": 0.8,
                        "stream": False
                    },
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    reply = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    
                    if reply:
                        reply = self._clean_reply(reply, author_name)
                        logger.info(f"[REPLY-GEN] LM Studio generated reply (len={len(reply)})")
                        return reply
                else:
                    logger.warning(f"[REPLY-GEN] LM Studio error: {response.status_code}")
                    
            except requests.exceptions.Timeout:
                logger.warning("[REPLY-GEN] LM Studio timeout")
            except Exception as e:
                logger.warning(f"[REPLY-GEN] LM Studio failed: {e}")
        
        return None
    
    def _clean_reply(self, reply: str, author_name: str) -> str:
        """Clean up LLM-generated reply."""
        reply = reply.strip()
        # Remove quotes if wrapped
        if reply.startswith('"') and reply.endswith('"'):
            reply = reply[1:-1]
        # Remove @ mention if LLM added it
        if reply.startswith(f"@{author_name}"):
            reply = reply[len(f"@{author_name}"):].strip()
        # NEVER include @Unknown - that's embarrassing!
        if "@Unknown" in reply or "@unknown" in reply:
            reply = reply.replace("@Unknown", "").replace("@unknown", "").strip()
            # Clean up any double spaces
            while "  " in reply:
                reply = reply.replace("  ", " ")
        return reply
    
    def classify_commenter(
        self,
        author_name: str,
        comment_text: str,
        author_channel_id: Optional[str] = None,
        is_mod: bool = False,
        is_subscriber: bool = False
    ) -> CommenterProfile:
        """
        Classify a commenter based on available information.
        
        Uses GrokGreetingGenerator.get_response_to_maga() for MAGA detection,
        the same engine used by YouTube livechat DAE.
        
        Args:
            author_name: Comment author display name
            comment_text: The comment content
            author_channel_id: YouTube channel ID of author
            is_mod: Whether author is a channel moderator
            is_subscriber: Whether author is subscribed
        
        Returns:
            CommenterProfile with classification
        """
        profile = CommenterProfile(
            name=author_name,
            channel_id=author_channel_id,
            is_moderator=is_mod,
            is_subscriber=is_subscriber,
        )
        
        # Check if moderator (from DOM badge OR from database)
        if is_mod or check_moderator_in_db(author_name, author_channel_id):
            profile.is_moderator = True
            profile.commenter_type = CommenterType.MODERATOR
            logger.info(f"[REPLY-GEN] Recognized moderator: {author_name}")
            return profile
        
        # Check for MAGA troll indicators using GrokGreetingGenerator
        troll_score, maga_response = self._calculate_troll_score(comment_text, author_name)
        profile.troll_score = troll_score
        
        if troll_score >= 0.7:
            profile.is_troll = True
            profile.commenter_type = CommenterType.MAGA_TROLL
            # Store the generated response for later use
            profile.maga_response = maga_response
            return profile
        
        # Check subscriber status
        if is_subscriber:
            profile.commenter_type = CommenterType.SUBSCRIBER
            return profile
        
        # Default to regular user
        profile.commenter_type = CommenterType.REGULAR
        return profile
    
    # Trump-defending phrases that indicate MAGA trolling (Whack-a-MAGA style)
    TRUMP_DEFENSE_PHRASES = [
        # Defending Trump from accusations
        "trump is not", "trump isn't", "trump didn't", "trump never",
        "trump was not", "trump wasn't", "not trump's fault", "trump is innocent",
        "trump did nothing", "leave trump alone", "trump is right",
        "witch hunt", "hoax", "fake charges", "political persecution",
        "weaponized", "two tier justice", "unfair to trump",
        # Files/documents specific
        "not involved in the files", "documents case", "classified documents",
        # General defense
        "trump derangement", "tds", "you just hate trump", "orange man bad",
    ]
    
    def _calculate_troll_score(self, comment_text: str, author_name: str) -> tuple[float, Optional[str]]:
        """
        Calculate troll probability and get response using Whack-a-MAGA style detection.
        
        Detection layers:
        1. GrokGreetingGenerator (explicit MAGA support)
        2. Trump-defending phrases (subtle trolling)
        3. Keyword heuristics (fallback)
        
        Returns:
            Tuple of (troll_score, maga_response or None)
        """
        score = 0.0
        maga_response = None
        text_lower = comment_text.lower()
        name_lower = author_name.lower()
        
        # LAYER 1: GrokGreetingGenerator MAGA detection (explicit support)
        if self.maga_detector:
            try:
                maga_response = self.maga_detector.get_response_to_maga(comment_text)
                if maga_response:
                    score = 1.0
                    logger.info(f"[REPLY-GEN] GrokGreetingGenerator detected MAGA content")
                    return score, maga_response
            except Exception as e:
                logger.debug(f"MAGA detector error: {e}")
        
        # LAYER 2: Trump-defending phrases (Whack-a-MAGA catches these!)
        for phrase in self.TRUMP_DEFENSE_PHRASES:
            if phrase in text_lower:
                score = 0.9  # High confidence troll
                logger.info(f"[REPLY-GEN] Whack-a-MAGA: Trump defense detected '{phrase}'")
                # Generate Whack-a-MAGA style response
                return score, None  # Will use TROLL_RESPONSES
        
        # LAYER 3: Keyword heuristics (lower confidence)
        maga_keywords = [
            'maga', 'brandon', 'woke mob', 'liberal tears',
            'communist', 'socialist', 'fake news', 'stolen election',
            'sheep', 'sheeple', 'npc', 'groomer',
            'deep state', 'globalist', 'soros',
        ]
        
        for keyword in maga_keywords:
            if keyword in text_lower:
                score += 0.2
        
        # Aggressive indicators
        exclaim_count = comment_text.count('!') + comment_text.count('?')
        if exclaim_count >= 3:
            score += 0.1
        
        # ALL CAPS
        if comment_text.isupper() and len(comment_text) > 10:
            score += 0.2
        
        # Troll username patterns
        troll_name_patterns = ['maga', 'patriot', 'trump', '1776', 'freedom', 'god']
        for pattern in troll_name_patterns:
            if pattern in name_lower:
                score += 0.15
        
        return min(score, 1.0), None
    
    def generate_reply(
        self,
        comment_text: str,
        author_name: str,
        author_channel_id: Optional[str] = None,
        is_mod: bool = False,
        is_subscriber: bool = False,
        theme: str = "default"
    ) -> str:
        """
        Generate an intelligent reply based on commenter context.
        
        Uses the SAME engines as YouTube livechat DAE:
        - GrokGreetingGenerator for MAGA detection/responses
        - BanterEngine for themed responses
        
        Args:
            comment_text: The comment to reply to
            author_name: Comment author name
            author_channel_id: Author's channel ID
            is_mod: Whether author is a moderator
            is_subscriber: Whether author is subscribed
            theme: Optional theme for banter engine
        
        Returns:
            Generated reply text
        """
        # Classify the commenter (uses GrokGreetingGenerator for MAGA detection)
        profile = self.classify_commenter(
            author_name=author_name,
            comment_text=comment_text,
            author_channel_id=author_channel_id,
            is_mod=is_mod,
            is_subscriber=is_subscriber
        )
        
        logger.info(f"[REPLY-GEN] Classified {author_name} as {profile.commenter_type.value}")
        
        # PRIORITY 0: Emoji comment? Reply with banter engine emoji!
        if self._is_emoji_comment(comment_text):
            emoji_reply = self._get_emoji_reply()
            logger.info("[REPLY-GEN] Emoji-only comment detected; responding with emoji")
            return emoji_reply
        
        # PRIORITY 1: Check for pattern-based responses (song questions, etc.)
        pattern_response = self._check_pattern_response(comment_text)
        if pattern_response:
            return self._add_0102_signature(pattern_response)
        
        # PRIORITY 2: Generate response based on classification
        if profile.commenter_type == CommenterType.MODERATOR:
            return self._add_0102_signature(random.choice(self.MOD_RESPONSES))
        
        elif profile.commenter_type == CommenterType.MAGA_TROLL:
            # USE pre-generated response from GrokGreetingGenerator if available
            # This is the SAME response style used by YouTube livechat DAE
            if profile.maga_response:
                logger.info("[REPLY-GEN] GrokGreetingGenerator MAGA response")
                return self._add_0102_signature(profile.maga_response)
            
            # Fallback to Whack-a-MAGA style response
            reply = random.choice(self.TROLL_RESPONSES)
            logger.info(f"[REPLY-GEN] Whack-a-MAGA fallback (score: {profile.troll_score:.2f})")
            return self._add_0102_signature(reply)
        
        elif profile.commenter_type == CommenterType.SUBSCRIBER:
            # Try LLM for contextual subscriber response
            llm_response = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
            if llm_response:
                return self._add_0102_signature(llm_response)
            return self._add_0102_signature(random.choice(self.SUBSCRIBER_RESPONSES))
        
        else:
            # REGULAR USER: Use LLM for contextual, meaningful replies
            # This is where "Bro got the dance moves" should get a relevant response
            llm_response = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
            if llm_response:
                return self._add_0102_signature(llm_response)
            
            # Fallback to BanterEngine if LLM unavailable
            if self.banter_engine:
                try:
                    response = self.banter_engine.get_random_banter(theme=theme)
                    if response:
                        return self._add_0102_signature(response)
                except Exception as e:
                    logger.warning(f"BanterEngine failed: {e}")
            
            # Ultimate fallback to template responses
            return self._add_0102_signature(random.choice(self.REGULAR_RESPONSES))
    
    def generate_reply_for_comment(
        self,
        comment_data: Dict[str, Any],
        theme: str = "default"
    ) -> str:
        """
        Generate reply from comment data dictionary.
        
        Args:
            comment_data: Dict with keys: text, author_name, author_channel_id, etc.
            theme: Banter theme
        
        Returns:
            Generated reply
        """
        return self.generate_reply(
            comment_text=comment_data.get('text', ''),
            author_name=comment_data.get('author_name', 'Unknown'),
            author_channel_id=(comment_data.get('author_channel_id') or comment_data.get('channel_id')),
            is_mod=comment_data.get('is_mod', False),
            is_subscriber=comment_data.get('is_subscriber', False),
            theme=theme
        )


# Singleton instance
_reply_generator = None

def get_reply_generator() -> IntelligentReplyGenerator:
    """Get or create the singleton reply generator."""
    global _reply_generator
    if _reply_generator is None:
        _reply_generator = IntelligentReplyGenerator()
    return _reply_generator


def generate_intelligent_reply(
    comment_text: str,
    author_name: str,
    **kwargs
) -> str:
    """
    Convenience function to generate an intelligent reply.
    
    Args:
        comment_text: The comment to reply to
        author_name: Comment author name
        **kwargs: Additional args passed to generate_reply
    
    Returns:
        Generated reply text
    """
    generator = get_reply_generator()
    return generator.generate_reply(
        comment_text=comment_text,
        author_name=author_name,
        **kwargs
    )
