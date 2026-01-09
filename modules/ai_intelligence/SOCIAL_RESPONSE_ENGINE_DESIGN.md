# Social Response Engine - Modular Architecture Design

**Status:** PROPOSED (2025-12-31)
**WSP Reference:** WSP 72 (Module Independence), WSP 96 (Skills Pattern)

---

## Problem Statement

Current response generation is embedded in `video_comments/intelligent_reply_generator.py` (~2000+ lines).
This is NOT reusable by future social media modules:
- LinkedIn comment engagement
- Facebook engagement
- X/Twitter replies
- Community forum responses

## Proposed Architecture

```
modules/
  ai_intelligence/
    social_response_engine/           # NEW: Shared response module
      src/
        response_generator.py         # Core LLM-based response generation
        context_enricher.py           # Real-time context (Grok → X search)
        cross_promoter.py             # Channel/account cross-promotion
        age_aware_responder.py        # Time-gap aware responses
        anti_regurgitation.py         # Duplicate/pattern detection
        commenter_profiler.py         # 012 classification (troll/regular/mod)
      INTERFACE.md
      README.md
      tests/
```

## Key Components

### 1. ResponseGenerator (Core)
```python
class ResponseGenerator:
    """Platform-agnostic response generation."""

    def generate(
        self,
        comment_text: str,
        author: AuthorProfile,
        context: ResponseContext,
        platform: Platform,  # YOUTUBE | LINKEDIN | FACEBOOK | X
    ) -> GeneratedResponse:
        """Generate contextual response."""
```

### 2. ContextEnricher (Real-time Search)
```python
class ContextEnricher:
    """Enrich response context with real-time data."""

    async def enrich(
        self,
        topic: str,
        search_source: str = "x",  # X, news, etc.
    ) -> EnrichedContext:
        """
        For political comments, search X for latest context.
        Example: "Trump" → Search X for latest Trump news → Include in prompt.
        """
```

### 3. CrossPromoter
```python
class CrossPromoter:
    """Cross-platform promotion logic."""

    PROMO_RULES = {
        'undaodu': {'promote': '@Move2Japan', 'probability': 0.3},
        'foundups': {'promote': '@Move2Japan', 'probability': 0.3},
        'move2japan': {'promote': None},  # Don't self-promote
    }
```

### 4. AgeAwareResponder
```python
class AgeAwareResponder:
    """Handle time-gap aware responses."""

    AGE_TIERS = {
        'recent': (0, 90),       # "Thanks for commenting!"
        'months': (90, 365),     # "Better late than never!"
        'years_1_3': (365, 1095), # "Going through the archives!"
        'years_3_plus': (1095, 1825), # "Hope you're still around!"
        'years_5_plus': (1825, None),  # "Wow, 6 years ago! @Move2Japan"
    }
```

## Integration Pattern

```python
# In YouTube comment engagement:
from modules.ai_intelligence.social_response_engine import ResponseEngine

engine = ResponseEngine(platform="youtube")
response = await engine.generate(
    comment_text="What do you think about Trump?",
    author=author_profile,
    context=ResponseContext(
        channel="move2japan",
        comment_age_days=2190,  # 6 years
        enrich_with_search=True,  # Search X for latest Trump news
    )
)

# In LinkedIn engagement (future):
engine = ResponseEngine(platform="linkedin")
response = await engine.generate(...)
```

## Benefits

1. **Reusability** - One engine for all social platforms
2. **Real-time context** - Grok searches X before responding to political comments
3. **Cross-promotion** - Automatic @Move2Japan promotion on other channels
4. **Age awareness** - Different responses for 90-day vs 6-year old comments
5. **Anti-regurgitation** - Centralized duplicate detection

## Migration Path

1. **Phase 1** (Current): Enhanced skill_3_old_comment_engagement with age tiers + cross-promo
2. **Phase 2**: Extract response logic from intelligent_reply_generator.py
3. **Phase 3**: Create social_response_engine module
4. **Phase 4**: Integrate with LinkedIn/Facebook engagement

## Real-time Context Example

**Comment:** "What's your thoughts on Trump? Is democracy screwed?"

**Current behavior:** Generic LLM response

**Proposed behavior:**
1. ContextEnricher detects political topic ("Trump", "democracy")
2. Grok searches X for "Trump democracy latest news"
3. Top 3 results summarized and added to LLM prompt
4. Response includes current context: "Given the recent [X news], I think..."

---

**Document Author:** 0102 autonomous operation
**Next Steps:** Implement ContextEnricher with Grok/X search integration
