# FoundUps pAVS IronClaw Roadmap (Agent Builder + Digital Twin)

## Status
- Phase: Prototype planning -> execution kickoff
- Date baseline: 2026-02-22
- Scope:
  - Run IronClaw inside pAVS as an agent-builder runtime
  - Run IronClaw inside pAVS as a Digital Twin execution lane
- WSP references: WSP 11, WSP 15, WSP 22, WSP 46, WSP 50, WSP 73, WSP 77, WSP 84, WSP 91, WSP 95, WSP 96

### Progress Update (2026-02-22)
- OpenClaw/IronClaw submenu and CLI flags now expose:
  - IronClaw chat/voice (key-isolated)
  - IronClaw runtime status
  - IronClaw gateway launcher command hook
- Conversation runtime now supports explicit backend routing:
  - `OPENCLAW_CONVERSATION_BACKEND=openclaw|ironclaw`
  - fail-closed key-isolation mode for external LLM fallbacks
- OpenClaw voice + STT/TTS modules are reused for IronClaw lane.
- Central local model routing now includes a direct editor path from OpenClaw menu and `--local-models` CLI.

## Terminology
- `pVAS` in prior notes is treated as `pAVS` (same target system in this roadmap).
- `IronClaw`: Rust runtime from `nearai/ironclaw`.
- `OpenClaw DAE`: existing FoundUps ingress/control plane in `modules/communication/moltbot_bridge/src/openclaw_dae.py`.

## Objective
Ship a low-risk integration where FoundUps keeps existing OpenClaw/WRE control contracts, while IronClaw provides:
1. OpenAI-compatible runtime and tool ecosystem for build/automation jobs.
2. A policy-governed Digital Twin execution lane for 012-style autonomous operations.

## First-Principles Constraints
1. Keep current ingress stable first; do not rewrite OpenClaw DAE before parity is proven.
2. All mutating actions must remain fail-closed and permission-gated.
3. Treasury/accounting must stay event-auditable through pAVS/FAM contracts.
4. Agent-builder speed cannot bypass supply-chain, secret, and webhook safeguards.
5. Digital Twin autonomy must be role-scoped, reversible, and observable.

## Architecture Decision (Occam)
Use IronClaw as a sidecar runtime, not a control-plane replacement in P0/P1.

- Partner (Ingress): OpenClaw bridge + OpenClaw DAE
- Principal (Planning): WRE orchestration in FoundUps
- Associate (Execution): IronClaw runtime for tool execution, OpenAI-compatible calls, routines/webhooks

This preserves WSP 73 Partner-Principal-Associate layering while adding a Rust execution substrate.

## Integration Surfaces
1. **Inference surface**: `POST /v1/chat/completions` (IronClaw gateway), consumed by FoundUps clients that already speak OpenAI-compatible payloads.
2. **Webhook surface**: payload adapter between IronClaw HTTP channel and FoundUps OpenClaw bridge contract.
3. **Event surface**: map runtime lifecycle into `fam_event_v1` / simulator event contracts.
4. **Policy surface**: align IronClaw tool/routine permissions with OpenClaw skill boundary policy.

## IronClaw Feature Deep Dive (Upstream -> FoundUps Mapping)

### Source-of-Truth References
- `https://docs.rs/crate/ironclaw/latest` (crate docs and module index)
- `https://raw.githubusercontent.com/nearai/ironclaw/main/FEATURE_PARITY.md` (implemented vs planned matrix)
- `https://raw.githubusercontent.com/nearai/ironclaw/main/README.md` (runtime modes, onboarding, security defaults)

### Capability Matrix
| IronClaw capability (upstream) | FoundUps use | Integration target |
|---|---|---|
| OpenAI-compatible API gateway | Unified LLM call path for pAVS builder + twin lane | `modules/communication/moltbot_bridge/src/ironclaw_gateway_client.py`, `modules/communication/moltbot_bridge/src/openclaw_dae.py` |
| Multi-provider abstraction (OpenAI/Anthropic/Gemini/local) | Controlled fallback strategy in WRE plans | New WRE worker plugin + policy routing |
| Routines engine | Deterministic worker recipes for pAVS tasks | New `ironclaw_routine_adapter` in WRE plugin surface |
| Hooks lifecycle | Policy gates pre/post tool execution and result checks | AI Overseer + security sentinel callbacks |
| Channel adapters (Discord/Telegram/Matrix/Webhook) | Keep OpenClaw ingress stable while enabling future direct channels | OpenClaw remains ingress; IronClaw channels optional P2 |
| Tool/MCP integration modules | Agent-builder tool execution substrate | WSP 95/96 policy boundary adapter |
| SQLite/Postgres persistence options | Worker memory and experiment logs | pAVS run ledger + simulator telemetry sink |
| Web UI / chat support | Operator console for worker health and traces | pAVS control panel bridge (P1/P2) |
| Maintenance and proxy modes | Safe rollout and shadow traffic testing | Staging canary deployment lane |

### Feature Parity Constraints (From Upstream Matrix)
Current upstream gaps called out in parity docs include:
- OpenClaw desktop UI parity is not complete.
- Routines and some multi-provider management pieces are marked as in-progress.
- Advanced scheduling and git workflow features are not yet at full parity.

FoundUps decision:
1. Use IronClaw as execution sidecar first (do not depend on missing UI parity).
2. Keep scheduler and git-orchestrated flows in existing FoundUps/WRE during P0/P1.
3. Consume only stable capabilities (gateway, hooks, routines subsets, provider routing).

## pAVS Worker Architecture (WRE + Overseer Native)

### Worker Roles
1. `ironclaw_builder_worker`
   - Purpose: build/refactor/patch/test workflows for FoundUp assets.
   - Input: structured build intent + policy profile.
   - Output: patch artifacts + verification report + ledger events.

2. `ironclaw_twin_worker`
   - Purpose: Digital Twin execution lane for bounded multi-step tasks.
   - Input: routed conversational/automation intents.
   - Output: action plan + executed steps + containment-safe response.

3. `ironclaw_sim_worker`
   - Purpose: simulator-driven what-if evaluation and stress testing.
   - Input: simulator scenarios (policy, model, load, failure).
   - Output: performance/reliability/cost metrics for WRE strategy updates.

### WRE Integration Contract
Create a dedicated WRE plugin adapter:
- Proposed file: `modules/infrastructure/wre_core/wre_master_orchestrator/src/plugins/ironclaw_worker.py`
- Contract:
  - `register(master)` binds worker routes.
  - `execute(task)` transforms WRE task -> IronClaw request.
  - `validate(result)` enforces WSP 50 output checks.
  - `emit_event()` writes standard event payloads for simulator + overseer.

Task envelope (minimum):
- `task_id`
- `work_type` (`builder|twin|sim`)
- `policy_profile`
- `allowed_tools`
- `max_steps`
- `max_runtime_sec`
- `input_payload`

### AI Overseer Integration Contract
Add IronClaw runtime monitors into overseer:
- Health probe and model inventory checks.
- Key-isolation compliance checks (`OPENCLAW_NO_API_KEYS`, `IRONCLAW_NO_API_KEYS`).
- Execution anomaly detection:
  - timeout escalation
  - tool-deny spikes
  - policy violation attempts
- Pattern memory feedback:
  - successful routine signatures
  - failed routine signatures
  - recommended routing updates for WRE.

Proposed touch points:
- `modules/ai_intelligence/ai_overseer/src/daemon_monitor_mixin.py`
- `modules/ai_intelligence/ai_overseer/src/openclaw_security_sentinel.py`
- `modules/ai_intelligence/ai_overseer/src/mission_execution_mixin.py`

### Simulator (pAVS) Integration Contract
Use IronClaw as a first-class simulation actor:
- Scenario dimensions:
  - model lane (`triage/general/code`)
  - backend lane (`openclaw|ironclaw`)
  - isolation mode (`keys_off|keys_on`)
  - workload class (`chat|build|automation|mixed`)
- KPI dimensions:
  - success rate
  - mean/95p latency
  - failure mode distribution
  - compute-credit proxy cost
  - policy violation rate

Proposed touch points:
- `modules/foundups/simulator/step_pipeline.py`
- `modules/foundups/simulator/ai/llm_inference.py`
- `modules/foundups/simulator/state_store.py`
- `modules/foundups/simulator/tests/*`

## Execution Plan by Phase

### Phase P0-A: Stable Worker Spine (1-2 weeks)
1. Add WRE IronClaw worker plugin skeleton + typed task envelope.
2. Add AI Overseer health/policy monitor hooks for IronClaw.
3. Add simulator toggle: route selected steps to IronClaw backend.
4. Add baseline smoke tests for builder/twin/sim worker calls.

Exit:
- Worker can run end-to-end through WRE with deterministic event logs.
- Overseer shows healthy/degraded state with cause.

### Phase P0-B: Agent Builder Vertical Slice (1-2 weeks)
1. Implement builder workflow template (`analyze -> patch -> verify -> summarize`).
2. Wire policy profile to allowed toolset.
3. Persist builder artifacts and validation events to simulator ledger.
4. Add failure replay mode for deterministic debugging.

Exit:
- Builder produces reproducible artifacts under policy constraints.

### Phase P1-A: Digital Twin Lane Hardening (2 weeks)
1. Add twin action profiles by authority tier.
2. Add containment and release controls via overseer.
3. Add channel-specific execution policies.
4. Add route-learning feedback into WRE selection strategy.

Exit:
- Twin lane runs approved tasks and blocks disallowed tasks with explicit reasons.

### Phase P1-B: Simulator/WRE Modeling Depth (2 weeks)
1. Run multi-episode simulations comparing OpenClaw vs IronClaw routes.
2. Calibrate WRE routing policy based on measured KPI deltas.
3. Publish model-selection recommendations per workload class.
4. Add CI regression suite for route quality and safety.

Exit:
- WRE has data-backed policy for when to route to IronClaw.

## Maximization Strategy for FoundUps Utility
1. Keep OpenClaw as ingress controller and policy brain.
2. Use IronClaw as execution accelerator where it is strongest:
   - OpenAI-compatible gateway
   - routine/hook execution
   - local-first backend flexibility
3. Use AI Overseer as runtime governor and incident detector.
4. Use Simulator as route optimizer before production rollout.
5. Ship by measurable KPI gains, not by architectural replacement rhetoric.

## WSP 15 Priority Queue (MPS)

| Work Item | C | I | D | Im | Score | Priority |
|---|---:|---:|---:|---:|---:|---|
| IronClaw sidecar bootstrap + health/auth wiring | 3 | 5 | 5 | 5 | 18 | P0 |
| OpenAI-compatible inference reroute toggle in FoundUps clients | 3 | 5 | 4 | 4 | 16 | P0 |
| IronClaw -> OpenClaw bridge payload adapter + token auth hardening | 4 | 5 | 4 | 4 | 17 | P0 |
| Safety parity (permission, rate limit, skill boundary, secret redaction) | 4 | 5 | 5 | 5 | 19 | P0 |
| Agent Builder MVP slice (template -> build -> verify -> publish event trail) | 4 | 5 | 4 | 5 | 18 | P0 |
| Digital Twin lane v1 (identity profile + channel policy + audit trail) | 4 | 5 | 4 | 5 | 18 | P0 |
| Builder catalog, reusable skill packs, workflow templates | 3 | 4 | 3 | 4 | 14 | P1 |
| Multi-tenant isolation and quota policy for many FoundUps | 4 | 4 | 3 | 4 | 15 | P1 |
| Economic lane calibration (CC debit/rebate linked to runtime actions) | 4 | 4 | 3 | 4 | 15 | P1 |
| Adaptive scheduling/pricing from runtime telemetry | 4 | 3 | 2 | 3 | 12 | P2 |

## Execution Tranches

### Tranche T0 (P0): Runtime Foundation
- Bring up IronClaw with fixed host/port/token in controlled environment.
- Add deterministic health checks and startup diagnostics.
- Enforce localhost-first binding where possible.

**Exit criteria**
- Runtime reachable and authenticated.
- Fail-closed behavior verified for invalid/missing auth.

### Tranche T1 (P0): Inference + Bridge Compatibility
- Add env-driven routing so compatible FoundUps clients can target IronClaw `/v1/chat/completions`.
- Implement adapter endpoint translating IronClaw webhook payload -> FoundUps `MoltbotMessage` shape.
- Preserve existing OpenClaw webhook contract for backwards compatibility.

**Exit criteria**
- Same prompt path works through existing FoundUps call sites using IronClaw backend.
- Bridge adapter passes contract tests for message/session/channel/sender mapping.

### Tranche T2 (P0): Agent Builder Vertical Slice
- Define minimal builder contract:
  - Input: goal + repository/workspace context + policy profile
  - Output: patch set + verification report + ledger events
- Route all build actions through existing permission and safety gates.
- Emit canonical events for `builder_session_started`, `builder_patch_proposed`, `builder_validation_passed|failed`.

**Exit criteria**
- One end-to-end agent builder flow works in staging with deterministic audit trail.
- Rejected operations leave explicit denial events.

### Tranche T3 (P0): Digital Twin v1
- Bind Digital Twin identity profile to per-FoundUp policy.
- Add role-scoped channel actions (read-only monitor vs mutating execution).
- Add containment/release controls via existing Overseer pathways.

**Exit criteria**
- Digital Twin can execute approved tasks and is blocked on disallowed tasks.
- Security/containment events are visible in observability plane.

### Tranche T4 (P1): Economics + Scale
- Connect runtime usage to compute-credit debit/rebate policy.
- Add tenant isolation and FoundUp-level quotas.
- Add template/skill catalog for repeatable builder deployment.

**Exit criteria**
- Runtime usage ties to pAVS accounting fields and reports.
- Multi-FoundUp concurrency remains stable under load tests.

## Agent Builder Lane (Product View)
1. Intake: FoundUp owner chooses template + policy profile.
2. Build: IronClaw executes toolchain with guardrails.
3. Verify: tests/lints/contract checks.
4. Commit/Publish: change artifacts + event log persisted.
5. Economics: compute usage booked to CC/UPS lanes.

## Digital Twin Lane (Operational View)
1. Profile: identity, voice, authority, channel scope.
2. Plan: OpenClaw DAE classifies and routes intent.
3. Execute: IronClaw performs bounded actions.
4. Observe: Overseer + DAEmon event stream.
5. Govern: human/operator override and containment release.

## Security and Governance Gates
- WSP 50: pre-action verification before file/tool mutations.
- WSP 95/96: skill boundary and MCP/tool governance checks.
- WSP 91: structured runtime and incident signals.
- WSP 22: all roadmap and change log updates recorded with module traceability.

## Validation Commands (Planned Baseline)
```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD='1'
.\.venv\Scripts\python.exe -m pytest `
  modules/communication/moltbot_bridge/tests `
  modules/foundups/agent_market/tests `
  modules/foundups/simulator/tests -q
```

```powershell
# Runtime smoke checks (example)
curl http://127.0.0.1:3000/api/health
curl -H "Authorization: Bearer $env:GATEWAY_AUTH_TOKEN" http://127.0.0.1:3000/v1/models
```

## Risks and Mitigations
1. Contract mismatch between IronClaw webhook schema and FoundUps bridge schema.
   - Mitigation: adapter layer + explicit schema tests.
2. Security drift between OpenClaw and IronClaw policy semantics.
   - Mitigation: policy parity matrix and enforced preflight checks.
3. Hidden economic leakage from unmetered runtime calls.
   - Mitigation: event-first metering with fail-closed debit checks.
4. Digital Twin overreach in mutating operations.
   - Mitigation: strict role tiers and containment controls.

## Immediate Next Actions
1. Implement P0 runtime bootstrap and env contract in a dedicated integration module.
2. Patch AI call surfaces to support `IRONCLAW_BASE_URL` and auth token routing.
3. Add webhook payload adapter with tests.
4. Add first Agent Builder and Digital Twin smoke tests to concatenated suite.
