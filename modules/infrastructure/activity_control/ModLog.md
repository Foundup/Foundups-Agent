# Activity Control Module - ModLog

This log tracks changes to the **activity_control** module in the **infrastructure** domain.

## WSP 22 ModLog Protocol
- **Purpose**: Track module-specific changes and evolution per WSP 22
- **Format**: Reverse chronological order (newest first)
- **Scope**: Activity routing, browser availability signaling, breadcrumb-based coordination

---

## MODLOG ENTRIES

### 2026-01-23: Activity Router Implementation (V1.0.0)

**By:** 0102
**WSP References:** WSP 22 (ModLog), WSP 77 (Agent Coordination), WSP 80 (DAE Pattern), WSP 91 (Observability)

**Change:** Implemented Activity Router to coordinate activities based on breadcrumb signals.

**Problem:**
- No coordination between comment engagement, shorts scheduling, video indexing, and live chat
- Browser availability not signaled after rotation complete
- `_rotation_processed_channels` set populated but never read
- System "hangs" after comments done instead of routing to next activity

**Solution:**
Created full Activity Router implementation replacing placeholder:

**Components:**
- `ActivityType` enum: COMMENT_ENGAGEMENT, SHORTS_SCHEDULING, VIDEO_INDEXING, LIVE_CHAT, IDLE
- `BrowserState` dataclass: Tracks Chrome/Edge availability
- `ActivityDecision` dataclass: Routing decision with browser recommendation
- `ActivityRouter` class: Main router with breadcrumb integration

**Key Methods:**
- `check_rotation_complete()`: Reads `rotation_complete` breadcrumbs from multi_channel_coordinator
- `get_next_activity()`: Returns priority-based activity decision
- `signal_browser_available()`: Signals browser ready for next activity
- `signal_activity_complete()`: Emits activity completion breadcrumb

**Priority Flow:**
```
1. Comments (base) - always returns here eventually
   ↓ rotation_complete breadcrumb
2. Shorts Scheduling (if YT_SHORTS_SCHEDULING_ENABLED)
   ↓ scheduling_complete breadcrumb
3. Video Indexing (if YT_VIDEO_INDEXING_ENABLED)
   ↓ indexing_complete breadcrumb
4. Live Chat (if stream active)
   ↓ chat_idle breadcrumb → Return to 1.
```

**Browser Routing:**
- Chrome (9222): Available when Move2Japan + UnDaoDu comments done
- Edge (9223): Available when FoundUps + RavingANTIFA comments done

**Files Changed:**
- `src/activity_control.py`: Full implementation (was placeholder)

---

## V0.0.0 - Initial Placeholder (2026-01-XX)

**By:** Template
**WSP References:** WSP 49 (Module Structure)

**Change:** Created module scaffold per WSP 49.
