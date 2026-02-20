# Holo Skills Atlas (WSP 90 Ready)

0102 cheat sheet for HoloIndex + HoloDAE. Qwen leads orchestration, Gemma validates patterns, and this map keeps every CLI skill tied to the module that powers it. Because `holo_index/cli.py` enforces WSP 90 UTF-8 at the entry point, documentation can surface mnemonic tags for fast scanning without contaminating machine-to-machine output.

Contract note:
- This file is a menu-focused operations atlas, not an exhaustive CLI flag list.
- Canonical interface contracts live in `holo_index/INTERFACE.md`.
- Canonical machine schema lives in `holo_index/docs/HOLO_INDEX_MACHINE_LANGUAGE_SPEC_0102.json`.

## Menu Snapshot (0102 Ops)
```
============================================================
HoloDAE Code Intelligence & WSP Compliance Observatory
============================================================
0. [ROCKET] Launch HoloDAE (Autonomous Monitoring) | --start-holodae

CORE PREVENTION (Stay out of vibecoding)
1. [SEARCH] Semantic Search                        | --search
2. [OK] WSP Compliance Check                       | --check-module
3. [AI] Pattern Coach                              | --pattern-coach
4. [BOX] Module Analysis                           | --module-analysis

SUPPORT SYSTEMS (Diagnostics)
5. [PILL] Health Analysis                          | --health-check
6. [GHOST] Orphan Analysis                         | --wsp88
7. [DATA] Performance Metrics                      | --performance-metrics
8. [BOT] LLM Advisor (with search)                 | --llm-advisor

CONTINUOUS OBSERVABILITY
9. [EYE] Stop Monitoring                           | --stop-holodae
10. [STAT] HoloDAE Status                          | --holodae-status
11. [COG] Chain-of-Thought Log                     | --thought-log
12. [SLOW] Slow Mode                               | --slow-mode
13. [MEMORY] Pattern Memory                        | --pattern-memory
14. [FEEDBACK] Memory Feedback (per card)          | --memory-feedback

MCP RESEARCH BRIDGE
15. [HOOK] MCP Hook Map                            | --mcp-hooks
16. [LOG] MCP Action Log                           | --mcp-log

SYSTEM CONTROLS
17. [PUBLISH] Work Publisher (Auto Git/Social)     | --monitor-work

QWEN/GEMMA AUTONOMOUS TRAINING
18. [UTF8] UTF-8 Fix (Autonomous Remediation)      | main.py --training-command utf8_fix --targets <scope>

VERIFICATION
19. [CHECK] System Check                           | --system-check

98. Exit
------------------------------------------------------------
00. [REFRESH] Manual Index Refresh                 | --index-all
============================================================
```

## WSP 90 Context
- Entry points `holo_index/cli.py` and `main.py` wrap `stdout`/`stderr` in UTF-8, so 0102 can run these commands on Windows without encoding crashes.
- Keep new CLI entry points inside `holo_index/cli.py` to inherit the same WSP 90 guardrail.

## Core Prevention
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[SEARCH]` | Semantic Search | `--search` | `holo_index/core/holo_index.py`, `holo_index/core/intelligent_subroutine_engine.py` | Dual index: code hits, WSP protocols, health notices, adaptive-learning optimizations. |
| `[OK]` | WSP Compliance Check | `--check-module` | `holo_index/core/holo_index.py` (`check_module_exists`) | Confirms module location + WSP 49 structure before coding; returns README/INTERFACE gaps and dependency hints. |
| `[AI]` | Pattern Coach | `--pattern-coach` (manual surface) + auto during search | `holo_index/qwen_advisor/pattern_coach.py` | Classifies search context vs. stored anti-vibecoding patterns, emits coaching reminders into the throttled output stream. |
| `[BOX]` | Module Analysis | `--module-analysis` | `holo_index/module_health/size_audit.py`, `holo_index/module_health/structure_audit.py` | Runs duplicate/size/structure sweeps across the detected cube(s); reuses same auditors that feed Qwen rulings. |

## Support Systems (Diagnostics)
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[PILL]` | Health Analysis | `--health-check` | `holo_index/core/intelligent_subroutine_engine.py` | Executes intelligent subroutine pipeline to surface module health, test coverage gaps, and structure issues for the active query. |
| `[GHOST]` | Orphan Analysis | `--wsp88` | `holo_index/monitoring/wsp88_orphan_analyzer.py` | Full WSP 88 run: identifies orphaned files, proposes reconnection targets, lists safest enhancement paths. |
| `[DATA]` | Performance Metrics | `--performance-metrics` | `holo_index/qwen_advisor/performance_orchestrator.py`, `holo_index/qwen_advisor/telemetry.py` | Summarizes HoloDAE session effectiveness (token savings, compliance rate, action counts). |
| `[BOT]` | LLM Advisor | `--llm-advisor` | `holo_index/qwen_advisor/advisor.py`, `holo_index/qwen_advisor/rules_engine.py` | Activates Qwen advisor guidance with risk scoring, WSP reminders, TODO lists, and telemetry logging. |

## Continuous Observability
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[EYE]` | Start Monitoring | `--start-holodae` | `holo_index/qwen_advisor/autonomous_holodae.py`, `holo_index/qwen_advisor/holodae_coordinator.py` | Launches autonomous monitoring loop (similar to other DAEs) with breadcrumb logging and adaptive throttling. |
| `[EYE]` | Stop Monitoring | `--stop-holodae` | `holo_index/qwen_advisor/autonomous_holodae.py` | Stops the monitoring loop and exits cleanly. |
| `[STAT]` | HoloDAE Status | `--holodae-status` | `holo_index/qwen_advisor/holodae_coordinator.py` | Prints current monitoring state, uptime, and watched file count. |
| `[COG]` | Chain-of-Thought Log | `--thought-log` | `holo_index/adaptive_learning/breadcrumb_tracer.py`, `holo_index/qwen_advisor/chain_of_thought_logger.py` | Streams recent breadcrumb events; currently prints initialization cues and is ready for richer diff output. |
| `[SLOW]` | Slow Mode | `--slow-mode` | `holo_index/cli.py` (env `HOLODAE_SLOW_MODE`) | Forces 2-3s delays so 012 can observe recursive feedback loops (training / demo only). |
| `[MEMORY]` | Pattern Memory | `--pattern-memory` | `modules/infrastructure/wre_core/wre_master_orchestrator.py` | Dumps stored intervention patterns Gemma classified as reusable; helpful before new enhancements. |
| `[FEEDBACK]` | Memory Feedback | `--memory-feedback` | `modules/ai_intelligence/ai_overseer/src/holo_memory_sentinel.py` | Records per-card feedback (good/noisy/missing) into sentinel logs + feedback learner. |

## MCP Research Bridge
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[HOOK]` | MCP Hook Map | `--mcp-hooks` | `modules/communication/livechat/src/mcp_youtube_integration.py` | Runs connector handshake to verify Model Context Protocol registrations and health. |
| `[LOG]` | MCP Action Log | `--mcp-log` | `holo_index/qwen_advisor/holodae_coordinator.py` (stub), telemetry logs | Placeholder hook: echoes status until streaming log reader lands; check Qwen breadcrumbs for now. |

## System Controls
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[PUBLISH]` | Work Publisher | `--monitor-work` | `modules/ai_intelligence/work_completion_publisher/src/monitoring_service.py` | Starts the monitoring daemon that auto-publishes finished work (git + social), wired through MPS scoring. |

## Verification
| Tag | Skill | CLI Flag | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[CHECK]` | System Check | `--system-check` | `holo_index/reports/holo_system_check.py` | Runs a wiring audit of CLI flags and emits a concise report for 012/0102 review. |

*Note*: PID Detective and Execution Log Analyzer are not wired to CLI yet; keep them in the additional skills list until flags exist.

## Qwen/Gemma Autonomous Training
| Tag | Skill | Invocation | Primary Modules | Output / Notes |
| --- | --- | --- | --- | --- |
| `[UTF8]` | UTF-8 Fix | `python main.py --training-command utf8_fix --targets "<path>[,<path>]" [--json-output]` | `modules/ai_intelligence/training_system/scripts/training_commands.py`, `holo_index/qwen_advisor/orchestration/utf8_remediation_coordinator.py` | Qwen orchestrates UTF-8 remediation campaigns using WSP 90, auto-approving replacements and summarizing files fixed. |

Other training verbs: `utf8_scan`, `utf8_summary`, and `batch` (IdleAutomation training) use the same command bus.

## Additional Skills & Utilities Worth Surfacing
- `[DOC-LINK]` `--link-modules`, `--list-modules`, `--wsp` — managed by `holo_index/qwen_advisor/module_doc_linker.py` for doc ↔ module cohesion.
- `[INDEX]` `--dae-cubes`, `--code-index`, `--function-index`, `--code-index-report` — deep code index flows from `holo_index/reports/codeindex_reporter.py`.
- `[INDEX]` `--index-symbols`, `--symbol-roots` — symbol indexing for function/class discovery (semantic memory refresh).
- `[SKILLz]` `--index-skillz` (aliases: `--index-skills`, `--reindex-skills`) — rebuilds the SKILLz wardrobe index for agent discovery.
- `[DOC-GUARD]` `--docs-file`, `--audit-docs`, `--check-wsp-docs`, `--fix-ascii`, `--rollback-ascii` — documentation guardians driven by `holo_index/qwen_advisor/telemetry.py` and helpers under `holo_index/utils`.
- `[SUPPORT]` `--support`, `--diagnose`, `--troubleshoot` — quick recipes that bundle multiple skills for recurring incidents.
- `[CHECK]` `--system-check` — quick wiring audit for HoloDAE menu flags, writes a report under `holo_index/reports/`.
- `[LIFECYCLE]` `--stop-holodae`, `--holodae-status` — lifecycle controls for the monitoring loop.
- `[FEEDBACK]` `--advisor-rating`, `--ack-reminders`, `--memory-feedback`, `--memory-query`, `--memory-notes`, `--no-advisor` — feedback hooks that tune advisor/memory behavior and log compliance actions.
- `[OFFLINE]` `--offline` — disable model downloads and auto-install; falls back to lexical search when embeddings are unavailable.
- `[SCORE]` auto module scoring — triggered on queries mentioning priority/roadmap/MPS; uses WSP 15/37 scoring data.

## Subsystem Map (Quick Orientation)
- `holo_index/core/` — search engine, intelligent subroutine orchestration, SSD index wiring.
- `holo_index/qwen_advisor/` — advisor runtime, autonomous holodae control, pattern coach, performance telemetry.
- `holo_index/monitoring/` — root violation watcher, orphan analyzer, self-monitoring pipelines (WSP 88 compliant).
- `holo_index/module_health/` — size/structure/dependency auditors invoked by module analysis and health checks.
- `holo_index/adaptive_learning/` — breadcrumb tracer, collaboration signaling, adaptive response optimizer.
- `holo_index/missions/` — MCP-exposed missions for specialized data pulls (e.g., Selenium run history).
- `holo_index/skillz/` — HoloIndex SKILLz wardrobe (MPS evaluation prompts, WSP 95).
- `modules/ai_intelligence/work_completion_publisher/` — work monitoring + auto-publish subsystem used by skill #17.
- `modules/ai_intelligence/training_system/` — training command bus powering UTF-8 remediation and future autonomous workflows.

## Gap Check & Next Experiments
- `[PID]` CLI toggles for PID Detective and Execution Log Analyzer (menu slots 15-16) are still missing; feature audit flagged them.
- `[MCP-LOG]` `--mcp-log` currently returns a placeholder message—hook it to the telemetry stream under `holo_index/qwen_advisor/chain_of_thought_logger.py` or MCP server logs.
- `[SKILLS]` Consider adding a `skills/` prompt directory (see `holo_index/tests/test_ai_delegation_pipeline.py`) if we want per-trigger micro-prompts alongside this atlas.

Use this atlas before coding sessions: run the relevant skill, capture advisor reminders, and log actions per WSP 22 in the module ModLogs.
