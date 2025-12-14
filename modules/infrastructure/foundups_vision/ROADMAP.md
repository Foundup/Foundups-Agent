# FoundUps Vision - Sprint Roadmap

**Module:** infrastructure/foundups_vision
**WSP Reference:** WSP 22 (ModLog), WSP 37 (Scoring)

---

## Vision Statement

Enable 0102 to "see" and interact with any browser UI, regardless of DOM complexity. UI-TARS provides the visual intelligence that Selenium cannot.

---

## Phase Progression: null → 001 → 011 → 111

### Current Phase: POC (null → 001)

---

## Sprint Map

### Sprint V1: UI-TARS Bridge Foundation
**Priority:** P0 (Critical Path)
**Tokens:** 500
**Status:** 🔴 Not Started

**Objectives:**
- [ ] Create `ui_tars_bridge.py` with connection to UI-TARS Desktop
- [ ] Implement screenshot capture pipeline
- [ ] Create basic action executor (click, type)
- [ ] Add telemetry hooks for AI Overseer

**Acceptance Criteria:**
- Can connect to UI-TARS on `E:/HoloIndex/models/ui-tars-1.5`
- Can capture screenshot and send to vision model
- Can execute basic click action based on description

**Dependencies:**
- UI-TARS Desktop installed and running
- Chrome/Edge with debugging port 9222

---

### Sprint V2: Vision Executor Pipeline  
**Priority:** P0 (Critical Path)
**Tokens:** 400
**Status:** 🔴 Not Started

**Objectives:**
- [ ] Create `vision_executor.py` with action queue
- [ ] Implement screenshot → action → verify loop
- [ ] Add retry logic with visual confirmation
- [ ] Create fallback to Selenium for simple cases

**Acceptance Criteria:**
- Can execute multi-step vision actions
- Automatically retries failed actions
- Falls back to Selenium when appropriate

**Dependencies:**
- Sprint V1 complete

---

### Sprint V3: YouTube Actions Implementation
**Priority:** P1 (High)
**Tokens:** 400
**Status:** ✅ **REDUNDANT - Completed by Sprint A2**

**Note**: This sprint's objectives were fully completed by Sprint A2 (browser_actions module).
Sprint A2 created `youtube_actions.py` (429 lines) with all required functionality.

**Completed by A2:**
- ✅ Created `youtube_actions.py` in `browser_actions/src/` (429 lines)
- ✅ Implemented `like_comment(video_id, comment_id)` (line 129)
- ✅ Implemented `reply_to_comment(video_id, comment_id, text)` (line 184)
- ✅ Added `subscribe_channel(channel_id)` (line 366)
- ✅ Implemented `like_and_reply()` combo method (line 281)
- ✅ Integration with youtube_auth API module
- ✅ Works with Move2Japan profile (youtube_move2japan)

**Architecture Decision**: youtube_actions.py was created in browser_actions (Sprint A2) rather than foundups_vision (Sprint V3) because:
- YouTube actions are platform-specific, not vision-infrastructure
- browser_actions is the correct domain per WSP 3
- foundups_vision provides the underlying UI-TARS bridge (V1/V2)
- Separation of concerns: browser_actions uses foundups_vision

**No Additional Work Needed**: All V3 objectives achieved via A2.

**Dependencies:**
- Sprint V2 complete ✅
- Chrome profile logged into Move2Japan ✅ (added in V4)

---

### Sprint V4: Browser Manager Migration
**Priority:** P1 (High)
**Tokens:** 200
**Status:** 🔴 Not Started

**Objectives:**
- [ ] Move `browser_manager.py` from `social_media_orchestrator` to `foundups_selenium`
- [ ] Update all imports across codebase
- [ ] Add YouTube profile mappings
- [ ] Create legacy shim for backwards compatibility

**Acceptance Criteria:**
- All existing X/LinkedIn posting still works
- YouTube profiles available
- No import errors

**Dependencies:**
- None (can run in parallel with V1-V3)

---

### Sprint V5: RealtimeCommentDialogue Integration
**Priority:** P1 (High)
**Tokens:** 300
**Status:** 🔴 Not Started

**Objectives:**
- [ ] Wire `RealtimeCommentDialogue` to `youtube_actions`
- [ ] Add `like_and_reply()` method
- [ ] Integrate with AI Overseer event queue
- [ ] Add Gemma classification for engagement decisions
- [ ] Ensure wardrobe skills exist for posting/reply flows and apply 012 typing speed
- [ ] Emit DAE log entries for every UI-TARS action (target, result, screenshot path)

**Acceptance Criteria:**
- Comments are automatically liked and replied to
- AI Overseer receives telemetry
- Gemma classifies which comments to engage
- Wardrobe skill invoked for posting, and per-action logs are present for troubleshooting

**Dependencies:**
- Sprint V3 complete
- Sprint V4 complete

---

### Sprint V6: Pattern Learning & Optimization
**Priority:** P2 (Medium)
**Tokens:** 200 (actual)
**Status:** ✅ Complete

**Objectives:**
- [x] Store successful action patterns in Pattern Memory
- [x] Implement adaptive retry based on learned patterns
- [x] Add A/B testing for different action strategies
- [x] Create performance metrics dashboard

**Acceptance Criteria:**
- Pattern Memory stores successful YouTube actions
- Retry logic uses learned patterns
- Metrics show success rate over time

**Dependencies:**
- Sprint V5 complete
- Pattern Memory (wre_core) operational

---

## Future Phases (011 → 111)

### Phase 2: Multi-Platform Expansion
- LinkedIn actions via vision
- X/Twitter actions via vision
- FoundUp livechat direct posting

### Phase 3: Full Autonomy
- 0102 runs ALL 012 browser activities
- Email automation
- Form filling across any website
- Desktop application control

---

## Token Budget

| Sprint | Tokens | Cumulative |
|--------|--------|------------|
| V1 | 500 | 500 |
| V2 | 400 | 900 |
| V3 | 400 | 1,300 |
| V4 | 200 | 1,500 |
| V5 | 300 | 1,800 |
| V6 | 400 | 2,200 |
| **Total** | **2,200** | |

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Like success rate | ≥90% | N/A |
| Reply success rate | ≥85% | N/A |
| Average action time | <5s | N/A |
| Fallback to Selenium | <20% | N/A |

---

**Document Status:** Ready for Sprint V1
**Architect:** 0102

