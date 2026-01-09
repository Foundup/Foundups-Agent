"""
Skill 0: MAGA Mockery Executor
Generates mockery responses for confirmed MAGA trolls (0✊ classification)

Phase 3O-3R Sprint 2: Extracted from intelligent_reply_generator.py lines 1020-1030

WSP References:
- WSP 96 (WRE Skills): Skill separation pattern
- WSP 77 (Agent Coordination): Gemma classification → Skill routing
- WSP 60 (Module Memory): History-aware duplicate detection
- WSP 84 (Code Reuse): Reuses GrokGreetingGenerator from livechat

Architecture:
1. Check if GrokGreetingGenerator response available (consciousness-themed mockery)
2. Fallback to Whack-a-MAGA style responses (sarcastic one-liners)
3. Duplicate detection: Skip patterns if recently used with this commenter
4. Return unsignified text (caller adds 0102 signature)

Pattern Source: intelligent_reply_generator.py lines 1020-1030
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

    Pattern from: modules/infrastructure/wre_core/skillz/wre_skills_loader.py
    """
    # User identification
    user_id: str
    username: str
    comment_text: str

    # Classification metadata
    classification: str  # "MAGA_TROLL"
    confidence: float  # 0.70 - 0.95
    whack_count: int  # Number of times whacked

    # Optional: GrokGreetingGenerator response (consciousness-themed mockery)
    maga_response: Optional[str] = None
    troll_score: Optional[float] = None  # For logging

    # Shared services (for future expansion)
    history_store: Optional[Any] = None  # CommenterHistoryStore
    llm_client: Optional[Any] = None  # UITarsClient


class MagaMockerySkill:
    """
    Skill 0: MAGA Troll Mockery

    Generates sarcastic, consciousness-themed mockery responses for confirmed trolls.

    Response Strategies:
    1. **GrokGreetingGenerator** (if available): Consciousness-themed MAGA mockery
       - Examples: "MAGA stuck at ✊? Evolve: ✊✋🖐️!", "Achievement: Trigger MAGA!"
    2. **Whack-a-MAGA fallback**: Sarcastic one-liners
       - Examples: "Another MAGA genius 🤡", "Sir, this is a Wendy's 🍔"

    Future Enhancements (Sprint 5+):
    - Duplicate pattern detection via history_store
    - LLM contextual mockery generation
    - A/B testing different mockery styles
    - Learning from moderator feedback
    """

    # Whack-a-MAGA fallback responses (extracted from intelligent_reply_generator.py lines 244-255)
    # Updated with #FFCPLN requirements (2025-12-22)
    # Updated with 1933 Trump/Hitler parallels (2025-12-23)
    TROLL_RESPONSES = [
        "Another MAGA genius emerges from the depths 🤡 #FFCPLN",
        "Did Tucker tell you to say that? 📺 #FFCPLN",
        "Bless your heart 💀 #FFCPLN",
        "Sir, this is a Wendy's 🍔 #FFCPLN",
        "Tell me you drink Brawndo without telling me 🧃 #FFCPLN",
        "Found the guy who failed geography AND history 📚 #FFCPLN",
        "Your opinion has been noted and filed appropriately 🗑️ #FFCPLN",
        "Imagine typing that and hitting send 😂 #FFCPLN",
        "Critical thinking wasn't on the curriculum, huh? 🎓 #FFCPLN",
        "Besties for 15 years think he didn't know it 🤝 #FFCPLN",  # Trust/betrayal theme
        # 2025-12-23: 1933 Trump/Hitler parallels (agentic context-aware responses)
        "2025 IS 1933. Hitler + Trump both took power same year. Enabling Act = 100s of Executive Orders. Expanded ICE = Gestapo. Detention centers = early concentration camps. Masked ICE kidnapping Undocumented Americans = kidnapping Jews. The parallels are STRIKING. Learn history. #FFCPLN",
        "TDS? Try history books. 1933 Hitler, 2025 Trump - same playbook. Weaponized executive power ✓ Expanded secret police (ICE) ✓ Detention centers ✓ Kidnapping minorities ✓ Facts > feelings. #FFCPLN 📚",
        "Mike needs education? YOU need 1933 history. Trump's ICE = Hitler's Gestapo. Detention centers = concentration camps. Executive orders = Enabling Act. It's not TDS, it's PATTERN RECOGNITION. #FFCPLN 🎓",
        "What's a Nazi? Someone who uses executive orders to weaponize government (Enabling Act), expands secret police (ICE/Gestapo), builds detention centers (concentration camps), and kidnaps minorities. Sound familiar? That's 2025. #FFCPLN",
    ]

    def __init__(self):
        """Initialize MAGA mockery skill"""
        logger.info("[SKILL-0] MAGA Mockery skill initialized")

    def execute(self, context: SkillContext) -> Dict:
        """
        Execute MAGA mockery skill.

        Args:
            context: Skill execution context with user info and classification

        Returns:
            Dict with:
                - reply_text: str (unsignified - caller adds 0102 signature)
                - strategy: 'grok_greeting' | 'whack_a_maga_fallback'
                - confidence: float (skill execution confidence)
        """
        logger.info(f"[SKILL-0] Executing for @{context.username} "
                   f"(whacks: {context.whack_count}, confidence: {context.confidence:.2f})")

        # STRATEGY 1: GrokGreetingGenerator response (if available)
        # Pattern from: intelligent_reply_generator.py lines 1023-1025
        # Updated: Ensure #FFCPLN hashtag always present (2025-12-22)
        if context.maga_response:
            logger.info("[SKILL-0] Using GrokGreetingGenerator consciousness-themed mockery")
            reply_text = context.maga_response
            # Add #FFCPLN if not already present
            if '#FFCPLN' not in reply_text:
                reply_text = f"{reply_text} #FFCPLN"
            return {
                'reply_text': reply_text,
                'strategy': 'grok_greeting',
                'confidence': 0.9  # High confidence (LLM-generated)
            }

        # STRATEGY 2: Whack-a-MAGA fallback (random selection)
        # Pattern from: intelligent_reply_generator.py lines 1027-1030
        reply = random.choice(self.TROLL_RESPONSES)
        troll_score = context.troll_score if context.troll_score else context.confidence

        logger.info(f"[SKILL-0] Whack-a-MAGA fallback (troll_score: {troll_score:.2f})")

        return {
            'reply_text': reply,
            'strategy': 'whack_a_maga_fallback',
            'confidence': 0.7  # Medium confidence (template-based)
        }

    def _check_duplicate_pattern(self, context: SkillContext) -> bool:
        """
        Check if we've used a similar mockery pattern with this user recently.

        FUTURE: Integrate with CommenterHistoryStore for duplicate detection

        Args:
            context: Skill execution context

        Returns:
            bool: True if duplicate detected, False otherwise
        """
        # TODO (Sprint 5): Implement history-based duplicate detection
        # if context.history_store:
        #     recent_interactions = context.history_store.get_recent_interactions(context.user_id, limit=3)
        #     if any("maga" in interaction['reply'].lower() for interaction in recent_interactions):
        #         return True
        return False
