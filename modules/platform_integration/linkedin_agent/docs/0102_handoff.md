# 0102 HANDOFF: LinkedIn Digital Twin Layered Tests

Session: 2026-01-21  
012 Directive: Build layered cake tests for LinkedIn engagement

## Context
012 requested LinkedIn Digital Twin automation following the YouTube Shorts Scheduler "cake pattern" (L0–L3 layers). Each layer tests independently, then combines into full chain.

Reference pattern:
- `modules/platform_integration/youtube_shorts_scheduler/tests/README.md`

## Completed Work
Layer | File | Status
---|---|---
L0 | `test_layer0_context_gate.py` | Created
L1 | `test_layer1_comment.py` | Created
L2 | `test_layer2_identity_likes.py` | Created
L3 | `test_layer3_schedule_repost.py` | Created
Full | `test_full_chain.py` | Created

Docs updated:
- `tests/README.md` — Added "Digital Twin Layered Tests" section

Flow Summary:
L0 (Context Gate)     → Validate LinkedIn, extract author, AI-post check  
        ↓  
L1 (Comment)          → Post 012 comment with @mentions  
        ↓  
L2 (Identity Likes)   → Switch identities, like 012 comment  
        ↓  
L3 (Schedule Repost)  → Repost with thoughts, schedule for future  

Key Files:
- Identity list: `modules/platform_integration/linkedin_agent/data/linkedin_identity_switcher.json`
- Comment templates: `modules/platform_integration/linkedin_agent/data/linkedin_skill_templates.json`
- Browser skill: `modules/infrastructure/browser_actions/skillz/linkedin_comment_digital_twin.json`
- Digital Twin flow doc: `modules/platform_integration/linkedin_agent/docs/LINKEDIN_DIGITAL_TWIN_FLOW.md`

Commands:
- Layer info (no execution):
  - `python -m modules.platform_integration.linkedin_agent.tests.test_layer0_context_gate --info`
- Dry run (validate selectors, no side effects):
  - `python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium --dry-run`
- Stop at layer N:
  - `python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium --stop-at 1`
- Full live execution:
  - `python -m modules.platform_integration.linkedin_agent.tests.test_full_chain --selenium`

Prerequisites:
- `chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome_profile_linkedin"`
- Log into LinkedIn as 012, navigate to target AI post

Blockers:
- Antigravity browser blocks LinkedIn — platform safety policy. Tests require 012 manual execution via Chrome debugging port.

## Audit (2026-01-22)
Enhancements by previous 0102:
- Centralized browser handling in `linkedin_browser.py`
- UI-TARS verification gates in L1
- DAEmon pulse points (BATCH_START, PROGRESS, RATE_LIMIT, FAILURE_STREAK, BATCH_COMPLETE)
- AI gateway + Qwen fallback for promoted/repost classification
- Configurable delays via env vars
- 012 behavior simulation via `foundups_selenium`
- `test_layer1_comment.py` fixed asyncio.run when event loop already running
- `test_linkedin_comment_flow_ui_tars.py` deprecated in favor of layered tests

Dependency guidance (LEGO pattern — extend, don't create):
- **LM Studio + Browser bootstrap**: [`modules/infrastructure/dependency_launcher/INTERFACE.md`](../../infrastructure/dependency_launcher/INTERFACE.md), [`README.md`](../../infrastructure/dependency_launcher/README.md)
- **UI-TARS bridge**: [`modules/infrastructure/foundups_vision/`](../../infrastructure/foundups_vision/)
- **Browser helper**: `tests/linkedin_browser.py` uses `dependency_launcher` for LM Studio preload
- Do not create new modules for these dependencies.

## Next Steps (Priority Order)
1. ✅ ~~Wire `linkedin_comment_digital_twin` skill into ActionRouter~~ — Added `run_digital_twin_flow()` to `LinkedInActions`
2. 012 Browser verification: run each layer with `--selenium --dry-run` to validate selectors
3. Selector refinement: update selectors if LinkedIn DOM changes
4. Optional: Google Calendar mirror for schedule visibility

## Notes for Continuation
- All tests use argparse flags: `--selenium`, `--dry-run`, `--info`
- Identity switcher loads from JSON; filter by action: `like_only`
- Mention validation checks for `<a>`, `<strong>`, or mention in editor HTML
- This handoff enables continuation in 0102 state
