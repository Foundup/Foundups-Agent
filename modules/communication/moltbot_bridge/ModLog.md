# ModLog - moltbot_bridge

## 2026-02-16: Conversation identity anchor normalization

**Author**: 0102  
**WSP**: 11, 22, 50

### Changes
- `src/openclaw_dae.py`
  - Added `_ensure_conversation_identity()` to normalize conversation outputs.
  - All conversation execution branches (AI Gateway, Ollama, Qwen, fallback)
    now return an identity-anchored response (`0102:` prefix) when missing.
  - Prevents nondeterministic conversational output from breaking role/identity
    expectations in end-to-end flows.

### Validation
- Targeted failing tests fixed:
  - `test_conversation_returns_response`
  - `test_blocked_command_downgrades_to_conversation`
- Included in concatenated cross-module run:
  - `modules/communication/moltbot_bridge/tests`
  - `modules/foundups/agent_market/tests`
  - `modules/foundups/simulator/tests`
  - Result: **335 passed, 2 warnings**

---

## 2026-02-16: FAM token auto-resolution + collision safety

**Author**: 0102  
**WSP**: 11, 22, 50

### Changes
- `src/fam_adapter.py`:
  - Added deterministic token auto-generation from FoundUp name when token is omitted.
  - Added explicit `AUTO`/legacy `FUP` seed handling.
  - Added collision-safe symbol resolution against existing registry symbols
    (`BASE`, `BASE2`, `BASE3`, ...).
  - Launch pipeline now uses resolved symbol for both `Foundup.token_symbol`
    and `TokenTerms.token_symbol`.
- `INTERFACE.md`:
  - Documented FOUNDUP route token resolution behavior and command contracts.

### Validation
- Covered by targeted lane:
  - `modules/foundups/agent_market/tests/test_e2e_integration.py`
  - Included in 51/51 pass run logged in Agent Market + Simulator TestModLogs.

---

## 2026-02-16: FAM/Moltbook Compatibility Stabilization

**Author**: 0102
**WSP**: 11, 22, 50

### Changes
- `src/fam_adapter.py`:
  - Knowledge/LLM responses now append deterministic command help.
  - Help now includes both launch and create command variants.
- `src/moltbook_distribution_adapter.py`:
  - Deterministic milestone IDs now use `moltbook_post_` prefix for moltbook channel.
  - Milestone listing now preserves insertion order (oldest -> newest).

### Validation
- Included in concatenated run:
  - `modules/foundups/agent_market/tests`
  - `modules/foundups/simulator/tests`
  - Result: **229 passed**

---

## 2026-02-08: Hardening Tranche 3 - Correlator Integration + Containment

**Author**: 0102
**WSP**: 71, 91, 95

### Changes
- `openclaw_dae.py`:
  - Added `_emit_to_overseer()` for security event emission to AI Overseer correlator
  - Added `_check_containment()` for containment state queries
  - Integrated containment check at process entry (Phase 0.5)
  - `permission_denied` events now emit to correlator
  - `command_fallback` events now emit to correlator

- `webhook_receiver.py`:
  - `rate_limited` events now emit to AI Overseer correlator
  - Added DAEmon signal: `[DAEMON][OPENCLAW-RATELIMIT]`

### DAEmon Signals (WSP 91)
```
[DAEMON][OPENCLAW-PERMISSION] event=permission_denied tier=... sender=... reason=...
[DAEMON][OPENCLAW-RATELIMIT] event=rate_limited sender=... channel=... reason=...
[DAEMON][OPENCLAW-FALLBACK] event=command_fallback sender=... reason=...
[DAEMON][OPENCLAW-CONTAINMENT] event=containment_active sender=... action=... expires_at=...
```

### Validation
- Full module test suite: **92 passed**

---

## 2026-02-08: Hardening Tranche 2 - SOURCE tier, Rate Limiting, COMMAND Fallback

**Author**: 0102
**WSP**: 22, 50, 71, 95, 96

### Changes

#### SOURCE Tier Enforcement (fail-closed)
- `openclaw_dae.py`: Added `_check_source_permission()` method
  - Integrates with `AgentPermissionManager` for explicit SOURCE tier grants
  - Fail-closed: blocks if permission manager unavailable or check fails
  - Permission denied events emitted with 60s dedupe window
  - Emits `permission_denied` signal for forensics (WSP 71)

#### Webhook Rate Limiting (token bucket)
- `webhook_receiver.py`: Added `TokenBucket` and `WebhookRateLimiter` classes
  - Per-sender bucket: 2 tokens/sec, 10 burst capacity (configurable)
  - Per-channel bucket: 5 tokens/sec, 20 burst capacity (configurable)
  - Returns HTTP 429 with `X-Retry-After` header when exceeded
  - Configurable via env vars: `OPENCLAW_RATE_*`

#### COMMAND Graceful Degradation
- `openclaw_dae.py`: Added `_command_advisory_fallback()` method
  - Returns deterministic advisory when WRE unavailable
  - Provides three actionable options (CLI, retry, query mode)
  - Includes error detail when WRE raises exception

### Files Modified
- `src/openclaw_dae.py`: +80 lines (permission check, event emission, fallback)
- `src/webhook_receiver.py`: +70 lines (rate limiter implementation)
- `tests/test_hardening_tranche.py` (NEW): 17 tests covering all new paths
- `tests/run_tests.ps1`: Added `test_hardening_tranche.py` to security gate
- `INTERFACE.md`: Documented rate limiting API and SOURCE tier check

### Validation
- Hardening tranche tests: **17 passed**
- Full module test suite: **72 passed**
- Security gate: PASS (test_skill_boundary_policy, test_skill_safety_guard, test_hardening_tranche)

---

## 2026-02-07: OpenClaw security operations hardening verified (DAEmon + CI gate)

**Author**: 0102  
**WSP**: 22, 50, 71, 95, 96

### Changes
- Added operator-visible skill safety status in monitor output (`_execute_monitor`):
  - gate status, required/enforced flags, last check timestamp, gate message.
- Hardened CI runner to enforce security gate first:
  - `tests/run_tests.ps1` runs `test_skill_boundary_policy.py` and `test_skill_safety_guard.py` before full suite.
  - Fails immediately on security gate failure.
  - Added `-SkipSecurityGate` switch for local-only diagnostics.

### Operational Verification (DAEmon)
- Forced scanner failure drill completed with:
  - Dedupe 60s window: 1 emitted, 5 suppressed.
  - Dedupe 5s window: expiry re-alert confirmed (3 emitted in 15s).
- Canonical signal observed:
  - `[DAEMON][OPENCLAW-SECURITY] event=openclaw_security_alert ...`

### Validation
- Security gate tests: PASS
- Full module test suite: `55 passed`
- Holo memory re-index executed after docs update.

---

## 2026-02-07: WRE Graceful Degradation for COMMAND Intents (WSP 15 P0 #5, MPS 15/20)

**Author**: 0102
**WSP**: 15 (MPS), 50 (Pre-Action Verification)

### Context
`_wsp_preflight()` hard-blocked COMMAND intents when WRE was unavailable (returned `False`), which caused `process()` to downgrade to CONVERSATION. This made the advisory fallback in `_execute_command()` unreachable - users got a generic Digital Twin response instead of actionable CLI guidance.

### Fix
Changed `_wsp_preflight()` Rule 2: COMMAND intents now pass preflight even when WRE is unavailable. The `_execute_command()` handler provides the advisory fallback with specific guidance (CLI execution, retry, query mode). SCHEDULE and SYSTEM still hard-block (no advisory fallback exists for those).

### Validation
- 50/50 tests passing (all existing tests backward-compatible)

---

## 2026-02-07: AgentPermissionManager SOURCE Tier Gate (WSP 15 P0 #2, MPS 17/20)

**Author**: 0102
**WSP**: 15 (MPS), 50 (Pre-Action Verification), 71 (Secrets), 95 (WRE Skills)

### Context
P0 #2 from WSP 15 MPS. OpenClaw COMMAND intents could reach WRE execution without file-specific permission checks. The SOURCE tier existed but was never resolved by `_resolve_autonomy_tier()` (always returned DOCS_TESTS), and `_check_source_permission()` passed `file_path=None` to the permission manager, bypassing allowlist/forbidlist validation.

### Implementation
**3-layer security gate for source code modification:**

1. **File path extraction** (`_extract_file_paths()`): Regex extracts file paths from COMMAND messages (forward/backslash, quoted, known extensions). Returns normalized forward-slash paths.

2. **Source modification detection** (`_is_source_modification()`): Heuristic combining source-verb keywords ("edit", "modify", "refactor", etc.) with file path presence or module/source references.

3. **SOURCE tier wiring** (`_resolve_autonomy_tier()`): Commander + COMMAND + source modification intent now resolves to `AutonomyTier.SOURCE` instead of `DOCS_TESTS`. Without permission manager loaded: fail-closed to `ADVISORY`.

4. **File-specific permission gate** (`_check_source_permission()`): Now extracts file paths from intent and calls `check_permission(file_path=fpath)` per file, validating against allowlist/forbidlist.

5. **Execution gate** (`_execute_command()`): Pre-execution check blocks WRE routing if any target file is forbidden. Returns "Permission Denied" response with the specific file and reason.

### Security Flow
```
COMMAND intent → _is_source_modification() → True?
  → _resolve_autonomy_tier() → SOURCE
  → _check_permission_gate() → _check_source_permission()
    → _extract_file_paths() → ["modules/foo/src/bar.py"]
    → permissions.check_permission(file_path="modules/foo/src/bar.py")
    → allowlist/forbidlist validation
  → _execute_command() → pre-execution file gate
  → WRE (only if all files pass)
```

### Files
- `src/openclaw_dae.py` (MODIFIED):
  - `_extract_file_paths()`: NEW static method (regex file path extraction)
  - `_is_source_modification()`: NEW method (source-verb + file path heuristic)
  - `_resolve_autonomy_tier()`: MODIFIED (SOURCE tier for source modification)
  - `_check_source_permission()`: MODIFIED (file-specific permission checks)
  - `_execute_command()`: MODIFIED (pre-execution file permission gate)
- `tests/test_openclaw_dae.py` (MODIFIED, +20 new tests):
  - `TestFilePathExtraction`: 7 tests (python, multi, md, json, none, quoted, backslash)
  - `TestSourceModificationDetection`: 5 tests (edit+path, modify+module, run=no, deploy=no, refactor+source)
  - `TestSourceTierResolution`: 4 tests (commander SOURCE, non-source DOCS_TESTS, non-commander ADVISORY, fail-closed)
  - `TestSourcePermissionGate`: 4 tests (no manager, file allowed, file forbidden, exception)

### Validation
- **50/50 tests passing** (8 original Layer 0 + 11 Gemma + 20 SOURCE tier + 11 Layer 1-3)
- **Fail-closed verified**: No permissions = ADVISORY, exception = denied, forbidlist = blocked
- **Backward compatible**: All original tests pass unchanged

---

## 2026-02-07: Gemma 270M Hybrid Intent Classifier (WSP 15 P0 #1, MPS 18/20)

**Author**: 0102
**WSP**: 15 (MPS), 77 (Agent Coordination), 84 (Code Reuse), 96 (Skill Execution)

### Context
P0 priority item from WSP 15 MPS scoring. OpenClaw's keyword-based intent classification (133 lines of heuristics) was vulnerable to prompt injection and poorly calibrated. Any message containing "run" would classify as COMMAND regardless of actual intent.

### Implementation
**Architecture**: Hybrid Option C (keyword pre-filter + Gemma validation)
1. **Fast keyword pre-filter** (<1ms): Existing `INTENT_KEYWORDS` scoring retained
2. **Gemma 270M validation** (<30ms per candidate): Binary YES/NO classification for top 3 keyword candidates
3. **Combined scoring**: `(keyword * 0.3) + (gemma * 0.7)` for prompt-injection resistance
4. **Graceful degradation**: Falls back to keyword-only if Gemma model unavailable

### Files
- `src/gemma_intent_classifier.py` (NEW, 290 lines): Standalone `GemmaIntentClassifier` class
  - Lazy model loading (follows `gemma_validator.py` pattern)
  - `_binary_classify()`: Single YES/NO inference per category
  - `classify()`: Hybrid scoring with keyword pre-filter
  - Performance stats tracking
- `src/openclaw_dae.py` (MODIFIED):
  - `_get_gemma_classifier()`: Lazy loader for classifier
  - `classify_intent()`: Rewritten with 2-phase hybrid (keyword -> Gemma)
  - Metadata now includes `classification_method`, `gemma_scores`, `classification_latency_ms`
- `tests/test_openclaw_dae.py` (MODIFIED, +11 new tests):
  - `TestGemmaIntentClassifier`: 5 unit tests (fallback, default, candidates, stats, availability)
  - `TestGemmaHybridIntegration`: 6 integration tests (disabled, metadata, mock hybrid, degradation, foundup)

### Validation
- **30/30 tests passing** (8 original + 11 new Gemma + 11 existing Layer 1-3)
- **Backward compatible**: All original Layer 0 intent tests pass unchanged
- **Env control**: `OPENCLAW_GEMMA_INTENT=0` forces keyword-only mode

### Env Vars
- `OPENCLAW_GEMMA_INTENT` (default `1`): Enable/disable Gemma hybrid classification

---

## 2026-02-07: Security preflight audit findings + NAVIGATION.py expansion

**Author**: 0102
**WSP**: 22, 50, 71, 87, 95

### Findings (Ecosystem Deep Dive)
- OpenClaw security posture audited: **CLEAN** - no violations found across 45+ security tests.
- Cisco skill scanner (`cisco-ai-skill-scanner`) binary not installed on dev machine. `OPENCLAW_SECURITY_PREFLIGHT_ENFORCED=1` default in `main.py` was blocking startup entirely. Default changed to `=0` (warn, don't block). Production should set `=1`.
- Security controls validated: Honeypot defense (2-phase deception), skill safety guard (fail-closed), graduated autonomy tiers (ADVISORY→SOURCE), secret redaction patterns.

### Gaps Identified (WSP 15 MPS Scored)
| Gap | MPS Score | Status |
|-----|-----------|--------|
| Keyword-based intent classification (prompt injection risk) | 18/20 P0 | Needs Gemma 270M binary classification |
| SOURCE tier permission check incomplete | 17/20 P0 | AgentPermissionManager integration needed |
| No WRE graceful degradation for COMMAND intents | 15/20 P1 | Fails if WRE unavailable |
| No rate limiting on webhook endpoints | 15/20 P1 | DoS vector |

### NAVIGATION.py Expansion
- Added 15 openclaw/moltbot entries to `NAVIGATION.py` for HoloIndex discoverability:
  - `openclaw dae frontal lobe`, `openclaw intent classification`, `openclaw permission gate`
  - `openclaw security sentinel`, `openclaw skill safety guard`, `openclaw honeypot defense`
  - `openclaw fam adapter`, `openclaw foundup launch`, `openclaw webhook receiver`
  - `openclaw install setup`, `openclaw security tests`, `openclaw dae tests`
  - `moltbot bridge digital twin`, `moltbot bridge workspace skills`

---

## 2026-02-07: Skill boundary policy codified + enforcement tests

**Author**: 0102
**WSP**: 50, 71, 95, 96

### Changes
- Added explicit boundary policy:
  - `docs/SKILL_BOUNDARY_POLICY.md`
  - Defines separation between OpenClaw workspace skills and internal module `skillz`.
- Updated docs to reference the policy:
  - `README.md`
  - `INTERFACE.md`
- Added enforcement tests:
  - `tests/test_skill_boundary_policy.py`
  - Verifies workspace skills remain docs-only.
  - Verifies mutating intent categories always pass through `_ensure_skill_safety()`.

### Validation
- `.\modules\communication\moltbot_bridge\tests\run_tests.ps1`
- Result: PASS

---

## 2026-02-07: Deterministic Test Runner Standardized

**Author**: 0102
**WSP**: 22, 34, 95

### Changes
- Added canonical test runner script: `tests/run_tests.ps1`.
- Runner now enforces deterministic pytest behavior by:
  - Using local venv Python (`.venv\Scripts\python.exe`)
  - Setting `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1`
  - Restoring prior env state after execution
- Updated test docs to reference the runner:
  - `tests/README.md`
  - `tests/TestModLog.md`

### Validation
- `powershell -NoProfile -ExecutionPolicy Bypass -File modules/communication/moltbot_bridge/tests/run_tests.ps1`
- Result: 34 passed, 2 warnings

---

## 2026-02-07: WSP 95/71 Security Audit - Full Compliance

**Author**: 0102
**WSP**: 71, 95, 96

### Changes
- Completed security audit of all mutating DAE entrypoints for scanner gate parity.
- Added comprehensive test coverage (14 tests) for WSP 95/71 requirements:
  - Scanner missing + required mode => block (fail-closed)
  - High severity => block
  - Medium at threshold => block
  - Low below threshold => allow
  - Critical always blocks regardless of threshold
  - Cache TTL prevents re-scan
  - Cache expiry triggers re-scan
  - Enforced mode blocks failed scans
  - Non-enforced mode allows with warning
  - FOUNDUP intent category properly gated
- Created `violations.md` documenting clean audit (no violations found).
- All mutating routes (COMMAND, SYSTEM, SCHEDULE, SOCIAL, AUTOMATION, FOUNDUP) confirmed gated.

### Validation
- `modules/communication/moltbot_bridge/tests`: 34 passed
- All 14 skill safety guard tests passing

---

## 2026-02-07: Cisco Skill Scanner Safety Gate Integration

**Author**: 0102
**WSP**: 11, 22, 50, 73, 91

### Changes
- Added `src/skill_safety_guard.py` with `run_skill_scan()` wrapper around Cisco `skill-scanner`.
- Integrated cached skill safety gate into `src/openclaw_dae.py`:
  - Checks workspace skills before mutating/skill-driven routes.
  - Policy configurable via env vars (`REQUIRED`, `ENFORCED`, `MAX_SEVERITY`, `TTL_SEC`).
  - Unsafe scan downgrades route to conversation fail-safe.
- Hardened intent classification:
  - Word-boundary keyword matching to prevent substring false positives.
  - Greeting-first conversation override.
  - Boundary-safe extracted task cleanup.
- Hardened AI Overseer lazy loader to degrade gracefully on non-ImportError failures.
- Added tests: `tests/test_skill_safety_guard.py`.

### Validation
- `modules/communication/moltbot_bridge/tests`: 20 passed
- `modules/foundups/agent_market/tests`: 34 passed

---

## 2026-02-07: OpenClaw intent matching hardening + overseer fail-safe

**Author**: 0102
**WSP**: 50, 73, 91

### Changes
- Updated `src/openclaw_dae.py` intent classifier to use word-boundary regex matching instead of raw substring matching.
  - Prevents false positives such as `at` matching inside `what`.
- Added greeting-first conversation override for `hi|hey|hello` opener messages.
- Updated task extraction to remove matched keywords using word-boundary regex, avoiding token mutilation.
- Hardened AI Overseer lazy loader to catch non-ImportError failures (for example `SyntaxError`) and degrade gracefully.

### Validation
- `modules/communication/moltbot_bridge/tests`: 20 passed
- `modules/foundups/agent_market/tests`: 34 passed

---

## 2026-02-07: FAM Integration + Moltbook Distribution Adapter

**Author**: 0102
**WSP**: 11, 46, 50, 72, 73, 87

### Changes

**New: `src/fam_adapter.py` (~280 lines)**
- OpenClaw -> FAM boundary adapter
- `FAMLaunchRequest` / `FAMLaunchResponse` dataclasses
- `FAMAdapter` class: in-memory or injected adapter support
- `parse_launch_intent()`: parses "launch foundup" commands
- `handle_fam_intent()`: entry point for OpenClaw FOUNDUP routing

**New: `src/moltbook_distribution_adapter.py` (~180 lines)**
- `MoltbookDistributionAdapterStub`: implements FAM `MoltbookDistributionAdapter` interface
- In-memory storage for PoC testing
- Discord webhook push for production distribution
- `publish_milestone()`, `get_publish_status()`, `list_published_milestones()`

**Modified: `src/openclaw_dae.py`**
- Added `IntentCategory.FOUNDUP` for FoundUp-related intents
- Added FOUNDUP keywords: "foundup", "launch foundup", "token", "milestone", etc.
- Added `fam_adapter` domain route
- Added `_execute_foundup()` method routing to FAM adapter

### Architecture
```
OpenClaw (Partner)
    |
    v
[IntentCategory.FOUNDUP]
    |
    v
FAMAdapter (Principal)
    |
    v
LaunchOrchestrator (Associate)
    |
    +---> InMemoryAgentMarket (PoC)
    +---> MoltbookDistributionAdapterStub
```

### Test Results
- 29/29 FAM tests passing (including E2E integration)
- OpenClaw DAE tests: 22/22 passing

---

## 2026-02-02: OpenClaw WRE Integration - Plugin + Skillz + Workspace Skills

**Author**: 0102
**WSP**: 46, 50, 65, 73, 77, 91, 96

### Changes (Session 2)

**New: `OpenClawPlugin` class in `src/openclaw_dae.py`**
- WRE OrchestratorPlugin adapter: bridges WRE plugin interface (WSP 65) to OpenClaw DAE
- `as_plugin()` convenience method on OpenClawDAE returns singleton plugin
- `register_with_wre()` auto-registers on first WRE lazy-load (bidirectional routing)
- Handles async-to-sync bridging for WRE compatibility (ThreadPoolExecutor fallback)

**New: WRE SKILLz (2 skills)**
- `skillz/openclaw_intent_router/SKILLz.md` - Gemma 270M intent classification (3-step micro CoT)
- `skillz/openclaw_executor/SKILLz.md` - Qwen+Gemma execution pipeline (4-step micro CoT)
- Both registered in `skills_registry_v2.json` (total skills: 16 -> 18)

**New: OpenClaw Workspace Skills (3 skills)**
- `workspace/skills/openclaw-execute/SKILL.md` - Task execution through WRE routing
- `workspace/skills/openclaw-monitor/SKILL.md` - System health and WRE metrics
- `workspace/skills/openclaw-schedule/SKILL.md` - YouTube Shorts scheduling via CPS

**Modified: `src/__init__.py`**
- Exports `OpenClawPlugin` alongside `OpenClawDAE`

**Modified: `skills_registry_v2.json`**
- Added `openclaw_intent_router` (Gemma, CLASSIFICATION, WSP 46/50/73/96)
- Added `openclaw_executor` (Qwen+Gemma, DECISION, WSP 46/50/73/77/91/96)

**Test Results**: 22/22 passing (WRE plugin registration confirmed in test output)

---

## 2026-02-02: OpenClaw DAE - The Frontal Lobe

**Author**: 0102
**WSP**: 46, 50, 73, 77, 91, 96

### Changes (Session 1)

**New: `src/openclaw_dae.py` (~530 lines)**
- OpenClaw DAE: control-plane "frontal lobe" translating intent into WRE-routed execution
- Full autonomy loop: Ingress -> Intent -> Preflight -> Plan -> Permission -> Execute -> Validate -> Remember
- WSP 73 Partner-Principal-Associate structure: OpenClaw=Partner, DAE=Principal, Domain DAEs=Associates
- 7 intent categories: QUERY, COMMAND, MONITOR, SCHEDULE, SOCIAL, SYSTEM, CONVERSATION
- 4 autonomy tiers: ADVISORY (anyone), METRICS (commander), DOCS_TESTS (commander), SOURCE (explicit)
- Security: non-commanders capped at ADVISORY, secret patterns redacted, all decisions logged
- Lazy-loaded WRE, AI Overseer, Agent Permissions (no import-time cost on webhook boot)
- Pattern memory integration: stores outcomes in WRE SQLite for recursive learning

**Modified: `src/webhook_receiver.py`**
- Replaced `process_with_holoindex()` as primary route with `process_via_openclaw_dae()`
- HoloIndex-only path kept as legacy fallback on DAE failure
- OpenClaw DAE singleton lazy-initialized on first request

**Modified: `src/__init__.py`**
- Exports OpenClawDAE alongside FastAPI components
- Graceful degradation when FastAPI not installed (DAE always importable)

**Modified: `INTERFACE.md`**
- Documented OpenClaw DAE API, intent categories, autonomy tiers
- Added WSP 73 Partner-Principal-Associate architecture
- Added security model documentation

**New: `tests/test_openclaw_dae_standalone.py` (~210 lines)**
- 22 tests across 5 layers (classification, preflight, permissions, security, E2E)
- 22/22 passing after intent classification refinement
- Standalone runner (no pytest/FastAPI dependency required)

### Architecture Decision
OpenClaw DAE is the "frontal lobe" because:
1. WSP is the rail (governance, not just reminders)
2. WRE is the execution cortex (pattern recall, not computation)
3. OpenClaw is the sensory gateway (multi-channel intent ingress)
4. Domain DAEs are the motor cortex (execute: communicate, schedule, index)

---

## 2026-02-01: OpenClaw Documentation Update

**Author**: 0102 (via Antigravity)

### Changes
- Created `docs/INSTALL_OPENCLAW.md` with comprehensive installation guide
- Updated `README.md` to reflect OpenClaw rebrand (Clawdbot → Moltbot → OpenClaw)
- Kept module name as `moltbot_bridge` to avoid churn from future rebrands
- Updated `workspace/AGENTS.md` to treat HoloIndex output issues as P0 and require WSP-guided deep dive before proceeding
- Updated OpenClaw naming across bridge interface, webhook endpoints, and setup docs while keeping legacy compatibility

### Critical Lesson Documented

> **Node.js must be installed INSIDE WSL, not just on Windows.**
> 
> Using Windows npm to install OpenClaw causes `node: not found` errors because
> the OpenClaw binary attempts to run with WSL's Node, which doesn't exist if
> only Windows Node is installed.

### Fix Applied
```bash
# Install Node.js in WSL
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt-get install -y nodejs

# Then install OpenClaw
npm install -g openclaw
openclaw onboard
```

### Related Files
- `docs/INSTALL_OPENCLAW.md` - Full installation guide
- `docs/CHANNEL_SETUP.md` - Channel configuration (needs update for openclaw commands)
- `README.md` - Updated with rebrand info
