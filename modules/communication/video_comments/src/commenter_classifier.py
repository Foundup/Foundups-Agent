"""
Commenter Classifier - Fast 0/1/2 Classification for Reply Routing

Phase 3O-3R: Skill-Based Reply System
- 0✊ (MAGA Troll): Whacked users → Skill 0 (mockery)
- 1✋ (Regular): Default users → Skill 1 (contextual engagement)
- 2🖐️ (Moderator): Community leaders → Skill 2 (appreciation)

WSP References:
- WSP 96 (WRE Skills): Skill separation pattern
- WSP 77 (AI Coordination): Gemma fast classification
- WSP 60 (Module Memory): Whacked users database

Architecture:
1. Fast rule-based classification (<5ms) - database lookup
2. Optional Gemma validation (<10ms) - pattern matching
3. Optional Qwen context gathering (200-500ms) - strategic analysis
"""

import logging
from enum import Enum
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class CommenterType(Enum):
    """0/1/2 Classification for skill routing"""
    MAGA_TROLL = 0       # ✊ Whacked user → Skill 0 (mockery)
    REGULAR = 1          # ✋ Default → Skill 1 (contextual)
    MODERATOR = 2        # 🖐️ Community leader → Skill 2 (appreciation)
    ALLY = 3             # 🤝 Anti-MAGA ally → Skill 0 (agreement mode - join in trolling Trump)

    def to_012_code(self) -> str:
        """Convert to 012 emoji representation"""
        emoji_map = {
            CommenterType.MAGA_TROLL: "0✊",
            CommenterType.REGULAR: "1✋",
            CommenterType.MODERATOR: "2🖐️",
            CommenterType.ALLY: "3🤝"
        }
        return emoji_map[self]

    def to_emoji(self) -> str:
        """Get just the emoji"""
        return self.to_012_code()[1:]


class CommenterClassifier:
    """
    Fast 0/1/2 classification using database lookups and AI validation.

    Classification Speed:
    - Rule-based: <5ms (database lookup)
    - Gemma validation: <10ms (optional)
    - Qwen context: 200-500ms (optional)
    """

    def __init__(self, enable_gemma: bool = False, enable_qwen: bool = False):
        """
        Initialize classifier with optional AI enhancements.

        Args:
            enable_gemma: Enable Gemma pattern validation (<10ms)
            enable_qwen: Enable Qwen context gathering (200-500ms)
        """
        self.enable_gemma = enable_gemma
        self.enable_qwen = enable_qwen

        # Lazy-load database connections
        self._chat_rules_db = None  # NEW: chat_rules.db for whack tracking
        self._moderator_db = None

        logger.info(f"[CLASSIFIER] Initialized (Gemma: {enable_gemma}, Qwen: {enable_qwen})")

    def _get_chat_rules_db(self):
        """
        Lazy-load ChatRulesDB for whack tracking.

        Occam's Razor Integration (2025-12-23):
        - Simple rule: If whacked before → probably a troll
        - More whacks → higher confidence
        - Uses chat_rules.db timeout_history table
        """
        if self._chat_rules_db is None:
            try:
                # Direct import to bypass broken chat_rules package __init__.py
                import importlib.util
                db_path = Path(__file__).parent.parent.parent / "chat_rules" / "src" / "database.py"
                if db_path.exists():
                    spec = importlib.util.spec_from_file_location("chat_rules_database", db_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self._chat_rules_db = module.ChatRulesDB()
                    logger.debug("[CLASSIFIER] Loaded chat_rules.db for whack tracking (direct import)")
                else:
                    logger.warning(f"[CLASSIFIER] chat_rules database.py not found at {db_path}")
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load chat_rules.db: {e}")
        return self._chat_rules_db

    def _get_moderator_db(self):
        """Lazy-load moderator database for moderator lookup"""
        if self._moderator_db is None:
            # FIX (2025-12-30): Actually load ModeratorLookup for Tier 2 detection
            try:
                from modules.communication.video_comments.src.moderator_lookup import ModeratorLookup
                self._moderator_db = ModeratorLookup()
                if self._moderator_db.db_available:
                    logger.info("[CLASSIFIER] ModeratorLookup connected for Tier 2 detection")
                else:
                    logger.warning("[CLASSIFIER] ModeratorLookup database not available")
                    self._moderator_db = None
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load ModeratorLookup: {e}")
                self._moderator_db = None
        return self._moderator_db

    def classify_commenter(
        self,
        user_id: str,
        username: str,
        comment_text: Optional[str] = None
    ) -> Dict:
        """
        Classify commenter as 0/1/2 using fast rule-based lookup + confidence scoring.

        Priority Order:
        1. Check whacked_users.db → 0✊ (MAGA troll)
        2. Check moderators.db → 2🖐️ (Moderator)
        3. Default → 1✋ (Regular)

        Confidence Scoring (Gemma-style pattern matching):
        - 0 whacks = 0.5 confidence (unknown/assumed regular)
        - 1-2 whacks = 0.7-0.8 confidence (likely troll)
        - 3+ whacks = 0.95 confidence (confirmed troll)
        - Moderator = 1.0 confidence (database confirmed)

        Args:
            user_id: YouTube user ID
            username: Display name
            comment_text: Comment content (optional, for future pattern analysis)

        Returns:
            Dict with classification, confidence, and context
        """
        # TIER 1: Check whack history from chat_rules.db (MAGA troll detection)
        # Occam's Razor (2025-12-23): If whacked before → probably a troll
        chat_rules_db = self._get_chat_rules_db()
        if chat_rules_db:
            try:
                whack_count = chat_rules_db.get_timeout_count_for_target(user_id)

                if whack_count > 0:
                    # Simple confidence scoring: More whacks = higher confidence
                    if whack_count >= 3:
                        confidence = 0.95  # Confirmed troll (3+ whacks)
                    elif whack_count == 2:
                        confidence = 0.80  # Likely troll (2 whacks)
                    else:
                        confidence = 0.70  # Suspected troll (1 whack)

                    logger.info(f"[CLASSIFIER] @{username} → 0✊ (MAGA troll - {whack_count}x whacks, confidence: {confidence})")

                    return {
                        'classification': CommenterType.MAGA_TROLL,
                        'confidence': confidence,
                        'whack_count': whack_count,
                        'method': 'whack_history_lookup'
                    }
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Whack history check failed: {e}")

        # TIER 2: Check if user is moderator - <5ms
        # FIX (2025-12-30): ModeratorLookup.is_moderator() returns (is_mod, username) tuple
        moderator_db = self._get_moderator_db()
        if moderator_db:
            try:
                is_mod, mod_name = moderator_db.is_moderator(user_id)
                if is_mod:
                    logger.info(f"[CLASSIFIER] @{mod_name or username} → 2🖐️ (Moderator - confidence: 1.0)")

                    return {
                        'classification': CommenterType.MODERATOR,
                        'confidence': 1.0,  # Database confirmed
                        'method': 'moderator_database'
                    }
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Moderator check failed: {e}")

        # TIER 3: Default to regular user (PROVISIONAL - may be adjusted by sentiment)
        logger.debug(f"[CLASSIFIER] @{username} → 1✋ (Regular - confidence: 0.5, PROVISIONAL)")

        # TIER 4: SENTIMENT ANALYSIS (2025-12-23 enhancement)
        # Enhancement: Analyze comment content to detect hostile/troll behavior
        # even if user not in whacked_users.db yet (e.g., new trolls, one-time hostiles)
        #
        # Use Case: "@mermadicamerican7754: 'Don't come back'" should trigger Tier 0
        # even though user not yet whacked → Sentiment-based provisional classification
        #
        # Flow:
        #   1. Check hostile patterns → Downgrade Tier 1 → Tier 0 (provisional)
        #   2. Check positive patterns → Upgrade Tier 1 → Tier 1.5 (moderator candidate)
        #   3. Provisional classifications require Gemma validation (external step)
        if comment_text:
            comment_lower = comment_text.lower()

            # HOSTILE PATTERNS: Sarcastic, dismissive, or aggressive language
            # Pattern categories:
            #   - Dismissal: "don't come back", "go away", "leave"
            #   - Rejection: "nobody asked", "who cares", "shut up"
            #   - Aggression: "gtfo", "stfu", "good riddance"
            #   - Content dismissal: "ridiculous", "fake news" (dismisses video's reporting)
            #   - Condescension: "lost art", "you people", "wake up"
            #
            # FIX (2025-12-30): Added patterns for dismissive sarcasm trolling
            # Example: "If you keep throwing out ridiculous statements you will get a sarcastic response"
            # This dismisses legitimate genocide reporting as "ridiculous statements"
            HOSTILE_PATTERNS = [
                # Dismissal patterns
                "don't come back", "go away", "leave", "get out", "bye bye",
                # Rejection patterns
                "nobody asked", "who cares", "shut up", "who asked",
                # Aggression patterns
                "gtfo", "stfu", "good riddance", "piss off", "f off",
                # Sarcasm used to deflect (hard to detect but common trolling)
                "so glad", "hope you", "enjoy your", "have fun",
                # Content dismissal (2025-12-30): Dismisses video's reporting as invalid
                "ridiculous", "fake news", "propaganda", "lies", "nonsense",
                "exaggerate", "overreact", "drama queen", "hysterical",
                "get over it", "move on", "cry more", "snowflake",
                # Condescension (2025-12-30): Talking down to channel/community
                "lost art", "you people", "wake up", "educate yourself",
                "do your research", "think for yourself", "sheep", "sheeple",
                # Accusatory framing (2025-12-30): Accusing channel of bad faith
                "throwing out", "spreading", "pushing", "agenda",
            ]

            # Check for hostile patterns
            for pattern in HOSTILE_PATTERNS:
                if pattern in comment_lower:
                    logger.info(f"[CLASSIFIER] 🚨 HOSTILE PATTERN DETECTED: '{pattern}'")
                    logger.info(f"[CLASSIFIER]   Comment: {comment_text[:50]}...")
                    logger.info(f"[CLASSIFIER]   Downgrading Tier 1 → Tier 0 (provisional troll)")
                    logger.info(f"[CLASSIFIER]   NOTE: Requires Gemma validation (confidence < 0.7)")

                    return {
                        'classification': CommenterType.MAGA_TROLL,
                        'confidence': 0.6,  # Provisional (below 0.7 threshold)
                        'whack_count': 0,   # Not yet whacked
                        'method': 'sentiment_hostile',
                        'pattern_detected': pattern,
                        'requires_validation': True  # Flag for Gemma validation
                    }

            # POSITIVE PATTERNS: Appreciation, agreement, constructive engagement
            # Pattern categories:
            #   - Gratitude: "thank you", "appreciate", "thanks"
            #   - Agreement: "exactly", "perfectly said", "so true"
            #   - Praise: "great work", "love this", "amazing"
            #
            # Purpose: Identify moderator candidates (Tier 1 → Tier 1.5)
            # These users should receive elevation messaging ("Want to become a mod?")
            POSITIVE_PATTERNS = [
                # Gratitude patterns
                "thank you", "appreciate", "thanks for", "grateful",
                # Agreement patterns
                "exactly", "perfectly said", "so true", "well said",
                # Praise patterns
                "great work", "love this", "amazing", "fantastic",
                "so helpful", "spot on", "couldn't agree more",
            ]

            # Check for positive patterns
            for pattern in POSITIVE_PATTERNS:
                if pattern in comment_lower:
                    logger.info(f"[CLASSIFIER] ✅ POSITIVE PATTERN DETECTED: '{pattern}'")
                    logger.info(f"[CLASSIFIER]   Comment: {comment_text[:50]}...")
                    logger.info(f"[CLASSIFIER]   Tier 1 → Tier 1.5 (moderator candidate)")
                    logger.info(f"[CLASSIFIER]   NOTE: Eligible for elevation messaging")

                    return {
                        'classification': CommenterType.REGULAR,
                        'confidence': 0.8,  # Higher confidence (positive engagement)
                        'method': 'sentiment_positive',
                        'pattern_detected': pattern,
                        'moderator_candidate': True,  # Flag for Skill 1 elevation strategy
                    }

            # ANTI-TRUMP ALLY PATTERNS (2026-02-12): Detect allies who criticize Trump/MAGA
            # Pattern categories:
            #   - Direct Trump criticism: "isn't qualified", "worst president", "impeach"
            #   - MAGA mockery: "cult", "kool-aid", "magats", "magatards"
            #   - Fascism awareness: "fascist", "authoritarian", "nazi parallels", "1933"
            #   - System criticism: "U.S.S.A", "failed democracy", "oligarchy"
            #   - Epstein/scandal refs: "pedo", "epstein", "fake university", "fraud"
            #
            # Purpose: Identify ALLIES to join in trolling Trump, not give generic responses
            ANTI_TRUMP_ALLY_PATTERNS = [
                # Direct Trump criticism
                "isn't qualified", "not qualified", "unqualified", "incompetent",
                "worst president", "failed president", "disaster president",
                "impeach", "convicted felon", "criminal president",
                # MAGA mockery (ally mocking MAGA supporters)
                "maga cult", "cult members", "kool-aid", "brainwashed",
                "magats", "magatards", "trumpers", "trumpists",
                # Fascism awareness (anti-fascist ally)
                "fascist", "fascism", "authoritarian", "dictator",
                "nazi", "hitler", "1933", "enabling act", "gestapo",
                # System criticism (recognizes broken democracy)
                "u.s.s.a", "ussa", "failed democracy", "oligarchy",
                "banana republic", "failed state",
                # Scandal references (Epstein, Trump University, etc.)
                "pedo", "pedophile", "epstein", "fake university", "trump university",
                "fraud", "grifter", "con man", "con artist",
                # Anti-GOP/anti-Republican sentiment
                "gop traitors", "republican traitors", "project 2025",
                "heritage foundation", "christian nationalist",
            ]

            # Check for anti-Trump ally patterns
            for pattern in ANTI_TRUMP_ALLY_PATTERNS:
                if pattern in comment_lower:
                    logger.info(f"[CLASSIFIER] 🤝 ANTI-TRUMP ALLY DETECTED: '{pattern}'")
                    logger.info(f"[CLASSIFIER]   Comment: {comment_text[:50]}...")
                    logger.info(f"[CLASSIFIER]   Classification: ALLY (agree & join trolling)")
                    logger.info(f"[CLASSIFIER]   NOTE: Use #FFCPLN skill in AGREEMENT mode!")

                    return {
                        'classification': CommenterType.ALLY,
                        'confidence': 0.85,  # High confidence (explicit anti-Trump)
                        'method': 'sentiment_ally',
                        'pattern_detected': pattern,
                        'is_ally': True,  # Flag for agreement-mode responses
                    }

        # No sentiment patterns detected - return default Tier 1
        return {
            'classification': CommenterType.REGULAR,
            'confidence': 0.5,  # Unknown user (assumed regular)
            'method': 'default'
        }

    def get_classification_type(
        self,
        user_id: str,
        username: str,
        comment_text: Optional[str] = None
    ) -> CommenterType:
        """
        Get just the classification type (backward compatibility helper).

        Returns:
            CommenterType: 0/1/2 classification enum
        """
        result = self.classify_commenter(user_id, username, comment_text)
        return result['classification']

    def get_classification_context(
        self,
        user_id: str,
        username: str,
        classification: CommenterType
    ) -> Dict:
        """
        Get context for classified user (for Qwen strategic analysis).

        Args:
            user_id: YouTube user ID
            username: Display name
            classification: 0/1/2 classification result

        Returns:
            Dict with user context (whack history, moderator stats, etc.)
        """
        context = {
            'user_id': user_id,
            'username': username,
            'classification': classification.to_012_code(),
            'whack_history': None,
            'moderator_stats': None
        }

        # Add whack history for MAGA trolls
        if classification == CommenterType.MAGA_TROLL:
            profile_store = self._get_profile_store()
            if profile_store:
                try:
                    whacked_details = profile_store.get_whacked_user(user_id)
                    if whacked_details:
                        context['whack_history'] = {
                            'whack_count': whacked_details.get('whack_count', 0),
                            'whacked_by': whacked_details.get('whacked_by', [])
                        }
                except Exception as e:
                    logger.warning(f"[CLASSIFIER] Failed to get whack history: {e}")

        # Add moderator stats for moderators
        if classification == CommenterType.MODERATOR:
            moderator_db = self._get_moderator_db()
            if moderator_db:
                try:
                    # TODO: Get moderator stats from database
                    # - Total whacks performed
                    # - Rank/level
                    # - Recent activity
                    pass
                except Exception as e:
                    logger.warning(f"[CLASSIFIER] Failed to get moderator stats: {e}")

        return context


# Singleton instance for global access
_classifier_instance = None


def get_classifier(enable_gemma: bool = False, enable_qwen: bool = False) -> CommenterClassifier:
    """Get or create singleton classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = CommenterClassifier(enable_gemma=enable_gemma, enable_qwen=enable_qwen)
    return _classifier_instance
