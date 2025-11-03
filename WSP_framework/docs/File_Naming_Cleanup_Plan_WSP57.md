# WSP File Naming Cleanup Plan

**Triggered By:** 012 observation: "NO md should be called WSP_ unless it is in src on wsp_framework"
**WSP Protocols:** WSP 57 (Naming Coherence), WSP 85 (Root Protection), WSP 22 (ModLog)
**Date:** 2025-10-14

## Problem Statement

Found 64 files with "WSP_" prefix outside of legitimate protocol locations (WSP_framework/src/, WSP_knowledge/src/). This creates naming confusion and violates WSP 57 coherence principles.

## Naming Rules (NEW)

### [OK] ALLOWED: "WSP_" Prefix

**ONLY these locations:**
1. `WSP_framework/src/WSP_*.md` - Official framework protocols
2. `WSP_knowledge/src/WSP_*.md` - Official knowledge protocols
3. `WSP_framework/reports/WSP_*/` - WSP-specific analysis reports
4. `WSP_knowledge/reports/WSP_*/` - WSP-specific analysis reports
5. `**/archive/**/WSP_*.md` - Historical archives
6. `**/wsp_archive/WSP_*.md` - Dedicated WSP archives
7. `docs/session_backups/WSP_*.md` - Session backup archives

### [FAIL] PROHIBITED: "WSP_" Prefix

**Module documentation:**
- Compliance reports -> `COMPLIANCE_REPORT.md`
- Audit reports -> `AUDIT_REPORT.md`
- SWOT analyses -> `SWOT_Analysis_*.md`
- Violation tracking -> `Violation_Analysis.md`
- Implementation status -> `IMPLEMENTATION_STATUS.md`

## Files to Rename (Priority Order)

### P0: Active Module Documentation (17 files)

```bash
# pqn_alignment module (3 files)
mv ./modules/ai_intelligence/pqn_alignment/docs/WSP_79_SWOT_ANALYSIS_analyze_run.md \
   ./modules/ai_intelligence/pqn_alignment/docs/SWOT_Analysis_Analyze_Run.md

mv ./modules/ai_intelligence/pqn_alignment/docs/WSP_79_SWOT_ANALYSIS_config_consolidation.md \
   ./modules/ai_intelligence/pqn_alignment/docs/SWOT_Analysis_Config_Consolidation.md

mv ./modules/ai_intelligence/pqn_alignment/docs/WSP_79_SWOT_ANALYSIS_pqn_chat_broadcaster.md \
   ./modules/ai_intelligence/pqn_alignment/docs/SWOT_Analysis_PQN_Chat_Broadcaster.md

mv ./modules/ai_intelligence/pqn_alignment/src/WSP_COMPLIANCE.md \
   ./modules/ai_intelligence/pqn_alignment/src/COMPLIANCE_STATUS.md

mv ./modules/ai_intelligence/pqn_alignment/WSP_COMPLIANCE_STATUS.md \
   ./modules/ai_intelligence/pqn_alignment/COMPLIANCE_STATUS.md

# livechat module (5 files - non-archived)
mv ./modules/communication/livechat/docs/WSP_AUDIT_REPORT.md \
   ./modules/communication/livechat/docs/Audit_Report.md

mv ./modules/communication/livechat/docs/WSP_COMPLIANCE_AUDIT.md \
   ./modules/communication/livechat/docs/Compliance_Audit.md

mv ./modules/communication/livechat/docs/WSP_COMPLIANCE_FINAL_REPORT.md \
   ./modules/communication/livechat/docs/Compliance_Final_Report.md

mv ./modules/communication/livechat/docs/WSP_COMPLIANCE_REPORT.md \
   ./modules/communication/livechat/docs/Compliance_Report.md

mv ./modules/communication/livechat/docs/WSP_VIOLATION_STATUS_REPORT.md \
   ./modules/communication/livechat/docs/Violation_Status_Report.md

# cursor_multi_agent_bridge module (2 files)
mv ./modules/development/cursor_multi_agent_bridge/WSP_21_PROMETHEUS_README.md \
   ./modules/development/cursor_multi_agent_bridge/PROMETHEUS_README.md

mv ./modules/development/cursor_multi_agent_bridge/WSP_COMPLIANCE_REPORT.md \
   ./modules/development/cursor_multi_agent_bridge/COMPLIANCE_REPORT.md

# github_integration module (1 file)
mv ./modules/platform_integration/github_integration/WSP_COMPLIANCE_SUMMARY.md \
   ./modules/platform_integration/github_integration/COMPLIANCE_SUMMARY.md

# system_health_monitor module (1 file)
mv ./modules/infrastructure/system_health_monitor/docs/WSP_85_VIOLATION_ANALYSIS.md \
   ./modules/infrastructure/system_health_monitor/docs/Root_Protection_Violation_Analysis.md

# banter_engine module (1 file)
mv ./modules/ai_intelligence/banter_engine/tests/WSP_AUDIT_REPORT.md \
   ./modules/ai_intelligence/banter_engine/tests/Audit_Report.md

# WSP_agentic misplaced files (3 files - move to proper domains)
mv ./WSP_agentic/WSP_50_Pre_Action_Verification_Protocol.md \
   ./docs/session_backups/Pre_Action_Verification_Implementation.md

mv ./WSP_agentic/WSP_COMPLIANCE_IMPLEMENTATION_2025_09_16.md \
   ./docs/session_backups/Compliance_Implementation_2025-09-16.md

mv ./WSP_agentic/src/WSP_33_AMIW_Execution_Protocol.md \
   ./docs/session_backups/AMIW_Execution_Protocol_Implementation.md
```

### P1: Generated/Documentation Files (4 files)

```bash
# Generated Sentinel section
mv ./docs/WSP_87_Sentinel_Section_Generated.md \
   ./docs/Sentinel_WSP87_Generated_Section.md

# WSP_framework documentation files
mv ./WSP_framework/docs/WSP_ASCII_REMEDIATION_LOG.md \
   ./WSP_framework/docs/ASCII_Remediation_Log.md

mv ./WSP_framework/docs/WSP_COMMENT_PATTERN.md \
   ./WSP_framework/docs/Comment_Pattern_Standard.md

mv ./WSP_framework/docs/WSP_HOLOINDEX_MANDATORY.md \
   ./WSP_framework/docs/HoloIndex_Mandatory_Usage.md
```

### P2: Test Files (2 files)

```bash
# WSP_agentic test reports
mv ./WSP_agentic/tests/WSP_50_VERIFICATION_REPORT.md \
   ./WSP_agentic/tests/Pre_Action_Verification_Report.md

mv ./WSP_agentic/tests/WSP_AUDIT_REPORT.md \
   ./WSP_agentic/tests/Audit_Report.md
```

### P3: Report Files (KEEP - in proper report directories)

**These are ACCEPTABLE** (in WSP_framework/reports/, WSP_knowledge/reports/):
- WSP_framework/reports/WSP_88/* (WSP-specific analysis directory) [OK]
- WSP_framework/reports/legacy/WSP_*.md (legacy reports) [OK]
- WSP_framework/reports/WSP_*.md (system-wide WSP analysis) [OK]
- WSP_knowledge/reports/WSP_*.md (knowledge WSP analysis) [OK]
- WSP_knowledge/reports/audit_reports/WSP_33_*.md (WSP 33 audits) [OK]

### P4: Archive Files (KEEP - properly archived)

**These are ACCEPTABLE** (in archive directories):
- docs/session_backups/WSP_22_Violation_Analysis.md [OK]
- docs/wsp_archive/WSP_22_Original_ModLog_Structure.md [OK]
- WSP_knowledge/archive/deprecated_wsps/WSP_*.md [OK]
- WSP_knowledge/archive/WSP_*.md [OK]
- modules/communication/livechat/_archive/wsp_compliance/WSP_*.md [OK]

### P5: Journal/Report Files (KEEP or MOVE)

```bash
# WSP_agentic journal reports - move to proper location
mv ./WSP_agentic/agentic_journals/reports/WSP_AUDIT_REPORT_0102_COMPREHENSIVE.md \
   ./docs/session_backups/Agentic_Audit_Report_0102_Comprehensive.md
```

## Summary

### Files to Rename: 24
- P0 (Active modules): 17
- P1 (Documentation): 4
- P2 (Tests): 2
- P5 (Journals): 1

### Files to Keep (Properly Named): 40
- In WSP_framework/reports/: 10
- In WSP_knowledge/reports/: 4
- In archive directories: 26

## Validation

After renaming, verify:
```bash
# Should ONLY find files in:
# - WSP_framework/src/
# - WSP_knowledge/src/
# - */reports/WSP_*/
# - */archive/*
# - */wsp_archive/
# - docs/session_backups/
find . -name "WSP_*.md" | grep -v "/WSP_framework/src/" | grep -v "/WSP_knowledge/src/" | \
  grep -v "/reports/WSP_" | grep -v "/archive/" | grep -v "wsp_archive" | grep -v "session_backups"
```

Should return: **0 files**

## Next Steps

1. Execute P0 renames (active module documentation)
2. Execute P1 renames (generated documentation)
3. Execute P2 renames (test files)
4. Execute P5 moves (journal reports)
5. Update WSP 57 (Naming Coherence) with explicit WSP file naming rules
6. Update WSP 85 (Root Protection) with WSP naming enforcement
7. Document in ModLog.md

## Implementation Status

- [ ] P0 renames executed
- [ ] P1 renames executed
- [ ] P2 renames executed
- [ ] P5 moves executed
- [ ] Validation passed
- [ ] WSP 57 updated
- [ ] WSP 85 updated
- [ ] ModLog documented
