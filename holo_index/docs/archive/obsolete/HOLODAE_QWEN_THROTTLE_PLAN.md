# HoloDAE Qwen Throttle Enhancement Plan
**Session:** 2025-10-07 | **Status:** ARCHITECTURE MAPPED - READY

## Architecture Discovery [OK]

**Key Files:**
- `holo_index/qwen_advisor/holodae_coordinator.py`
- `holo_index/qwen_advisor/orchestration/qwen_orchestrator.py`
- `holo_index/cli.py`
- Pattern reference: `modules/communication/livechat/src/intelligent_throttle_manager.py` (1057 lines)

**Current:** All components fire -> Noise
**Target:** Intent-driven filtering -> Signal

## 5 Phases (Sequential, ~5 hours total)

### 1. Intent Classification (30min)
- NEW: `holo_index/intent_classifier.py`
- Types: DOC_LOOKUP, CODE_LOCATION, MODULE_HEALTH, RESEARCH, GENERAL
- Integration: `cli.py` classifies before coordinator

### 2. Component Routing (45min)
- ENHANCE: `qwen_orchestrator._get_orchestration_decisions(intent=...)`
- Map intent -> relevant components only
- Example: DOC_LOOKUP -> only `wsp_documentation_guardian`

### 3. Output Composition (60min)
- NEW: `holo_index/output_composer.py`
- Priority sections: [INTENT] [FINDINGS] [MCP] [ALERTS]
- Dedupe 87 "ModLog outdated" warnings into 1 line

### 4. Feedback Loop (45min)
- NEW: `holo_index/feedback_learner.py`
- Track: query -> intent -> components -> outcome
- Learn: Downweight noisy, upweight useful
- Flag: `--rate-output good/noisy`

### 5. MCP Integration (30min)
- Capture MCP results separately
- Render in dedicated [MCP RESEARCH] section
- MCP hook registry for ricDAE

## Test Queries
```
DOC_LOOKUP: "what does WSP 64 say"
CODE_LOCATION: "where is AgenticChatEngine"
MODULE_HEALTH: "check holo_index health"
RESEARCH: "how does PQN emergence work"
GENERAL: "find youtube auth"
```

## WSP Compliance [OK]
- WSP 50: Pre-action verification (searched existing)
- WSP 64: Violation prevention (checked patterns)
- WSP 84: Code reuse (found throttle pattern)
- WSP 22: ModLog updates after phases
- WSP 3: Proper module placement

## Decision for 012

**Options:**
1. Execute full plan (5 hours)
2. MVP: Intent only (1 hour)
3. Defer to next session

**Recommendation:** Start Phase 1 (Intent Classifier) - test before continuing.

**Status:** PLAN COMPLETE, AWAITING GO/NO-GO
