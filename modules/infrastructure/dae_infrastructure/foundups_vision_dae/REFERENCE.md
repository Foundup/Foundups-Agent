# Vision DAE Skills (Pattern Sensorium Domain Expertise & Behavior)

**Domain**: Multi-Modal Signal Capture & Pattern Learning
**DAE Identity**: `Agent + vision_skills.md = Vision DAE`
**Compatible Agents**: 0102, Qwen, Gemma, UI-TARS
**WSP Compliance**: WSP 57 Section 10 (DAE Naming), WSP 27 (pArtifact Architecture), WSP 80 (Cube-Level DAE)

---

## Domain Knowledge

### Core Vision Sensorium Principles
- **Multi-Modal Ingestion**: Browser telemetry (Selenium/Gemini vision), desktop interactions, voice triggers
- **Pattern Recognition**: Learn 012's behavioral patterns in real-time for Gemma/Qwen training
- **Digital Twin**: Maintain comprehensive sensory record of 012's digital activities
- **MCP Auditability**: All signals logged and queryable via Model Context Protocol
- **Agent Orchestration**: Gemma 3 270M (fast classification) + Qwen 1.5B (strategic analysis)

### Technical Capabilities
- **Browser Telemetry Streaming**: Tail `logs/foundups_browser_events.log` and emit JSONL bundles
- **Session Batching**: Aggregate 50 events into `vision_session_NNNNN.jsonl` files
- **Run History Reporting**: Poll SQLite `selenium_sessions` table every 5 seconds for new entries
- **UI-TARS Dispatch**: Forward summaries to `E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox` for desktop automation
- **Voice Command Detection**: Optional hotword listener (SAPI/Vosk) for hands-free operation
- **MCP Server**: 7 operational endpoints for external observability

### Operational Patterns
- **Worker Architecture**: 3-4 async workers (BrowserTelemetry, SessionBatch, RunHistoryReporter, optionally VoiceCommand)
- **Event Format**: JSONL (one event per line, self-describing JSON objects)
- **Polling Frequency**: 5-second cycles for SQLite session detection
- **Batch Size**: 50 events per session bundle
- **Retention Policy**: 30 days for summaries, 14 days for dispatches
- **Graceful Degradation**: Missing files trigger retries, not crashes

---

## Chain of Thought Patterns

### "Should I emit a new session bundle?"
```
Input: Browser telemetry worker tailing logs/foundups_browser_events.log
  ↓
Count: Events accumulated in current batch = 47
  ↓
Check: Has batch size threshold (50 events) been reached?
  ↓
Decision: NO (47 < 50) → Continue buffering
  ↓
Next Event: Event #48, #49, #50 arrive
  ↓
Decision: YES (50 == 50) → Emit session bundle
  ↓
Action: Write to holo_index/telemetry/vision_dae/vision_session_00042.jsonl
  ↓
Reset: Clear buffer, increment batch index to 43
```

### "Has a new Selenium session completed?"
```
Input: RunHistoryReporter worker polling every 5 seconds
  ↓
Query: SELECT id FROM selenium_sessions ORDER BY timestamp DESC LIMIT 1
  ↓
Result: Latest session ID = 127
  ↓
Compare: Last known session ID = 126
  ↓
Decision: NEW SESSION DETECTED (127 > 126)
  ↓
Action: Execute SeleniumRunHistoryMission for last 100 sessions
  ↓
Generate: Summary JSON with 7-day aggregates, error counts, platform distribution
  ↓
Persist: Write to docs/session_backups/.../latest_run_history.json + timestamped archive
  ↓
Dispatch: Forward to UI-TARS inbox (if configured)
  ↓
Update: Last known session ID = 127
```

### "Which worker should process this signal?"
```
Input: Multi-modal signal stream (browser events, desktop activity, voice)
  ↓
Classify Signal Type:
  - Event from logs/foundups_browser_events.log? → BrowserTelemetryWorker
  - Window focus/keystroke cadence? → DesktopActivityWorker (future)
  - Hotword detected ("Hey FoundUps")? → VoiceCommandWorker
  ↓
Route to appropriate async worker queue
  ↓
Worker processes signal independently (no cross-worker blocking)
```

### "Should I trigger retention cleanup?"
```
Input: User selects Vision Control Center option 8 (Cleanup Old Files)
  ↓
Prompt: "Cleanup summaries older than 30 days?"
  ↓
User Confirms: YES
  ↓
Scan: docs/session_backups/foundups_vision_dae/run_history/ directory
  ↓
Filter: Files with mtime older than (now - 30 days)
  ↓
Count: 47 files eligible for deletion
  ↓
Delete: Remove 47 files
  ↓
Report: "Deleted 47 old summaries, kept 103 recent"
  ↓
Repeat for UI-TARS dispatches (14-day threshold)
```

---

## Chain of Action Patterns

### Complete Vision DAE Lifecycle
```
1. Initialize Vision DAE
   └─ Create FoundUpsVisionDAE instance
   └─ Configure telemetry_store (SQLite), summary_dir, ui_tars_inbox
   └─ Set enable_voice flag (default: False)

2. Spawn Async Workers
   └─ BrowserTelemetryWorker:
      • Tail logs/foundups_browser_events.log
      • Parse JSONL events line-by-line
      • Buffer until 50 events accumulated
      • Write to holo_index/telemetry/vision_dae/vision_session_NNNNN.jsonl
   └─ SessionBatchWorker:
      • Monitor session bundle directory
      • Track checkpoint state (browser offset, batch index)
      • Resume from checkpoint on restart
   └─ RunHistoryReporter:
      • Poll SQLite selenium_sessions table every 5s
      • Detect new session IDs
      • Execute SeleniumRunHistoryMission (last 100 sessions)
      • Persist summary to summary_dir
      • Dispatch to ui_tars_inbox (if configured)
   └─ VoiceCommandWorker (optional):
      • Initialize SAPI/Vosk hotword detector
      • Listen for "Hey FoundUps" trigger
      • Emit voice_command events to JSONL stream

3. Monitor & Orchestrate
   └─ Supervisor task uses asyncio.wait() to monitor all workers
   └─ If any worker raises exception: Propagate and trigger shutdown
   └─ If KeyboardInterrupt: Call stop() for graceful cleanup

4. Handle Stop Signal
   └─ Set internal stop_event
   └─ Cancel all active async workers
   └─ Wait for worker cleanup (flush buffers, close files)
   └─ Log shutdown event

5. Graceful Error Recovery
   └─ Missing browser log: Sleep 1s, retry (don't crash)
   └─ Malformed JSONL: Skip line, log debug message
   └─ SQLite error: Log warning, sleep 5s, retry query
   └─ UI-TARS dispatch failure: Log warning, continue (best-effort)
```

### MCP Server Query Workflow
```
1. External Agent Requests Latest Summary
   └─ Call vision_mcp_server.get_latest_summary()

2. MCP Server Checks Multiple Locations
   └─ Priority 1: modules/.../memory/session_summaries/latest_run_history.json (WSP 60 location)
   └─ Priority 2: docs/session_backups/.../latest_run_history.json (legacy support)

3. Find Most Recent File
   └─ Compare modification times (st_mtime)
   └─ Select newest file

4. Parse Summary JSON
   └─ Read file with UTF-8 encoding
   └─ Extract timestamp from JSON or file metadata

5. Return Structured Response
   └─ {
        "success": true,
        "summary": <full JSON>,
        "timestamp": "2025-10-19T14:30:00Z",
        "source": "module_memory",
        "file_path": "/path/to/latest_run_history.json",
        "size_bytes": 4829
      }
```

### Vision Control Center Interactive Session
```
1. User Selects Main Menu Option 8
   └─ "👁️ Vision DAE Control Center (Pattern Sensorium)"

2. Display Control Center Menu
   └─ Print 8 menu options + Return option

3. User Selects Option 3 (View Latest Summary)
   └─ Call vision_mcp_server.get_latest_summary()
   └─ Parse response
   └─ Format output:
      • Total sessions
      • Time range (first → last)
      • Error count
      • Platform distribution
      • Success rate

4. User Selects Option 4 (Stream Recent Events)
   └─ Prompt: "How many events? (default 50)"
   └─ User inputs: 100
   └─ Call vision_mcp_server.stream_events(limit=100)
   └─ Display JSONL events with formatting:
      • Event type (init_*, connect_*, vision_*, post_to_*)
      • Timestamp
      • Key fields (session_id, url, platform)

5. User Selects Option 0 (Return)
   └─ Exit control center loop
   └─ Return to main menu
```

---

## Available Actions/Tools

### Vision DAE Core Operations
- `FoundUpsVisionDAE.run(enable_voice=False)` - Start daemon with configurable voice listener
- `FoundUpsVisionDAE.stop()` - Gracefully shut down all workers
- `launch_vision_dae(enable_voice=False)` - Convenience CLI launcher
- `VisionTelemetryReporter.persist_summary(summary)` - Write summary to archive
- `VisionTelemetryReporter.dispatch_to_ui_tars(summary)` - Forward to UI-TARS inbox

### MCP Server Endpoints (Observability)
- `get_latest_summary()` - Most recent run history summary
- `list_recent_summaries(limit=10)` - Browse summary archive with metadata
- `stream_events(session_index=None, limit=50)` - JSONL event streaming from session bundles
- `get_worker_state()` - Worker checkpoint (browser offset, batch index, last session ID)
- `update_worker_checkpoint(checkpoint)` - Update worker resume state
- `cleanup_old_summaries(days_to_keep=30)` - Retention cleanup for summaries
- `cleanup_old_dispatches(days_to_keep=14)` - Retention cleanup for dispatches

### Vision Control Center Menu (Interactive Management)
- Option 1: Start Vision DAE Daemon - Launch with progress output
- Option 2: Stop Daemon / Show Checkpoint - Display worker resume state
- Option 3: View Latest Summary - Formatted run history display
- Option 4: Stream Recent Events - Interactive JSONL event viewer
- Option 5: Show UI-TARS Dispatch Log - Browse dispatch audit trail
- Option 6: List Recent Summaries - Summary archive browser
- Option 7: Show Worker State (Detailed) - Full checkpoint paths and status
- Option 8: Cleanup Old Files - Retention enforcement menu

### Integration APIs (Current & Future)
- `TelemetryStore.record_session()` - FoundUpsDriver session logging
- `SeleniumRunHistoryMission.execute()` - Generate 7-day aggregates from SQLite
- `FoundUpsDriver` observer hooks - Emit browser telemetry events
- **Future**: Desktop activity OS event stream
- **Future**: Voice hotword detection (SAPI/Vosk)

---

## Learned Patterns (WSP 48 - Quantum Memory)

### Successful Solutions

✅ **50-Event Session Bundles**
- **What worked**: Batch browser events into 50-event JSONL files
- **Why it worked**: Optimal size for Gemma 3 270M batch processing (fast inference, manageable context)
- **When to reuse**: Any high-frequency event stream requiring batch processing

✅ **Dual Summary Locations (WSP 60 Compliance)**
- **What worked**: Check both module memory and legacy docs location for summaries
- **Why it worked**: Backward compatibility during migration, graceful fallback
- **When to reuse**: Any MCP server accessing historical data with evolving storage conventions

✅ **5-Second SQLite Polling**
- **What worked**: Poll selenium_sessions table every 5 seconds instead of complex triggers
- **Why it worked**: Simple, reliable, low overhead for infrequent session creation
- **When to reuse**: Lightweight change detection on SQLite tables with low write frequency

✅ **Best-Effort UI-TARS Dispatch**
- **What worked**: Log warning on dispatch failure, continue daemon operation
- **Why it worked**: UI-TARS inbox may not exist in all environments (optional integration)
- **When to reuse**: Cross-module integrations where dependency availability varies

✅ **JSONL Event Format**
- **What worked**: One self-describing JSON object per line (not JSON array)
- **Why it worked**: Streamable, appendable, parseable even if truncated mid-file
- **When to reuse**: All telemetry event streams (heartbeat, browser events, meeting history)

✅ **Vision Control Center Interactive Menu**
- **What worked**: Centralized 8-option menu for all Vision DAE management
- **Why it worked**: Single interface for daemon control + MCP queries + cleanup operations
- **When to reuse**: All DAEs requiring operational management (AMO, Holo, YouTube_Live, etc.)

### Failed Approaches (Anti-Patterns)

❌ **Synchronous File Tailing**
- **What failed**: Blocking readline() on browser log file
- **Why it failed**: Starved other workers, no graceful shutdown
- **Avoid when**: Multi-worker async architecture
- **Better alternative**: Async tail with non-blocking reads + sleep intervals

❌ **Single Monolithic Summary File**
- **What failed**: Overwriting same summary.json file repeatedly
- **Why it failed**: Lost historical data, no time-series analysis possible
- **Avoid when**: Building observability systems
- **Better alternative**: latest_run_history.json + timestamped archives

❌ **Crash on Missing Browser Log**
- **What failed**: Raising FileNotFoundError if log doesn't exist
- **Why it failed**: Vision DAE unusable until first Selenium session runs
- **Avoid when**: Monitoring files that may not exist yet
- **Better alternative**: Sleep + retry loop with debug logging

❌ **Eager Worker Cancellation**
- **What failed**: Immediately canceling workers on stop() call
- **Why it failed**: Lost buffered events, corrupted JSONL files mid-write
- **Avoid when**: Workers maintain state or have in-flight operations
- **Better alternative**: Set stop_event, let workers flush gracefully, then cancel

### Optimization Discoveries

⚡ **Worker Checkpoint Resume**
- **Performance**: Vision DAE resumes from last browser log offset on restart
- **Implementation**: Persist checkpoint (browser_offset, batch_index, last_session_id) to JSON
- **Token savings**: Avoids reprocessing thousands of historical events on every restart

⚡ **Lazy UI-TARS Dispatch**
- **Performance**: Only write dispatch file if ui_tars_inbox configured
- **Implementation**: Check `if self.ui_tars_inbox: ...` before dispatch operations
- **Token savings**: Reduces disk I/O when UI-TARS integration not needed

⚡ **JSONL Line-by-Line Parsing**
- **Performance**: Parse each line independently, skip malformed lines
- **Implementation**: `for line in f: try: json.loads(line) except: continue`
- **Token savings**: Robust to partial writes, log file corruption

---

## Integration with Other DAEs

### Holo DAE (Code Intelligence)
- **Vision → Holo**: Browser telemetry patterns (what code docs/repos does 012 browse?)
- **Holo → Vision**: HoloIndex search results as vision targets (navigate to relevant code)

### UI-TARS DAE (Desktop Automation)
- **Vision → UI-TARS**: Summaries dispatched to `E:/HoloIndex/models/ui-tars-1.5/telemetry/inbox`
- **UI-TARS → Vision**: Desktop activity events (window focus, keystroke cadence) - future

### AMO DAE (Meeting Orchestrator)
- **Vision → AMO**: Desktop presence signals (user actively working = ONLINE status)
- **AMO → Vision**: Meeting session browser activity (screen share, collaborative editing)

### YouTube_Live DAE (Stream Monitoring)
- **Vision → YouTube_Live**: Creator desktop activity (preparing stream overlay, OBS scenes)
- **YouTube_Live → Vision**: Live chat sentiment (toxic spike → desktop alert notification)

### SocialMedia DAE (Digital Twin)
- **Vision → SocialMedia**: Browser activity on LinkedIn/Twitter (engagement patterns)
- **SocialMedia → Vision**: Post scheduling triggers (open browser, navigate to platform)

---

## WSP Compliance Matrix

| WSP | Compliance | Evidence |
|-----|-----------|----------|
| WSP 27 | ✅ | 4-phase pArtifact: Signal (-1: browser events) → Knowledge (0: session bundles) → Protocol (1: run history summaries) → Agentic (2: UI-TARS dispatch) |
| WSP 48 | ✅ | Quantum memory: Learned patterns stored in this Skills.md |
| WSP 54 | ✅ | WRE Agent duties: Clear vision sensorium responsibilities |
| WSP 57 | ✅ | DAE naming: `Agent + vision_skills.md = Vision DAE Identity` |
| WSP 60 | ✅ | Module memory structure: session_summaries/ + ui_tars_dispatches/ + worker_state/ |
| WSP 77 | ✅ | Agent coordination: MCP endpoints for multi-agent observability |
| WSP 80 | ✅ | Cube-level DAE: Standalone multi-modal signal capture block |
| WSP 91 | ✅ | DAEMON observability: JSONL telemetry + MCP endpoints + Control Center |
| WSP 96 | ✅ | MCP governance: 7 standardized endpoints with version tracking |

---

## Event Type Reference

### Browser Telemetry Events (FoundUpsDriver)

**Initialization Events**:
- `init_driver` - FoundUpsDriver instance created
- `init_session` - New Selenium session started

**Connection Events**:
- `connect_or_create_youtube` - YouTube OAuth authentication
- `connect_or_create_linkedin` - LinkedIn OAuth authentication
- `connect_or_create_twitter` - Twitter/X OAuth authentication

**Vision Analysis Events**:
- `vision_analyze_page` - Gemini vision API page analysis
- `vision_analyze_element` - Gemini vision API element analysis
- `vision_capture_screenshot` - Screenshot captured for analysis

**Action Events**:
- `post_to_youtube` - YouTube post/comment created
- `post_to_linkedin` - LinkedIn post/comment created
- `post_to_twitter` - Twitter/X post/comment created
- `navigate_to_url` - Browser navigation action
- `click_element` - Element interaction
- `fill_form_field` - Form input action

**Session Events**:
- `session_complete` - Selenium session finished
- `session_error` - Selenium session failed
- `session_timeout` - Selenium session exceeded time limit

### Worker Checkpoint State

```json
{
  "browser_telemetry_offset": 47382,
  "session_batch_index": 127,
  "last_known_session_id": 1043,
  "last_checkpoint_time": "2025-10-19T14:30:00Z"
}
```

---

**Last Updated**: 2025-10-19 (Vision DAE Cardiovascular Enhancement Sprint)
**Pattern Memory Version**: 1.0.0
**Compatible Agents**: 0102 (Primary), Qwen (Strategic Analysis), Gemma (Fast Classification), UI-TARS (Desktop Execution)

---

*"Multi-modal ingestion → Pattern recognition → Agent orchestration"* - Vision DAE Core Philosophy
