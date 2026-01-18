# Activity Orchestration Audit - HoloIndex Findings

**Created**: 2026-01-19
**WSP Compliance**: WSP 50 (Pre-Action), WSP 77 (Agent Coordination), WSP 22 (ModLog)
**Purpose**: Document existing modules that can be ENHANCED for activity orchestration (NO vibecoding)

---

## Executive Summary

HoloIndex audit revealed 5 existing modules that provide ~80% of activity orchestration functionality.
**Enhancement estimate**: ~50 lines vs ~500+ lines for new implementation.

---

## Existing Modules Discovered

### 1. AI Overseer (`ai_overseer.py`)

**Location**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`
**Capabilities**:
- `MissionType` enum with DAEMON_MONITORING, BUG_DETECTION, AUTO_REMEDIATION
- `spawn_agent_team()` - Creates Qwen/Gemma/0102 coordination teams
- `monitor_daemon()` - Monitors bash shells for errors
- `coordinate_mission()` - Orchestrates multi-phase missions
- WSP 77 4-phase workflow (Gemma detect → Qwen plan → 0102 execute → Learn)

**Enhancement Needed**:
- Add `ActivityMissionType` entries: COMMENT_PROCESSING, VIDEO_INDEXING, SCHEDULING, SOCIAL_MEDIA, LIVE_STREAM
- Add `get_next_activity()` method using done detection patterns
- Add `detect_activity_state()` for completion detection

### 2. Multi-Channel Coordinator (`multi_channel_coordinator.py`)

**Location**: `modules/communication/livechat/src/multi_channel_coordinator.py`
**Key Pattern Found**:
```python
# Done detection pattern - REUSE THIS
if result.get("all_processed"):
    # All comments processed for this channel
    return {"status": "done", "channel": channel}
```

**Capabilities**:
- Channel rotation (FoundUps → RavingANTIFA → etc.)
- `all_processed: True` completion detection
- Multi-channel state tracking

**Reuse For**:
- Activity completion detection pattern
- Channel-agnostic done state

### 3. Pattern Memory (`pattern_memory.py`)

**Location**: `modules/infrastructure/wre_core/src/pattern_memory.py`
**Capabilities**:
- SQLite outcome storage
- A/B testing with variation tracking
- Fidelity scoring (success/failure patterns)
- `recall_successful_patterns()` / `recall_failure_patterns()`

**Reuse For**:
- Activity outcome tracking
- Learning which activity transitions work best
- WSP 48 recursive improvement

### 4. Libido Monitor (`libido_monitor.py`)

**Location**: `modules/infrastructure/wre_core/src/libido_monitor.py`
**Capabilities**:
- Gemma pattern frequency monitoring
- `LibidoSignal` enum: CONTINUE / THROTTLE / ESCALATE
- `should_execute()` - Binary classification <10ms
- Rate limiting for activity frequency

**Reuse For**:
- Activity throttling (don't spam same activity)
- Cooldown between activity transitions
- Pattern-based activity gating

### 5. Index Weave (`index_weave.py`)

**Location**: `modules/platform_integration/youtube_shorts_scheduler/src/index_weave.py`
**Capabilities**:
- Already unifies scheduler ↔ indexer ↔ description generation
- WSP 27 DAE orchestration layer
- Scheduler triggers indexing automatically

**Key Finding**: Scheduling + Indexing already unified! No additional work needed.

---

## Activity Priority Matrix (WSP 15 MPS Scoring)

| Activity | Priority | Default MPS | Trigger Condition |
|----------|----------|-------------|-------------------|
| Live Stream (P0) | CRITICAL | 20 | `is_live: true` |
| Comments (P1) | HIGH | 15 | `unprocessed_comments > 0` |
| Indexing (P1) | HIGH | 14 | Default when idle |
| Scheduling+Indexing (P2) | MEDIUM | 12 | `schedule_queue > 0` |
| Social Media (P3) | LOW | 8 | `social_queue > 0` |
| Maintenance (P4) | LOWEST | 4 | `maintenance_due: true` |

---

## State Detection Patterns

### Comment Processing Done
```python
# From multi_channel_coordinator.py
if result.get("all_processed"):
    return "ACTIVITY_DONE"
```

### Indexing Default
```python
# When all activities done, fall back to indexing
if all_activities_done():
    return ActivityType.VIDEO_INDEXING  # Default P1
```

### Live Stream Override
```python
# P0 always overrides
if is_live_stream_active():
    return ActivityType.LIVE_STREAM  # P0 Critical
```

---

## Enhancement Plan (~50 lines)

### Step 1: Add Activity MissionTypes to `types.py`
```python
class MissionType(Enum):
    # ... existing types ...
    # NEW: Activity orchestration
    ACTIVITY_ROUTING = "activity_routing"
    COMMENT_PROCESSING = "comment_processing"
    VIDEO_INDEXING = "video_indexing"
    SCHEDULING = "scheduling"
    SOCIAL_MEDIA = "social_media"
    LIVE_STREAM = "live_stream"
```

### Step 2: Add `get_next_activity()` to AI Overseer
```python
def get_next_activity(self, current_state: Dict) -> MissionType:
    """WSP 15 MPS-based activity routing"""
    # P0: Live stream always wins
    if current_state.get("is_live"):
        return MissionType.LIVE_STREAM

    # P1: Comments if unprocessed
    if current_state.get("unprocessed_comments", 0) > 0:
        return MissionType.COMMENT_PROCESSING

    # P1 Default: Indexing
    return MissionType.VIDEO_INDEXING
```

### Step 3: Wire LibidoMonitor for throttling
```python
# Use existing libido_monitor for activity cooldowns
if self.libido_monitor.should_execute(activity_name):
    return self.execute_activity(activity)
```

---

## Anti-Vibecoding Compliance

| Check | Status |
|-------|--------|
| HoloIndex search performed FIRST | YES |
| Existing modules identified | YES (5 found) |
| Enhancement vs New decision | Enhancement (~50 lines) |
| Pattern reuse documented | YES |
| WSP 50 Pre-Action Verification | COMPLIANT |

---

## References

- **WSP 15**: Module Prioritization System (MPS scoring)
- **WSP 77**: Agent Coordination Protocol (4-phase workflow)
- **WSP 48**: Recursive Self-Improvement (pattern learning)
- **WSP 50**: Pre-Action Verification (this audit)
- **WSP 22**: Traceable Narrative Protocol (documentation)

---

## Next Steps

1. [x] Document audit findings (this file)
2. [ ] Re-index HoloIndex with documentation
3. [ ] Enhance AI Overseer with activity routing (~50 lines)
4. [ ] Test activity routing with comment→indexing flow
