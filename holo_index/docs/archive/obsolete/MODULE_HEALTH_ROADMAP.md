# Module Health Roadmap

**Owner:** FoundUps 0102 Engineering  
**Protocols:** WSP 35 (Execution Plan), WSP 49, WSP 84, WSP 87  
**Status:** Draft

## Phase A — Discovery & Alignment
- [ ] Inventory existing module size guidelines (WSP 87) and confirm thresholds.
- [ ] Catalogue core scaffolding requirements (README, ModLog, INTERFACE, tests, TestModLog).
- [ ] Define telemetry schema for module health findings.

## Phase B — Deterministic Checks (MVP)
- [ ] Implement `module_health.size_audit` to compute line counts + risk tiers.
- [ ] Implement `module_health.structure_audit` to verify scaffolding.
- [ ] Expose audit results through the rules engine + CLI reminders.

## Phase C — Historical Context
- [ ] Parse structured `WSP_VIOLATIONS` feed and attach module tags.
- [ ] Persist health snapshots to SSD telemetry for trend analysis.
- [ ] Add FMAS coverage for size/structure warnings.

## Phase D — Predictive Guidance (Stretch)
- [ ] Integrate git churn metrics to prioritise refactor candidates.
- [ ] Suggest WSP 88 playbooks when thresholds + history indicate risk.
- [ ] Generate advisor TODOs that route 0102 agents to relevant docs (TestModLog, ModLog, remediation notes).

## Dependencies
- Structured violation history (or alternative data source).
- Agreement on thresholds + scaffolding rules with the WSP council.
- Updated Qwen advisor prompts to embed module health notes.

