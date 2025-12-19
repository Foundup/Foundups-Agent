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

    def to_012_code(self) -> str:
        """Convert to 012 emoji representation"""
        emoji_map = {
            CommenterType.MAGA_TROLL: "0✊",
            CommenterType.REGULAR: "1✋",
            CommenterType.MODERATOR: "2🖐️"
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
        self._profile_store = None
        self._moderator_db = None

        logger.info(f"[CLASSIFIER] Initialized (Gemma: {enable_gemma}, Qwen: {enable_qwen})")

    def _get_profile_store(self):
        """Lazy-load ProfileStore for whacked_users lookup"""
        if self._profile_store is None:
            try:
                from modules.gamification.whack_a_magat.src.whack import get_profile_store
                self._profile_store = get_profile_store()
                logger.debug("[CLASSIFIER] Loaded whacked_users database")
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load whacked_users database: {e}")
        return self._profile_store

    def _get_moderator_db(self):
        """Lazy-load moderator database for moderator lookup"""
        if self._moderator_db is None:
            try:
                from modules.communication.chat_rules.src.database import ModeratorDatabase
                self._moderator_db = ModeratorDatabase()
                logger.debug("[CLASSIFIER] Loaded moderator database")
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Failed to load moderator database: {e}")
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
        # TIER 1: Check if user is whacked (MAGA troll) - <1ms
        profile_store = self._get_profile_store()
        if profile_store:
            try:
                if profile_store.is_whacked_user(user_id):
                    whacked_details = profile_store.get_whacked_user(user_id)
                    whack_count = whacked_details.get('whack_count', 1) if whacked_details else 1

                    # Confidence scoring based on whack frequency (Gemma-style pattern)
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
                        'whacked_by': whacked_details.get('whacked_by', []),
                        'method': 'database_lookup'
                    }
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Whacked user check failed: {e}")

        # TIER 2: Check if user is moderator - <5ms
        moderator_db = self._get_moderator_db()
        if moderator_db:
            try:
                if moderator_db.is_moderator(username) or moderator_db.is_moderator(user_id):
                    logger.info(f"[CLASSIFIER] @{username} → 2🖐️ (Moderator - confidence: 1.0)")

                    return {
                        'classification': CommenterType.MODERATOR,
                        'confidence': 1.0,  # Database confirmed
                        'method': 'moderator_database'
                    }
            except Exception as e:
                logger.warning(f"[CLASSIFIER] Moderator check failed: {e}")

        # TIER 3: Default to regular user
        logger.debug(f"[CLASSIFIER] @{username} → 1✋ (Regular - confidence: 0.5)")

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
