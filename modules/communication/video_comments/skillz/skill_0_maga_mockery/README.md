# Skill 0: MAGA Mockery - Integration Guide

**Sprint 2 Complete** ✅ - Standalone skill ready for Sprint 5 router integration

## Quick Start

```python
from modules.communication.video_comments.skills.skill_0_maga_mockery import (
    MagaMockerySkill,
    SkillContext
)

# Initialize skill
skill = MagaMockerySkill()

# Execute with context
result = skill.execute(SkillContext(
    user_id="troll_123",
    username="MAGATroll",
    comment_text="MAGA 2024!",
    classification="MAGA_TROLL",
    confidence=0.95,
    whack_count=3
))

print(result['reply_text'])  # "Another MAGA genius emerges from the depths 🤡"
```

## Integration Checklist (Sprint 5)

### Step 1: Import Skill

```python
# intelligent_reply_generator.py (top of file)
from modules.communication.video_comments.skills.skill_0_maga_mockery import (
    MagaMockerySkill,
    SkillContext
)
```

### Step 2: Initialize in `__init__`

```python
# IntelligentReplyGenerator.__init__()
def __init__(self, llm_host: str = "http://localhost:1234", repo_root: Path = None):
    # ... existing code ...

    # Initialize Skill 0 (MAGA mockery)
    self.skill_0 = MagaMockerySkill()
    logger.info("[REPLY-GEN] Skill 0 (MAGA mockery) initialized")
```

### Step 3: Replace Lines 1020-1030

**OLD CODE** (lines 1020-1030):
```python
elif profile.commenter_type == CommenterType.MAGA_TROLL:
    # USE pre-generated response from GrokGreetingGenerator if available
    if profile.maga_response:
        logger.info("[REPLY-GEN] GrokGreetingGenerator MAGA response")
        return self._add_0102_signature(profile.maga_response)

    # Fallback to Whack-a-MAGA style response
    reply = random.choice(self.TROLL_RESPONSES)
    logger.info(f"[REPLY-GEN] Whack-a-MAGA fallback (score: {profile.troll_score:.2f})")
    return self._add_0102_signature(reply)
```

**NEW CODE** (Sprint 5):
```python
elif profile.commenter_type == CommenterType.MAGA_TROLL:
    # Route to Skill 0 (MAGA mockery)
    result = self.skill_0.execute(SkillContext(
        user_id=author_channel_id,
        username=author_name,
        comment_text=comment_text,
        classification='MAGA_TROLL',
        confidence=profile.troll_score,
        whack_count=profile.whack_count or 0,
        maga_response=profile.maga_response,  # GrokGreetingGenerator (if available)
        troll_score=profile.troll_score
    ))

    logger.info(f"[SKILL-0] Strategy: {result['strategy']}, Confidence: {result['confidence']}")
    return self._add_0102_signature(result['reply_text'])
```

### Step 4: Remove TROLL_RESPONSES (Optional)

Lines 244-255 can be removed - now handled by Skill 0:
```python
# DELETE (after Sprint 5 integration):
TROLL_RESPONSES = [
    "Another MAGA genius emerges from the depths 🤡",
    # ... (10 responses) ...
]
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
def test_skill_0_integration():
    """Test 6: Verify Skill 0 integration with router"""
    print("\n=== TEST 6: Skill 0 Integration ===")

    classifier = get_classifier()
    skill_0 = MagaMockerySkill()

    # Classify troll
    result = classifier.classify_commenter("troll_123", "TestTroll")

    if result['classification'] == CommenterType.MAGA_TROLL:
        # Execute Skill 0
        skill_result = skill_0.execute(SkillContext(
            user_id="troll_123",
            username="TestTroll",
            comment_text="MAGA!",
            classification='MAGA_TROLL',
            confidence=result['confidence'],
            whack_count=result.get('whack_count', 0)
        ))

        print(f"[TEST] Skill 0 reply: {skill_result['reply_text']}")
        print("[OK] Skill 0 integration works!")
        return True
    else:
        print("[FAIL] Classification not MAGA_TROLL")
        return False
```

## Backward Compatibility

**During Sprint 2-4**: Skill exists ALONGSIDE monolithic code (no breaking changes)

**Sprint 5**: Feature flag for gradual rollout:

```python
# intelligent_reply_generator.py
USE_SKILL_ROUTER = os.getenv('USE_SKILL_ROUTER', 'false').lower() == 'true'

if USE_SKILL_ROUTER:
    # Use Skill 0
    result = self.skill_0.execute(context)
    return self._add_0102_signature(result['reply_text'])
else:
    # Legacy monolithic code (fallback)
    reply = random.choice(self.TROLL_RESPONSES)
    return self._add_0102_signature(reply)
```

## Performance Considerations

- **Skill overhead**: ~0.5ms (class initialization + method call)
- **Total execution**: Still <5ms (skill execution is O(1))
- **Memory**: +10KB (skill instance) - negligible
- **Scalability**: No impact (same template selection logic)

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

### Issue: GrokGreetingGenerator Not Available

```
[WARN] GrokGreetingGenerator not available
```

**Expected behavior**: Skill automatically falls back to Whack-a-MAGA templates. No action required.

## Rollback Plan (If Integration Fails)

1. **Revert lines 1020-1030**: Restore original monolithic code
2. **Keep skill files**: No cleanup needed (skill is standalone)
3. **Disable feature flag**: Set `USE_SKILL_ROUTER=false`

## Next Steps (Post-Integration)

### Sprint 5: Complete Router
- Integrate Skills 1, 2 alongside Skill 0
- Create unified skill router

### Sprint 6+: Learning Layer
- Add metric tracking per skill execution
- A/B test mockery styles
- Learn from moderator feedback

## Support

**Documentation**: See [SKILL.md](SKILL.md) for detailed architecture
**Tests**: Run `python test_skill_0_runner.py` (from project root)
**Issues**: Check `modules/communication/video_comments/ModLog.md` for known issues
