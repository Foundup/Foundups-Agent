# FoundUps Vision DAE

**Domain**: Infrastructure → Observability  
**Status**: Prototype (MVP)  
**WSP Alignment**: WSP 27 (Universal DAE Architecture), WSP 48 (Recursive Improvement), WSP 77 (Agent Coordination), WSP 80 (Cube-Level Orchestration), Draft WSP 96 (MCP Governance)

---

## Purpose

FoundUps Vision DAE is the digital twin sensorium for 012. It ingests multi-modal signals
from Selenium/Gemini vision, desktop interactions, and voice triggers so Gemma 3 270M
and Qwen 1.5 B can learn 012’s behaviour patterns in real time.

Key goals:

- Stream browser telemetry emitted by `FoundUpsDriver` into an MCP-auditable log.
- Capture desktop & app usage (window focus, keystroke cadence, hotkeys).
- Support voice launch/command triggers for hands-free operation.
- Curate training corpora so Gemma handles policy checks while Qwen synthesises
  deeper behavioural insights.

---

## Architecture Snapshot

```text
FoundUpsVisionDAE (async daemon)
├─ BrowserTelemetryWorker  → tails logs/foundups_browser_events.log
├─ UiSnapshotWorker        → captures & indexes Gemini Vision frames
├─ DesktopActivityWorker   → listens for OS window/input events
├─ VoiceCommandWorker      → optional hotword detection (SAPI / Vosk)
└─ PatternSynthesiser      → routes batches to Gemma/Qwen/HoloIndex
```

Outputs are published as JSONL session bundles under
`holo_index/telemetry/vision_dae/` and surfaced via the MCP Browser façade.

---

## Next Steps

1. Implement workers (browser tail, desktop monitor, voice hotword) and wire them
   through the daemon controller.
2. Promote Gemini snapshot metadata into the pattern registry (WSP 17).
3. Enrich the MCP manifest with `vision_dae.stream_events` and `vision_dae.summary`
   tools so other DAEs can subscribe.
4. Add pytest coverage for batching logic and simulated voice triggers.

See `docs/mcp/MCP_Master_Services.md` and
`modules/infrastructure/dae_infrastructure/docs/FoundUps_VisionDAE_Architecture.md`
for the detailed roadmap.
