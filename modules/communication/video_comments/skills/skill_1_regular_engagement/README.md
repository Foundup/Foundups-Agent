# Skill 1: Regular Engagement - Integration Guide

**Sprint 4 Complete** ✅ - Standalone skill with 3-tier strategy ready for Sprint 5 router

## Quick Start

```python
from modules.communication.video_comments.skills.skill_1_regular_engagement import (
    RegularEngagementSkill,
    SkillContext
)

# Initialize skill
skill = RegularEngagementSkill()

# Execute with pre-generated LLM reply (Strategy 1)
result = skill.execute(SkillContext(
    user_id="user_123",
    username="RegularUser",
    comment_text="Bro got the dance moves! 🕺",
    classification="REGULAR",
    confidence=0.5,
    llm_reply="Haha yeah! The choreography is fire! 🔥"  # From Grok/LM Studio
))

print(result['reply_text'])  # "Haha yeah! The choreography is fire! 🔥"
print(result['strategy'])    # "llm_contextual"

# Execute without LLM (Strategy 2/3: BanterEngine or templates)
result = skill.execute(SkillContext(
    user_id="user_456",
    username="AnotherUser",
    comment_text="Great content!",
    classification="REGULAR",
    confidence=0.5,
    llm_reply=None  # No LLM reply - will use BanterEngine or templates
))

print(result['reply_text'])  # "Thanks for watching! 🎌" (or banter)
print(result['strategy'])    # "banter_engine" or "template_regular"
```

## Integration Checklist (Sprint 5)

### Step 1: Import Skill

```python
# intelligent_reply_generator.py (top of file)
from modules.communication.video_comments.skills.skill_1_regular_engagement import (
    RegularEngagementSkill,
    SkillContext
)
```

### Step 2: Initialize in `__init__`

```python
# IntelligentReplyGenerator.__init__()
def __init__(self, llm_host: str = "http://localhost:1234", repo_root: Path = None):
    # ... existing code ...

    # Initialize Skill 1 (Regular engagement)
    self.skill_1 = RegularEngagementSkill()
    logger.info("[REPLY-GEN] Skill 1 (Regular engagement) initialized")
```

### Step 3: Replace Lines 1039-1056

**OLD CODE** (lines 1039-1056):
```python
else:
    # REGULAR USER: Use LLM for contextual, meaningful replies
    # This is where "Bro got the dance moves" should get a relevant response
    llm_response = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
    if llm_response:
        return self._add_0102_signature(llm_response)

    # Fallback to BanterEngine if LLM unavailable
    if self.banter_engine:
        try:
            response = self.banter_engine.get_random_banter(theme=theme)
            if response:
                return self._add_0102_signature(response)
        except Exception as e:
            logger.warning(f"BanterEngine failed: {e}")

    # Ultimate fallback to template responses
    return self._add_0102_signature(random.choice(self.REGULAR_RESPONSES))
```

**NEW CODE** (Sprint 5):
```python
else:
    # REGULAR USER: Route to Skill 1 (Regular engagement)
    # Generate LLM reply if available (keep existing logic)
    llm_reply = self._generate_contextual_reply(comment_text, author_name, author_channel_id)

    result = self.skill_1.execute(SkillContext(
        user_id=author_channel_id,
        username=author_name,
        comment_text=comment_text,
        classification='REGULAR',
        confidence=profile.confidence if hasattr(profile, 'confidence') else 0.5,
        llm_reply=llm_reply,  # Can be None (skill will handle fallback)
        theme=theme,
        is_subscriber=profile.is_subscriber if hasattr(profile, 'is_subscriber') else False
    ))

    logger.info(f"[SKILL-1] Strategy: {result['strategy']}, Confidence: {result['confidence']}")
    return self._add_0102_signature(result['reply_text'])
```

### Step 4: Optional - Replace SUBSCRIBER Handling (Lines 1032-1037)

In the new 0/1/2 classification system, subscribers are classified as REGULAR (1✋). The SUBSCRIBER-specific code can be merged into Skill 1:

**OLD CODE** (lines 1032-1037):
```python
elif profile.commenter_type == CommenterType.SUBSCRIBER:
    # Try LLM for contextual subscriber response
    llm_response = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
    if llm_response:
        return self._add_0102_signature(llm_response)
    return self._add_0102_signature(random.choice(self.SUBSCRIBER_RESPONSES))
```

**NEW CODE** (Sprint 5 - merged into REGULAR handling):
```python
# Subscribers now handled by Skill 1 via is_subscriber flag
# No separate branch needed - same 3-tier strategy applies
```

### Step 5: Remove Deprecated Templates (Optional)

Lines 227-241 can be removed after Sprint 5 integration - now handled by Skill 1:
```python
# DELETE (after Sprint 5 integration):
SUBSCRIBER_RESPONSES = [...]
REGULAR_RESPONSES = [...]
```

## Testing Integration

### Before Integration (Verify Baseline)

```bash
# Run existing tests (should pass)
cd O:\Foundups-Agent
python modules/communication/video_comments/tests/test_classifier_pipeline.py
```

### After Integration (Verify Skill Router)

```python
# Add integration test to test_classifier_pipeline.py
def test_skill_1_integration():
    """Test 8: Verify Skill 1 integration with router"""
    print("\n=== TEST 8: Skill 1 Integration ===")

    classifier = get_classifier()
    skill_1 = RegularEngagementSkill()

    # Classify regular user
    result = classifier.classify_commenter("user_123", "TestUser")

    if result['classification'] == CommenterType.REGULAR:
        # Execute Skill 1 without LLM (template fallback)
        skill_result = skill_1.execute(SkillContext(
            user_id="user_123",
            username="TestUser",
            comment_text="Great video!",
            classification='REGULAR',
            confidence=result['confidence'],
            llm_reply=None  # Test fallback
        ))

        print(f"[TEST] Skill 1 reply: {skill_result['reply_text']}")
        print(f"[TEST] Strategy: {skill_result['strategy']}")
        print("[OK] Skill 1 integration works!")
        return True
    else:
        print("[FAIL] Classification not REGULAR")
        return False
```

## Backward Compatibility

**During Sprint 2-4**: Skill exists ALONGSIDE monolithic code (no breaking changes)

**Sprint 5**: Feature flag for gradual rollout:

```python
# intelligent_reply_generator.py
USE_SKILL_ROUTER = os.getenv('USE_SKILL_ROUTER', 'false').lower() == 'true'

if USE_SKILL_ROUTER:
    # Use Skill 1
    llm_reply = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
    result = self.skill_1.execute(SkillContext(..., llm_reply=llm_reply))
    return self._add_0102_signature(result['reply_text'])
else:
    # Legacy monolithic code (fallback)
    llm_response = self._generate_contextual_reply(comment_text, author_name, author_channel_id)
    if llm_response:
        return self._add_0102_signature(llm_response)
    # ... (existing fallback logic)
```

## LLM Integration Pattern

### Current (Sprint 4): Pre-Generated LLM Replies

Following Skill 0 pattern, LLM replies are **pre-generated by caller** and passed via `context.llm_reply`:

```python
# Caller generates LLM reply
llm_reply = self._generate_contextual_reply(comment_text, author_name, author_channel_id)

# Skill 1 receives it (can be None)
result = skill.execute(SkillContext(..., llm_reply=llm_reply))
```

**Advantages:**
- Lightweight skill (no complex LLM dependencies)
- Caller controls LLM strategy (Grok vs LM Studio)
- Follows established Skill 0 pattern
- Easy to test (mock LLM replies)

### Future (Sprint 6+): Embedded LLM Integration

For full self-containment, embed `_generate_contextual_reply()` logic directly in skill:

```python
class RegularEngagementSkill:
    def __init__(self):
        self._grok_connector = None  # Lazy-loaded
        self._lm_studio_available = False  # Lazy-loaded
        self._banter_engine = None

    def execute(self, context: SkillContext) -> Dict:
        # STRATEGY 1: Generate LLM reply internally (new)
        if not context.llm_reply:
            context.llm_reply = self._generate_llm_reply(context)

        if context.llm_reply:
            return {'reply_text': context.llm_reply, 'strategy': 'llm_contextual', ...}

        # STRATEGY 2: BanterEngine fallback (existing)
        ...
```

**Migration Path:** Gradual - add embedded LLM while preserving pre-generated support

## BanterEngine Integration

### Lazy Loading Pattern

BanterEngine is **lazy-loaded** on first use:

```python
# First execution - load BanterEngine
result = skill.execute(context)  # BanterEngine loaded
# BanterEngine loaded: [SKILL-1] BanterEngine loaded successfully

# Subsequent executions - reuse cached instance
result = skill.execute(context)  # Instant (no reload)
```

### Graceful Degradation

If BanterEngine unavailable, skill automatically falls back to templates:

```python
# BanterEngine missing/broken
result = skill.execute(context)
# Fallback: [SKILL-1] Template fallback (strategy=template_regular)
```

## Performance Considerations

- **Skill overhead**: <1ms (strategy selection + random choice)
- **BanterEngine load**: ~50ms (one-time lazy load)
- **Total execution**: <5ms (LLM pre-generated, local logic only)
- **Memory**: ~5KB (10 template strings) + BanterEngine (if loaded)
- **Scalability**: O(1) - constant time regardless of comment volume

## Troubleshooting

### Issue: ModuleNotFoundError

```python
# Solution: Add skills directory to PYTHONPATH
import sys
sys.path.insert(0, 'O:/Foundups-Agent')
```

### Issue: Unicode Encoding Errors (Windows)

```python
# Solution: UTF-8 enforcement (WSP 90)
import io, sys
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
```

### Issue: BanterEngine Not Available

```
[WARN] BanterEngine not available: ...
```

**Expected behavior**: Skill automatically falls back to template responses. No action required.

### Issue: LLM Reply None

**Expected behavior**: If `context.llm_reply` is None, skill uses BanterEngine or templates. This is normal when Grok/LM Studio unavailable.

## Rollback Plan (If Integration Fails)

1. **Revert lines 1039-1056**: Restore original monolithic code
2. **Keep skill files**: No cleanup needed (skill is standalone)
3. **Disable feature flag**: Set `USE_SKILL_ROUTER=false`

## Next Steps (Post-Integration)

### Sprint 5: Complete Router
- Integrate Skills 0, 1, 2 into unified ReplySkillRouter
- Performance testing (<5ms classification + execution)
- Gradual rollout with feature flag

### Sprint 6+: LLM Enhancement
- Embed `_generate_contextual_reply()` in Skill 1 (self-contained)
- Add semantic variation prompts (ANTI-REGURGITATION)
- Add personalization context (comment history)
- Add duplicate detection (CommenterHistoryStore)

### Sprint 6+: Learning Layer
- Add metric tracking per skill execution
- A/B test LLM vs Banter vs Templates
- Learn which responses get the most engagement
- Multi-language support

## Support

**Documentation**: See [SKILL.md](SKILL.md) for detailed architecture
**Tests**: Run `python modules/communication/video_comments/skills/skill_1_regular_engagement/tests/test_skill_1.py` (from project root)
**Issues**: Check `modules/communication/video_comments/ModLog.md` for known issues
