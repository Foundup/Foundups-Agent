# Holo Command Interface

**Status:** Draft adopting VisionDAE MVP (2025-10-17)  
**Scope:** Define how 0102 executes actions via Holo so that every DAE shows its chain of thought

---

## 1. Principle

All FoundUps automation flows through the Holo command interface.
- 0102 issues a command (voice, JSON, CLI shim).
- Holo dispatches it to the correct DAE/worker.
- The daemon emits telemetry so 012 can observe the chain of reasoning.

CLI menus are read-only facades. They may invoke commands, but the command bus is canonical.

---

## 2. Command Bus Contract

Implementers MUST provide three layers:

1. **Command verb** ? registered in HoloIndex (e.g., 	raining.batch, 	raining.utf8_scan, ision.start).
2. **Action handler** ? logic that runs the command (reuses existing helpers to avoid vibecoding).
3. **Telemetry emitter** ? daemon stream entries (event, payload) so observers see the pulse of the system.

### Event Schema
`json
{
  "timestamp": "2025-10-17T12:34:56.123Z",
  "daemon": "vision_dae",
  "command": "training.utf8_scan",
  "event": "completed",
  "payload": {
    "findings": 12,
    "targets": ["modules/infrastructure/..."],
    "stored_patterns": 12
  }
}
`

---

## 3. Example (VisionDAE UTF-8 Hygiene)

1. CLI submenu option 12 Å® 2 triggers 	raining.utf8_scan.
2. The same verb is available to 0102 via holo_index.command.run("training.utf8_scan").
3. VisionDAE worker tails telemetry and emits highlights.
4. Gemma/Qwen receive the findings via PatternMemory.

Summary of actions:
- CLI forwards to un_utf8_hygiene_scan.
- Command bus calls the same helper with interactive=False.
- Daemon writes JSONL events in holo_index/telemetry/vision_dae/.

---

## 4. Implementation Checklist

| Step | Description | Status | WSP |
|------|-------------|--------|-----|
| 1 | Register command verb in HoloIndex command controller | Required | WSP 77/80 |
| 2 | Implement handler (reuse module functions) | Required | WSP 33 |
| 3 | Emit telemetry (daemon log + session bundle) | Required | Draft WSP 96 |
| 4 | Update ModLogs/Docs (CLI notes optional) | Required | WSP 22 |
| 5 | Add automated tests / Gemma training as needed | Recommended | WSP 46/48 |

---

## 5. FAQ

**Q:** Can a module execute actions directly without the command bus?  \
**A:** No. All commands must route through Holo so daemons remain the source of truth.

**Q:** Do we still need the CLI menu?  \
**A:** Yes, as an observer/control panel for 012. Internally it forwards to the command bus.

**Q:** How do we add new commands?  \
**A:** Extend the command controller, register the handler, update telemetry, document the verb.

---

**Reminder:** The daemon stream is the chain of thought. Every new capability must be visible there, whether it runs via YouTube, Vision, or the core HoloDAE.
