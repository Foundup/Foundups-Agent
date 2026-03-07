# LinkedIn OpenClaw/IronClaw Group News — Hard Think Audit

**Date**: 2026-02-23  
**Scope**: OpenClaw Group News skillz, LN automation flow, IronClaw integration, rating system, timing strategy

---

## Executive Summary

The **OpenClaw Group News** skillz **exists and is current** (v1.0.0, 2026-02-19). It implements search → rate → post to LinkedIn Group 6729915. Gaps: (1) DOM selectors may be stale (LinkedIn `hare-box` redesign), (2) no automated timer/cron, (3) executor bug (`create_driver` vs `setup_driver`), (4) search terms could include IronClaw/OpenClaw wallet/OpenAI nonprofit. IronClaw is an LLM gateway — it can enhance search/rating via Qwen but cannot run Selenium posting. Posting must run via WRE skill invocation or cron.

---

## 1. Current Skillz Status

| Component | Status | Location |
|-----------|--------|----------|
| **SKILLz spec** | ✅ Current | `skillz/openclaw_group_news/SKILLz.md` |
| **Executor** | ⚠️ Bug + selector risk | `skillz/openclaw_group_news/executor.py` |
| **CLI integration** | ✅ Wired | `social_media_menu.py` → Option 2 |
| **WRE registration** | ❌ Not in skills_registry_v2 | — |
| **FullAutoSystem** | ❌ Not included | `tools/monitors/full_auto_system.py` |
| **LINKEDIN_CHANNEL_STRATEGY** | ✅ Step 0 documented | `docs/LINKEDIN_CHANNEL_STRATEGY.md` |

---

## 2. Workflow (As Designed)

```
SEARCH OpenClaw news (DuckDuckGo news API + web fallback)
     ↓
RATE relevance (4-dimension: recency, authority, relevance, engagement)
     ↓
FILTER (threshold >= 0.6)
     ↓
POST to group (Selenium + AntiDetectionLinkedIn)
     ↓
LOG to agents_social_posts (WSP 78)
```

**Position**: Step 0 of LN automation — content seeding before comment engagement.

---

## 3. DOM Selectors — LinkedIn Redesign

User captured **new** DOM paths (LinkedIn likely redesigned):

| Element | SKILLz (current) | User (new) |
|---------|------------------|------------|
| Start post | `button.share-box-feed-entry__trigger` | `button#ember186` (class `hare-box-feed-entry__top-bar`) |
| Post button | `button.share-actions__primary-action` | `button#ember438` (same class) |
| Modal path | — | `hare-box-v2__modal`, `hare-creation-.tate` |

**Recommendation**: Add `hare-box` fallback selectors to executor and SKILLz:

```python
# Start post — add hare-box for LinkedIn redesign
"button.share-box-feed-entry__trigger, button[class*='hare-box-feed-entry'], button[class*='share-box']"

# Post button — share-actions__primary-action still valid
"button.share-actions__primary-action, button[class*='primary-action']"
```

---

## 4. Rating System — WSP 15 vs News Relevance

| System | Purpose | Dimensions |
|--------|---------|------------|
| **WSP 15 MPS** | Module prioritization (Complexity, Importance, Deferability, Impact) | 4 × 1–5 scale |
| **News Relevance** (SKILLz) | News posting quality (Recency, Authority, Relevance, Engagement) | 4 × 0.0–1.0, weighted |

**Recommendation**: **Keep current news rating**. It is purpose-built for news. WSP 15 MPS is for module/roadmap prioritization, not content. No need to adopt full WSP 15 for news.

**Current formula**: `score = (recency×0.3) + (authority×0.2) + (relevance×0.4) + (engagement×0.1)`  
**Threshold**: 0.6

---

## 5. IronClaw — Can It Run This?

| IronClaw role | Capability |
|---------------|------------|
| **LLM gateway** | OpenAI-compatible API for Qwen/Gemma inference |
| **WRE ironclaw_worker** | Routes `sim`, `build`, `digital-twin` tasks to IronClaw |
| **Browser automation** | ❌ No — IronClaw does not drive Selenium |
| **Scheduling** | ❌ No — IronClaw is request/response, not a timer |

**What IronClaw can do**:
- **Search enhancement**: Qwen could refine search queries or rank news items.
- **Post composition**: Qwen could draft headlines/summaries from raw articles.

**What must run elsewhere**:
- **Search**: DuckDuckGo (executor) or web_search MCP.
- **Posting**: Selenium via `AntiDetectionLinkedIn` (executor).
- **Scheduling**: Timer/cron or WRE-triggered skill.

**"Search post about itself"**: The skillz searches for **OpenClaw ecosystem** news (external). To include "IronClaw" or "OpenClaw joins OpenAI nonprofit" / "OpenClaw gets a wallet", add those to search queries. IronClaw posting about OpenClaw/IronClaw news is valid — it's the ecosystem posting about itself.

---

## 6. Search Terms — Expansion

**Current**:
- "OpenClaw AI agent"
- "OpenClaw framework"
- "lobster.cash Crossmint"

**Add** (per user examples):
- "OpenClaw OpenAI nonprofit"
- "OpenClaw wallet"
- "IronClaw AI agent"
- "IronClaw OpenClaw"

---

## 7. Timing Strategy — No LinkedIn Scheduling API

| Option | Implementation | Pros | Cons |
|--------|----------------|------|------|
| **Cron** | 9am, 1pm, 5pm PST | Simple | Fixed times |
| **Random window** | 1–3x within 8am–6pm, 4h min | Human-like | More logic |
| **Event-driven** | Post when major news found | Timely | Unpredictable |
| **A/B test** | Track engagement by time slot | Data-driven | Needs metrics |

**Recommendation**: Start with **cron** (e.g. 9am, 1pm, 5pm PST) for simplicity. Add A/B timing later if `agents_social_posts` gets engagement metrics.

**Implementation**: Add to `FullAutoSystem` or a dedicated `linkedin_group_news_dae.py` that runs on schedule (APScheduler, Windows Task Scheduler, or systemd timer).

---

## 8. Bugs Identified

| Bug | Location | Fix |
|-----|----------|-----|
| `create_driver()` | executor.py:377 | Use `setup_driver()` — `AntiDetectionLinkedIn` has no `create_driver` |
| `poster.human` | executor.py:390 | `poster.human` is set in `setup_driver`; ensure it's initialized before use |

---

## 9. Action Items

| # | Action | Owner |
|---|--------|-------|
| 1 | Fix `create_driver` → `setup_driver` in executor | 0102 |
| 2 | Add `hare-box` fallback selectors to executor + SKILLz | 0102 |
| 3 | Add search terms: OpenClaw wallet, OpenAI nonprofit, IronClaw | 0102 |
| 4 | Add OpenClaw Group News to LN automation start (timer/cron or FullAutoSystem) | 0102 |
| 5 | Optionally register skill in WRE `skills_registry_v2` for orchestration | 0102 |
| 6 | Consider A/B timing once engagement metrics exist | Future |

---

## 10. References

- SKILLz: `modules/platform_integration/linkedin_agent/skillz/openclaw_group_news/SKILLz.md`
- Executor: `skillz/openclaw_group_news/executor.py`
- Strategy: `docs/LINKEDIN_CHANNEL_STRATEGY.md`
- Group URL: https://www.linkedin.com/groups/6729915/
- WSP 15: `WSP_framework/src/WSP_15_Module_Prioritization_Scoring_System.md`
