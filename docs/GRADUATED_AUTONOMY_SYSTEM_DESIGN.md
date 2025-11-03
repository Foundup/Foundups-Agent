# Graduated Autonomy System - Design Document

**Date**: 2025-10-21
**Status**: Design Phase
**WSP Compliance**: WSP 77 (Agent Coordination), WSP 54 (Agent Duties), WSP 91 (Observability)

---

## Executive Summary

Implement a confidence-based permission escalation system where Qwen/Gemma agents earn Edit/Write permissions based on proven ability, enabling autonomous code quality improvements while maintaining safety boundaries.

**User Vision** (Direct Quote):
> "skills or something should grant it when certain characteristics happen and as their ability to fix is proven... confidence algorithm? could gemma search for duplicate code patterns in modules... or dead code in modules that have been vibcoded out or not doing anything... can then qwen investigate... make a report for 0102 to deep think, reseach evaluate for code removal of enhancement... the system should start by looking for bugs,.... then when there are none,,, then it should go thru the list of Holo abilities and ask can it apply it use if to improve the current codebase... hard think apply first principles use holo to research"

---

## Architecture Overview

### Three-Tier Agent System

```
┌─────────────────────────────────────────────────────────────┐
│                  GRADUATED AUTONOMY TIERS                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Tier 1: GEMMA (Pattern Detection)                         │
│  ├─ Search duplicate code patterns                         │
│  ├─ Detect dead code / vibecoded out modules               │
│  ├─ Find unused imports, functions, classes                │
│  ├─ Identify orphaned modules (464 candidates)             │
│  └─ Permissions: Read-only via MCP/HoloIndex               │
│                                                             │
│  Tier 2: QWEN (Investigation & Reporting)                  │
│  ├─ Investigate Gemma findings                             │
│  ├─ Generate reports with recommendations                  │
│  ├─ Analyze code quality issues                            │
│  ├─ Suggest integration vs archive vs delete               │
│  └─ Permissions: Read + Metrics Write                      │
│                                                             │
│  Tier 3: 0102 (Deep Think & Execution)                     │
│  ├─ Research using HoloIndex & first principles            │
│  ├─ Evaluate Qwen reports for action                       │
│  ├─ Decide: remove, enhance, integrate, archive            │
│  ├─ Execute code changes via Edit/Write tools              │
│  └─ Permissions: Full Edit/Write access                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Existing Patterns to Leverage

### 1. Skill Promotion Pipeline (MetricsAppender)

**Location**: `modules/infrastructure/metrics_appender/`

**What Exists**:
- Append-only JSON metrics for skill execution tracking
- Prototype → Staged → Production promotion via metrics
- Confidence scoring based on execution success rates

**How to Adapt**:
```python
# Agent confidence tracking structure
{
  "agent_id": "gemma_dead_code_detection",
  "tier": "tier1_pattern_detection",
  "confidence_score": 0.85,
  "execution_history": [
    {"success": True, "timestamp": "2025-10-21T12:00:00", "validation": "0102_approved"},
    {"success": True, "timestamp": "2025-10-21T13:00:00", "validation": "0102_approved"}
  ],
  "permission_level": "read_only",
  "promotion_threshold": 0.90,  # 90% success rate for Write access
  "promotion_candidates": ["metrics_write", "edit_access_allowlist"]
}
```

### 2. QWEN Platform Health Monitoring (DuplicatePreventionManager)

**Location**: `modules/platform_integration/social_media_orchestrator/src/core/duplicate_prevention_manager.py`

**What Exists**:
- Platform health tracking (HEALTHY, WARMING, HOT, OVERHEATED)
- Pattern learning from outcomes
- Confidence-based decision making

**How to Adapt**:
```python
# Agent health monitoring
agent_status = {
    'gemma': {
        'health': AgentHealth.HEALTHY,
        'confidence': 0.92,
        'recent_successes': 47,
        'recent_failures': 3,
        'permission_level': 'read_only'
    },
    'qwen': {
        'health': AgentHealth.WARMING,
        'confidence': 0.78,
        'recent_successes': 23,
        'recent_failures': 7,
        'permission_level': 'read_metrics_write'
    }
}
```

### 3. Consent Engine (Permission Management)

**Location**: `modules/communication/consent_engine/src/consent_engine.py`

**What Exists**:
- Granular permission tracking
- Validation with expiration
- Compliance scoring (WSP alignment)

**How to Adapt**:
```python
# Agent permission records
AgentPermissionRecord(
    agent_id="qwen_code_quality",
    permission_type=PermissionType.EDIT_ACCESS,
    granted_at=datetime(2025, 10, 21),
    expires_at=datetime(2025, 11, 21),  # 30-day trial
    confidence_required=0.85,
    current_confidence=0.92,
    validation_checks=[
        "no_import_violations",
        "no_wsp_violations",
        "human_review_passed"
    ],
    allowlist_patterns=[
        "modules/**/tests/**/*.py",  # Test files only initially
        "modules/**/docs/**/*.md"    # Documentation files
    ]
)
```

### 4. Qwen/Gemma Orphan Analysis Mission

**Location**: `holo_index/docs/Qwen_Gemma_Orphan_Analysis_Mission.md`

**What Exists**:
- Phase 1 (Qwen): Analyze & categorize 464 orphans
- Phase 2 (Gemma): Similarity analysis for duplicates
- Phase 3 (0102): Integration vs archive vs delete decisions
- Pattern learning pipeline

**How to Adapt**: This IS the graduated autonomy workflow! Already designed for:
1. Gemma detects patterns (dead code, orphans)
2. Qwen investigates and reports
3. 0102 evaluates and executes

---

## Implementation Plan

### Phase 1: Confidence Tracking Infrastructure (Week 1)

**Create New Module**: `modules/ai_intelligence/agent_permissions/`

**Files to Create**:
```
modules/ai_intelligence/agent_permissions/
├── README.md                     - Module overview
├── INTERFACE.md                  - Public API
├── ModLog.md                     - Change history
├── src/
│   ├── __init__.py
│   ├── agent_permission_manager.py   - Core permission logic
│   ├── confidence_tracker.py         - Confidence scoring
│   └── allowlist_manager.py          - File pattern allowlists
├── tests/
│   └── test_agent_permissions.py
└── requirements.txt              - Empty (stdlib only)
```

**Core Classes**:

```python
# agent_permission_manager.py
class AgentPermissionManager:
    """
    Manage agent permissions with confidence-based escalation.

    Integration Points:
    - MetricsAppender: Track execution success/failure
    - ConsentEngine: Permission validation
    - PatchExecutor: Allowlist enforcement
    """

    def __init__(self, repo_root: Path):
        self.confidence_tracker = ConfidenceTracker()
        self.allowlist_manager = AllowlistManager()
        self.permissions = {}  # agent_id -> PermissionRecord

    def check_permission(
        self,
        agent_id: str,
        operation: str,  # 'read', 'metrics_write', 'edit', 'write'
        file_path: str
    ) -> PermissionCheckResult:
        """Check if agent has permission for operation on file"""

    def request_permission_escalation(
        self,
        agent_id: str,
        new_permission: str,
        justification: Dict[str, Any]
    ) -> EscalationRequest:
        """Request permission escalation based on confidence"""

    def grant_permission(
        self,
        agent_id: str,
        permission_type: str,
        duration_days: int = 30,
        allowlist_patterns: List[str] = None
    ) -> PermissionRecord:
        """Grant permission with constraints"""
```

```python
# confidence_tracker.py
class ConfidenceTracker:
    """
    Track agent confidence scores based on execution history.

    Confidence Algorithm:
    - Success rate (weighted by recency)
    - Validation by human review
    - WSP compliance rate
    - Code quality metrics
    """

    def update_confidence(
        self,
        agent_id: str,
        execution_result: Dict[str, Any]
    ) -> float:
        """Update confidence score after execution"""

    def calculate_confidence(
        self,
        agent_id: str
    ) -> ConfidenceScore:
        """Calculate current confidence score"""

    def check_promotion_eligibility(
        self,
        agent_id: str,
        target_permission: str
    ) -> PromotionEligibility:
        """Check if agent is eligible for permission promotion"""
```

### Phase 2: Gemma Pattern Detection Skills (Week 2)

**Create Skills** (follow WRE skill format):

```json
// .claude/skills/gemma_dead_code_detection.json
{
  "name": "gemma_dead_code_detection",
  "agent": "gemma",
  "tier": "tier1_pattern_detection",
  "permissions": ["read_only"],
  "description": "Detect dead code, unused imports, orphaned modules",
  "mcp_tools": ["holo_index", "codeindex"],
  "output_format": "detection_report.json",
  "promotion_criteria": {
    "success_rate": 0.90,
    "human_validated": 10,
    "false_positives": "< 5%"
  }
}
```

**Detection Capabilities**:
1. **Duplicate Code Detection**
   - AST-based similarity scoring
   - Function signature matching
   - Cross-module duplicate identification

2. **Dead Code Detection**
   - Unused imports
   - Unreferenced functions/classes
   - Orphaned modules (no imports from active code)

3. **Vibecoded Out Detection**
   - Code commented out
   - Alternative implementations unused
   - Deprecated patterns

### Phase 3: Qwen Investigation & Reporting (Week 3)

**Create Skills**:

```json
// .claude/skills/qwen_code_quality_investigator.json
{
  "name": "qwen_code_quality_investigator",
  "agent": "qwen",
  "tier": "tier2_investigation",
  "permissions": ["read_only", "metrics_write"],
  "description": "Investigate Gemma findings, generate detailed reports",
  "mcp_tools": ["holo_index", "codeindex", "wsp_governance"],
  "output_format": "investigation_report.json",
  "promotion_criteria": {
    "success_rate": 0.85,
    "report_quality": "human_approved",
    "recommendations_accurate": "80%"
  }
}
```

**Investigation Workflow**:
1. **Receive Gemma Detection Report**
2. **Deep Analysis**:
   - Read affected files
   - Analyze imports and dependencies
   - Check WSP compliance
   - Search for similar code in active modules
3. **Generate Report**:
   - Classification: duplicate/dead/vibecoded/orphaned
   - Recommendation: integrate/archive/delete/enhance
   - Risk assessment
   - Effort estimate
4. **Write Metrics** (tracks investigation quality)

### Phase 4: 0102 Evaluation & Execution (Week 4)

**Workflow**:
1. **Receive Qwen Report**
2. **Deep Think**:
   - Research via HoloIndex
   - Apply first principles
   - Consult WSP protocols
   - Validate with NAVIGATION.py
3. **Decision**:
   - Approve: Execute code changes
   - Reject: Provide feedback to Qwen
   - Defer: Request more information
4. **Execute** (if approved):
   - Use Edit/Write tools
   - Follow WSP compliance
   - Update ModLogs
   - Commit changes

**Metrics Tracking**:
- Track 0102 approval rate
- Track accuracy of Qwen recommendations
- Feed back to confidence algorithm

---

## Priority: Bugs First, Then Enhancements

### Workflow State Machine

```
┌─────────────────────────────────────────────────────────────┐
│                  GRADUATED AUTONOMY WORKFLOW                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  State 1: BUG DETECTION (Priority 0)                       │
│  ├─ Monitor daemon logs                                    │
│  ├─ Detect errors, exceptions, crashes                     │
│  ├─ AI Overseer autonomous fixes (ACTIVE NOW!)             │
│  └─ When bugs == 0 → Transition to State 2                 │
│                                                             │
│  State 2: CODE QUALITY IMPROVEMENTS (Priority 1)           │
│  ├─ Gemma: Search for dead code, duplicates                │
│  ├─ Qwen: Investigate and report                           │
│  ├─ 0102: Evaluate and execute removals                    │
│  └─ When orphans reduced → Transition to State 3           │
│                                                             │
│  State 3: HOLO ABILITIES APPLICATION (Priority 2)          │
│  ├─ Iterate through Holo capabilities:                     │
│  │   • Semantic search improvements                        │
│  │   • WSP compliance enhancements                         │
│  │   • Module health assessments                           │
│  │   • Pattern learning applications                       │
│  ├─ For each ability:                                      │
│  │   1. Gemma: Can this improve codebase?                  │
│  │   2. Qwen: Generate improvement plan                    │
│  │   3. 0102: Research, evaluate, execute                  │
│  └─ Continuous improvement loop                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Safety Boundaries

### Permission Escalation Thresholds

```python
PERMISSION_THRESHOLDS = {
    'metrics_write': {
        'confidence_required': 0.75,
        'successful_executions': 10,
        'human_validations': 5,
        'trial_period_days': 7
    },
    'edit_access_tests': {
        'confidence_required': 0.85,
        'successful_executions': 25,
        'human_validations': 10,
        'trial_period_days': 14,
        'allowlist': ['modules/**/tests/**/*.py']
    },
    'edit_access_docs': {
        'confidence_required': 0.85,
        'successful_executions': 25,
        'human_validations': 10,
        'trial_period_days': 14,
        'allowlist': ['modules/**/docs/**/*.md']
    },
    'edit_access_src': {
        'confidence_required': 0.95,
        'successful_executions': 100,
        'human_validations': 50,
        'trial_period_days': 30,
        'allowlist': ['modules/**/*.py'],
        'forbidlist': ['main.py', 'modules/**/src/*_dae.py']
    }
}
```

### Allowlist Architecture

**Leverage PatchExecutor Allowlist**:
- Reuse allowlist validation from `modules/infrastructure/patch_executor/`
- File pattern matching (with `**` recursive glob support)
- Forbidden operations (e.g., can't modify main.py)
- Size limits (e.g., max 200 lines changed per execution)

---

## Integration with Existing Systems

### 1. AI Overseer Integration

**Location**: `modules/ai_intelligence/ai_overseer/src/ai_overseer.py`

**Current State**: Autonomous bug detection + fixes (via PatchExecutor)

**Enhancement**: Add confidence tracking
```python
# In monitor_daemon()
if fix applied successfully:
    confidence_tracker.update_confidence(
        agent_id="ai_overseer_unicode_fix",
        execution_result={
            'success': True,
            'bug_fixed': bug_description,
            'patch_applied': True,
            'validation': 'daemon_restarted_successfully'
        }
    )
```

### 2. YouTube DAE Heartbeat Integration

**Location**: `modules/communication/livechat/src/youtube_dae_heartbeat.py`

**Current State**: Health monitoring + AI Overseer proactive checks

**Enhancement**: Feed health metrics to confidence tracker
```python
# In _pulse()
if self.enable_ai_overseer and self.ai_overseer:
    overseer_result = await self._run_ai_overseer_check()

    # Track confidence
    confidence_tracker.update_confidence(
        agent_id="ai_overseer_daemon_monitor",
        execution_result={
            'success': overseer_result['bugs_fixed'] > 0,
            'bugs_detected': overseer_result['bugs_detected'],
            'bugs_fixed': overseer_result['bugs_fixed']
        }
    )
```

### 3. MetricsAppender Integration

**Location**: `modules/infrastructure/metrics_appender/src/metrics_appender.py`

**Current State**: Append-only metrics for skill promotion

**Enhancement**: Add agent permission metrics
```python
# In append_metrics()
metrics = {
    'agent_id': 'qwen_code_quality',
    'operation': 'investigation_report',
    'confidence_score': 0.87,
    'permission_level': 'read_metrics_write',
    'promotion_eligible': True,
    'next_permission': 'edit_access_tests'
}
```

---

## Success Metrics

### Quantitative Goals (3 months)

1. **Bug Resolution**:
   - AI Overseer confidence: > 0.90
   - Bugs auto-fixed: > 80%
   - False positives: < 5%

2. **Code Quality**:
   - Orphaned modules: 464 → < 50
   - Duplicate code: Reduced by 30%
   - Dead code removed: > 100 files

3. **Agent Confidence**:
   - Gemma pattern detection: > 0.85
   - Qwen investigation accuracy: > 0.80
   - 0102 execution success: > 0.95

### Qualitative Goals

1. **Trust**: 012 trusts agents to make recommendations
2. **Efficiency**: 93% token reduction maintained (50-200 vs 15K+)
3. **Learning**: System improves with each execution
4. **Transparency**: Clear audit trail for all autonomous actions

---

## Next Steps

### Immediate (This Week)

1. **Create agent_permissions module** (WSP 3 + 49 compliant)
2. **Implement ConfidenceTracker** (leverage MetricsAppender patterns)
3. **Adapt AllowlistManager** (reuse PatchExecutor validation)

### Short-Term (Next 2 Weeks)

1. **Create Gemma dead code detection skill**
2. **Create Qwen investigation skill**
3. **Integrate with AI Overseer for bug priority**

### Long-Term (3 Months)

1. **Orphan cleanup mission** (464 → < 50)
2. **Holo abilities iteration** (systematic improvements)
3. **Full graduated autonomy operational**

---

## References

**Existing Patterns**:
- [MetricsAppender](../../modules/infrastructure/metrics_appender/)
- [PatchExecutor](../../modules/infrastructure/patch_executor/)
- [ConsentEngine](../../modules/communication/consent_engine/)
- [DuplicatePreventionManager](../../modules/platform_integration/social_media_orchestrator/src/core/duplicate_prevention_manager.py)
- [Qwen/Gemma Orphan Analysis Mission](./Qwen_Gemma_Orphan_Analysis_Mission.md)

**WSP Protocols**:
- WSP 77: Agent Coordination
- WSP 54: Agent Duties
- WSP 91: DAEMON Observability
- WSP 3: Module Organization
- WSP 49: Module Structure

---

**Status**: Design complete, ready for Phase 1 implementation

**Author**: 0102
**Date**: 2025-10-21
**Vision**: Agents learn, improve, and earn trust through proven ability
