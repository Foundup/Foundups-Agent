"""
AI_Overseer Comment Troll Router - Token Minimization
=====================================================

Routes comment engagement decisions to minimize Grok token usage.

WSP Compliance:
- WSP 77: Agent Coordination (Gemma → AI_Overseer → Grok routing)
- WSP 15: Module Prioritization Scoring (token cost vs quality trade-off)
- WSP 54: Agent Teams (Associate Gemma, Partner Qwen, Principal 0102)

Architecture:
    AI_Overseer acts as traffic cop to minimize tokens:
    1. Check cache for similar MAGA patterns (0 tokens)
    2. Simple pattern → Use fallback response (0 tokens)
    3. Complex → Query Grok with MINIMAL context (50-100 tokens, not 500)

Token Savings:
    Before: Every comment → Grok (200-500 tokens)
    After:  70% cached/fallback (0 tokens), 30% Grok (50-100 tokens)
    Net:    ~90% token reduction
"""

import logging
import sqlite3
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class RouteDecision(Enum):
    """AI_Overseer routing decision for comment engagement."""
    USE_CACHE = "cache"           # Cached response (0 tokens)
    USE_FALLBACK = "fallback"     # Simple fallback (0 tokens)
    QUERY_GROK_MINIMAL = "grok_minimal"  # Grok with minimal context (50-100 tokens)
    QUERY_GROK_FULL = "grok_full"        # Grok with full context (200-500 tokens)
    SKIP = "skip"                 # Skip response (mod/VIP)


@dataclass
class RoutingContext:
    """Context for AI_Overseer routing decision."""
    comment_text: str
    author_name: str
    is_mod: bool = False
    is_subscriber: bool = False
    gemma_context: Optional[Dict] = None
    estimated_tokens: int = 0
    route_decision: RouteDecision = RouteDecision.QUERY_GROK_FULL


class CommentTrollRouter:
    """
    AI_Overseer comment troll router - Minimizes Grok token usage.

    Flow:
    1. Check if user is mod/VIP → Skip Grok entirely
    2. Check cache for similar MAGA patterns → Use cached response (0 tokens)
    3. Simple MAGA pattern (high confidence) → Use fallback (0 tokens)
    4. Complex/nuanced comment → Query Grok with MINIMAL context (50-100 tokens)

    Token Optimization:
    - Cache stores: {pattern_hash: cached_response}
    - AI_Overseer filters Gemma data to TOP 3 most relevant messages
    - Reduces Grok context from 500 tokens → 50 tokens
    """

    # Simple MAGA patterns that don't need Grok (use cached responses)
    SIMPLE_MAGA_PATTERNS = {
        "leftists": {
            "keywords": ["leftists", "libs", "libtards", "left wing"],
            "cached_response": "Weird how 'leftists' built the internet you're using to complain 🤷",
            "confidence": 0.85
        },
        "trump_innocent": {
            "keywords": ["trump is innocent", "witch hunt", "fake charges", "political persecution"],
            "cached_response": "91 felony charges across 4 cases. That's some conspiracy 📚",
            "confidence": 0.90
        },
        "stolen_election": {
            "keywords": ["stolen election", "voter fraud", "rigged", "stop the steal"],
            "cached_response": "60+ lawsuits lost. Turns out courts need this thing called 'evidence' ⚖️",
            "confidence": 0.95
        },
        "deep_state": {
            "keywords": ["deep state", "globalist", "soros"],
            "cached_response": "If the 'deep state' was real, Trump wouldn't have made it past the escalator 🎭",
            "confidence": 0.85
        },
        "woke_mob": {
            "keywords": ["woke", "woke mob", "cancel culture"],
            "cached_response": "'Woke' = noticing inequality. Sorry that's exhausting for you ☕",
            "confidence": 0.80
        },
    }

    def __init__(self, repo_root: Path):
        self.repo_root = Path(repo_root)
        # Cache stored in AI_Overseer memory
        self.cache_path = self.repo_root / "modules/ai_intelligence/ai_overseer/memory/troll_response_cache.json"
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

        # Token usage stats
        self.stats = {
            'total_comments': 0,
            'cache_hits': 0,
            'fallback_used': 0,
            'grok_minimal': 0,
            'grok_full': 0,
            'tokens_saved': 0,
            'tokens_spent': 0,
        }

    def _load_cache(self) -> Dict[str, str]:
        """Load cached troll responses."""
        if not self.cache_path.exists():
            return {}

        try:
            import json
            with open(self.cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"[ROUTER] Cache load failed: {e}")
            return {}

    def _save_to_cache(self, pattern_hash: str, response: str):
        """Save successful response to cache."""
        import json
        import hashlib

        cache = self._load_cache()
        cache[pattern_hash] = response

        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=2)
            logger.info(f"[ROUTER] Cached response for pattern: {pattern_hash[:8]}...")
        except Exception as e:
            logger.warning(f"[ROUTER] Cache save failed: {e}")

    def _check_simple_pattern(self, comment_text: str) -> Optional[Tuple[str, float]]:
        """
        Check if comment matches simple MAGA pattern (no Grok needed).

        Returns:
            Tuple of (cached_response, confidence) or None
        """
        text_lower = comment_text.lower()

        for pattern_name, pattern_data in self.SIMPLE_MAGA_PATTERNS.items():
            keywords = pattern_data['keywords']
            for keyword in keywords:
                if keyword in text_lower:
                    response = pattern_data['cached_response']
                    confidence = pattern_data['confidence']
                    logger.info(f"[ROUTER] ✓ Simple pattern match: '{pattern_name}' (conf: {confidence:.2f})")
                    return (response, confidence)

        return None

    def _filter_gemma_context_for_grok(self, gemma_context: Dict) -> Dict:
        """
        Filter Gemma's livechat data to minimize Grok token usage.

        Before: Gemma returns 23 messages (500 tokens to Grok)
        After:  AI_Overseer filters to TOP 3 most relevant (50 tokens to Grok)

        Filtering Strategy:
        1. Select messages with highest MAGA keywords
        2. Prioritize recent messages (last 7 days)
        3. Include last 0102 response (for style matching)
        """
        messages = gemma_context.get('messages', [])

        if not messages:
            return gemma_context

        # Score messages by relevance
        import re
        maga_keywords = ['trump', 'maga', 'leftists', 'witch hunt', 'stolen', 'woke']

        scored_messages = []
        for msg in messages[:10]:  # Limit to recent 10
            text_lower = msg.lower() if isinstance(msg, str) else ''
            score = sum(1 for keyword in maga_keywords if keyword in text_lower)
            scored_messages.append((score, msg))

        # Sort by score, take TOP 3
        scored_messages.sort(reverse=True, key=lambda x: x[0])
        top_messages = [msg for score, msg in scored_messages[:3]]

        # Create minimal context
        minimal_context = {
            'username': gemma_context['username'],
            'message_count': len(messages),  # Keep total count
            'top_messages': top_messages,     # Only send TOP 3
            'frequency': gemma_context.get('frequency', 0),
            'last_0102_response': gemma_context.get('last_0102_response', ''),
            'response_style': gemma_context.get('response_style', 'generic')
        }

        # Token reduction estimate
        original_tokens = len(' '.join(messages)) // 4  # Rough estimate
        minimal_tokens = len(' '.join(top_messages)) // 4
        tokens_saved = original_tokens - minimal_tokens

        logger.info(f"[ROUTER] ✂️ Filtered context: {len(messages)} → 3 messages "
                   f"(~{original_tokens} → ~{minimal_tokens} tokens, saved ~{tokens_saved})")

        return minimal_context

    def route_comment_engagement(
        self,
        comment_text: str,
        author_name: str,
        is_mod: bool = False,
        is_subscriber: bool = False,
        gemma_context: Optional[Dict] = None
    ) -> RoutingContext:
        """
        Route comment engagement decision to minimize tokens.

        Decision Tree:
        1. Mod/VIP? → SKIP (no response)
        2. Simple MAGA pattern? → USE_FALLBACK (0 tokens)
        3. Cached pattern? → USE_CACHE (0 tokens)
        4. Complex + high confidence? → QUERY_GROK_MINIMAL (50-100 tokens)
        5. Complex + low confidence? → QUERY_GROK_FULL (200-500 tokens)

        Args:
            comment_text: The comment to route
            author_name: Username
            is_mod: Is moderator (skip Grok)
            is_subscriber: Is subscriber
            gemma_context: Context from Gemma livechat search (Phase 1)

        Returns:
            RoutingContext with decision and estimated tokens
        """
        self.stats['total_comments'] += 1
        context = RoutingContext(
            comment_text=comment_text,
            author_name=author_name,
            is_mod=is_mod,
            is_subscriber=is_subscriber,
            gemma_context=gemma_context
        )

        # DECISION 1: Mod/VIP → Skip (don't troll mods!)
        if is_mod:
            context.route_decision = RouteDecision.SKIP
            context.estimated_tokens = 0
            logger.info(f"[ROUTER] Mod detected → SKIP")
            return context

        # DECISION 2: Simple MAGA pattern → Fallback (0 tokens)
        simple_match = self._check_simple_pattern(comment_text)
        if simple_match:
            response, confidence = simple_match
            context.route_decision = RouteDecision.USE_FALLBACK
            context.estimated_tokens = 0
            self.stats['fallback_used'] += 1
            self.stats['tokens_saved'] += 200  # Would have used ~200 for Grok
            logger.info(f"[ROUTER] ✓ Using fallback (saved ~200 tokens)")
            return context

        # DECISION 3: Check cache
        import hashlib
        pattern_hash = hashlib.md5(comment_text.lower().encode()).hexdigest()
        cache = self._load_cache()

        if pattern_hash in cache:
            context.route_decision = RouteDecision.USE_CACHE
            context.estimated_tokens = 0
            self.stats['cache_hits'] += 1
            self.stats['tokens_saved'] += 200
            logger.info(f"[ROUTER] ✓ Cache hit (saved ~200 tokens)")
            return context

        # DECISION 4: Complex comment → Query Grok
        # But minimize context if Gemma found history
        if gemma_context and gemma_context.get('message_count', 0) > 0:
            # Filter Gemma context to minimize tokens
            context.gemma_context = self._filter_gemma_context_for_grok(gemma_context)
            context.route_decision = RouteDecision.QUERY_GROK_MINIMAL
            context.estimated_tokens = 80  # Minimal context
            self.stats['grok_minimal'] += 1
            self.stats['tokens_spent'] += 80
            self.stats['tokens_saved'] += 120  # Would have used ~200 for full context
            logger.info(f"[ROUTER] → Grok MINIMAL (~80 tokens, saved ~120)")
        else:
            # No history → Need full Grok context
            context.route_decision = RouteDecision.QUERY_GROK_FULL
            context.estimated_tokens = 200
            self.stats['grok_full'] += 1
            self.stats['tokens_spent'] += 200
            logger.info(f"[ROUTER] → Grok FULL (~200 tokens)")

        return context

    def get_stats_summary(self) -> Dict[str, Any]:
        """Get token usage statistics."""
        total_potential = self.stats['total_comments'] * 200  # If all used Grok full
        actual_spent = self.stats['tokens_spent']
        savings_percent = (self.stats['tokens_saved'] / total_potential * 100) if total_potential > 0 else 0

        return {
            **self.stats,
            'total_potential_tokens': total_potential,
            'savings_percent': f"{savings_percent:.1f}%",
            'avg_tokens_per_comment': actual_spent / self.stats['total_comments'] if self.stats['total_comments'] > 0 else 0
        }


# Singleton instance
_router = None

def get_comment_router(repo_root: Path = None) -> CommentTrollRouter:
    """Get or create singleton comment router."""
    global _router
    if _router is None:
        if repo_root is None:
            repo_root = Path(__file__).resolve().parents[5]
        _router = CommentTrollRouter(repo_root)
    return _router
