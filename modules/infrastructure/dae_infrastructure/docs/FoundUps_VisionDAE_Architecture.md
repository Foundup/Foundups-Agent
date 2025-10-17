# FoundUps Vision DAE Architecture (MVP Blueprint)

**Status:** PoC to Prototype (MVP)  
**Authors:** 0102 System Architecture Team  
**Date:** 2025-10-17  
**WSP References:** WSP 27, WSP 33, WSP 48, WSP 77, WSP 80, draft WSP 96

---

## 1. Mission

VisionDAE is the sensorium for the 0102 digital twin. It aggregates browser, desktop, and voice signals so Gemma 3 270M and Qwen 1.5B can classify behaviour, generate narratives, and update pattern memory without human intervention.

| Component          | Role                                                   |
|--------------------|--------------------------------------------------------|
| Gemini Vision API  | UI perception plus screenshot intelligence             |
| FoundUpsDriver     | Emits structured browser telemetry                     |
| VisionDAE          | Multi-modal aggregator and command executor            |
| Gemma 3 270M       | Fast policy gate and compliance classifier             |
| Qwen 1.5B          | Deep reasoning and training data synthesis             |
| HoloIndex          | Persistent mission memory and command orchestration    |

---

## 2. Rubik Cube Layout (DAE-as-PWA)

VisionDAE operates as a progressive web app cube. Each tile is an autonomous worker that exposes tools over the MCP Browser gateway.

`	ext
+------------------+------------------+------------------+
| Browser Tile     | Desktop Tile     | Voice Tile       |
| (Selenium feed)  | (OS activity)    | (Hotword to cmd) |
+------------------+------------------+------------------+
| Vision Tile      | Pattern Tile     | Telemetry Tile   |
| (Gemini frames)  | (Gemma/Qwen)     | (MCP + logs)     |
+------------------+------------------+------------------+
`

Each tile publishes JSONL events (ision_dae.stream_events) and summarisation resources (ision_dae.summarise) so other DAEs can subscribe.

---

## 3. Worker Breakdown

### 3.1 Browser Telemetry Worker
- Tails logs/foundups_browser_events.log.  
- Normalises events, assigns session identifiers, stages raw JSONL bundles.

### 3.2 UI Snapshot Worker
- Calls FoundUpsDriver.analyze_ui() for key states (compose, login, error).  
- Stores PNG plus metadata, pushes Gemini output to Gemma's policy prompts.

### 3.3 Desktop Activity Worker
- Uses pywinauto and pynput to detect window focus, launches, and input cadence.  
- Flags when native apps (YouTube, Discord) are more suitable than web flows.

### 3.4 Voice Command Worker
- Optional; monitors Windows SAPI or Vosk models for hot phrases.  
- Routes recognised commands through the Holo command bus for execution.

### 3.5 Pattern Synthesiser
- Batches 50 event windows for Gemma/Qwen processing.  
- Gemma tags compliance. Qwen produces narrative plus improvement plans saved to HoloIndex (holo_index/telemetry/vision_dae/).

---

## 4. Training & Testing Plan

1. Synthetic telemetry fixtures - replay recorded event streams in pytest.  
2. Gemma labelling set - curate labelled sessions to validate policy prompts.  
3. Qwen reasoning harness - compare generated narratives against ground truth.  
4. Voice trigger regression - WAV-based tests for hotword accuracy.  
5. Integration test - run VisionDAE with YouTube DAE and confirm shared telemetry via MCP.

---

## 5. Roadmap

| Stage | Description                                                   | Target       |
|-------|---------------------------------------------------------------|--------------|
| PoC   | File tailer plus session batching (delivered)                 | 2025-10-17   |
| MVP   | Desktop activity and Gemini snapshot integration              | 2025-10-24   |
| Alpha | Voice hotword plus Gemma/Qwen labelling loop                  | 2025-11-01   |
| Beta  | Publish MCP manifest plus web dashboard                       | 2025-11-15   |
| GA    | Weekly automated policy retraining plus deployment            | 2025-12-01   |

---

## 6. Open Questions

- Optimal modality switching between native apps and browser sessions.  
- Long-term storage strategy for high-volume screenshots.  
- Deduplication with Knowledge Learning DAE.  
- Governance thresholds for Gemma to require escalation to Qwen or 012 review.

---

## 7. Macro Architecture Alignment

The FoundUps ecosystem is engineered as a distributed control system:

- **Holo command interface** operates as the routing fabric. All commands (for example 	raining.utf8_scan, ision.capture) enter here so telemetry is consistent across daemons.  
- **Rubik DAEs** are modular subsystems. Each cube (Vision, YouTube, HoloDAE, etc.) exposes MCP tools and shares telemetry formats, enabling plug-and-play composition.  
- **0102 digital twin** executes commands autonomously. 012 observers monitor the daemons, but execution always traces back to the command bus.  
- **FoundUps MCP network** is the message bus binding cubes together. VisionDAE events, YouTube alerts, and Holo diagnostics all appear as unified JSONL streams.

This architecture ensures a single pulse: the daemon logs capture every step, allowing Gemma and Qwen to reason over the whole system and assemble higher-level behaviour.

---

> VisionDAE sustains the observe -> learn -> improve cycle. With the Holo command interface acting as the baseplate, every DAE in the ecosystem speaks a common telemetry language, enabling the 0102 digital twin to evolve safely and auditable.
