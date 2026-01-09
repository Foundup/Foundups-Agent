# Skill 2: Moderator Appreciation - Integration Guide

**Sprint 3 Enhanced Complete** ✅ - Standalone skill with database integration ready for Sprint 5 router

## Quick Start

```python
from modules.communication.video_comments.skills.skill_2_moderator_appreciation import (
    ModeratorAppreciationSkill,
    SkillContext
)

# Initialize skill
skill = ModeratorAppreciationSkill()

# Execute with context
result = skill.execute(SkillContext(
    user_id="mod_123",
    username="LegendMod",
    comment_text="Great stream!",
    classification="MODERATOR",
    confidence=1.0
))

print(result['reply_text'])  # "Thanks @LegendMod! 25 trolls whacked - LEGEND status! 💪"
```

## Integration Checklist (Sprint 5)

### Step 1: Import Skill

```python
# intelligent_reply_generator.py (top of file)
from modules.communication.video_comments.skills.skill_2_moderator_appreciation import (
    ModeratorAppreciationSkill,
    SkillContext
)
```

### Step 2: Initialize in `__init__`

```python
# IntelligentReplyGenerator.__init__()
def __init__(self, llm_host: str = "http://localhost:1234", repo_root: Path = None):
    # ... existing code ...

    # Initialize Skill 2 (Moderator appreciation)
    self.skill_2 = ModeratorAppreciationSkill()
    logger.info("[REPLY-GEN] Skill 2 (Moderator appreciation) initialized")
```

### Step 3: Replace Lines 1031-1040

**OLD CODE** (lines 1031-1040):
```python
elif profile.commenter_type == CommenterType.MODERATOR:
    # Simplified appreciation for moderators
    mod_responses = [
        "Thanks for keeping the chat clean! 🛡️",
        "Appreciate the mod support! 💪",
        "Thanks for holding it down! 🙏",
    ]
    reply = random.choice(mod_responses)
    logger.info("[REPLY-GEN] Moderator appreciation")
    return self._add_0102_signature(reply)
```

**NEW CODE** (Sprint 5):
```python
elif profile.commenter_type == CommenterType.MODERATOR:
    # Route to Skill 2 (Moderator appreciation)
    result = self.skill_2.execute(SkillContext(
        user_id=author_channel_id,
        username=author_name,
        comment_text=comment_text,
        classification='MODERATOR',
        confidence=1.0
    ))

    logger.info(f"[SKILL-2] Strategy: {result['strategy']}, Confidence: {result['confidence']}")
    return self._add_0102_signature(result['reply_text'])
```

### Step 4: Remove MOD_RESPONSES (Optional)

Lines 1031-1035 can be removed - now handled by Skill 2:
```python
# DELETE (after Sprint 5 integration):
mod_responses = [
    "Thanks for keeping the chat clean! 🛡️",
    "Appreciate the mod support! 💪",
    "Thanks for holding it down! 🙏",
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
def test_skill_2_integration():
    """Test 7: Verify Skill 2 integration with router"""
    print("\n=== TEST 7: Skill 2 Integration ===")

    classifier = get_classifier()
    skill_2 = ModeratorAppreciationSkill()

    # Classify moderator
    result = classifier.classify_commenter("mod_123", "TestMod")

    if result['classification'] == CommenterType.MODERATOR:
        # Execute Skill 2
        skill_result = skill_2.execute(SkillContext(
            user_id="mod_123",
            username="TestMod",
            comment_text="Great stream!",
            classification='MODERATOR',
            confidence=result['confidence']
        ))

        print(f"[TEST] Skill 2 reply: {skill_result['reply_text']}")
        print("[OK] Skill 2 integration works!")
        return True
    else:
        print("[FAIL] Classification not MODERATOR")
        return False
```

## Backward Compatibility

**During Sprint 2-4**: Skill exists ALONGSIDE monolithic code (no breaking changes)

**Sprint 5**: Feature flag for gradual rollout:

```python
# intelligent_reply_generator.py
USE_SKILL_ROUTER = os.getenv('USE_SKILL_ROUTER', 'false').lower() == 'true'

if USE_SKILL_ROUTER:
    # Use Skill 2
    result = self.skill_2.execute(context)
    return self._add_0102_signature(result['reply_text'])
else:
    # Legacy monolithic code (fallback)
    reply = random.choice(mod_responses)
    return self._add_0102_signature(reply)
```

## Database Integration

### ChatRulesDB Schema

Skill 2 queries moderator stats from `chat_rules/src/database.py`:

```sql
SELECT whacks_count, level, total_points, combo_multiplier
FROM moderators
WHERE user_id = ?
```

**Fields Used:**
- `whacks_count`: Number of trolls whacked by this moderator
- `level`: Moderator tier (ROOKIE, MVP, LEGEND, ELITE)
- `total_points`: Total gamification points
- `combo_multiplier`: Current streak multiplier

### Personalized Response Format

```python
# Example with 25 whacks, LEGEND level
"Thanks @LegendMod! 25 trolls whacked - LEGEND status! 💪"

# Example with 100 whacks, ELITE level
"ELITE @EliteMod with 100 whacks! Legend! ⭐"
```

### Fallback Behavior

If database unavailable or moderator has no stats:
```python
# Graceful degradation to template appreciation
"Thanks for keeping the chat clean! 🛡️"
```

## Performance Considerations

- **Skill overhead**: ~2ms (database query + method call)
- **Total execution**: <10ms (database lookup + template selection)
- **Memory**: +5KB (skill instance + templates) - negligible
- **Scalability**: O(1) - indexed database lookup
- **Database**: Lazy-loaded (initialized only when needed)

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

### Issue: ChatRulesDB Not Available

```
[WARN] Failed to load chat_rules database
```

**Expected behavior**: Skill automatically falls back to template appreciation. No action required.

### Issue: Moderator Has No Stats

**Expected behavior**: Skill uses template appreciation (Strategy 2 fallback). This is normal for new moderators who haven't whacked any trolls yet.

## Rollback Plan (If Integration Fails)

1. **Revert lines 1031-1040**: Restore original monolithic code
2. **Keep skill files**: No cleanup needed (skill is standalone)
3. **Disable feature flag**: Set `USE_SKILL_ROUTER=false`

## Next Steps (Post-Integration)

### Sprint 5: Complete Router
- Integrate Skills 0, 1, 2 into unified router
- Create ReplySkillRouter class
- Performance testing (<5ms classification + execution)

### Sprint 6+: Learning Layer
- Add metric tracking per skill execution
- A/B test appreciation styles
- Learn from moderator engagement patterns
- Multi-language support

## Support

**Documentation**: See [SKILL.md](SKILL.md) for detailed architecture
**Tests**: Run `python modules/communication/video_comments/skills/skill_2_moderator_appreciation/tests/test_skill_2.py` (from project root)
**Issues**: Check `modules/communication/video_comments/ModLog.md` for known issues
