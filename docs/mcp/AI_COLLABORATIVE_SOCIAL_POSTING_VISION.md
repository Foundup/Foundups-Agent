# AI-Collaborative Social Media Posting Architecture
**Vision**: QWEN/Gemma/UI-TARS collaborative decision-making with Occam's Razor & First Principles

**Date**: 2025-10-20
**Status**: Design Phase
**Related**: MCP Playwright, UI-TARS Desktop, Vision DAE integration

---

## Current Architecture (What IS Happening)

```
YouTube DAE detects stream
  ↓
QWEN Intelligence Layer:
  - Channel prioritization (QWEN-SCORE)
  - Duplicate analysis (QWEN-SOCIAL) ⚠️ Cache bug
  - Posting decision (QWEN-DECISION: ['linkedin', 'x_twitter'])
  - Stagger timing (QWEN-STAGGER: 15s delay)
  ↓
PlatformPostingService:
  - Direct Selenium browser automation
  - linkedin_agent/anti_detection_poster.py
  - x_twitter/x_anti_detection_poster.py
  ↓
Result: Posted (no AI verification)
```

**Problems**:
1. **QWEN manages strategy BUT NOT execution** - Selenium is dumb automation
2. **No AI review of post content** - QWEN approves, but doesn't improve
3. **No execution verification** - Did it actually post? Screenshot verification?
4. **No A/B testing** - MCP Playwright vs Selenium (which performs better?)
5. **Duplicate prevention broken** - DB cache staleness (CRITICAL)

---

## Vision: AI-First Collaborative Architecture

### Phase 1: QWEN Strategic Decision Layer ✅ (Exists)
**Responsibility**: Analyze context, make strategic decisions

```python
# QWEN analyzes stream detection event
qwen_strategy = {
    'duplicate_check': 'QUERY_DB',  # Don't trust stale cache
    'platforms': ['linkedin', 'x_twitter'],
    'stagger_delay': 15,  # seconds between platforms
    'content_enhancement': True,  # Improve post before sending
    'verification_required': True  # Screenshot + visual confirmation
}
```

**Occam's Razor**: QWEN decides minimum viable actions (don't post if duplicate)

---

### Phase 2: Gemma Fast Pattern Matching (NEW)
**Responsibility**: Binary classification (50-100ms decisions)

```python
# Gemma fast checks BEFORE posting
gemma_checks = {
    'duplicate_in_db': gemma.query_db(video_id),  # Fast SQL
    'content_quality': gemma.score_post_text(title),  # Pattern match
    'platform_ready': gemma.check_rate_limits(),  # Health status
    'proceed': True/False  # GO/NO-GO decision
}
```

**First Principles**: Fastest AI makes fastest decisions (duplicate check = pattern match, not logic)

---

### Phase 3: QWEN Content Enhancement (NEW)
**Responsibility**: Improve post content BEFORE execution

```python
# QWEN enhances post text
enhanced_post = qwen.enhance_content({
    'original': 'Move2Japan [JAPAN] is LIVE!',
    'context': {
        'channel': 'Move2Japan',
        'typical_viewers': 2000,
        'stream_category': 'Japan Walking Tour'
    }
})

# Result:
enhanced_post = {
    'linkedin': '🗾 Move2Japan is LIVE - Join 2K+ viewers exploring Tokyo! [LINK]',
    'x_twitter': '🔴 LIVE NOW: Tokyo Walking Tour with @Move2Japan 🗾✨ [LINK]',
    'engagement_score': 8.5  # QWEN prediction
}
```

**First Principles**: AI writes better than templates

---

### Phase 4: UI-TARS Desktop Execution (NEW - MCP Integration)
**Responsibility**: AI-controlled browser posting with visual verification

```python
# UI-TARS controls posting via MCP Playwright
ui_tars_result = await mcp_playwright.post_to_linkedin({
    'content': enhanced_post['linkedin'],
    'page_id': '104834798',
    'verification': {
        'screenshot': True,
        'vision_dae_check': True,  # Vision DAE analyzes screenshot
        'retry_on_failure': True
    }
})

# Vision DAE verifies screenshot
vision_verification = vision_dae.analyze_screenshot({
    'screenshot': ui_tars_result.screenshot,
    'expected': 'Post successful confirmation',
    'confidence_threshold': 0.85
})
```

**First Principles**: AI verifies AI actions (self-correction loop)

---

### Phase 5: A/B Testing Framework (NEW)
**Responsibility**: QWEN decides which execution method to use

```python
# QWEN manages A/B test
execution_method = qwen.select_posting_method({
    'methods': {
        'selenium': {'success_rate': 0.65, 'speed': 'fast', 'detection_risk': 'medium'},
        'mcp_playwright': {'success_rate': 0.92, 'speed': 'medium', 'detection_risk': 'low'},
        'ui_tars_desktop': {'success_rate': 0.98, 'speed': 'slow', 'detection_risk': 'very_low'}
    },
    'context': {
        'platform': 'linkedin',
        'recent_failures': 3,  # Selenium failing lately
        'priority': 'reliability'  # vs 'speed'
    }
})

# Result: qwen.decision = 'ui_tars_desktop'  # Most reliable
```

**Occam's Razor**: Use simplest method that works (Selenium if 100% success, UI-TARS if failures detected)

---

## Complete Flow: AI Collaboration

```
1. [YOUTUBE DAE] Stream detected: Move2Japan dON8mcyRRZU

2. [GEMMA] Fast duplicate check (50ms)
   └─> Query DB directly (not cache)
   └─> Result: NOT IN DB (safe to post)

3. [QWEN] Strategic analysis (200-500ms)
   ├─> Channel priority: Move2Japan = HIGH
   ├─> Platforms: ['linkedin', 'x_twitter']
   ├─> Content enhancement: ENABLED
   ├─> Execution method: A/B test decision
   └─> Verification: Vision DAE screenshot check

4. [QWEN] Content enhancement
   ├─> Original: "Move2Japan [JAPAN] is LIVE!"
   └─> Enhanced: "🗾 Move2Japan LIVE - Join 2K+ viewers exploring Tokyo!"

5. [QWEN] Select execution method
   ├─> Selenium: 3 recent failures → REJECT
   ├─> MCP Playwright: 92% success → CONSIDER
   └─> UI-TARS Desktop: 98% success → SELECT

6. [UI-TARS via MCP Playwright] Execute posting
   ├─> Open LinkedIn via Playwright
   ├─> Post enhanced content
   ├─> Take screenshot
   └─> Return result + screenshot

7. [VISION DAE] Verify posting (via MCP)
   ├─> Analyze screenshot
   ├─> Confirm "Post successful" UI element
   └─> Confidence: 0.96 ✅

8. [GEMMA] Mark as posted in DB (fast write)
   └─> video_id: dON8mcyRRZU, platform: linkedin, status: SUCCESS

9. [QWEN] Learn from outcome
   └─> ui_tars_desktop: +1 success (update A/B test metrics)
```

---

## Implementation Roadmap

### Immediate (Fix Duplicate Bug)
- [ ] **Gemma DB Query**: Replace stale cache with direct SQL
- [ ] **QWEN cache strategy**: Decide when to trust cache vs query DB
- [ ] **Mark failed posts**: Already fixed in refactored_posting_orchestrator.py

### Sprint 1: Content Enhancement
- [ ] **QWEN skill**: `social_media_content_enhancement.md`
- [ ] **Integration point**: DuplicatePreventionManager.qwen_enhance_content()
- [ ] **A/B test**: Enhanced vs template posts (engagement metrics)

### Sprint 2: UI-TARS Execution
- [ ] **MCP Playwright integration**: Replace anti_detection_poster.py
- [ ] **UI-TARS desktop skill**: `ui_tars_social_posting.md`
- [ ] **Vision DAE verification**: Screenshot analysis via MCP

### Sprint 3: A/B Testing Framework
- [ ] **QWEN execution selector**: Choose Selenium vs Playwright vs UI-TARS
- [ ] **Metrics collection**: Success rate, speed, detection events
- [ ] **Auto-optimization**: QWEN learns which method works best per platform

---

## Skills Architecture

```
.claude/skills/
├── social_media_ai_orchestration/
│   ├── SKILL.md                           # Core AI collaboration workflow
│   ├── qwen_strategy_layer.md             # Strategic decision templates
│   ├── gemma_fast_checks.md               # Binary classification patterns
│   ├── content_enhancement_prompts.md     # QWEN post improvement
│   └── ui_tars_execution_protocol.md      # MCP Playwright integration
```

---

## Success Metrics

**Token Efficiency**:
- Current: 15K+ tokens per posting cycle (Selenium debugging)
- Target: 200-500 tokens (QWEN strategy) + 50-100 tokens (Gemma checks)
- Improvement: **30-75x reduction**

**Reliability**:
- Current: 65% success rate (Selenium failures)
- Target: 98% success rate (UI-TARS + Vision DAE verification)
- Improvement: **50% increase**

**Intelligence**:
- Current: Dumb automation (no content improvement)
- Target: AI-enhanced posts (QWEN writes better copy)
- Improvement: **Infinite** (human-level writing vs templates)

---

## First Principles Applied

1. **Occam's Razor**:
   - Gemma handles fast/simple decisions (duplicate check = SQL query)
   - QWEN handles complex decisions (content enhancement, A/B testing)
   - UI-TARS handles execution (most reliable method)

2. **Separation of Concerns**:
   - Strategy (QWEN) ≠ Execution (UI-TARS) ≠ Verification (Vision DAE)
   - Each AI does what it's best at

3. **Self-Correction Loop**:
   - Vision DAE verifies UI-TARS actions
   - QWEN learns from outcomes
   - System improves over time

4. **No Vibecoding**:
   - Don't fix duplicate bug with manual logic
   - Let QWEN decide cache strategy
   - Let Gemma handle DB queries

---

**Next Steps**: Create `social_media_ai_orchestration` skill and integrate MCP Playwright.
