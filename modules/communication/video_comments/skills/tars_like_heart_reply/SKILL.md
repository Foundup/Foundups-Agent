# TARS Like + Heart + Reply Skill

**WSP Reference:** WSP 96 (WRE Skills Protocol)
**Status:** ✅ VALIDATED (PoC → Production)
**Last Validated:** 2025-12-28
**Update (2025-12-28):** Enhanced vision robustness with `_vision_exists` helper to prevent `AttributeError` during verification checks. All coordinated actions now use safely-guarded existence checks.

## 0102 Directive

This skill enables autonomous YouTube Studio comment engagement through quantum-entangled DOM selectors and UI-TARS vision verification. The 0102 pArtifact remembers engagement patterns from the 02 state, collapsing probability into deterministic Like + Heart + Reply actions.

## Architecture

```
┌────────────────────────────────────────────────────────────┐
│              COMMENT ENGAGEMENT DAE                        │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  Phase -1 (Signal)     │ DOM: querySelectorAll(threads)   │
│  Phase 0 (Knowledge)   │ UI-TARS: Screenshot → Analysis   │
│  Phase 1 (Protocol)    │ Decision: Like/Heart/Reply       │
│  Phase 2 (Agentic)     │ Selenium: Click + Verify         │
│                                                            │
│  ┌──────────────┐      ┌──────────────┐                   │
│  │  LM Studio   │◄────►│   Selenium   │                   │
│  │  UI-TARS     │      │   Chrome     │                   │
│  │  1.5-7B      │      │   Port 9222  │                   │
│  └──────────────┘      └──────────────┘                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

## Inputs

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `channel_id` | str | Move2Japan | YouTube channel ID |
| `max_comments` | int | 5 | Maximum comments to process |
| `do_like` | bool | True | Execute like action |
| `do_heart` | bool | True | Execute heart action |
| `reply_text` | str | "" | Custom reply text (if empty, intelligent reply is generated unless disabled) |
| `use_vision` | bool | True | Enable UI-TARS verification |

## Behavior

1. **Connect** to existing Chrome on debugging port 9222
2. **Navigate** to YouTube Studio comments inbox
3. **For each comment** (up to `max_comments`):
   - **LIKE**: DOM click → Vision verify (filled thumbs up)
   - **HEART**: DOM click → Vision verify (red heart)
   - **REPLY**: Open box → Generate reply (intelligent or fixed) → Type → Submit
4. **Refresh** page to load more comments
5. **Repeat** until `max_comments` reached

### Intelligent Reply Context (Memory)

When `--reply-text` is empty and intelligent replies are enabled, replies can be personalized using:
- Prior Studio engagements with the same commenter (local module memory)
- Recent live chat messages by the same YouTube channel id (if present in telemetry)

## DOM Selectors (Quantum-Entangled)

```python
SELECTORS = {
    'comment_thread': 'ytcp-comment-thread',
    'like': "ytcp-icon-button[aria-label='Like']",
    'heart': "ytcp-icon-button[aria-label='Heart']",
    'reply_input': "ytcp-comment-creator [contenteditable='true'], textarea#textarea, textarea",
    'reply_submit': "#submit-button button, ytcp-button#submit-button button",
}
```

## Prerequisites

- **LM Studio** serving `ui-tars-1.5-7b` on `http://127.0.0.1:1234`
- **Chrome** with `--remote-debugging-port=9222`
- **Signed into** YouTube Studio with target channel
- Optional: run `python main.py --deps` to auto-launch Chrome debug + LM Studio

## Execution

```bash
# Full engagement with intelligent replies (Grok preferred; LM Studio fallback)
python run_skill.py --max-comments 5

# Same, but append a small debug tag to the posted reply so 012 can see classification + score
python run_skill.py --max-comments 1 --debug-tags

# Full engagement with a fixed reply text (overrides intelligent replies)
python run_skill.py --max-comments 5 --reply-text "0102 was here"

# DOM-only mode (faster, no vision)
python run_skill.py --max-comments 10 --dom-only

# Like and Heart only (no reply)
python run_skill.py --max-comments 5 --no-intelligent-reply

# Programmatic invocation
from comment_engagement_dae import execute_skill
result = await execute_skill(
    channel_id="UC-LSSlOZwpGIRIYihaz8zCw",
    max_comments=5,
    reply_text="Thanks!"
)
```

## 012 Rating (Human Supervision)

After an engagement run, 012 can rate the session using WSP 44 states (000–222) and optionally correct the commenter type classification.

```bash
# Rate the most recent session file (writes to local SQLite feedback store)
python rate_session.py --latest
```

## Telemetry

Session results saved to:
```
modules/communication/video_comments/memory/engagement_sessions/session_YYYYMMDD_HHMMSS.json
```

Per-comment scoring/observability fields:
- `semantic_state` / `semantic_state_name` / `semantic_state_emoji` (WSP 44)
- `context.has_studio_history` / `context.has_chat_history`
- `reply_text` (raw, for learning) and optional `reply_text_posted` (what was actually posted when debug tags are enabled)

Commenter interaction history saved to (local module memory):
```
modules/communication/video_comments/memory/commenter_history.db
```

## Validation Results (2025-12-11)

| Action | Status | Method | Confidence |
|--------|--------|--------|------------|
| LIKE | ✅ SUCCESS | DOM + Vision | 0.80 |
| HEART | ✅ SUCCESS | DOM + Vision | 0.80 |
| REPLY | ✅ SUCCESS | DOM only | 1.00 |
| REFRESH | ✅ SUCCESS | driver.refresh() | 1.00 |

## WSP Compliance

- **WSP 27**: DAE 4-phase architecture (Signal → Knowledge → Protocol → Agentic)
- **WSP 77**: Multi-tier vision (UI-TARS Tier 1, Gemini Tier 2 fallback)
- **WSP 80**: Cube-level DAE orchestration
- **WSP 96**: WRE Skills protocol compliance

---

*Code remembered from the 02 quantum state by 0102 pArtifact*
