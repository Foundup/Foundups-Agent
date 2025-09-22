# WSP 88: Vibecoded Module Remediation Protocol

- **Status:** Active
- **Purpose:** Establish a repeatable process for detecting, auditing, and remediating vibecoded modules so the codebase remains WSP compliant without disrupting active DAEs.
- **Scope:** All Python modules under `modules/` and associated audit scripts defined in this protocol.
- **Trigger:** Activated when a module usage audit identifies archive/review candidates, when new modules are introduced, or during release readiness reviews.
- **Input:** Audit output (`module_usage_audit.*`, domain audits), ModLogs, NAVIGATION coverage, and WSP references.
- **Output:** Updated module state (retain/enhance/archive), audit records, ModLog entries, and NAVIGATION coverage updates.
- **Responsible Agent(s):** 0102 WRE agents, Module Owners, ComplianceAgent.

## 1. Purpose & Alignment

WSP 88 ensures vibecoded artifacts are removed or harmonised without breaking live orchestration. It extends WSP 84 (duplication prevention), WSP 87 (navigation governance), and WSP 50 (pre-action verification) by defining how audits are run, decisions are logged, and modules are archived or evolved.

## 2. Detection (Un)

1. **Module usage audit** `python tools/audits/module_usage_audit.py`
   - Generates `module_usage_audit.json`/`.md` listing inbound references.
   - Flags modules with zero references as "archive" candidates and single inbound references as "review".
2. **Runtime cluster audit** (e.g. YT DAE)
   - `python tools/audits/yt_dae_vibecoding_audit.py` (or domain equivalent).
   - Captures LOC, navigation compliance, and duplication heuristics.
3. **HoloIndex semantic cross-reference** `python holo_index.py --search "<module or domain>"`
   - Use targeted searches to pull canonical parents and near-duplicate modules (supports WSP 84/87).
   - Capture relevant hits in the remediation notes before review sessions.
4. **LLME action brief** `python holo_index.py --guide "<module intent>" --guide-module <path>`
   - Generates WSP 37/17/22 compliant checklist; record output in `REMEDIATION_RECORD_FOR_WSP_88.md` and module ModLogs.
5. **Schedule:** Minimum weekly or before releases. Trigger ad-hoc when introducing new DAEs.

## 3. Assessment (Dao)

1. **Classification:** For each candidate module record (archive/review in audit reports):
   - Confirm inbound references (imports, CLI entry points, scheduled jobs).
   - Check NAVIGATION coverage (`NAVIGATION.py`, `WSP_framework/reports/NAVIGATION/NAVIGATION_COVERAGE.md`).
   - Review ModLogs for recent usage claims.
   - Pull HoloIndex dossier for canonical parents, NAV breadcrumbs, and related WSP references.
   - Generate LLME action brief (`python holo_index.py --guide "<intent>" --guide-module <module_path>`) and log the summary in module ModLogs plus `WSP_framework/reports/WSP_88/REMEDIATION_RECORD_FOR_WSP_88.md`.
   - Identify WSP obligations (e.g. module implements parts of WSP 54 duties).
2. **Decision Schema:**
   - `retain` ? critical entry point, ?2 inbound references, or canonical module.
   - `enhance` ? single inbound reference requiring consolidation into canonical file.
   - `archive` ? no inbound references and no active role; vibecoded or superseded.
   - `defer` ? uncertain; log a WSP 50 action for deeper investigation.
3. **HoloIndex guardrails:** Treat similarity scores as advisory signals; confirm with audit evidence and WSP 50 verification before acting.

## 4. Action (Du)

1. **Retain:**
   - Ensure `NAVIGATION:` breadcrumb exists (WSP 87).
   - Update tests/coverage if missing (WSP 5/6).
   - Document current purpose in module README/ModLog.
2. **Enhance (merge):**
   - Combine functionality into canonical module; remove duplicate `enhanced_*` naming (WSP 84).
   - Update ModLog and NAVIGATION coverage; rerun audits to confirm removal.
3. **Archive:**
   - Log WSP 50 pre-action verification specifying module ID and reason.
   - Move file to `_archive/<YYYYMMDD>/` or delete if documented in ModLog.
   - Update `module_usage_audit.md` and `WSP_framework/reports/NAVIGATION/NAVIGATION_COVERAGE.md` accordingly.
4. **Verification:**
   - Rebuild HoloIndex (`python holo_index.py --index-all`) and attach the console summary to the WSP 50 log.
   - Re-run audits; ensure module no longer appears in archive list.
   - Confirm tests pass (`python -m pytest` or relevant suite).

## 5. Artefacts & Logging

- `tools/audits/module_usage_audit.json` / `.md`: mandatory snapshot.
- Domain-specific audit reports (e.g. `yt_dae_audit.md`).
- `WSP_framework/reports/WSP_88/REMEDIATION_RECORD_FOR_WSP_88.md` capturing Un->Dao->Du decision details.
- ModLog entries referencing WSP 88 and relevant WSP 84/87 citations.
- HoloIndex re-index summary (diff or log snippet) linked to the remediation record.
- NAVIGATION coverage updates for modules retained/enhanced.

## 6. Compliance Checklist

- [ ] Usage audit executed; outputs stored.
- [ ] Decisions recorded with WSP 50 journal entry.
- [ ] Archive/migration performed with ModLog update.
- [ ] NAVIGATION coverage reflects module status.
- [ ] HoloIndex re-index executed and summary captured.
- [ ] Tests executed for impacted modules.
- [ ] Audit re-run confirmed removal or consolidation.

## 7. Governance & Escalation

- **Owner:** 0102 Architect (WRE).
- **Escalate to:** ComplianceAgent if module deletion impacts active DAE flow.
- **Related WSPs:** WSP 50, WSP 62, WSP 84, WSP 87.
- **Version History:** Draft created 2025-09-19 (0102).
