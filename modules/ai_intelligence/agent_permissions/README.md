# Agent Permissions - Graduated Autonomy System

**Module**: `modules/ai_intelligence/agent_permissions/`
**Purpose**: Confidence-based permission escalation for Qwen/Gemma agents
**Status**: Phase 1 Implementation Complete

---

## Overview

Implements graduated autonomy where agents earn Edit/Write permissions based on proven ability through:
- **Confidence tracking** with exponential time decay
- **Automatic downgrade** when confidence drops
- **Skills registry integration** (single source of truth)
- **JSONL audit trail** for WSP 50 compliance

---

## Quick Start

```python
from pathlib import Path
from modules.ai_intelligence.agent_permissions.src import (
    AgentPermissionManager,
    ConfidenceTracker,
    ConfidenceBoostEvent
)

# Initialize
repo_root = Path("O:/Foundups-Agent")
perm_mgr = AgentPermissionManager(repo_root)

# Check permission
result = perm_mgr.check_permission(
    agent_id="gemma_dead_code_detection",
    operation="edit",
    file_path="modules/test/test_example.py"
)

if result.allowed:
    # Agent can proceed
    print(f"Allowed: {result.permission_level}, Confidence: {result.confidence:.2f}")
else:
    print(f"Denied: {result.reason}")

# Update confidence after successful execution
tracker = perm_mgr.confidence_tracker
tracker.update_confidence(
    agent_id="gemma_dead_code_detection",
    execution_result={
        'success': True,
        'event_type': 'HUMAN_APPROVAL',
        'validation': '0102_approved'
    }
)
```

---

## Architecture

### Three-Tier Permission System

```
Read-Only (Default)
    ↓ (75% confidence, 10 successes)
Metrics Write
    ↓ (85% confidence, 25 successes)
Edit Tests & Docs
    ↓ (95% confidence, 100 successes, 50 human approvals)
Edit Source Code (with allowlist)
```

### Confidence Algorithm

```python
confidence_score = (
    (weighted_success_rate * 0.6) +
    (human_approval_rate * 0.3) +
    (wsp_compliance_rate * 0.1)
) * failure_decay_multiplier

failure_multiplier = max(0.5, 1.0 - (recent_failures * 0.1))
```

**Decay Events**:
- Rollback: -0.15
- Rejection: -0.10
- WSP Violation: -0.20
- Regression: -0.25
- Security Issue: -0.50

**Boost Events**:
- Human Approval: +0.10
- Tests Passed: +0.05
- Production Stable (7 days): +0.15

---

## Integration Points

### 1. Skills Registry (`.claude/skills/skills_registry.json`)

Single source of truth for skills + permissions:

```json
{
  "skills": [
    {
      "name": "gemma_dead_code_detection",
      "agent": "gemma",
      "permission_level": "metrics_write",
      "permission_granted_at": "2025-10-21T12:00:00",
      "permission_granted_by": "0102",
      "confidence_score": 0.78,
      "promotion_history": [
        {
          "from": "read_only",
          "to": "metrics_write",
          "date": "2025-10-21T12:00:00",
          "confidence": 0.78,
          "approval_signature": "sha256:a3f2b9c1..."
        }
      ]
    }
  ]
}
```

### 2. Permission Events (`.../memory/permission_events.jsonl`)

Append-only audit trail for WSP 50 compliance:

```jsonl
{"event_type": "PERMISSION_GRANTED", "agent_id": "gemma_dead_code", "permission": "metrics_write", "granted_by": "0102", "confidence_at_grant": 0.78, "timestamp": "2025-10-21T12:00:00"}
{"event_type": "PERMISSION_DOWNGRADE", "agent_id": "qwen_investigator", "permission_before": "edit_access_tests", "permission_after": "metrics_write", "reason": "Confidence dropped to 0.72", "timestamp": "2025-10-22T08:00:00"}
```

### 3. Confidence Events (`.../memory/confidence_events.jsonl`)

Track all confidence updates:

```jsonl
{"agent_id": "gemma_dead_code", "success": true, "event_type": "HUMAN_APPROVAL", "confidence_before": 0.68, "confidence_after": 0.78, "timestamp": "2025-10-21T11:30:00"}
```

---

## Safety Boundaries

### Allowlist/Forbidlist

```python
# Edit access to tests (safe to start)
allowlist = [
    "modules/**/tests/**/*.py",
    "modules/**/docs/**/*.md"
]

# Source code edit (restricted)
allowlist = ["modules/**/*.py"]
forbidlist = [
    "main.py",
    "modules/**/*_dae.py",  # Core DAE entry points
    ".env",
    "modules/infrastructure/wsp_orchestrator/**",
    "modules/infrastructure/mcp_manager/**"
]
```

### Automatic Downgrade

When confidence drops below threshold:
1. Permission drops one level (e.g., `edit_access_src` → `edit_access_tests`)
2. 48-hour cooldown before re-approval eligibility
3. Human re-approval required to escalate again

---

## WSP Compliance

- **WSP 77 (Agent Coordination)**: Confidence-based permission escalation
- **WSP 50 (Pre-Action Verification)**: Check permissions before operations
- **WSP 91 (Observability)**: JSONL telemetry for all events
- **WSP 3 (Module Organization)**: Placed in `ai_intelligence/` domain (AI coordination)
- **WSP 49 (Module Structure)**: README, INTERFACE, ModLog, src/, tests/

---

## Next Steps

### Phase 2: Gemma Skills (Week 2)
- Create `gemma_dead_code_detection.json` skill
- Create `gemma_duplicate_finder.json` skill
- Test with read-only permissions

### Phase 3: Qwen Skills (Week 3)
- Create `qwen_code_quality_investigator.json` skill
- Integrate with metrics_write permission
- Test promotion pipeline

### Phase 4: Full Pipeline (Week 4)
- Gemma → Qwen → 0102 coordination
- Automatic permission escalation based on proven ability
- Production deployment

---

## Documentation

- **Design**: [docs/GRADUATED_AUTONOMY_SYSTEM_DESIGN.md](../../../docs/GRADUATED_AUTONOMY_SYSTEM_DESIGN.md)
- **Upgrades**: [docs/GRADUATED_AUTONOMY_DESIGN_UPGRADES.md](../../../docs/GRADUATED_AUTONOMY_DESIGN_UPGRADES.md)
- **Summary**: [docs/GRADUATED_AUTONOMY_SUMMARY.md](../../../docs/GRADUATED_AUTONOMY_SUMMARY.md)
- **Interface**: [INTERFACE.md](./INTERFACE.md)
- **ModLog**: [ModLog.md](./ModLog.md)

---

**Status**: Phase 1 Complete - Core infrastructure operational
**Author**: 0102
**Date**: 2025-10-21
