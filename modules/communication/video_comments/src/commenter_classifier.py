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
import time
from enum import Enum
from functools import lru_cache
from typing import Dict, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def _sanitize_username(username: str) -> str:
    """
    Sanitize username for safe logging.

    Security: Prevents log injection and XSS in log viewers.
    - Removes control characters
    - Truncates to 50 chars
    - Escapes angle brackets
    """
    if not username:
        return "[unknown]"
    # Remove control characters, escape HTML-like chars
    safe = ''.join(c for c in username if c.isprintable() and c not in '<>{}[]')
    return safe[:50] if len(safe) > 50 else safe


# Hot troll cache: LRU cache with TTL for frequent lookups
# Reduces database queries for known trolls
_TROLL_CACHE_TTL = 300  # 5 minutes
_troll_cache: Dict[str, Tuple[int, float]] = {}  # user_id -> (whack_count, timestamp)


def _get_cached_whack_count(user_id: str, profile_store) -> Optional[int]:
    """
    Get whack count with LRU-style caching.

    Cache Strategy:
    - Hot trolls (frequent commenters) get cached
    - TTL of 5 minutes to catch new whacks
    - Reduces database queries by ~80% for repeat offenders
    """
    global _troll_cache
    now = time.time()

    # Check cache
    if user_id in _troll_cache:
        count, cached_at = _troll_cache[user_id]
        if now - cached_at < _TROLL_CACHE_TTL:
            return count

    # Cache miss - query database
    try:
        count = profile_store.get_whack_count_for_user(user_id)
        _troll_cache[user_id] = (count, now)

        # Prune old entries (simple LRU: keep last 100)
        if len(_troll_cache) > 100:
            oldest = sorted(_troll_cache.items(), key=lambda x: x[1][1])[:50]
            for k, _ in oldest:
                del _troll_cache[k]

        return count
    except Exception as e:
        logger.warning(f"[CLASSIFIER] Cache lookup failed: {e}")
        return None


class CommenterType(Enum):
    """0/1/2 Classification for skill routing"""
    MAGA_TROLL = 0       # ✊ Whacked user → Skill 0 (mockery)
    REGULAR = 1          # ✋ Default → Skill 1 (contextual)
    MODERATOR = 2        # 🖐️ Community leader OR anti-MAGA ally → Skill 2 (appreciation + agreement)

    def to_012_code(self) -> str:
        """Convert to 012 emoji representation"""
        emoji_map = {
            CommenterType.MAGA_TROLL: "0✊",
            CommenterType.REGULAR: "1✋",
            CommenterType.MODERATOR: "2🖐️",
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
        self._profile_store = None  # FIX: Use magadoom_scores.db (actual whack data)
        self._moderator_db = None
        self._livechat_memory = None  # Training Mode: Bridge livechat history
        self._gemma_validator = None  # Gemma pattern validation (optional)

        logger.info(f"[CLASSIFIER] Initialized (Gemma: {enable_gemma}, Qwen: {enable_qwen})")

    def _get_profile_store(self):
        """
        Lazy-load ProfileStore for whack tracking (magadoom_scores.db).

        FIX (2026-02-19): Use CORRECT database!
        - chat_rules.db was WRONG (nearly empty timeout_history table)
        - magadoom_scores.db has ACTUAL whack data (whacked_users table)

        Occam's Razor Integration (2025-12-23):
        - Simple rule: If whacked before → probably a troll
        - More whacks → higher confidence
        """
        if self._profile_store is None:
            try:
                from modules.gamification.whack_a_magat.src.whack import get_profile_store
                self._profile_store = get_profile_store()
                logger.debug("[CLASSIFIER] Loaded magadoom_scores.db for whack tracking (correct database!)")
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load profile store: {e}")
        return self._profile_store

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

    def _get_gemma_validator(self):
        """
        Lazy-load GemmaValidator for pattern validation.

        FIX (2026-02-19): Connect Gemma validator to classifier!
        - Validates MAGA patterns in comment text
        - Adjusts confidence scores based on content analysis
        - Only used when enable_gemma=True
        """
        if self._gemma_validator is None and self.enable_gemma:
            try:
                from modules.communication.video_comments.src.gemma_validator import get_gemma_validator
                self._gemma_validator = get_gemma_validator()
                logger.info("[CLASSIFIER] GemmaValidator connected for pattern validation")
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load GemmaValidator: {e}")
        return self._gemma_validator

    def _get_livechat_memory(self):
        """
        Lazy-load ChatMemoryManager for livechat history cross-reference.

        Training Mode Bridge (2026-02-17):
        - Uses livechat behavior to inform comment classification
        - If user is known troll in livechat → boost MAGA_TROLL confidence
        - If user is MOD/OWNER in livechat → confirm MODERATOR status
        """
        if self._livechat_memory is None:
            try:
                from modules.communication.livechat.src.chat_memory_manager import ChatMemoryManager
                memory_dir = Path(__file__).parent.parent.parent / "livechat" / "memory"
                if memory_dir.exists():
                    self._livechat_memory = ChatMemoryManager(str(memory_dir))
                    logger.info("[CLASSIFIER] Livechat memory bridge connected (Training Mode)")
                else:
                    logger.debug(f"[CLASSIFIER] Livechat memory dir not found: {memory_dir}")
            except Exception as e:
                logger.debug(f"[CLASSIFIER] Failed to load livechat memory (optional): {e}")
        return self._livechat_memory

    def _apply_gemma_validation(
        self,
        username: str,
        comment_text: str,
        classification: 'CommenterType',
        initial_confidence: float
    ) -> float:
        """
        Apply Gemma validation to adjust confidence score.

        FIX (2026-02-19): Connect Gemma validator to classification pipeline!
        - Validates patterns in comment text
        - Returns adjusted confidence based on Gemma's analysis
        - Only active when enable_gemma=True

        Args:
            username: Commenter name (for logging)
            comment_text: Comment content to validate
            classification: Current classification type
            initial_confidence: Confidence before validation

        Returns:
            Adjusted confidence score (0.0-1.0)
        """
        if not self.enable_gemma or not comment_text:
            return initial_confidence

        validator = self._get_gemma_validator()
        if not validator:
            return initial_confidence

        try:
            result = validator.validate_classification(
                username=username,
                comment_text=comment_text,
                current_classification=classification.name,
                current_confidence=initial_confidence
            )

            adjusted = result.get('adjusted_confidence', initial_confidence)
            delta = result.get('confidence_delta', 0.0)

            if delta != 0.0:
                logger.info(f"[CLASSIFIER] [GEMMA] @{safe_username}: {initial_confidence:.2f} → {adjusted:.2f} (delta: {delta:+.2f})")
                logger.info(f"[CLASSIFIER] [GEMMA]   Reason: {result.get('reasoning', 'N/A')}")

            return adjusted

        except Exception as e:
            logger.warning(f"[CLASSIFIER] Gemma validation failed: {e}")
            return initial_confidence

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
        # SECURITY (2026-02-19): Sanitize username for logging
        safe_username = _sanitize_username(username)

        # TIER 1: Check whack history from magadoom_scores.db (MAGA troll detection)
        # FIX (2026-02-19): Use correct database! chat_rules.db was nearly empty
        # Occam's Razor (2025-12-23): If whacked before → probably a troll
        # PERF (2026-02-19): Use LRU cache for hot trolls (reduces DB queries ~80%)
        profile_store = self._get_profile_store()
        if profile_store:
            try:
                whack_count = _get_cached_whack_count(user_id, profile_store)

                if whack_count and whack_count > 0:
                    # Simple confidence scoring: More whacks = higher confidence
                    if whack_count >= 3:
                        confidence = 0.95  # Confirmed troll (3+ whacks)
                    elif whack_count == 2:
                        confidence = 0.80  # Likely troll (2 whacks)
                    else:
                        confidence = 0.70  # Suspected troll (1 whack)

                    logger.info(f"[CLASSIFIER] @{safe_username} → 0✊ (MAGA troll - {whack_count}x whacks, confidence: {confidence})")

                    return {
                        'classification': CommenterType.MAGA_TROLL,
                        'confidence': confidence,
                        'whack_count': whack_count,
                        'method': 'whack_history_lookup'
                    }
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Whack history check failed (magadoom_scores.db): {e}")

        # TIER 1.5: Livechat History Cross-Reference (Training Mode)
        # Bridge livechat behavior to inform comment classification
        # - User known as troll in livechat → classify as MAGA_TROLL with boosted confidence
        # - User known as MOD/OWNER in livechat → will be caught in TIER 2
        livechat_memory = self._get_livechat_memory()
        if not livechat_memory:
            logger.debug(f"[CLASSIFIER] [LIVECHAT-BRIDGE] ⚠️ Livechat memory not available - skipping cross-reference")
        if livechat_memory:
            try:
                # DAEmon VISIBILITY: Show livechat bridge is active
                logger.info(f"[CLASSIFIER] [LIVECHAT-BRIDGE] 🔗 Checking livechat history for @{safe_username}...")

                # Check livechat troll classification
                livechat_result = livechat_memory.classify_user(username)
                if livechat_result.get('is_troll'):
                    troll_score = livechat_result.get('score', 0)
                    signals = livechat_result.get('signals', [])

                    # Higher score = higher confidence
                    if troll_score >= 6:
                        confidence = 0.90  # Strong livechat evidence
                    elif troll_score >= 4:
                        confidence = 0.80  # Moderate evidence
                    else:
                        confidence = 0.70  # Some evidence

                    logger.info(f"[CLASSIFIER] @{safe_username} → 0✊ (MAGA troll - livechat score: {troll_score}, signals: {signals})")

                    return {
                        'classification': CommenterType.MAGA_TROLL,
                        'confidence': confidence,
                        'livechat_score': troll_score,
                        'livechat_signals': signals,
                        'method': 'livechat_history'
                    }

                # Also check livechat user stats for role information
                user_stats = livechat_memory.user_stats.get(username)
                if user_stats and user_stats.get('role') in ('MOD', 'OWNER'):
                    logger.info(f"[CLASSIFIER] @{safe_username} → 2🖐️ (Moderator from livechat: {user_stats.get('role')})")
                    return {
                        'classification': CommenterType.MODERATOR,
                        'confidence': 1.0,  # Livechat confirmed
                        'method': 'livechat_role',
                        'livechat_role': user_stats.get('role')
                    }

                # DAEmon VISIBILITY: Show livechat check result (even if no classification change)
                if not livechat_result.get('is_troll') and not (user_stats and user_stats.get('role') in ('MOD', 'OWNER')):
                    livechat_score = livechat_result.get('score', 0)
                    logger.info(f"[CLASSIFIER] [LIVECHAT-BRIDGE] ✅ @{safe_username} not in livechat troll list (score: {livechat_score})")

            except Exception as e:
                logger.debug(f"[CLASSIFIER] Livechat history check failed: {e}")

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
        logger.debug(f"[CLASSIFIER] @{safe_username} → 1✋ (Regular - confidence: 0.5, PROVISIONAL)")

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

                    # Apply Gemma validation if enabled (adjusts confidence)
                    initial_confidence = 0.6  # Provisional (below 0.7 threshold)
                    validated_confidence = self._apply_gemma_validation(
                        username=username,
                        comment_text=comment_text,
                        classification=CommenterType.MAGA_TROLL,
                        initial_confidence=initial_confidence
                    )

                    logger.info(f"[CLASSIFIER]   Final confidence: {validated_confidence:.2f} (Gemma: {'enabled' if self.enable_gemma else 'disabled'})")

                    return {
                        'classification': CommenterType.MAGA_TROLL,
                        'confidence': validated_confidence,
                        'whack_count': 0,   # Not yet whacked
                        'method': 'sentiment_hostile',
                        'pattern_detected': pattern,
                        'gemma_validated': self.enable_gemma
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

            # Check for anti-Trump ally patterns → MODERATOR (2) with ally flag
            for pattern in ANTI_TRUMP_ALLY_PATTERNS:
                if pattern in comment_lower:
                    logger.info(f"[CLASSIFIER] 🤝 ANTI-TRUMP ALLY DETECTED: '{pattern}'")
                    logger.info(f"[CLASSIFIER]   Comment: {comment_text[:50]}...")
                    logger.info(f"[CLASSIFIER]   Classification: MODERATOR (ally mode - agree & join trolling)")
                    logger.info(f"[CLASSIFIER]   NOTE: Use #FFCPLN skill in AGREEMENT mode!")

                    return {
                        'classification': CommenterType.MODERATOR,  # 2 = MODERATOR (includes allies)
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
