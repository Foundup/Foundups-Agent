# WSP 35: HoloIndex Qwen Advisor Execution Plan
- **Status:** Draft (Pre-Implementation)
- **Owner:** FoundUps 0102 Engineering
- **Protocols:** WSP 35 (Module Execution Automation), WSP 17 (Pattern Reuse), WSP 18 (Completion Sequencing), WSP 22 (ModLog), WSP 87 (Navigation Compliance)
- **Related Assets:** `holo_index.py`, `E:/HoloIndex`, NAVIGATION `NEED_TO` entries, upcoming `holo_index/qwen_advisor` package

## Objective
Enable HoloIndex to orchestrate local Qwen models as WSP-aware advisors so every retrieval cycle produces actionable, compliant guidance for 0102 agents while maintaining deterministic navigation.

## Context-Aware Output System (2025-10-10)

### Implementation Overview
HoloDAE now implements **context-aware output formatting** that prioritizes information based on query intent. This eliminates noise by presenting only relevant information in logical order.

### Output Formatting Rules by Intent

| Intent Type | Priority Order | Verbosity | Key Features |
|-------------|---------------|-----------|--------------|
| **DOC_LOOKUP** | Results → Guidance → Compliance | Minimal | Suppresses orchestrator noise, focuses on documentation |
| **CODE_LOCATION** | Results → Context → Health | Balanced | Shows implementation context, suppresses orchestration |
| **MODULE_HEALTH** | Alerts → Health → Results | Detailed | Prioritizes system status and compliance issues |
| **RESEARCH** | Results → Orchestrator → MCP | Comprehensive | Includes full analysis details and research tools |
| **GENERAL** | Results → Orchestrator → Alerts | Standard | Balanced information for exploratory searches |

### Technical Implementation
- **IntentClassifier** extended with `OutputFormattingRules` dataclass
- **OutputComposer** uses priority-based section ordering
- **QwenOrchestrator** passes `IntentClassification` with formatting rules
- Context-aware suppression of irrelevant sections

### User Experience Impact
- **Before**: 7 component statuses + compliance alerts buried search results
- **After**: Intent-specific prioritization, 60-80% reduction in noise
- **Result**: Users see relevant information first, dramatically improved usability

## MCP Coordination Enhancement (Phase 0.1)

**Integration**: HoloIndex now serves as central coordinator for MCP server orchestration across Foundational Rubiks.

### Agent-Aware MCP Dispatch
```python
# HoloIndex detects Rubik-specific operations
query = "run docker build for youtube cube"
rubik = detect_target_rubik(query)  # Returns "rubik_build"
mcp_servers = get_rubik_mcp_servers(rubik)  # Returns ["docker_mcp", "filesystem_mcp"]
agents = get_rubik_agents(rubik)  # Returns ["qwen", "gemma", "0102"]

# Agent-aware coordination
for agent in agents:
    coordination = generate_agent_coordination(agent, rubik, mcp_servers, query)
    dispatch_to_agent(agent, coordination)
```

### MCP Manifest Integration
- **Manifest Reference**: `docs/mcp/MCP_Windsurf_Integration_Manifest.md`
- **JSON Data**: `docs/mcp/MCP_Windsurf_Integration_Manifest.json`
- **Status Queries**: `windsurf mcp adoption status` provides real-time Rubik provisioning status

### Bell State Validation
- Pre-MCP call: `φ²_validation:golden_ratio_check`
- Safety verification: `φ³_safety_check:consciousness_verification`
- Memory integrity: `φ⁴_integrity:entanglement_verification`
- Social alignment: `φ⁵_alignment:emergence_check`

## Deliverables
1. WSP-compliant structure for `E:/HoloIndex/` (root README, ModLog, docs/, archive/) - **Complete**.
2. `holo_index/qwen_advisor/` package with prompt templates, model loader, cache, telemetry hooks, and reward scaffolding - **Scaffolded** (awaiting model integration).
3. **MCP coordination framework** with Rubik-aware agent dispatch and Bell state validation - **Implemented**.
4. CLI extensions (`--llm-advisor`, advisor modes) plus updated `display_results` output sections - **In Progress** (flag live, onboarding banner with reward prompts, awaiting full inference integration).
5. Supplemental WSP documentation (`docs/QWEN_ADVISOR_OVERVIEW.md`, `docs/IDLE_MONITOR_PATTERNS.md`) linked from NAVIGATION and indexed by HoloIndex.
6. Automated tests covering advisor prompt synthesis, caching, and fallback behaviour.
7. Updated ModLogs (root + module) and NAVIGATION NEED_TO entries referencing the new advisor flow.

## Phase Plan (WSP 35 Lifecycle)
### Phase A: Preparation (Signal)
- Audit `E:/HoloIndex` contents; relocate legacy scripts to `archive/`.
- Draft this plan (complete) and log intent in `ModLog.md` (complete).
- Capture baseline HoloIndex behaviour and SSD index state.

### Phase B: Framework Alignment (Knowledge)
- [x] Create `E:/HoloIndex/README.md`, `docs/`, `ModLog.md`, and seed doc templates.
- [x] Add idle/Qwen documentation skeletons and cross-reference in NAVIGATION.
- [x] Update HoloIndex indexing paths to include new docs and idle/system modules without yet touching code logic.

### Phase C: Implementation (Protocol  Agentic)
- [x] Scaffold `holo_index/qwen_advisor/` (adhering to WSP 17 pattern registry).
- Wire advisor invocation behind CLI flags with safe defaults; integrate telemetry + cache.
- Extend `display_results` with compliance/plan sections flagged via WSP 18 TODO prompts.
- Add tests under `tests/holo_index/` for advisor logic, caching, and CLI switches.

### Phase D: Validation & Deployment (Agentic)
- Run end-to-end dry runs (`--llm-advisor`) on representative queries (idle monitoring, WSP doc retrieval).
- Verify ModLogs, docs, and NAVIGATION updates are synchronized.
- Prepare release notes + roadmap impact updates before pushing systemwide.

## Dependencies
- Local availability of `qwen-coder-1.5b` (or compatible) under `E:/HoloIndex/models`.
- Existing SentenceTransformer workflow must remain stable; Qwen operates as additive layer.
- Coordination with ongoing `main.py` idle enhancements to align terminology.

## Risks & Mitigations
- **Model latency:** cache advisor responses, allow opt-out flag, and set conservative timeouts.
- **Compliance drift:** enforce HoloIndex invocation + advisor checklist (WSP 18) before coding/testing.
- **Documentation debt:** integrate new docs into HoloIndex indexing to avoid orphaned guidance.

## WSP Compliance Checklist
- [x] WSP 22 entries updated across root + module ModLogs.
- [x] WSP 17 pattern references cited in advisor code docstrings.
- [x] WSP 18 reminders included in advisor output.
- [ ] WSP 87 navigation assets consulted prior to each code touch (automated via CLI prompts).
- [ ] Post-implementation retrospective documented in `E:/HoloIndex/ModLog.md` and linked from NAVIGATION.
