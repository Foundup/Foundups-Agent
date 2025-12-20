# Sprint 4: YouTube Automation Safety & Observability Micro‑Sprints

**Date**: 2025-12-15  
**Goal**: Reduce operational risk via *gating + observability + circuit breakers*, and make experimentation reproducible so multiple 0102s can work in parallel without stepping on each other.

## Safety Boundary (Non‑Goals)

This sprint is **compliance-first**:
- ✅ Improve reliability, safety, logging, and controlled testing.
- ✅ Prefer official APIs where available.
- ❌ Do not implement “stealth/anti‑detection” techniques intended to bypass platform enforcement.

## Current Cardiovascular Signals (from `012.txt` lines 1–910)

Generated via `modules/infrastructure/instance_monitoring/scripts/log_vitals.py`:
- **P0** `missing_script_detected`: comment engagement subprocess path resolved to `.../modules/modules/...` in older logs (should be fixed by defensive path candidates in `modules/communication/livechat/src/engagement_runner.py`).
- **P1** `terminated_chrome_count=10`: `InstanceLock.cleanup_browser_windows()` terminated multiple `chrome.exe` processes (cleanup is opt‑in via `INSTANCE_LOCK_CLEANUP_BROWSERS`).
- **P2** `oauth_cache_noise_count=21`: `googleapiclient.discovery_cache` INFO spam (noise; reduce via `cache_discovery=False` in `youtube_auth` build).
- **P2** `Recursive systems not available`: indicates optional WRE wiring missing/disabled for that run.

## Parallel Workstreams (Designed for Multiple 0102s)

Each workstream is intentionally scoped to **minimize merge conflicts** by staying inside a small module subtree.

### Workstream A — Safety Switchboard + STOP File (WSP 77/91)

**Owner**: 0102‑A  
**Primary scope**: `modules/communication/livechat/`  
**Goal**: A single, auditable “stop now” mechanism that disables automation surfaces without touching unrelated code.

**Tasks**
- Add a STOP file gate (e.g., `memory/STOP_YT_AUTOMATION`) checked by:
  - Livechat send path
  - Comment engagement runner entrypoints
  - Any UI action surfaces that can post/submit
- Add a helper that returns a **gate snapshot** for telemetry/heartbeat.

**Acceptance Criteria**
- If STOP file exists, the system **does not send/post/click**; it logs `automation_disabled_by_stop_file` with `YT_AUTOMATION_RUN_ID`.
- Heartbeat includes the gate snapshot so the operator can confirm the system state.

---

### Workstream B — Gate‑Lab Reporting & Correlation (WSP 91)

**Owner**: 0102‑B  
**Primary scope**: `modules/communication/livechat/scripts/` + `modules/infrastructure/instance_monitoring/`  
**Goal**: Make each “gate flip” experiment produce a compact report that correlates:
1) process logs, 2) heartbeat pulses, 3) key counters.

**Tasks**
- Extend `modules/communication/livechat/scripts/youtube_automation_gate_lab.py` to ingest `logs/youtube_dae_heartbeat.jsonl` and attach recent pulses filtered by `YT_AUTOMATION_RUN_ID`.
- Generate an optional `report.md` (or `report.json`) per run with:
  - top errors/warnings
  - counters (messages attempted/sent, subprocess runs, etc.)
  - gate snapshot

**Acceptance Criteria**
- One command produces: `summary.json` + `report.md` under `logs/automation_gate_lab/<run_id>/`.
- Reports are stable for automated comparison across scenarios.

---

### Workstream C — Dependency & Process Hygiene (WSP 3 modular)

**Owner**: 0102‑C  
**Primary scope**: `modules/infrastructure/dependency_launcher/` + `modules/infrastructure/instance_lock/`  
**Goal**: Avoid collateral damage and make dependencies observable (Chrome debug + LM Studio reachability), without coupling to any single DAE.

**Tasks**
- Ensure browser cleanup remains **opt‑in** (`INSTANCE_LOCK_CLEANUP_BROWSERS=false` by default) and never kills the protected Chrome debug port.
- Add “deps status” output (Chrome debug reachable? LM Studio reachable? which port?) to the dependency launcher command path.

**Acceptance Criteria**
- YouTube DAE startup does not terminate a user’s normal Chrome.
- Dependency checks complete quickly and print actionable status.

---

### Workstream D — Comment Engagement Reliability (WSP 27/77)

**Owner**: 0102‑D  
**Primary scope**: `modules/communication/livechat/src/engagement_runner.py` + `modules/communication/video_comments/`  
**Goal**: Make the engagement runner deterministic and debuggable (no “silent hangs”), regardless of execution mode.

**Tasks**
- Confirm path resolution for `run_skill.py` is correct from all call sites.
- Standardize JSON result schema and ensure it is always emitted (even on failure).
- Add explicit progress logging checkpoints (connect → detect comments → like/heart/reply → verify → next).

**Acceptance Criteria**
- Engagement runner produces structured output (stats + timings + error) and never fails silently.
- Timeout behavior is consistent across `max_comments=0` and bounded runs.

---

### Workstream E — Contextual Replies + Semantic Rating Hooks (WSP 44)

**Owner**: 0102‑E  
**Primary scope**: `modules/communication/video_comments/src/` + `modules/infrastructure/wsp_core/src/semantic_state_engine.py`  
**Goal**: Use existing chat/session logs as memory to produce better replies *and* score them for later learning.

**Tasks**
- Extract: commenter handle + comment text + link context into `commenter_history_store`.
- Use the existing intelligent reply generator to create a reply when enabled.
- Attach an optional “debug tag” that includes:
  - commenter classification (moderator / troll / info‑seeker)
  - WSP 44 semantic state (e.g., `💬 122`)

**Acceptance Criteria**
- When `YT_COMMENT_INTELLIGENT_REPLY_ENABLED=true`, replies are contextual (not placeholders).
- When `YT_REPLY_DEBUG_TAGS=true`, the posted reply contains the debug tag.

---

### Workstream F — Safe Test Channel Defaults (FoundUps1934)

**Owner**: 0102‑F  
**Primary scope**: `modules/platform_integration/stream_resolver/` + `.env.example` + docs  
**Goal**: Make “test channel first” the default workflow without code edits per run.

**Tasks**
- Ensure `TEST_CHANNEL_ID` and `YT_CHANNELS_TO_CHECK` are honored consistently across stream resolver + DAE launch.
- Add a `gate-lab` example that uses the test channel by default when `TEST_CHANNEL_ID` is set.

**Acceptance Criteria**
- Gate-lab and YouTube DAE can run against the test channel using only env vars.

## Operator Workflow (Reproducible Experiments)

Use `YT_AUTOMATION_RUN_ID` to correlate all logs for a test run:
- `YT_AUTOMATION_RUN_ID=gate_YYYYMMDD_HHMMSS`
- Gate-lab logs: `logs/automation_gate_lab/<run_id>/`
- Heartbeat stream: `logs/youtube_dae_heartbeat.jsonl`

Example: run “observe only” for 10 minutes against the test channel:
```powershell
python modules/communication/livechat/scripts/youtube_automation_gate_lab.py `
  --scenario observe_only `
  --channels $env:TEST_CHANNEL_ID `
  --duration-seconds 600
```

