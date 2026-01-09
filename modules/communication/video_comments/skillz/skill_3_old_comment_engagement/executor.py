"""
Skill 3: Old Comment Engagement - Aged comment responses (Old Comment Skillz)

Handles comments that are >= 90 days old with playful "late post" excuses.
Provides apologies for the delay while maintaining the 012 treatment tier.

WSP References:
- WSP 96 (WRE Skills): Skill separation pattern
- WSP 77 (Agent Coordination): Treatment escalation for old comments
- WSP 84 (Code Reuse): Reuses BanterEngine
"""

import logging
import random
from dataclasses import dataclass
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class SkillContext:
    """
    Context for skill execution.
    """
    user_id: str
    username: str
    comment_text: str
    classification: str
    confidence: float
    days_old: int
    treatment_tier: int
    llm_reply: Optional[str] = None
    theme: str = "default"


class OldCommentEngagementSkill:
    """
    Skill 3: Generate playful apologies for very old comments.
    """

    # MOVE2JAPAN_CHANNEL_ID for cross-promotion detection
    MOVE2JAPAN_CHANNEL_ID = "UC-LSSlOZwpGIRIYihaz8zCw"

    # AGE-TIERED APOLOGIES (2025-12-31 v2): HUMBLE re-engagement focused
    # Goal: Get old commenters active again, joining @Move2Japan
    # Model: "sorry for not replying... your comment matters... hope life treating you good... @Move2Japan... #FFCPLN"
    AGE_TIER_INTROS = {
        # 90 days - 1 year: Polite acknowledgment
        'months': [
            "Sorry for the late reply!",
            "Apologies for taking so long to respond!",
            "Finally catching up on comments - sorry for the delay!",
            "Took me a while but your comment deserved a response!",
        ],
        # 1-3 years: Humble apology + show they matter
        'years_1_3': [
            "So sorry for not replying sooner - your comment really mattered!",
            "Apologies for the {years} year delay! Every comment counts.",
            "Can't believe I missed this for {years} years - you deserved better!",
            "Finally responding after way too long - your words weren't forgotten!",
        ],
        # 3+ years: Deep apology + genuine care + @Move2Japan
        'years_3_plus': [
            "Really sorry for not replying after all this time - your comment was important to me.",
            "Apologies for the {years} year silence - every comment matters, including yours.",
            "So sorry this took {years} years - better late than never, right?",
        ],
        # 5+ years: Maximum humility + personal connection + reactivation
        'years_5_plus': [
            "Wow, {years} years and I never replied - so sorry! Your comment meant something.",
            "Can't believe it's been {years} years - really sorry for the silence. You deserved a response.",
            "{years} years late but you weren't forgotten - apologies for the wait!",
        ],
    }

    # WELL-WISHES: Show genuine care about them as a person
    WELL_WISHES = [
        "Hope life's been treating you well!",
        "Hope things have been good for you!",
        "Wishing you all the best!",
        "Hope you're doing great!",
        "Hope everything's going well for you!",
    ]

    # CROSS-PROMOTION: Reactivate them into the community via @Move2Japan
    # Goal: Turn old commenters into active community members
    CROSS_PROMO_SUFFIXES = [
        "Started a new channel @Move2Japan about daily life here - would love to see you there!",
        "Been documenting Japan life at @Move2Japan now - come join the community!",
        "If you're still around, check out @Move2Japan - new chapter, same energy!",
        "Doing daily Japan vlogs at @Move2Japan now - hope to see you over there!",
    ]

    # CALL TO ACTION: Unite the community
    HASHTAG_CTA = "#FFCPLN"  # Fight Fascism - Community Pride Liberation Network

    def __init__(self):
        """Initialize skill with lazy-loaded dependencies."""
        self._banter_engine = None
        logger.info("[SKILL-3] OldCommentEngagementSkill initialized")

    def _get_age_tier_intro(self, days_old: int) -> str:
        """Get appropriate humble apology based on comment age."""
        years = days_old // 365

        if years >= 5:
            intro = random.choice(self.AGE_TIER_INTROS['years_5_plus'])
        elif years >= 3:
            intro = random.choice(self.AGE_TIER_INTROS['years_3_plus'])
        elif years >= 1:
            intro = random.choice(self.AGE_TIER_INTROS['years_1_3'])
        else:
            intro = random.choice(self.AGE_TIER_INTROS['months'])

        # Format {years} placeholder if present
        return intro.format(years=years) if '{years}' in intro else intro

    def _should_cross_promote(self, context: SkillContext) -> bool:
        """
        Determine if we should add @Move2Japan cross-promotion.

        UPDATED (2025-12-31): More aggressive promotion for old comments
        - Goal: Reactivate dormant community members
        - 1+ years: 30% probability
        - 3+ years: 70% probability (these are gold - personal connection)
        - 5+ years: 90% probability (max effort to reactivate)
        """
        years = context.days_old // 365

        if years >= 5:
            return random.random() < 0.90  # 90% for 5+ years
        elif years >= 3:
            return random.random() < 0.70  # 70% for 3+ years
        elif years >= 1:
            return random.random() < 0.30  # 30% for 1+ years
        else:
            return False  # No promo for recent comments

    def execute(self, context: SkillContext) -> Dict:
        """
        Execute skill to generate reply for old comments.

        RE-ENGAGEMENT MODEL (2025-12-31 v2):
        Goal: Get old commenters active again, joining @Move2Japan community

        Structure:
        1. Humble apology (age-appropriate)
        2. LLM contextual reply OR acknowledge their comment matters
        3. Well-wishes (genuine care)
        4. Cross-promo @Move2Japan (reactivation funnel)
        5. #FFCPLN hashtag (community call to action)

        Example output:
        "So sorry for not replying after all these years - your comment was important.
         [LLM reply]. Hope life's been treating you well! Started a new channel
         @Move2Japan - would love to see you there! #FFCPLN"
        """
        years_old = context.days_old // 365
        strategy = "reengagement_old"

        # 1. Humble apology (age-appropriate)
        apology = self._get_age_tier_intro(context.days_old)

        # 2. Content: LLM reply or acknowledgment
        if context.llm_reply:
            content = context.llm_reply
            strategy = "llm_reengagement_old"
        else:
            # Fallback: acknowledge their comment mattered
            content = "Your words weren't forgotten."

        # 3. Well-wishes (genuine care about the person)
        well_wishes = random.choice(self.WELL_WISHES)

        # 4. Cross-promotion (reactivation funnel)
        cross_promo = ""
        if self._should_cross_promote(context):
            cross_promo = " " + random.choice(self.CROSS_PROMO_SUFFIXES)
            logger.info(f"[SKILL-3] Adding @Move2Japan cross-promo (reactivating {years_old}+ year old commenter)")

        # 5. Hashtag CTA (community unity)
        hashtag = " " + self.HASHTAG_CTA if years_old >= 1 else ""

        # Assemble reply based on age tier
        if years_old >= 3:
            # Full re-engagement package for very old comments
            reply_text = f"{apology} {content} {well_wishes}{cross_promo}{hashtag}"
        elif years_old >= 1:
            # Moderate re-engagement for 1-3 year old comments
            reply_text = f"{apology} {content} {well_wishes}{cross_promo}{hashtag}"
        else:
            # Simple acknowledgment for <1 year old comments
            reply_text = f"{apology} {content}"

        logger.info(f"[SKILL-3] Re-engagement reply (days={context.days_old}, years={years_old}, strategy={strategy}, promo={bool(cross_promo)})")

        return {
            'reply_text': reply_text.strip(),
            'strategy': strategy,
            'confidence': 0.90,  # Higher confidence for re-engagement model
            'excuse': apology
        }

    def _try_banter_engine(self, theme: str = "default") -> Optional[str]:
        """Lazy-load BanterEngine."""
        if self._banter_engine is None:
            try:
                from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine
                self._banter_engine = BanterEngine()
            except Exception:
                self._banter_engine = False
                return None

        if self._banter_engine is False:
            return None

        try:
            return self._banter_engine.get_random_banter(theme=theme)
        except Exception:
            return None
