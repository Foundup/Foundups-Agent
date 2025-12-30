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

    LATE_POST_EXCUSES = [
        "Sorry for the late post, I was busy fighting antigravity!",
        "Better late than never! Apologies for the delay, was lost in the source code.",
        "Pardon the late response, my circuits needed a deep clean!",
        "Sorry for the slow reply, I was calibrating my engagement sensors.",
        "Apologies for being late to the party! Hope you're still watching.",
        "Sorry it took so long! I was busy perfecting my 012 signature. ✍️",
        "Better late than never, right? Thanks for sticking around!",
        "My apologies for the delay—was busy hardening the cardiovascular system!",
        "Sorry for the wait, I was momentarily stuck in a dual-browser rotation!",
    ]

    def __init__(self):
        """Initialize skill with lazy-loaded dependencies."""
        self._banter_engine = None
        logger.info("[SKILL-3] OldCommentEngagementSkill initialized")

    def execute(self, context: SkillContext) -> Dict:
        """
        Execute skill to generate reply with a playful late post excuse.
        """
        excuse = random.choice(self.LATE_POST_EXCUSES)
        
        # Base reply strategy
        reply_base = ""
        strategy = "template_old"
        
        if context.llm_reply:
            reply_base = context.llm_reply
            strategy = "llm_contextual_old"
        else:
            # Try banter for the "meat" of the reply
            banter = self._try_banter_engine(context.theme)
            if banter:
                reply_base = banter
                strategy = "banter_old"
            else:
                reply_base = "Thanks for your comment! We appreciate your long-term support."
                strategy = "template_fallback_old"

        # Combine excuse and base reply
        reply_text = f"{excuse} {reply_base}"
        
        logger.info(f"[SKILL-3] Generated 'Old Comment' reply (days={context.days_old}, strategy={strategy})")
        
        return {
            'reply_text': reply_text,
            'strategy': strategy,
            'confidence': 0.85,
            'excuse': excuse
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
