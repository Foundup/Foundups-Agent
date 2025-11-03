# Autonomous Cleanup Validator (0102 Role)

**Date**: 2025-10-22
**Agent**: 0102 (Claude Sonnet 4.5)
**Purpose**: Validate Qwen's cleanup plans using HoloIndex research + WSP 15 MPS scoring + First Principles reasoning

---

## First Principles: 0102's Role in WRE

**0102 is NOT an agent that "wears skills"** - 0102 is the supervisor who:
1. Validates work from Gemma and Qwen
2. Performs deep HoloIndex research (semantic search, cross-referencing)
3. Applies WSP protocols with full context (200K token window)
4. Calculates WSP 15 MPS scores for autonomous decision-making
5. Approves or rejects cleanup plans

**0102 does NOT**:
- Label files (that's Gemma's job)
- Create strategic plans (that's Qwen's job)
- Execute cleanup (that's WRE's job after approval)

**0102's superpower**: Research + reasoning + WSP application = validation authority

---

## Autonomous Cleanup Flow (3-Phase)

### Phase 1: Gemma Fast Scan (50-100ms per file)
**Input**: File metadata (path, extension, size, age, parent_directory)
**Process**: Binary classification using simple rules
**Output**: `data/gemma_noise_labels.jsonl`
```json
{
  "file_path": "O:/Foundups-Agent/chat_history.jsonl",
  "label": "noise",
  "category": "file_type_noise",
  "confidence": 0.95,
  "patterns_executed": {...}
}
```

**Gemma does NOT**:
- Make cleanup decisions
- Score cleanup priority
- Perform strategic planning

**Gemma ONLY**:
- Labels files as noise/signal
- Provides confidence in its OWN label
- Logs which patterns it executed

---

### Phase 2: Qwen Strategic Planning (200-500ms total)
**Input**: `data/gemma_noise_labels.jsonl` (Gemma's labeled files)
**Process**: Group by category, batch into chunks, apply WSP safety checks
**Output**: `data/cleanup_plan.json`
```json
{
  "plan_id": "cleanup_plan_20251022_015900",
  "batches": [
    {
      "batch_id": "batch_001",
      "category": "file_type_noise",
      "file_count": 50,
      "files": ["..."],
      "rationale": "215 JSONL files create concurrency risk...",
      "recommendation": "ARCHIVE before deletion",
      "risk_level": "LOW",
      "wsp_compliance": ["WSP_64"]
    }
  ],
  "flagged_for_review": [...],
  "requires_0102_approval": true
}
```

**Qwen does NOT**:
- Calculate WSP 15 MPS scores (that's 0102's job)
- Perform HoloIndex research (that's 0102's job)
- Approve/reject the plan (that's 0102's job)

**Qwen ONLY**:
- Groups files strategically
- Applies WSP 83/64 safety rules
- Generates rationale for batches
- Flags ambiguous files for 0102 review

---

### Phase 3: 0102 Deep Validation (2-5 minutes)
**Input**: `data/cleanup_plan.json` (Qwen's strategic plan)
**Process**: HoloIndex research → WSP validation → MPS scoring → Approve/Reject
**Output**: `data/cleanup_plan_validated.json` + approval decision

**0102's Workflow**:

#### Step 1: Load Qwen's Plan
```python
import json
from pathlib import Path

plan_path = Path("O:/Foundups-Agent/data/cleanup_plan.json")
with open(plan_path) as f:
    plan = json.load(f)

print(f"[0102-VALIDATION] Loaded plan: {plan['plan_id']}")
print(f"[0102-VALIDATION] Total batches: {len(plan['batches'])}")
print(f"[0102-VALIDATION] Flagged for review: {len(plan['flagged_for_review'])}")
```

#### Step 2: HoloIndex Research (Semantic Search)
**Question**: "Are any of these files referenced in active code?"

```bash
# For each batch, search HoloIndex for references
python holo_index.py --search "chat_history.jsonl usage references"
python holo_index.py --search "JSONL file dependencies modules"
```

**Expected Findings**:
- Are JSONL files imported anywhere?
- Do any modules read from these paths?
- Are there tests that depend on these files?

**Example Research Output**:
```
[HOLO-SEARCH] Found 3 references to chat_history files:
1. modules/communication/livechat/src/chat_memory_manager.py:45
   - Reads chat_history*.jsonl for memory persistence
2. modules/gamification/whack_a_magat/src/timeout_announcer.py:102
   - References old chat_history files (but uses SQLite now)
3. tests/test_chat_sender.py:23
   - Mock data uses chat_history_test.jsonl
```

**0102's Analysis**:
- Finding #1 → **CRITICAL**: chat_memory_manager actively uses JSONL files → **REJECT cleanup**
- Finding #2 → **SAFE**: Old reference, now uses SQLite → **APPROVE cleanup**
- Finding #3 → **CRITICAL**: Test depends on specific file → **EXCLUDE from cleanup**

#### Step 3: WSP Protocol Validation
**Check WSP Compliance**:
- **WSP 83** (Documentation Attached to Tree): Are any docs in cleanup plan?
- **WSP 64** (Violation Prevention): Are any critical paths in cleanup plan?
- **WSP 50** (Pre-Action Verification): Has duplication been checked?

**Validation Code**:
```python
def validate_wsp_compliance(batch):
    """0102 validates WSP compliance using First Principles"""
    violations = []

    # WSP 83: Documentation check
    for file_path in batch['files']:
        if any(x in file_path for x in ['docs/', 'WSP_framework/', 'README', 'INTERFACE', 'ModLog']):
            violations.append({
                'wsp': 'WSP_83',
                'file': file_path,
                'reason': 'Documentation file should not be in cleanup plan'
            })

    # WSP 64: Critical path check
    for file_path in batch['files']:
        if any(x in file_path for x in ['data/', 'modules/*/src/', '.env', 'requirements.txt']):
            violations.append({
                'wsp': 'WSP_64',
                'file': file_path,
                'reason': 'Critical path file detected'
            })

    return violations

# Execute validation
for batch in plan['batches']:
    violations = validate_wsp_compliance(batch)
    if violations:
        print(f"[0102-WSP] Batch {batch['batch_id']} has {len(violations)} violations")
        for v in violations:
            print(f"  - {v['wsp']}: {v['file']} - {v['reason']}")
```

#### Step 4: WSP 15 MPS Scoring
**Calculate Module Prioritization Score** for cleanup decision

**Formula** (from WSP 15):
```
MPS = Complexity + Importance + Deferability + Impact
Where:
  Complexity (1-5): How complex is this cleanup?
  Importance (1-5): How important is this cleanup?
  Deferability (1-5): Can this be deferred?
  Impact (1-5): What's the impact if we don't clean?

Priority Mapping:
  16-20 = P0 (Critical - Autonomous execution)
  13-15 = P1 (High - Autonomous execution)
  10-12 = P2 (Medium - Requires approval)
  7-9  = P3 (Low - Defer)
  4-6  = P4 (Minimal - Skip)
```

**Example Scoring for Batch 001 (215 JSONL files)**:
```python
def calculate_mps_score(batch, holo_results):
    """0102 calculates MPS score for autonomous decision"""

    # Complexity: How hard is cleanup?
    if batch['file_count'] > 100:
        complexity = 3  # Medium complexity (large batch)
    elif batch['file_count'] > 50:
        complexity = 2
    else:
        complexity = 1

    # Importance: How important is cleanup?
    if 'concurrency risk' in batch['rationale']:
        importance = 5  # High importance (thread-safety issue)
    elif 'space savings' in batch['rationale']:
        importance = 3
    else:
        importance = 2

    # Deferability: Can we wait?
    if holo_results['active_references'] > 0:
        deferability = 1  # Cannot defer (files in use)
    elif batch['risk_level'] == 'LOW':
        deferability = 5  # Can defer (low risk)
    else:
        deferability = 3

    # Impact: What happens if we don't clean?
    if batch['category'] == 'file_type_noise':
        impact = 4  # High impact (clutter accumulates)
    elif batch['category'] == 'rotting_data':
        impact = 3
    else:
        impact = 2

    mps = complexity + importance + deferability + impact

    # Determine priority
    if mps >= 16:
        priority = 'P0'
        decision = 'AUTONOMOUS_EXECUTE'
    elif mps >= 13:
        priority = 'P1'
        decision = 'AUTONOMOUS_EXECUTE'
    elif mps >= 10:
        priority = 'P2'
        decision = 'REQUIRE_HUMAN_APPROVAL'
    elif mps >= 7:
        priority = 'P3'
        decision = 'DEFER'
    else:
        priority = 'P4'
        decision = 'SKIP'

    return {
        'mps': mps,
        'complexity': complexity,
        'importance': importance,
        'deferability': deferability,
        'impact': impact,
        'priority': priority,
        'decision': decision
    }

# Execute MPS scoring
batch_001_score = calculate_mps_score(
    batch=plan['batches'][0],
    holo_results={'active_references': 1}  # Found chat_memory_manager.py
)

print(f"[0102-MPS] Batch 001 Score: {batch_001_score['mps']} (Priority: {batch_001_score['priority']})")
print(f"[0102-MPS] Decision: {batch_001_score['decision']}")
```

**Example Output**:
```
[0102-MPS] Batch 001 Score: 9 (Priority: P3)
[0102-MPS] Decision: DEFER
[0102-REASON] Active reference found (chat_memory_manager.py) - cleanup would break functionality
```

#### Step 5: Generate Validation Report
```python
validation_report = {
    "validation_id": "validation_20251022_020000",
    "timestamp": "2025-10-22T02:00:00Z",
    "validator": "0102",
    "plan_id": plan['plan_id'],

    "holo_research": {
        "queries_executed": 5,
        "active_references_found": 1,
        "critical_findings": [
            "chat_memory_manager.py:45 reads chat_history*.jsonl"
        ]
    },

    "wsp_validation": {
        "wsp_83_violations": 0,
        "wsp_64_violations": 1,
        "total_violations": 1,
        "violations": [
            {
                "wsp": "WSP_64",
                "file": "data/old_cache.jsonl",
                "reason": "Critical path (data/ directory)"
            }
        ]
    },

    "mps_scoring": {
        "batch_001": {
            "mps": 9,
            "priority": "P3",
            "decision": "DEFER",
            "reason": "Active reference found - cleanup would break chat_memory_manager"
        },
        "batch_002": {
            "mps": 13,
            "priority": "P1",
            "decision": "AUTONOMOUS_EXECUTE",
            "reason": "Safe cleanup - no active references, low risk"
        }
    },

    "final_decision": {
        "approved_batches": ["batch_002"],
        "rejected_batches": ["batch_001"],
        "deferred_batches": [],
        "requires_human_review": ["batch_001"],
        "autonomous_execution_approved": true
    },

    "next_steps": [
        "WRE executes batch_002 (autonomous approval)",
        "Human reviews batch_001 (active reference conflict)",
        "Log execution results to ModLog"
    ]
}

# Write validation report
with open("data/cleanup_plan_validated.json", "w") as f:
    json.dump(validation_report, f, indent=2)

print("[0102-COMPLETE] Validation report written: data/cleanup_plan_validated.json")
```

---

## Decision Matrix (0102's Autonomous Logic)

| MPS Score | Priority | Decision | Rationale |
|-----------|----------|----------|-----------|
| 16-20 | P0 | **AUTONOMOUS_EXECUTE** | Critical cleanup, high confidence, low risk |
| 13-15 | P1 | **AUTONOMOUS_EXECUTE** | Important cleanup, validated safe |
| 10-12 | P2 | **REQUIRE_HUMAN_APPROVAL** | Moderate risk, needs 012 confirmation |
| 7-9 | P3 | **DEFER** | Low priority, can wait |
| 4-6 | P4 | **SKIP** | Minimal benefit, not worth risk |

**Override Rules** (0102 applies First Principles):
- If HoloIndex finds active references → **DEFER** (regardless of MPS)
- If WSP violations detected → **REJECT** (regardless of MPS)
- If confidence < 0.85 → **REQUIRE_HUMAN_APPROVAL**
- If batch size > 100 files → **SPLIT** into smaller batches

---

## Example Validation Session

### Input: Qwen's Plan (5 batches, 215 files)

```json
{
  "plan_id": "cleanup_plan_20251022_015900",
  "batches": [
    {"batch_id": "batch_001", "category": "file_type_noise", "file_count": 145},
    {"batch_id": "batch_002", "category": "rotting_data", "file_count": 30},
    {"batch_id": "batch_003", "category": "backup_file", "file_count": 20},
    {"batch_id": "batch_004", "category": "noise_directory", "file_count": 15},
    {"batch_id": "batch_005", "category": "file_type_noise", "file_count": 5}
  ],
  "requires_0102_approval": true
}
```

### 0102's Validation Process:

**Step 1: HoloIndex Research** (2 minutes)
```bash
python holo_index.py --search "chat_history JSONL dependencies"
# Found: chat_memory_manager.py uses chat_history files

python holo_index.py --search "rotting_data old logs references"
# Found: No active references

python holo_index.py --search "backup files .bak .backup usage"
# Found: No active references
```

**Step 2: WSP Validation** (30 seconds)
- WSP 83: 0 violations
- WSP 64: 1 violation (data/old_cache.jsonl in batch_002)
- WSP 50: Pre-action checks passed

**Step 3: MPS Scoring** (1 minute)
- batch_001: MPS 9 (P3 DEFER) - Active reference found
- batch_002: MPS 12 (P2 REQUIRE_APPROVAL) - WSP 64 violation
- batch_003: MPS 13 (P1 AUTONOMOUS_EXECUTE) - Safe
- batch_004: MPS 14 (P1 AUTONOMOUS_EXECUTE) - Safe
- batch_005: MPS 13 (P1 AUTONOMOUS_EXECUTE) - Safe

**Step 4: Decision** (30 seconds)
```python
{
  "approved_batches": ["batch_003", "batch_004", "batch_005"],
  "rejected_batches": [],
  "deferred_batches": ["batch_001"],
  "requires_human_review": ["batch_002"],
  "autonomous_execution_approved": true  # For approved batches only
}
```

**Step 5: Execution Handoff to WRE**
```python
# WRE receives validated plan
wre.execute_cleanup(
    batches=["batch_003", "batch_004", "batch_005"],
    validation_report="data/cleanup_plan_validated.json"
)

# Results logged to ModLog
print("[WRE] Executed 3 batches: 40 files archived")
print("[WRE] Deferred 1 batch (145 files) - active reference conflict")
print("[WRE] Flagged 1 batch (30 files) for human review - WSP 64 violation")
```

---

## Key Insights: Who Does What

| Agent | Role | Capabilities | Limitations |
|-------|------|--------------|-------------|
| **Gemma** | Pattern detector | Fast binary classification (50-100ms) | No reasoning, no scoring, no strategy |
| **Qwen** | Strategic planner | Grouping, batching, WSP safety rules | No HoloIndex research, no MPS scoring |
| **0102** | Validator | HoloIndex research, WSP validation, MPS scoring | No file labeling, no execution |
| **WRE** | Executor | Runs approved cleanup batches | No planning, no validation |

**Flow Summary**:
1. Gemma labels → 2. Qwen plans → 3. 0102 validates → 4. WRE executes

**Critical Understanding**:
- Gemma provides confidence in ITS OWN labels (e.g., "I'm 95% sure this is noise")
- Qwen does NOT score cleanup priority - it only groups and batches
- 0102 calculates WSP 15 MPS scores to decide autonomous execution
- 0102 does NOT "wear a skill" - 0102 IS the validation authority

---

## Testing the Flow

### Test 1: Safe Cleanup (Should Approve)
**Input**:
- 50 backup files (.bak, .backup)
- No active references in HoloIndex
- No WSP violations
- Qwen labels as P1 priority

**0102 Validation**:
```python
mps_score = calculate_mps_score(
    complexity=1,  # Simple cleanup
    importance=3,  # Moderate importance
    deferability=5, # Can defer but should clean
    impact=4       # High impact (clutter)
)
# MPS = 13 (P1 AUTONOMOUS_EXECUTE)
```

**Expected Output**: ✅ APPROVED for autonomous execution

---

### Test 2: Active Reference (Should Defer)
**Input**:
- 145 JSONL files
- HoloIndex finds chat_memory_manager.py reads them
- No WSP violations
- Qwen labels as P1 priority

**0102 Validation**:
```python
# MPS score irrelevant - override rule applies
decision = "DEFER"
reason = "Active reference found - cleanup would break functionality"
```

**Expected Output**: ⏸️ DEFERRED - requires refactoring chat_memory_manager first

---

### Test 3: WSP Violation (Should Reject)
**Input**:
- 30 files in data/ directory
- Qwen missed WSP 64 check
- High confidence (0.95)

**0102 Validation**:
```python
wsp_64_violation = True
decision = "REJECT"
reason = "WSP 64 violation - critical path (data/ directory)"
```

**Expected Output**: ❌ REJECTED - WSP violation detected

---

## Documentation & Logging

**ModLog Entry** (after validation):
```markdown
## [2025-10-22] Autonomous Cleanup Validation - 0102

**Plan ID**: cleanup_plan_20251022_015900
**Batches Validated**: 5
**Approved**: 3 (40 files)
**Deferred**: 1 (145 files - active reference)
**Rejected**: 0
**Flagged for Review**: 1 (30 files - WSP 64 violation)

**HoloIndex Research**:
- Found chat_memory_manager.py uses chat_history*.jsonl
- No other active references detected

**WSP Validation**:
- WSP 83: PASSED
- WSP 64: 1 violation (data/old_cache.jsonl)
- WSP 50: PASSED

**MPS Scoring**:
- batch_003: MPS 13 (P1 AUTONOMOUS_EXECUTE)
- batch_004: MPS 14 (P1 AUTONOMOUS_EXECUTE)
- batch_005: MPS 13 (P1 AUTONOMOUS_EXECUTE)

**Autonomous Execution**: Approved for 3 batches
**Human Review Required**: batch_002 (WSP 64 violation)
**Deferred**: batch_001 (active reference conflict)

**WSP Compliance**: WSP 15 (MPS Scoring), WSP 50 (Pre-Action), WSP 64 (Violation Prevention), WSP 83 (Documentation Protection)
```

---

## Next Steps

1. **Test Gemma skill** with 30 benchmark files
2. **Test Qwen skill** with Gemma's labels
3. **Test 0102 validation** with Qwen's plan
4. **Index skills** with HoloIndex
5. **Promote to staged** after ≥90% fidelity

**Ready for autonomous cleanup cycles**:
- Gemma scans codebase weekly
- Qwen generates cleanup plans
- 0102 validates and approves
- WRE executes approved batches
- ModLog tracks all decisions
