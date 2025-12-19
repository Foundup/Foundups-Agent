"""
Skill 2: Moderator Appreciation Executor
Generates appreciation responses for community moderators (2🖐️ classification)

Phase 3O-3R Sprint 3 (Enhanced): Extracted from intelligent_reply_generator.py lines 1017-1018

WSP References:
- WSP 96 (WRE Skills): Skill separation pattern
- WSP 77 (Agent Coordination): Gemma classification → Skill routing
- WSP 60 (Module Memory): Mod stats integration with chat_rules database
- WSP 84 (Code Reuse): Reuses ChatRulesDB from chat_rules module

Architecture:
1. Try personalized appreciation with mod stats (whacks, level, points)
2. Fallback to template appreciation if stats unavailable
3. Return unsignified text (caller adds 0102 signature)

Pattern Source: intelligent_reply_generator.py lines 1017-1018, 219-225
Database Integration: modules/communication/chat_rules/src/database.py
"""

import logging
import random
from dataclasses import dataclass
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)


@dataclass
class SkillContext:
    """
    Dependency injection context for skill execution.

    Pattern from: modules/infrastructure/wre_core/skills/wre_skills_loader.py
    """
    # User identification
    user_id: str
    username: str
    comment_text: str

    # Classification metadata
    classification: str  # "MODERATOR"
    confidence: float  # Should be 1.0 (database confirmed)

    # Optional: Moderator stats (populated by router)
    mod_whack_count: Optional[int] = None  # Whacks performed by this mod
    mod_rank: Optional[str] = None  # Rank/level
    recent_activity: Optional[str] = None  # Recent moderation actions

    # Shared services (for future expansion)
    history_store: Optional[Any] = None  # CommenterHistoryStore
    llm_client: Optional[Any] = None  # UITarsClient


class ModeratorAppreciationSkill:
    """
    Skill 2: Moderator Appreciation

    Generates appreciation responses for community moderators and leaders.

    Response Strategies:
    1. **Personalized stats** (Sprint 3 enhanced): "Thanks @ModName! 15 trolls whacked - LEGEND status! 💪"
    2. **Template appreciation** (fallback): 5 randomized appreciation messages
    3. **LLM contextual** (future): Custom appreciation based on recent actions

    Database Integration (Sprint 3):
    - Integrates with chat_rules.db moderator stats
    - Pulls: whacks_count, level, total_points
    - Personalizes appreciation with actual contributions
    """

    # Moderator appreciation templates (extracted from intelligent_reply_generator.py lines 219-225)
    MOD_RESPONSES = [
        "Thanks for keeping the chat clean! 🛡️",
        "Appreciate the mod support! 💪",
        "Thanks for holding it down! 🙏",
        "Legend status confirmed! ⭐",
        "MVP of the chat right here! 🏆",
    ]

    def __init__(self):
        """Initialize moderator appreciation skill"""
        self._chat_rules_db = None  # Lazy load
        logger.info("[SKILL-2] Moderator appreciation skill initialized")

    def execute(self, context: SkillContext) -> Dict:
        """
        Execute moderator appreciation skill.

        Args:
            context: Skill execution context with user info and classification

        Returns:
            Dict with:
                - reply_text: str (unsignified - caller adds 0102 signature)
                - strategy: 'template' | 'personalized_stats' | 'llm_contextual'
                - confidence: float (skill execution confidence)
        """
        logger.info(f"[SKILL-2] Executing for moderator @{context.username} "
                   f"(confidence: {context.confidence:.2f})")

        # STRATEGY 1: Personalized with mod stats (if available)
        # Sprint 3 Enhanced: Integrate with chat_rules database
        mod_stats = self._get_mod_stats(context)
        if mod_stats and mod_stats.get('whacks_count', 0) > 0:
            whack_count = mod_stats['whacks_count']
            level = mod_stats.get('level', 'MOD')

            # Personalized appreciation with stats
            personalized = self._generate_personalized_appreciation(
                username=context.username,
                whack_count=whack_count,
                level=level
            )

            logger.info(f"[SKILL-2] Personalized appreciation (whacks: {whack_count}, level: {level})")

            return {
                'reply_text': personalized,
                'strategy': 'personalized_stats',
                'confidence': 1.0
            }

        # STRATEGY 2: Template appreciation fallback
        # Pattern from: intelligent_reply_generator.py line 1018
        reply = random.choice(self.MOD_RESPONSES)

        logger.info(f"[SKILL-2] Template appreciation (mod stats unavailable)")

        return {
            'reply_text': reply,
            'strategy': 'template',
            'confidence': 1.0  # High confidence (database-confirmed moderator)
        }

    def _generate_personalized_appreciation(
        self,
        username: str,
        whack_count: int,
        level: str
    ) -> str:
        """
        Generate personalized appreciation message with mod stats.

        Args:
            username: Moderator username
            whack_count: Total whacks performed
            level: Mod rank/level

        Returns:
            str: Personalized appreciation message
        """
        # Variation templates to avoid regurgitation (WSP 96: semantic variation)
        templates = [
            f"Thanks @{username}! {whack_count} trolls whacked - {level} status! 💪",
            f"Appreciate you @{username}! {whack_count} whacks and counting! 🛡️",
            f"{level} @{username} with {whack_count} whacks! Legend! ⭐",
            f"MVP @{username}! {whack_count} trolls eliminated! 🏆",
            f"Thanks for the {whack_count} whacks, @{username}! {level} confirmed! 🙏",
        ]

        return random.choice(templates)

    def _get_mod_stats(self, context: SkillContext) -> Optional[Dict]:
        """
        Get moderator statistics from chat_rules database.

        Sprint 3 Enhanced: Real database integration

        Args:
            context: Skill execution context

        Returns:
            Dict with mod stats or None if unavailable
        """
        # Try to load from chat_rules database
        if self._chat_rules_db is None:
            try:
                from modules.communication.chat_rules.src.database import ChatRulesDB
                self._chat_rules_db = ChatRulesDB()
                logger.debug("[SKILL-2] Loaded chat_rules database")
            except Exception as e:
                logger.warning(f"[SKILL-2] Failed to load chat_rules database: {e}")
                return None

        # Query moderator stats
        try:
            with self._chat_rules_db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT whacks_count, level, total_points, combo_multiplier
                    FROM moderators
                    WHERE user_id = ?
                """, (context.user_id,))

                row = cursor.fetchone()

                if row:
                    stats = {
                        'whacks_count': row['whacks_count'],
                        'level': row['level'],
                        'total_points': row['total_points'],
                        'combo_multiplier': row['combo_multiplier']
                    }
                    logger.debug(f"[SKILL-2] Loaded stats for @{context.username}: {stats}")
                    return stats
                else:
                    logger.debug(f"[SKILL-2] No stats found for @{context.username}")
                    return None

        except Exception as e:
            logger.warning(f"[SKILL-2] Failed to query mod stats: {e}")
            return None
