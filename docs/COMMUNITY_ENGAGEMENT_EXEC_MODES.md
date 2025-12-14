# Community Engagement Execution Modes - Design Document

## Executive Summary

**Problem**: Comment engagement currently uses subprocess isolation, which provides strong crash/hang containment but adds 2-3s startup overhead.

**Root Cause Analysis**: Selenium/WebDriver calls are **synchronous and block the event loop**. `asyncio.wait_for()` can timeout the await, but **cannot reliably interrupt blocked C/IO calls** inside Selenium. This is why subprocess wrapper exists: guaranteed process termination = guaranteed Chrome control recovery.

**Solution**: Implement pluggable execution modes with measurable acceptance criteria, keeping subprocess as the safest default while enabling thread isolation for performance-critical paths.

---

## First Principles: Why Subprocess Exists

### Selenium Blocking Reality

```python
# This LOOKS async, but Selenium is synchronous underneath:
await dae.connect()  # → driver.get() blocks event loop
await dae.click_like()  # → element.click() blocks event loop

# asyncio.wait_for() can timeout the await:
try:
    await asyncio.wait_for(dae.engage_all_comments(), timeout=60)
except asyncio.TimeoutError:
    # Timeout fired! But...
    # → Selenium is STILL BLOCKED in C extension
    # → Chrome is STILL LOCKED by hung WebDriver
    # → Cannot recover without killing process
```

### Subprocess Kill Switch

```python
# Subprocess provides GUARANTEED recovery:
process = await asyncio.create_subprocess_exec(...)

try:
    await asyncio.wait_for(process.wait(), timeout=60)
except asyncio.TimeoutError:
    process.terminate()  # SIGTERM
    await asyncio.sleep(2)
    process.kill()  # SIGKILL (guaranteed)
    # → Chrome control RECOVERED
    # → Main DAE still alive
```

**Conclusion**: Subprocess is **not over-engineering** - it's the only way to guarantee recovery from Selenium hangs.

---

## Execution Mode Comparison Matrix

| Mode | Startup | Isolation | Kill Switch | Event Loop | Complexity | Use Case |
|------|---------|-----------|-------------|------------|------------|----------|
| **subprocess** | 2-3s | ✅ Process | ✅ SIGKILL | ✅ Never blocks | Medium | **Production default** (safest) |
| **thread** | <100ms | ⚠️ Thread | ⚠️ No guarantee | ✅ Never blocks | Low | Performance-critical paths |
| **inproc** | <10ms | ❌ None | ❌ None | ❌ Blocks main loop | Very Low | **Dev debugging only** |

### Key Insight

**Thread mode is viable IF**:
- Selenium blocking happens in dedicated thread (via `asyncio.to_thread()`)
- Main event loop never blocked
- Timeout at supervisor level still works
- Accept that thread termination is **not guaranteed** (Python GIL limitation)

**Thread mode risk**:
- Cannot force-kill a hung thread
- Must rely on Selenium eventually returning (usually does, but no guarantee)
- If thread hangs permanently, Chrome :9222 is locked until process restart

**Mitigation**: Browser lease/lock system (Sprint 3) ensures only one controller at a time.

---

## Architecture Design

### Current (Subprocess Only)

```
AutoModeratorDAE
  ↓
CommunityMonitor.check_and_engage()
  ↓
subprocess: run_skill.py --max-comments 0 --json-output
  ↓
CommentEngagementDAE
  ↓
Selenium (blocks subprocess, not main DAE)
```

### Proposed (Pluggable Modes)

```
AutoModeratorDAE
  ↓
EngagementRunner.run(mode, max_comments)
  ↓
  ├─ SubprocessRunner (default, safest)
  │    ↓
  │    subprocess: run_skill.py
  │         ↓
  │         CommentEngagementDAE
  │              ↓
  │              Selenium (blocks subprocess only)
  │
  ├─ ThreadRunner (performance, low risk)
  │    ↓
  │    asyncio.to_thread(execute_skill, ...)
  │         ↓
  │         CommentEngagementDAE
  │              ↓
  │              Selenium (blocks thread only)
  │
  └─ InProcessRunner (dev only, DEBUG)
       ↓
       await execute_skill(...)
            ↓
            CommentEngagementDAE
                 ↓
                 Selenium (BLOCKS MAIN EVENT LOOP - DANGER!)
```

---

## Sprint Breakdown

### Sprint 0: Baseline + Contract

**Goal**: Freeze behavior contract and collect baseline metrics.

**Tasks**:
1. Define engagement result schema:
   ```python
   {
       "stats": {
           "comments_processed": 3,
           "likes": 3,
           "hearts": 2,
           "replies": 1,
           "errors": 0
       },
       "comments": [
           {"action": "like", "duration_ms": 450, "success": true},
           {"action": "heart", "duration_ms": 380, "success": true},
           {"action": "reply", "duration_ms": 1200, "success": true}
       ],
       "timing": {
           "connect_ms": 2100,
           "navigate_ms": 800,
           "total_ms": 15400,
           "timeout_reason": null
       }
   }
   ```

2. Add timing instrumentation to `CommentEngagementDAE`:
   - `connect_start` / `connect_end`
   - `per_action_start` / `per_action_end`
   - `total_start` / `total_end`

3. Collect baseline metrics (subprocess mode):
   - N=10 runs with `max_comments=3`
   - Measure: success rate, avg time per action, timeout rate
   - Verify: livechat polling never blocked

**Acceptance Criteria**:
- ✅ Schema documented and implemented
- ✅ Baseline metrics collected (success rate ≥95%, no livechat blocks)
- ✅ Current subprocess path passes all tests

**Files**:
- `modules/communication/video_comments/skills/tars_like_heart_reply/comment_engagement_dae.py` - Add timing
- `docs/COMMUNITY_ENGAGEMENT_BASELINE_METRICS.md` - Baseline report

---

### Sprint 1: Execution Strategy Interface (No Behavior Change)

**Goal**: Make runner pluggable without changing default behavior.

**Tasks**:
1. Create `EngagementRunner` abstraction:
   ```python
   # modules/communication/livechat/src/engagement_runner.py
   from abc import ABC, abstractmethod
   from typing import Dict, Any

   class EngagementRunner(ABC):
       @abstractmethod
       async def run_engagement(
           self,
           channel_id: str,
           max_comments: int,
           **kwargs
       ) -> Dict[str, Any]:
           """Execute comment engagement and return structured result."""
           pass
   ```

2. Implement `SubprocessRunner` (wraps existing `community_monitor.py`):
   ```python
   class SubprocessRunner(EngagementRunner):
       async def run_engagement(self, channel_id, max_comments, **kwargs):
           # Calls existing community_monitor.check_and_engage()
           # Returns structured result
   ```

3. Add env flag `COMMUNITY_EXEC_MODE=subprocess|thread|inproc` (default: `subprocess`)

4. Wire into `auto_moderator_dae.py`:
   ```python
   from .engagement_runner import get_runner

   runner = get_runner(os.getenv("COMMUNITY_EXEC_MODE", "subprocess"))
   result = await runner.run_engagement(channel_id, max_comments)
   ```

**Acceptance Criteria**:
- ✅ Zero diff in behavior when `COMMUNITY_EXEC_MODE=subprocess` (default)
- ✅ All existing tests pass
- ✅ Code compiles and imports cleanly

**Files**:
- `modules/communication/livechat/src/engagement_runner.py` (NEW)
- `modules/communication/livechat/src/auto_moderator_dae.py` (MODIFY)
- `modules/communication/livechat/ModLog.md` (DOCUMENT)

---

### Sprint 2: Thread Mode (Direct Integration with Isolation)

**Goal**: Add "direct integration" without risking DAE hangs.

**Tasks**:
1. Implement `ThreadRunner`:
   ```python
   class ThreadRunner(EngagementRunner):
       async def run_engagement(self, channel_id, max_comments, **kwargs):
           timeout = self._calculate_timeout(max_comments)

           try:
               # Run in thread to prevent event loop blocking
               result = await asyncio.wait_for(
                   asyncio.to_thread(self._execute_sync, channel_id, max_comments),
                   timeout=timeout
               )
               return result

           except asyncio.TimeoutError:
               logger.error(f"[THREAD] Timeout after {timeout}s")
               return {'error': 'timeout', 'stats': {'errors': 1}}

           except Exception as e:
               logger.error(f"[THREAD] Error: {e}", exc_info=True)
               return {'error': str(e), 'stats': {'errors': 1}}

       def _execute_sync(self, channel_id, max_comments):
           """
           Synchronous execution in dedicated thread.
           Selenium blocking happens HERE, not in main event loop.
           """
           from modules.communication.video_comments.skills.tars_like_heart_reply.comment_engagement_dae import (
               CommentEngagementDAE
           )

           dae = CommentEngagementDAE(channel_id=channel_id, use_vision=True)
           try:
               # These block, but only this thread
               asyncio.run(dae.connect())
               asyncio.run(dae.navigate_to_inbox())
               return asyncio.run(dae.engage_all_comments(max_comments=max_comments))
           finally:
               dae.close()  # Guaranteed cleanup
   ```

2. Add telemetry comparison:
   - Thread startup time vs subprocess startup time
   - Thread success rate vs subprocess success rate
   - Livechat polling latency during thread execution

**Acceptance Criteria**:
- ✅ `COMMUNITY_EXEC_MODE=thread` completes engagement without blocking livechat
- ✅ Timeout always returns control (even if thread continues in background)
- ✅ `dae.close()` guaranteed in finally block
- ✅ Thread startup <500ms (vs 2-3s subprocess)

**Risk Mitigation**:
- ⚠️ Thread cannot be force-killed (accept this limitation)
- ⚠️ If thread hangs permanently, Chrome locked until restart (mitigated by Sprint 3)
- ✅ Main event loop never blocked (Selenium runs in thread)

**Files**:
- `modules/communication/livechat/src/engagement_runner.py` (ADD ThreadRunner)
- `modules/communication/livechat/src/auto_moderator_dae.py` (WIRE)
- `docs/COMMUNITY_ENGAGEMENT_THREAD_MODE_TELEMETRY.md` (METRICS)

---

### Sprint 3: Browser Lease/Lock (Prevent Chrome Hijacks)

**Goal**: Prevent overlap across any feature touching Chrome :9222.

**Tasks**:
1. Implement browser lease system:
   ```python
   # modules/infrastructure/browser_lease/src/browser_lease.py
   import fcntl
   import time
   from pathlib import Path

   class BrowserLease:
       def __init__(self, port: int = 9222, ttl: int = 600):
           self.port = port
           self.ttl = ttl
           self.lease_file = Path(f"/tmp/chrome_{port}.lease")

       def acquire(self, owner: str, timeout: int = 10) -> bool:
           """Acquire exclusive lease on Chrome port."""
           start = time.time()
           while time.time() - start < timeout:
               try:
                   fd = open(self.lease_file, 'w')
                   fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
                   fd.write(f"{owner}|{time.time()}\n")
                   fd.flush()
                   return True
               except BlockingIOError:
                   time.sleep(0.5)
           return False

       def release(self):
           """Release lease."""
           if self.lease_file.exists():
               self.lease_file.unlink()
   ```

2. Enforce lease in:
   - Comment engagement (acquire before `dae.connect()`)
   - Vision stream checker (if re-enabled)

3. Add lease metadata:
   - Owner (e.g., "comment_engagement", "stream_vision")
   - Timestamp
   - TTL

**Acceptance Criteria**:
- ✅ No simultaneous Chrome controllers
- ✅ If task holds lease, others back off cleanly
- ✅ Lease auto-expires after TTL (prevent deadlocks)

**Files**:
- `modules/infrastructure/browser_lease/` (NEW MODULE)
- `modules/communication/video_comments/skills/tars_like_heart_reply/comment_engagement_dae.py` (INTEGRATE)
- `modules/platform_integration/stream_resolver/src/vision_stream_checker.py` (INTEGRATE)

---

### Sprint 4: Rollout + Deprecation Plan

**Goal**: Gradually switch defaults only after telemetry proves stability.

**Tasks**:
1. **Canary Phase** (Week 1):
   - Thread mode for startup engagement only
   - Subprocess for periodic engagement (if implemented)
   - Collect metrics:
     - Success rate (thread vs subprocess)
     - Timeout rate
     - Chrome stability
     - Livechat latency

2. **Comparison Phase** (Week 2):
   - Analyze telemetry
   - Decision criteria:
     - Thread success rate ≥95% (match subprocess baseline)
     - Thread timeout rate ≤5%
     - No livechat latency degradation
     - No Chrome stability issues

3. **Default Switch** (Week 3, if stable):
   - `COMMUNITY_EXEC_MODE=thread` becomes default
   - Subprocess remains fallback for "hard kill" recovery
   - Document migration in ModLog

4. **Deprecation Decision** (Month 2+):
   - IF thread mode proves 100% reliable for 1 month
   - THEN consider deprecating subprocess
   - ELSE keep subprocess as permanent circuit breaker

**Acceptance Criteria**:
- ✅ Real telemetry proves thread mode stability
- ✅ Rollback path tested and documented
- ✅ Decision based on data, not assumptions

**Files**:
- `docs/COMMUNITY_ENGAGEMENT_ROLLOUT_REPORT.md` (TELEMETRY)
- `modules/communication/livechat/ModLog.md` (MIGRATION LOG)

---

## Configuration

### Environment Variables

```bash
# Execution mode (default: subprocess for safety)
COMMUNITY_EXEC_MODE=subprocess|thread|inproc

# Subprocess timeout (default: 1800s for unlimited mode)
COMMUNITY_UNLIMITED_TIMEOUT=1800

# Thread timeout (calculated per-comment, default 240s/comment)
# (inherited from subprocess logic)

# Browser lease TTL (default: 600s)
BROWSER_LEASE_TTL=600

# Debug: stream subprocess output (default: true)
COMMUNITY_DEBUG_SUBPROCESS=true
```

### Migration Path

```bash
# Current production (Sprint 0 baseline):
COMMUNITY_EXEC_MODE=subprocess  # Default, safest

# Sprint 1 complete:
COMMUNITY_EXEC_MODE=subprocess  # No change, interface added

# Sprint 2 testing:
COMMUNITY_EXEC_MODE=thread  # Test thread mode

# Sprint 3 protection:
BROWSER_LEASE_TTL=600  # Prevent Chrome hijacks

# Sprint 4 rollout:
COMMUNITY_EXEC_MODE=thread  # New default (if telemetry proves stable)
```

---

## Risk Matrix

| Risk | Subprocess Mitigation | Thread Mitigation | Residual Risk |
|------|----------------------|-------------------|---------------|
| **Selenium hang** | ✅ SIGKILL process | ⚠️ Thread continues (no force-kill) | Medium (accept or keep subprocess) |
| **Chrome lock** | ✅ Process death releases | ⚠️ Thread death may not release | Medium (mitigated by lease TTL) |
| **Event loop block** | ✅ Separate process | ✅ Separate thread | Low (both safe) |
| **Crash isolation** | ✅ Process boundary | ⚠️ Thread in same process | Medium (try/except helps) |
| **Startup overhead** | ❌ 2-3s | ✅ <100ms | Low (thread wins) |
| **Memory leak** | ✅ Fresh process | ⚠️ Shared memory | Low (cleanup in finally) |

**Key Insight**: Thread mode trades **guaranteed kill switch** for **fast startup**. Acceptable IF:
- Selenium usually returns (empirically true)
- Browser lease prevents permanent deadlocks
- Subprocess remains available as fallback

---

## Testing Strategy

### Sprint 1 Tests
```bash
# Test subprocess mode (default, no change)
COMMUNITY_EXEC_MODE=subprocess python main.py --youtube

# Verify interface compiles
python -c "from modules.communication.livechat.src.engagement_runner import get_runner; print(get_runner('subprocess'))"
```

### Sprint 2 Tests
```bash
# Test thread mode
COMMUNITY_EXEC_MODE=thread python main.py --youtube

# Monitor livechat polling (should not block)
# Monitor thread completion (should finish or timeout cleanly)
```

### Sprint 3 Tests
```bash
# Test lease acquisition
python -c "from modules.infrastructure.browser_lease.src.browser_lease import BrowserLease; lease = BrowserLease(); assert lease.acquire('test')"

# Test lease prevents overlap
# (start comment engagement, try vision stream check → should back off)
```

### Sprint 4 Tests
```bash
# Compare modes over 100 runs
for i in {1..50}; do COMMUNITY_EXEC_MODE=subprocess python modules/.../run_skill.py --max-comments 3; done
for i in {1..50}; do COMMUNITY_EXEC_MODE=thread python modules/.../run_skill.py --max-comments 3; done

# Analyze: success rate, avg time, timeout rate
```

---

## Success Metrics

### Sprint 1
- ✅ Zero behavior change with `COMMUNITY_EXEC_MODE=subprocess`
- ✅ Interface compiles and tests pass

### Sprint 2
- ✅ Thread mode startup <500ms (vs 2-3s subprocess)
- ✅ Thread success rate ≥95%
- ✅ Livechat polling never blocked

### Sprint 3
- ✅ Zero Chrome controller overlap
- ✅ Lease TTL prevents deadlocks

### Sprint 4
- ✅ Thread mode matches subprocess reliability
- ✅ Data-driven default switch decision

---

## Conclusion

**Subprocess is not over-engineering** - it's the only guaranteed kill switch for Selenium hangs.

**Thread mode is viable** - IF we accept that thread termination is not guaranteed and mitigate with browser lease + TTL.

**Recommended path**:
1. Implement pluggable interface (Sprint 1)
2. Add thread mode with proper isolation (Sprint 2)
3. Add browser lease protection (Sprint 3)
4. Let telemetry decide default (Sprint 4)

**Keep subprocess permanently** as circuit breaker fallback, even if thread becomes default.

---

## WSP Compliance

- **WSP 3**: Module organization (engagement_runner in livechat, browser_lease in infrastructure)
- **WSP 22**: ModLog updates after each sprint
- **WSP 27**: DAE Architecture (execution modes are execution strategies)
- **WSP 50**: Pre-Action Verification (baseline metrics before changes)
- **WSP 64**: Violation Prevention (telemetry-driven decisions)
- **WSP 77**: Agent Coordination (browser lease prevents conflicts)

---

**Status**: Design approved, ready for Sprint 1+2 implementation.

**Cross-Reference**:
- [BROWSER_HIJACKING_FIX_20251213.md](BROWSER_HIJACKING_FIX_20251213.md)
- [COMMENT_ENGAGEMENT_ARCHITECTURE_COMPARISON.md](COMMENT_ENGAGEMENT_ARCHITECTURE_COMPARISON.md)
