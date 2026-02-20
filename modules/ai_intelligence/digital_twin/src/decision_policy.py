# -*- coding: utf-8 -*-
"""
Decision Policy - Determine whether to comment/like/ignore.

WSP Compliance:
    WSP 77: Agent Coordination (Digital Twin)

Purpose:
    Heuristic v0 decision policy:
    - Comment if high relevance + low toxicity + cooldown ok
    - Like if medium relevance
    - Ignore otherwise
"""

import logging
import time
from typing import Any, Dict, Optional

from .schemas import CommentAction, CommentDecision

logger = logging.getLogger(__name__)


class DecisionPolicy:
    """
    Determine whether to engage with a thread.
    
    Heuristic v0:
    - COMMENT: relevance > 0.7 AND toxicity < 0.3 AND cooldown ok
    - LIKE: 0.4 < relevance <= 0.7
    - IGNORE: otherwise
    
    Example:
        >>> policy = DecisionPolicy()
        >>> decision = policy.decide(relevance=0.8, toxicity=0.1)
        >>> # decision.action == "comment"
    """
    
    def __init__(
        self,
        comment_threshold: float = 0.7,
        like_threshold: float = 0.4,
        toxicity_threshold: float = 0.3,
        default_cooldown_s: int = 300
    ):
        """
        Initialize policy.
        
        Args:
            comment_threshold: Min relevance to comment
            like_threshold: Min relevance to like
            toxicity_threshold: Max toxicity to engage
            default_cooldown_s: Default cooldown between comments
        """
        self.comment_threshold = comment_threshold
        self.like_threshold = like_threshold
        self.toxicity_threshold = toxicity_threshold
        self.default_cooldown_s = default_cooldown_s
        
        # Track last comment times per thread/user
        self._last_comment_times: Dict[str, float] = {}
    
    def decide(
        self,
        relevance_score: float,
        toxicity_score: float = 0.0,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        cooldown_s: Optional[int] = None
    ) -> CommentDecision:
        """
        Decide whether to engage.
        
        Args:
            relevance_score: 0-1 relevance to 012's topics
            toxicity_score: 0-1 toxicity level
            thread_id: Thread identifier for cooldown tracking
            user_id: User identifier for cooldown tracking
            context: Additional context
            cooldown_s: Override default cooldown
            
        Returns:
            CommentDecision with action and reason
        """
        cooldown_s = cooldown_s or self.default_cooldown_s
        context = context or {}
        
        # Check cooldown
        cooldown_ok, cooldown_reason = self._check_cooldown(
            thread_id, user_id, cooldown_s
        )
        
        # Check toxicity
        if toxicity_score > self.toxicity_threshold:
            logger.info(f"[DECISION-POLICY] IGNORE | toxicity={toxicity_score:.2f} > threshold={self.toxicity_threshold}")
            return CommentDecision(
                should_comment=False,
                action=CommentAction.IGNORE,
                reason=f"Toxicity too high: {toxicity_score:.2f} > {self.toxicity_threshold}",
                confidence=0.9,
                cooldown_s=cooldown_s
            )
        
        # Check relevance for COMMENT
        if relevance_score > self.comment_threshold:
            if not cooldown_ok:
                decision = CommentDecision(
                    should_comment=False,
                    action=CommentAction.LIKE,
                    reason=f"Would comment but {cooldown_reason}",
                    confidence=0.7,
                    cooldown_s=cooldown_s
                )
                logger.info(f"[DECISION-POLICY] LIKE | relevance={relevance_score:.2f} | {cooldown_reason}")
                return decision

            decision = CommentDecision(
                should_comment=True,
                action=CommentAction.COMMENT,
                reason=f"High relevance: {relevance_score:.2f}",
                confidence=min(relevance_score, 0.95),
                cooldown_s=cooldown_s
            )
            logger.info(f"[DECISION-POLICY] COMMENT | relevance={relevance_score:.2f} | confidence={decision.confidence:.2f}")
            return decision
        
        # Check relevance for LIKE
        if relevance_score > self.like_threshold:
            decision = CommentDecision(
                should_comment=False,
                action=CommentAction.LIKE,
                reason=f"Medium relevance: {relevance_score:.2f}",
                confidence=relevance_score,
                cooldown_s=cooldown_s
            )
            logger.info(f"[DECISION-POLICY] LIKE | relevance={relevance_score:.2f}")
            return decision

        # Default: IGNORE
        decision = CommentDecision(
            should_comment=False,
            action=CommentAction.IGNORE,
            reason=f"Low relevance: {relevance_score:.2f}",
            confidence=0.8,
            cooldown_s=cooldown_s
        )
        logger.debug(f"[DECISION-POLICY] IGNORE | relevance={relevance_score:.2f}")
        return decision
    
    def _check_cooldown(
        self,
        thread_id: Optional[str],
        user_id: Optional[str],
        cooldown_s: int
    ) -> tuple[bool, str]:
        """Check if cooldown period has passed."""
        now = time.time()
        
        # Check thread cooldown
        if thread_id:
            key = f"thread:{thread_id}"
            last_time = self._last_comment_times.get(key, 0)
            if now - last_time < cooldown_s:
                remaining = int(cooldown_s - (now - last_time))
                return False, f"Thread cooldown: {remaining}s remaining"
        
        # Check user cooldown (longer)
        if user_id:
            key = f"user:{user_id}"
            user_cooldown = cooldown_s * 12  # 1 hour for same user
            last_time = self._last_comment_times.get(key, 0)
            if now - last_time < user_cooldown:
                remaining = int(user_cooldown - (now - last_time))
                return False, f"User cooldown: {remaining}s remaining"
        
        return True, "OK"
    
    def record_comment(
        self,
        thread_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> None:
        """Record that we commented (for cooldown tracking)."""
        now = time.time()
        
        if thread_id:
            self._last_comment_times[f"thread:{thread_id}"] = now
        if user_id:
            self._last_comment_times[f"user:{user_id}"] = now
    
    def estimate_relevance(
        self,
        thread_text: str,
        keywords: Optional[list] = None
    ) -> float:
        """
        Simple keyword-based relevance estimation.
        
        In production: Use embeddings or classifier.
        """
        keywords = keywords or [
            "japan", "visa", "business", "startup", "tokyo",
            "ai", "consciousness", "foundups", "012", "0102",
            "entrepreneur", "immigration", "work permit"
        ]
        
        text_lower = thread_text.lower()
        matches = sum(1 for kw in keywords if kw in text_lower)
        
        return min(matches / 3, 1.0)  # Normalize
    
    def estimate_toxicity(self, text: str) -> float:
        """
        Simple toxicity estimation.
        
        In production: Use classifier or API.
        """
        toxic_patterns = [
            "hate", "stupid", "idiot", "kill", "die",
            "scam", "fake", "liar", "trash", "garbage"
        ]
        
        text_lower = text.lower()
        matches = sum(1 for p in toxic_patterns if p in text_lower)
        
        return min(matches / 2, 1.0)


# =============================================================================
# Quick Test
# =============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Decision Policy Test")
    print("=" * 60)
    
    policy = DecisionPolicy()
    
    test_cases = [
        {"relevance": 0.9, "toxicity": 0.1, "desc": "High relevance, low toxicity"},
        {"relevance": 0.5, "toxicity": 0.1, "desc": "Medium relevance"},
        {"relevance": 0.2, "toxicity": 0.1, "desc": "Low relevance"},
        {"relevance": 0.9, "toxicity": 0.5, "desc": "High toxicity"},
    ]
    
    for case in test_cases:
        decision = policy.decide(
            relevance_score=case["relevance"],
            toxicity_score=case["toxicity"]
        )
        print(f"\n{case['desc']}:")
        print(f"  Action: {decision.action.value}")
        print(f"  Reason: {decision.reason}")
        print(f"  Confidence: {decision.confidence:.2f}")
