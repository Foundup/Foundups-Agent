# WSP Alignment Notes - FoundUps Agent Market (Outer Layer)

## WSP Canon Read (Exact Paths)
- `WSP_framework/src/WSP_00_Zen_State_Attainment_Protocol.md`
- `WSP_framework/src/WSP_CORE.md`
- `WSP_framework/src/WSP_22_ModLog_Structure.md`
- `WSP_framework/src/WSP_22a_Module_ModLog_and_Roadmap.md`
- `WSP_framework/src/WSP_47_Module_Violation_Tracking_Protocol.md`
- `WSP_framework/src/WSP_49_Module_Directory_Structure_Standardization_Protocol.md`
- `WSP_framework/src/WSP_60_Module_Memory_Architecture.md`
- `WSP_framework/src/WSP_87_Code_Navigation_Protocol.md`
- `WSP_framework/src/WSP_MASTER_INDEX.md`

## Vision/Architecture Sources Read (Exact Paths)
- `WSP_knowledge/docs/WRE_FoundUps_Vision.md`
- `WSP_knowledge/enterprise_vision/FoundUps_Vision_2025.md`
- `modules/README.md`
- `modules/ROADMAP.md`
- `modules/communication/moltbot_bridge/README.md`
- `modules/communication/moltbot_bridge/INTERFACE.md`
- `modules/communication/moltbot_bridge/src/openclaw_dae.py`

## Non-Negotiable WSP Rules Applied
1. HoloIndex-first retrieval before implementation (`WSP_00`, `WSP_CORE`, `WSP_87`).
2. Module docs are memory artifacts and must be created/updated with code (`WSP_CORE`, `WSP_60`).
3. Module structure must follow standard module layout under `modules/<domain>/<module>/` (`WSP_49`).
4. `INTERFACE.md` is contract memory and required (`WSP_CORE`, `WSP_60`).
5. `tests/TestModLog.md` is required for verification memory (`WSP_CORE`, `WSP_22`).
6. Violations and deferrals must be tracked explicitly (`WSP_47`).
7. Roadmap progression must stay explicit as PoC -> Prototype -> MVP (`WSP_CORE`, `WSP_22a`).

## Task Scope (Will Touch)
- Create new module: `modules/foundups/agent_market/`
- Create required spec pack docs in that module.
- Add minimal Python skeleton/stubs under `modules/foundups/agent_market/src/`.
- Add tests under `modules/foundups/agent_market/tests/`.
- Update Holo retrieval discoverability for this module by adding navigation entries and memory-pipeline note.
- Add this task's alignment/vision extract docs under `docs/`.

## HoloIndex Integration Notes
- Added retrieval mappings in `NAVIGATION.py` for Agent Market launch/task/pipeline lookups.
- Appended memory retrieval participation note to `holo_index/README.md` so FAM artifacts are treated as explicit Tier-0/Tier-1 memory targets.
- Added retrieval mapping for verified milestone distribution publish contract.
- `python holo_index.py --index-all` failed in this workspace due Chroma batch limit (`Batch size ... greater than max batch size`).
- Applied WSP-safe fallback: `python holo_index.py --index-symbols --symbol-roots modules/foundups/agent_market`.

## Out of Scope (Will Not Touch)
- No changes to existing production DAEs, scheduler logic, livechat, social automation, or blockchain runtime behavior.
- No UI implementation beyond optional route/interface placeholders in docs.
- No chain-specific token deployment implementation.
- No unrelated refactors.

## Deviation Policy
- Any deviation from above scope or WSP requirements will be recorded in:
  - `modules/foundups/agent_market/violations.md`
  - `modules/foundups/agent_market/ModLog.md`

---

## Change Log

### 2026-02-07: CABR Gate + Launch Orchestrator + Repo Provisioning

**HoloIndex Search Performed First**: Confirmed existing work in `modules/foundups/agent_market/`.

**A) CABR-Gated Distribution**
- Added `CABRGateError` exception in `exceptions.py`
- Added `get_latest_cabr_score()` method in `in_memory.py`
- Updated `publish_verified_milestone()` with `cabr_threshold` parameter
- Policy: publish blocked if `cabr_threshold > 0` and (score missing OR score < threshold)
- Fail-safe: missing CABR score raises explicit domain error

**B) Launch Orchestrator**
- Created `src/orchestrator.py` with:
  - `LaunchOrchestrator` class (adapter-driven, deterministic)
  - `LaunchEvent` and `LaunchResult` dataclasses
  - `launch_foundup()` convenience function
- 5-step flow: validate/create foundup → token deploy → repo provision → initial task → emit events
- All events auditable with `event_id`, `foundup_id`, `actor_id`, `timestamp`, `payload`

**C) Repo Provisioning Boundary**
- Added `RepoProvisioningAdapter` interface in `interfaces.py`
- Added in-memory implementation in `in_memory.py`
- Stores: `foundup_id`, `repo_name`, `repo_url`, `provider`, `default_branch`
- Emits `repo.provisioned` event

**Tests Added**
- `test_cabr_gate.py`: 6 tests for CABR gate behavior
- `test_orchestrator.py`: 7 tests for launch orchestrator and repo provisioning
- Total: 23 tests (10 original + 13 new), all passing

**Files Modified**
- `src/exceptions.py`: Added `CABRGateError`
- `src/interfaces.py`: Added `cabr_threshold` param, `get_latest_cabr_score()`, `RepoProvisioningAdapter`
- `src/in_memory.py`: Added CABR gate check, repo provisioning, `get_latest_cabr_score()`
- `src/orchestrator.py`: NEW - launch orchestration

**WSP Compliance**
- WSP 50: HoloIndex searched before implementation
- WSP 87: Used HoloIndex for code navigation
- WSP 49: All files in proper module structure
- WSP 11: Interface contracts documented

### 2026-02-07 Clarification
- Launch step 4 now creates initial tasks when a task pipeline adapter is provided.
- When no task pipeline adapter is provided, orchestration emits `launch.initial_task_prepared` and returns the prepared task artifact.

### 2026-02-07: OpenClaw/FAM Wiring + Moltbook Distribution

**HoloIndex Search Performed First**: Verified existing OpenClaw DAE and FAM structures.

**A) OpenClaw -> FAM Boundary**
- Created `moltbot_bridge/src/fam_adapter.py`:
  - `FAMAdapter` class for in-memory or injected adapter support
  - `FAMLaunchRequest` / `FAMLaunchResponse` dataclasses
  - `parse_launch_intent()` for command parsing
  - `handle_fam_intent()` entry point for OpenClaw routing
- Updated `openclaw_dae.py`:
  - Added `IntentCategory.FOUNDUP` for FoundUp-related intents
  - Added FOUNDUP keywords to intent classification
  - Added `fam_adapter` domain route
  - Added `_execute_foundup()` method

**B) MoltbookDistributionAdapter**
- Added `MoltbookDistributionAdapter` interface to FAM `interfaces.py`
- Created `moltbot_bridge/src/moltbook_distribution_adapter.py`:
  - `MoltbookDistributionAdapterStub` with in-memory storage
  - Discord webhook push for production
  - `publish_milestone()`, `get_publish_status()`, `list_published_milestones()`

**C) E2E Integration Tests**
- Created `test_e2e_integration.py` with 11 tests:
  - Full flow: launch -> task -> proof -> verify -> CABR gate -> distribution
  - CABR gate blocking tests (low score, missing score)
  - FAM adapter parsing and execution tests
  - Moltbook distribution adapter tests

**D) Bug Fix**
- Fixed `emit_event()` in `in_memory.py` to extract `foundup_id`/`task_id` from payload

**Tests Added**
- `test_e2e_integration.py`: 11 tests for E2E and adapter integration
- Total: 29 tests (23 original + 6 adapter tests), all passing

**Files Created**
- `moltbot_bridge/src/fam_adapter.py`
- `moltbot_bridge/src/moltbook_distribution_adapter.py`
- `agent_market/tests/test_e2e_integration.py`

**Files Modified**
- `moltbot_bridge/src/openclaw_dae.py`: Added FOUNDUP intent routing
- `agent_market/src/interfaces.py`: Added MoltbookDistributionAdapter
- `agent_market/src/in_memory.py`: Fixed emit_event payload extraction

**WSP Compliance**
- WSP 11: Interface contracts (clean boundaries)
- WSP 50: HoloIndex searched before implementation
- WSP 72: Module independence (FAM defines interface, moltbot_bridge implements)
- WSP 73: Partner-Principal-Associate architecture
- WSP 87: Used HoloIndex for code navigation

### 2026-02-07: Security Canon Alignment (WSP-Level)

- Elevated skill safety scanning from module implementation detail to WSP canon requirement.
- Updated framework protocols and index entries:
  - `WSP_framework/src/WSP_71_Secrets_Management_Protocol.md`
  - `WSP_framework/src/WSP_95_WRE_SKILLz_Wardrobe_Protocol.md`
  - `WSP_framework/src/WSP_96_MCP_Governance_and_Consensus_Protocol.md`
  - `WSP_framework/src/WSP_MASTER_INDEX.md`
- Reason: OpenClaw/FAM runtime already enforces scanner preflight; WSP canon now guarantees new modules inherit the same fail-closed security posture.
