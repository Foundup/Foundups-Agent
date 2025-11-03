# FoundUps Vision DAE

**Domain**: Infrastructure -> Observability  
**Status**: Prototype (MVP)  
**WSP Alignment**: WSP 27 (Universal DAE Architecture), WSP 48 (Recursive Improvement), WSP 77 (Agent Coordination), WSP 80 (Cube-Level Orchestration), Draft WSP 96 (MCP Governance)

---

## Purpose

FoundUps Vision DAE is the digital twin sensorium for 012. It ingests multi-modal signals
from Selenium/Gemini vision, desktop interactions, and voice triggers so Gemma 3 270M
and Qwen 1.5 B can learn 012’s behaviour patterns in real time.

Key goals:

- Stream browser telemetry emitted by `FoundUpsDriver` into an MCP-auditable log.
- Summarise Selenium run history into SQLite + Holo missions so Qwen/Gemma see every session.
- Capture desktop & app usage (window focus, keystroke cadence, hotkeys).
- Support voice launch/command triggers for hands-free operation.
- Curate training corpora so Gemma handles policy checks while Qwen synthesises
  deeper behavioural insights, and relay summaries to UI-TARS-1.5 for desktop execution.

---

## Architecture Snapshot

```text
FoundUpsVisionDAE (async daemon)
+- BrowserTelemetryWorker   -> tails logs/foundups_browser_events.log
+- SessionBatchWorker       -> bundles raw events into JSONL archives
+- RunHistoryReporter       -> polls SQLite (foundups.db) and runs Holo missions
+- UITARSDispatcher         -> drops summaries into E:/HoloIndex/models/ui-tars-1.5/telemetry
+- VoiceCommandWorker       -> optional hotword detection (SAPI / Vosk)
```

Outputs are published as JSONL session bundles under
`holo_index/telemetry/vision_dae/` and surfaced via the MCP Browser façade.

## Running the Vision DAE

### Vision Control Center (Sprint 4 - Interactive Menu)

**Main menu**: Choose option `8. 👁️ Vision DAE Control Center (Pattern Sensorium)`

The Vision Control Center provides an interactive menu with 8 management options:

1. **Start Vision DAE Daemon** - Launch the daemon with progress output
2. **Stop Daemon / Show Worker Checkpoint State** - Display checkpoint (browser offset, batch index, session ID)
3. **View Latest Summary** - Formatted display of most recent run history
4. **Stream Recent Events** - Interactive JSONL event viewer with limit selection
5. **Show UI-TARS Dispatch Log Directory** - Browse dispatch audit trail
6. **List Recent Summaries** - Browse summary archive with metadata
7. **Show Worker State (Detailed)** - Full checkpoint file paths and status
8. **Cleanup Old Files** - Retention enforcement menu (30-day summaries, 14-day dispatches)

**Standalone mode**:
```bash
python modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/menu.py
```

### Direct Daemon Launch (Bypass Menu)

- **CLI**: `python modules/infrastructure/dae_infrastructure/foundups_vision_dae/scripts/launch.py`
  - `--voice` flag enables the placeholder voice listener.
- **Main.py flag**: `python main.py --vision`

**Outputs**:
- Summaries appear under `docs/session_backups/foundups_vision_dae/run_history/`.
- UI-TARS dispatch (if `E:/HoloIndex/models/ui-tars-1.5/telemetry` exists) receives timestamped JSON for downstream automation.

---

## MCP Server Interface (Sprint 3 + Sprint 4)

Vision DAE provides a dedicated MCP server for querying telemetry summaries and worker state:

```python
from modules.infrastructure.dae_infrastructure.foundups_vision_dae.mcp.vision_mcp_server import VisionMCPServer

server = VisionMCPServer()
latest = server.get_latest_summary()
summaries = server.list_recent_summaries(limit=10)
events = server.stream_events(limit=50)  # Sprint 4 addition
state = server.get_worker_state()
```

**Endpoints** (7 total):
- `get_latest_summary` - Returns most recent run history summary
- `list_recent_summaries` - Lists recent summaries with metadata
- `stream_events` - Stream browser telemetry events from JSONL bundles (Sprint 4)
- `get_worker_state` - Returns worker checkpoint
- `update_worker_checkpoint` - Updates worker resume state
- `cleanup_old_summaries` - Retention cleanup for summaries (30 days)
- `cleanup_old_dispatches` - Retention cleanup for dispatches (14 days)

See [INTERFACE.md](INTERFACE.md) for complete API documentation.

---

## Status & Next Steps

- [x] Browser telemetry ingestion → JSONL bundles + SQLite run history summaries.
- [x] Holo mission wiring (`selenium_run_history`) for Qwen/Gemma dashboards.
- [x] UI-TARS inbox dispatcher for desktop-autonomy hand-off.
- [x] **Sprint 3**: MCP server endpoints (21/21 tests passing) - get_latest_summary, list_recent_summaries, worker checkpoints, retention cleanup
- [x] **Sprint 4**: Vision Control Center interactive menu (scripts/menu.py) - 8 management options with MCP integration
- [x] **Sprint 4**: stream_events MCP endpoint - JSONL event streaming from session bundles
- [x] **Sprint 4**: Main.py startup status prints - visibility during warm-up
- [x] **Sprint 5**: Skills.md agent-agnostic domain expertise (WSP 57 Section 10.5) - Complete cardiovascular observability
- [ ] Desktop activity + voice workers (hook into OS event stream).
- [ ] Automated remediation flows once summaries detect regressions.

See **[Skills.md](Skills.md)** for Vision DAE domain expertise (chain of thought, chain of action, learned patterns).

## Related Documentation

- **MCP Federated Nervous System**: `docs/mcp/MCP_FEDERATED_NERVOUS_SYSTEM.md` - Vision for 10K+ DAE federation via MCP
- **WSP Update Recommendations**: `docs/mcp/WSP_UPDATE_RECOMMENDATIONS_MCP_FEDERATION.md` - WSP protocols requiring MCP federation updates
- **MCP Master Services**: `docs/mcp/MCP_Master_Services.md` - Complete MCP ecosystem overview
- **Vision MCP Manifest**: `docs/mcp/vision_dae_mcp_manifest.json` - Full API specification
- **VisionDAE Architecture**: `modules/infrastructure/dae_infrastructure/docs/FoundUps_VisionDAE_Architecture.md` - Detailed technical roadmap

**Key Insight**: VisionDAE MCP is the **universal Selenium cardiovascular system**, monitoring ALL FoundUps browser automation including UI-TARS, not just VisionDAE testing. This enables 0102 to observe the entire browser automation nervous system across federated DAEs.
