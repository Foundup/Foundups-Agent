# YouTube Shorts Scheduler - ROADMAP

> **0102 Pickup Point**: Full WRE stack validated manually. Ready for Selenium automation.

## Current Status: V0.5.0 (2026-01-01)

✅ **Layer 1-5 Manual Validation Complete**
- All layers executed via browser subagent
- DOM selectors identified and documented
- Critical path: L0 → L1 → L2 → L3 → L4 → L5.1-5.5 → LOOP

---

## Phase 1: Layer-by-Layer Selenium Tests (CURRENT)

### Sprint 1.1: Layer Tests with Visual Validation

Each layer gets its own test file with two modes:
1. **Visual Mode**: Browser subagent validates DOM (initial verification)  
2. **Selenium Mode**: Pure DOM automation (production speed)

| Layer | Test File | Visual | Selenium |
|-------|-----------|--------|----------|
| L0 | `test_layer0_entry.py` | ⬜ TODO | ⬜ TODO |
| L1 | `test_layer1_visibility.py` | ✅ Verified | ⬜ TODO |
| L2 | `test_layer2_date.py` | ✅ Verified | ⬜ TODO |
| L3 | `test_layer3_time.py` | ✅ Verified | ⬜ TODO |
| L4 | `test_layer4_done.py` | ✅ Verified | ⬜ TODO |
| L5.1 | `test_layer5_related.py` | ⚠️ Selector issue | ⬜ TODO |
| L5.2 | `test_layer5_select.py` | ⚠️ Top-left fix | ⬜ TODO |
| L5.3 | `test_layer5_save.py` | ✅ Verified | ⬜ TODO |
| L5.4 | `test_layer5_return.py` | ✅ Verified | ⬜ TODO |
| L5.5 | `test_layer5_refresh.py` | ✅ Verified | ⬜ TODO |

### Sprint 1.2: Known Issues

**L5.1-5.2 Related Video Selection:**
- [ ] Fix: Select first thumbnail (top-left), not arbitrary position
- [ ] Add: Search feature support for related video
- [ ] Selector: Need reliable DOM path for video grid

---

## Phase 2: Layer Linking (WRE Loop)

### Sprint 2.1: Sequential Layer Chain
```python
def run_scheduling_chain(video_index: int = 0):
    """Execute L0-L5.5 as atomic unit."""
    l0_entry()        # Select video from list
    l1_visibility()   # Open dialog
    l2_date(date)     # Set date
    l3_time(time)     # Set time
    l4_done()         # Confirm
    l5_related()      # Set related video
    l5_save()         # Save changes
    l5_return()       # Back to list
    l5_refresh()      # Refresh (CRITICAL before loop)
```

### Sprint 2.2: Recursive Loop
```python
def run_batch_scheduling(max_videos: int = 8):
    """Process all unlisted videos in queue."""
    for i in range(max_videos):
        if not has_unlisted_videos():
            break
        run_scheduling_chain(i)
        log(f"Scheduled video {i+1}/{max_videos}")
```

---

## Phase 3: DAE Integration (Self-Monitoring)

### Sprint 3.1: YouTubeShortsSchedulerDAE
- [ ] Create `dae_orchestrator.py` following WSP 27/80 pattern
- [ ] 4-phase DAE: SENSE → PROCESS → ACT → LEARN
- [ ] Pattern memory integration for error recovery
- [ ] AI Overseer gate registration

### Sprint 3.2: Self-Improvement Loop
- [ ] Error detection and retry logic per layer
- [ ] Screenshot capture on failure for WRE training
- [ ] DOM selector auto-healing (fallback chains)

---

## DOM Selector Reference (L0-L5)

```
L0  Entry:        click(video_row[0]) → edit page
L1  Visibility:   //button[contains(@aria-label,'visibility')]
L1.1 Expand:      //button[contains(@aria-label,'expand')]
L2  Date:         //input[contains(@aria-label,'Date')]
L3  Time:         //input[contains(@aria-label,'time')]
L4  Done:         //button[.//span[text()='Done']]
L5.1 Related:     ytcp-dropdown-trigger (index 1)
L5.2 Select:      video-grid thumbnail[0] ← NEEDS FIX
L5.3 Save:        button#save-button
L5.4 Return:      #back-button
L5.5 Refresh:     F5 key
```

---

## Acceptance Criteria

| Phase | Criteria |
|-------|----------|
| Phase 1 | Each layer test passes independently |
| Phase 2 | Full chain executes 3+ videos without error |
| Phase 3 | DAE runs autonomously for 1 hour with recovery |

---

## Dependencies

- Chrome with remote debugging (port 9222)
- Selenium WebDriver
- WSP 27/80 DAE patterns
- AI Overseer (optional, for gating)

---

## Last Updated

**V0.5.0** (2026-01-01): WRE stack validated, layer tests planned
