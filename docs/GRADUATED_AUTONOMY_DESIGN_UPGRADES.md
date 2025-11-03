# Graduated Autonomy System - Design Upgrades

**Date**: 2025-10-21
**Status**: Critical Design Improvements Before Implementation
**Purpose**: Address 6 robustness gaps identified in initial design

---

## Upgrade 1: Failure Weighting in Confidence Model

### Problem
Initial design only tracks successes - confidence can only increase. No mechanism for automatic de-escalation when agents fail or get rejected by humans.

### Solution: Decay-Based Confidence Algorithm

**Mathematical Model**:
```python
# Time-weighted confidence with exponential decay on failures
confidence_score = (
    (weighted_success_rate * 0.6) +
    (human_approval_rate * 0.3) +
    (wsp_compliance_rate * 0.1)
) * failure_decay_multiplier

where:
  weighted_success_rate = Σ(success_i * time_weight_i) / total_executions
  time_weight_i = exp(-decay_rate * days_since_execution_i)
  failure_decay_multiplier = max(0.5, 1.0 - (recent_failures * 0.1))
```

**Decay Triggers**:
```python
class ConfidenceDecayEvent(Enum):
    """Events that trigger confidence decay"""
    EDIT_ROLLED_BACK = -0.15        # Human reverted the change
    HUMAN_REJECTION = -0.10         # Report rejected by 0102
    WSP_VIOLATION = -0.20           # Broke WSP compliance
    REGRESSION_CAUSED = -0.25       # Tests failed after change
    SECURITY_ISSUE = -0.50          # Created security vulnerability
    FALSE_POSITIVE = -0.05          # Gemma detection was wrong
    DUPLICATE_WORK = -0.03          # Redundant with existing

class ConfidenceBoostEvent(Enum):
    """Events that boost confidence"""
    HUMAN_APPROVAL = +0.10          # 0102 approved recommendation
    TESTS_PASSED = +0.05            # All tests passed after change
    WSP_COMPLIANT = +0.03           # No violations detected
    PEER_VALIDATION = +0.08         # Another agent verified work
    PRODUCTION_STABLE = +0.15       # Change stable after 7 days
```

**Implementation in ConfidenceTracker**:
```python
# modules/ai_intelligence/agent_permissions/src/confidence_tracker.py

class ConfidenceTracker:
    def __init__(self):
        self.decay_rate = 0.05  # 5% decay per day for old events
        self.lookback_window_days = 30

    def update_confidence(
        self,
        agent_id: str,
        execution_result: Dict[str, Any]
    ) -> float:
        """
        Update confidence with decay-based weighting

        Args:
            execution_result: {
                'success': bool,
                'timestamp': ISO datetime,
                'event_type': ConfidenceDecayEvent | ConfidenceBoostEvent,
                'validation': str,  # 'human_approved', 'tests_passed', etc.
                'rollback_reason': Optional[str]
            }
        """
        # Get agent history
        history = self._get_agent_history(agent_id)

        # Calculate time-weighted success rate
        now = datetime.now()
        weighted_successes = 0.0
        weighted_total = 0.0

        for event in history:
            days_ago = (now - event['timestamp']).days
            if days_ago > self.lookback_window_days:
                continue

            # Exponential decay: recent events weighted higher
            time_weight = math.exp(-self.decay_rate * days_ago)
            weighted_total += time_weight

            if event['success']:
                # Apply boost from event type
                boost = event.get('boost', 0.0)
                weighted_successes += time_weight * (1.0 + boost)
            else:
                # Apply decay from event type
                decay = event.get('decay', 0.0)
                weighted_successes += time_weight * decay  # Negative contribution

        # Calculate base confidence
        if weighted_total == 0:
            base_confidence = 0.5  # Neutral starting point
        else:
            base_confidence = max(0.0, weighted_successes / weighted_total)

        # Apply recent failure multiplier
        recent_failures = self._count_recent_failures(agent_id, days=7)
        failure_multiplier = max(0.5, 1.0 - (recent_failures * 0.1))

        final_confidence = base_confidence * failure_multiplier

        # Update stored confidence
        self._store_confidence(agent_id, final_confidence)

        # Check if permission downgrade needed
        self._check_permission_downgrade(agent_id, final_confidence)

        return final_confidence

    def _check_permission_downgrade(
        self,
        agent_id: str,
        current_confidence: float
    ) -> None:
        """Automatically downgrade permissions if confidence drops"""
        permission_mgr = AgentPermissionManager.get_instance()
        current_permission = permission_mgr.get_permission_level(agent_id)

        # Downgrade thresholds (lower than promotion thresholds)
        downgrade_thresholds = {
            'edit_access_src': 0.90,    # Need 95% to promote, drop at 90%
            'edit_access_tests': 0.80,  # Need 85% to promote, drop at 80%
            'metrics_write': 0.70        # Need 75% to promote, drop at 70%
        }

        threshold = downgrade_thresholds.get(current_permission)
        if threshold and current_confidence < threshold:
            logger.warning(
                f"[CONFIDENCE-DOWNGRADE] {agent_id}: {current_confidence:.2f} < {threshold:.2f}"
            )
            permission_mgr.downgrade_permission(
                agent_id=agent_id,
                reason=f"Confidence dropped to {current_confidence:.2f}",
                requires_reapproval=True
            )
```

**Metrics Storage** (in MetricsAppender format):
```json
{
  "agent_id": "qwen_code_quality",
  "timestamp": "2025-10-21T14:30:00",
  "event_type": "EDIT_ROLLED_BACK",
  "confidence_before": 0.87,
  "confidence_after": 0.72,
  "decay_applied": -0.15,
  "permission_before": "edit_access_tests",
  "permission_after": "metrics_write",
  "rollback_reason": "Introduced import cycle in test_agent_permissions.py",
  "human_feedback": "Good intent, but check imports before edits",
  "requires_retraining": true
}
```

---

## Upgrade 2: Promotion Record Format & Audit Trail

### Problem
Permission escalation thresholds mentioned but no specification of where approvals are stored or how WSP 50 audits can inspect them.

### Solution: Permission Events Registry

**Storage Location**: `modules/ai_intelligence/agent_permissions/memory/permission_events.jsonl`

**Format** (JSONL for append-only audit trail):
```jsonl
{"event_id": "perm_001", "agent_id": "gemma_dead_code", "event_type": "PERMISSION_GRANTED", "permission": "read_only", "granted_by": "system", "granted_at": "2025-10-21T10:00:00", "expires_at": null, "confidence_at_grant": 0.50, "justification": "Initial agent registration", "approval_signature": null}
{"event_id": "perm_002", "agent_id": "gemma_dead_code", "event_type": "EXECUTION_SUCCESS", "operation": "detect_orphans", "confidence_after": 0.68, "timestamp": "2025-10-21T11:30:00", "files_scanned": 150, "findings": 23}
{"event_id": "perm_003", "agent_id": "gemma_dead_code", "event_type": "HUMAN_APPROVAL", "approved_by": "012", "timestamp": "2025-10-21T12:00:00", "confidence_boost": 0.10, "confidence_after": 0.78, "notes": "Accurate orphan detection"}
{"event_id": "perm_004", "agent_id": "gemma_dead_code", "event_type": "PERMISSION_PROMOTION_REQUEST", "current_permission": "read_only", "requested_permission": "metrics_write", "confidence": 0.78, "threshold_required": 0.75, "execution_count": 12, "success_rate": 0.92, "timestamp": "2025-10-22T09:00:00"}
{"event_id": "perm_005", "agent_id": "gemma_dead_code", "event_type": "PERMISSION_GRANTED", "permission": "metrics_write", "granted_by": "0102", "granted_at": "2025-10-22T09:15:00", "expires_at": "2025-11-21T09:15:00", "confidence_at_grant": 0.78, "justification": "Proven pattern detection ability", "approval_signature": "sha256:a3f2b9c1..."}
{"event_id": "perm_006", "agent_id": "gemma_dead_code", "event_type": "EXECUTION_FAILURE", "operation": "detect_duplicates", "error": "AST parsing failed on malformed file", "confidence_decay": -0.05, "confidence_after": 0.73, "timestamp": "2025-10-23T14:00:00"}
{"event_id": "perm_007", "agent_id": "gemma_dead_code", "event_type": "PERMISSION_DOWNGRADE", "permission_before": "metrics_write", "permission_after": "read_only", "reason": "Confidence dropped below 70% threshold", "confidence": 0.68, "downgraded_by": "system_automatic", "timestamp": "2025-10-25T08:00:00", "requires_reapproval": true}
```

**Approval Signature** (for human-granted permissions):
```python
def generate_approval_signature(
    agent_id: str,
    permission: str,
    granted_by: str,
    timestamp: datetime
) -> str:
    """
    Generate cryptographic signature for permission grant
    Enables WSP 50 audit verification
    """
    approval_data = {
        'agent_id': agent_id,
        'permission': permission,
        'granted_by': granted_by,
        'timestamp': timestamp.isoformat()
    }

    signature_string = json.dumps(approval_data, sort_keys=True)
    return f"sha256:{hashlib.sha256(signature_string.encode()).hexdigest()}"
```

**WSP 50 Audit Query**:
```python
# modules/ai_intelligence/agent_permissions/src/audit.py

class PermissionAudit:
    """WSP 50 compliant permission audit"""

    def audit_agent_permissions(
        self,
        agent_id: str,
        start_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Generate audit report for agent permissions

        Returns:
            {
                'agent_id': str,
                'current_permission': str,
                'permission_history': List[PermissionEvent],
                'promotion_count': int,
                'downgrade_count': int,
                'human_approvals': int,
                'automatic_downgrades': int,
                'confidence_trajectory': List[float],
                'violations': List[str],
                'audit_passed': bool
            }
        """
```

**Integration with skills_registry.json**:
```json
// .claude/skills/skills_registry.json
{
  "skills": [
    {
      "name": "gemma_dead_code_detection",
      "agent": "gemma",
      "status": "staged",
      "permission_level": "metrics_write",
      "permission_granted_at": "2025-10-22T09:15:00",
      "permission_granted_by": "0102",
      "permission_expires_at": "2025-11-21T09:15:00",
      "confidence_score": 0.78,
      "promotion_history": [
        {
          "from": "prototype",
          "to": "staged",
          "date": "2025-10-20T10:00:00",
          "reason": "Initial testing complete"
        },
        {
          "from": "read_only",
          "to": "metrics_write",
          "date": "2025-10-22T09:15:00",
          "reason": "Proven detection accuracy",
          "confidence": 0.78,
          "approval_signature": "sha256:a3f2b9c1..."
        }
      ]
    }
  ]
}
```

---

## Upgrade 3: Verification Contracts Per Tier

### Problem
Tiers return findings/reports with no required post-check. Confidence scores may reflect actions taken, not tested outcomes.

### Solution: Tier-Specific Verification Protocol

**Tier 1 (Gemma) - Pattern Detection Verification**:
```python
class GemmaVerificationContract:
    """
    Verification requirements for Gemma pattern detection
    """

    @staticmethod
    def verify_detection(
        detection_report: Dict[str, Any],
        rerun: bool = True
    ) -> VerificationResult:
        """
        Verify Gemma detection findings

        Steps:
        1. Rerun pattern detection on same files
        2. Check if findings still exist (not already fixed)
        3. Validate file paths exist
        4. Check for false positives
        5. Cross-check with active modules (not orphans)

        Returns:
            VerificationResult(
                verified=bool,
                confidence_adjustment=float,  # ±0.1 based on accuracy
                false_positives=List[str],
                true_positives=List[str],
                findings_still_valid=bool
            )
        """

        if rerun:
            # Rerun detection
            rerun_report = gemma_engine.detect_patterns(
                files=detection_report['files_analyzed']
            )

            # Compare original vs rerun findings
            original_findings = set(detection_report['findings'])
            rerun_findings = set(rerun_report['findings'])

            # Findings that disappeared = false positives
            false_positives = original_findings - rerun_findings

            # Findings confirmed = true positives
            true_positives = original_findings & rerun_findings

            accuracy = len(true_positives) / len(original_findings) if original_findings else 0.0

            return VerificationResult(
                verified=accuracy >= 0.80,  # 80% accuracy threshold
                confidence_adjustment=0.10 if accuracy >= 0.90 else -0.05,
                false_positives=list(false_positives),
                true_positives=list(true_positives),
                findings_still_valid=len(true_positives) > 0
            )
```

**Tier 2 (Qwen) - Investigation Report Verification**:
```python
class QwenVerificationContract:
    """
    Verification requirements for Qwen investigation reports
    """

    @staticmethod
    def verify_investigation(
        investigation_report: Dict[str, Any]
    ) -> VerificationResult:
        """
        Verify Qwen investigation report

        Steps:
        1. Validate all file paths referenced exist
        2. Check recommendations against WSP compliance
        3. Verify import dependency analysis is accurate
        4. Confirm similarity scores with AST comparison
        5. Validate integration plan feasibility

        Returns:
            VerificationResult(
                verified=bool,
                confidence_adjustment=float,
                issues=List[str],
                wsp_compliant=bool,
                recommendation_valid=bool
            )
        """

        # Validate file existence
        missing_files = []
        for file_path in investigation_report['files_referenced']:
            if not Path(file_path).exists():
                missing_files.append(file_path)

        if missing_files:
            return VerificationResult(
                verified=False,
                confidence_adjustment=-0.10,
                issues=[f"Referenced non-existent files: {missing_files}"],
                wsp_compliant=False,
                recommendation_valid=False
            )

        # Check WSP compliance
        wsp_check = wsp_governance_mcp.check_compliance(
            recommendation=investigation_report['recommendation']
        )

        # Verify import analysis
        for module, imports in investigation_report['import_analysis'].items():
            actual_imports = ast_parser.get_imports(module)
            if set(imports) != set(actual_imports):
                return VerificationResult(
                    verified=False,
                    confidence_adjustment=-0.10,
                    issues=[f"Import analysis incorrect for {module}"],
                    wsp_compliant=wsp_check['compliant'],
                    recommendation_valid=False
                )

        return VerificationResult(
            verified=True,
            confidence_adjustment=0.05,
            issues=[],
            wsp_compliant=wsp_check['compliant'],
            recommendation_valid=True
        )
```

**Tier 3 (0102) - Code Change Verification**:
```python
class ZeroOneTwoVerificationContract:
    """
    Verification requirements for 0102 code changes
    """

    @staticmethod
    def verify_code_change(
        change_description: Dict[str, Any],
        files_modified: List[str]
    ) -> VerificationResult:
        """
        Verify 0102 code changes

        Steps:
        1. Run module tests (pytest)
        2. Check WSP compliance
        3. Verify no import cycles introduced
        4. Confirm no security vulnerabilities
        5. Validate ModLog updated

        Returns:
            VerificationResult(
                verified=bool,
                confidence_adjustment=float,
                tests_passed=bool,
                wsp_compliant=bool,
                no_regressions=bool,
                modlog_updated=bool
            )
        """

        # 1. Run tests
        test_result = pytest_runner.run_tests_for_modules(files_modified)

        if not test_result['all_passed']:
            return VerificationResult(
                verified=False,
                confidence_adjustment=-0.20,
                tests_passed=False,
                wsp_compliant=False,
                no_regressions=False,
                modlog_updated=False,
                errors=test_result['failures']
            )

        # 2. WSP compliance check
        wsp_check = wsp_governance_mcp.check_file_compliance(files_modified)

        # 3. Import cycle detection
        import_cycles = dependency_analyzer.detect_cycles(files_modified)

        # 4. ModLog verification (WSP 22)
        modlog_updated = all([
            _check_modlog_updated(Path(f).parent)
            for f in files_modified
            if not f.endswith('test_*.py')
        ])

        verified = (
            test_result['all_passed'] and
            wsp_check['compliant'] and
            not import_cycles and
            modlog_updated
        )

        return VerificationResult(
            verified=verified,
            confidence_adjustment=0.15 if verified else -0.10,
            tests_passed=test_result['all_passed'],
            wsp_compliant=wsp_check['compliant'],
            no_regressions=not import_cycles,
            modlog_updated=modlog_updated
        )
```

**Integration into Confidence Tracking**:
```python
# After each tier execution, run verification
def execute_tier_with_verification(
    tier: str,  # 'gemma', 'qwen', '0102'
    operation: str,
    **kwargs
) -> Dict[str, Any]:
    """Execute tier operation with mandatory verification"""

    # Execute operation
    result = tier_executor.execute(tier, operation, **kwargs)

    # Run verification contract
    if tier == 'gemma':
        verification = GemmaVerificationContract.verify_detection(result)
    elif tier == 'qwen':
        verification = QwenVerificationContract.verify_investigation(result)
    elif tier == '0102':
        verification = ZeroOneTwoVerificationContract.verify_code_change(result)

    # Update confidence based on verification
    confidence_tracker.update_confidence(
        agent_id=f"{tier}_{operation}",
        execution_result={
            'success': verification.verified,
            'verification_passed': verification.verified,
            'confidence_adjustment': verification.confidence_adjustment,
            'timestamp': datetime.now(),
            'details': verification.dict()
        }
    )

    return {
        'operation_result': result,
        'verification': verification,
        'confidence_updated': True
    }
```

---

## Upgrade 4: Skills Infrastructure Integration

### Problem
Design references ConsentEngine and DuplicatePreventionManager but doesn't explain how AgentPermissionManager writes back into skills_registry.json or WRE wardrobe. Risk of two parallel registries.

### Solution: Unified Skill & Permission Registry

**Architecture**:
```
┌─────────────────────────────────────────────────────────────┐
│              UNIFIED SKILL & PERMISSION SYSTEM              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  skills_registry.json (Source of Truth)                    │
│  ├─ Skill definitions                                      │
│  ├─ Permission levels                                      │
│  ├─ Confidence scores                                      │
│  └─ Promotion history                                      │
│                                                             │
│  AgentPermissionManager (Reads/Writes Registry)            │
│  ├─ check_permission() → Query registry                    │
│  ├─ grant_permission() → Update registry                   │
│  ├─ update_confidence() → Update registry                  │
│  └─ audit_trail() → Query permission_events.jsonl          │
│                                                             │
│  MetricsAppender (Metrics Only - No Permissions)           │
│  └─ append_metrics() → Write execution metrics             │
│                                                             │
│  WRE Wardrobe (Skill Promotion Only)                       │
│  └─ promote_skill() → Update wardrobe status               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Integration Code**:
```python
# modules/ai_intelligence/agent_permissions/src/agent_permission_manager.py

class AgentPermissionManager:
    """
    Unified manager for agent permissions and skill registry
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.skills_registry_path = repo_root / ".claude" / "skills" / "skills_registry.json"
        self.permission_events_path = repo_root / "modules" / "ai_intelligence" / "agent_permissions" / "memory" / "permission_events.jsonl"

        # Load existing registry
        self.skills_registry = self._load_skills_registry()

        # Initialize confidence tracker
        self.confidence_tracker = ConfidenceTracker(
            permission_manager=self  # Circular reference for registry updates
        )

    def _load_skills_registry(self) -> Dict[str, Any]:
        """Load skills registry from .claude/skills/skills_registry.json"""
        if not self.skills_registry_path.exists():
            return {'skills': [], 'version': '1.0.0'}

        with open(self.skills_registry_path, 'r') as f:
            return json.load(f)

    def _save_skills_registry(self) -> None:
        """Save skills registry (atomic write)"""
        temp_path = self.skills_registry_path.with_suffix('.tmp')
        with open(temp_path, 'w') as f:
            json.dump(self.skills_registry, f, indent=2)
        temp_path.replace(self.skills_registry_path)

    def grant_permission(
        self,
        agent_id: str,
        permission_type: str,
        granted_by: str,  # '0102', '012', 'system_automatic'
        duration_days: int = 30,
        allowlist_patterns: List[str] = None,
        justification: str = None
    ) -> PermissionRecord:
        """
        Grant permission and update skills registry
        """
        # Find skill in registry
        skill = self._find_skill(agent_id)

        if not skill:
            raise ValueError(f"Skill {agent_id} not found in registry")

        # Create permission record
        granted_at = datetime.now()
        expires_at = granted_at + timedelta(days=duration_days)

        permission_record = {
            'permission_level': permission_type,
            'granted_at': granted_at.isoformat(),
            'granted_by': granted_by,
            'expires_at': expires_at.isoformat(),
            'confidence_at_grant': self.confidence_tracker.get_confidence(agent_id),
            'allowlist_patterns': allowlist_patterns or [],
            'justification': justification,
            'approval_signature': self._generate_approval_signature(
                agent_id, permission_type, granted_by, granted_at
            )
        }

        # Update skill in registry
        skill['permission_level'] = permission_type
        skill['permission_granted_at'] = granted_at.isoformat()
        skill['permission_granted_by'] = granted_by
        skill['permission_expires_at'] = expires_at.isoformat()
        skill.setdefault('promotion_history', []).append({
            'from': skill.get('permission_level', 'none'),
            'to': permission_type,
            'date': granted_at.isoformat(),
            'reason': justification,
            'confidence': permission_record['confidence_at_grant'],
            'approval_signature': permission_record['approval_signature']
        })

        # Save registry (atomic write)
        self._save_skills_registry()

        # Append to audit trail
        self._append_permission_event({
            'event_type': 'PERMISSION_GRANTED',
            'agent_id': agent_id,
            'permission': permission_type,
            'granted_by': granted_by,
            'timestamp': granted_at.isoformat(),
            **permission_record
        })

        # Notify WRE Wardrobe (if skill promotion stage changes)
        if permission_type in ['edit_access_tests', 'edit_access_src']:
            self._notify_wre_wardrobe(agent_id, 'staged' if permission_type == 'edit_access_tests' else 'production')

        return permission_record

    def _notify_wre_wardrobe(self, agent_id: str, new_stage: str) -> None:
        """
        Notify WRE Wardrobe of skill promotion
        (Prevents two parallel registries)
        """
        try:
            from modules.infrastructure.wre_core.src.wre_wardrobe import WREWardrobe

            wardrobe = WREWardrobe(self.repo_root)
            wardrobe.update_skill_stage(
                skill_name=agent_id,
                new_stage=new_stage,
                reason=f"Permission escalated via confidence threshold"
            )
        except Exception as e:
            logger.warning(f"Could not notify WRE Wardrobe: {e}")

    def check_permission(
        self,
        agent_id: str,
        operation: str,  # 'read', 'metrics_write', 'edit', 'write'
        file_path: str
    ) -> PermissionCheckResult:
        """
        Check permission by querying skills registry
        """
        skill = self._find_skill(agent_id)

        if not skill:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Skill {agent_id} not registered"
            )

        # Check expiration
        expires_at = datetime.fromisoformat(skill.get('permission_expires_at', '2000-01-01'))
        if datetime.now() > expires_at:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Permission expired on {expires_at}"
            )

        # Check permission level
        permission_level = skill.get('permission_level', 'read_only')

        # Check allowlist
        if operation in ['edit', 'write']:
            allowlist_patterns = skill.get('promotion_history', [{}])[-1].get('allowlist_patterns', [])
            if not self._file_matches_allowlist(file_path, allowlist_patterns):
                return PermissionCheckResult(
                    allowed=False,
                    reason=f"File {file_path} not in allowlist"
                )

        # Check confidence (must remain above downgrade threshold)
        current_confidence = self.confidence_tracker.get_confidence(agent_id)
        downgrade_threshold = DOWNGRADE_THRESHOLDS.get(permission_level, 0.0)

        if current_confidence < downgrade_threshold:
            return PermissionCheckResult(
                allowed=False,
                reason=f"Confidence {current_confidence:.2f} below threshold {downgrade_threshold}"
            )

        return PermissionCheckResult(
            allowed=True,
            permission_level=permission_level,
            confidence=current_confidence
        )
```

**No Parallel Registries** - Single source of truth:
- `.claude/skills/skills_registry.json` = Skills + Permissions + Confidence
- `permission_events.jsonl` = Audit trail only (WSP 50 compliance)
- `MetricsAppender` = Execution metrics only (no permissions)
- `WRE Wardrobe` = Notified by AgentPermissionManager (stays in sync)

---

## Upgrade 5: "No Bugs" → Code Quality Transition Metric

### Problem
State 1 → State 2 transition defined as "bugs == 0" but live logs show constant low-grade noise. System needs clear metric to switch focus.

### Solution: Operational Stability Threshold

**Transition Metric**:
```python
class OperationalState(Enum):
    """System operational states"""
    BUG_DETECTION = "bug_detection"          # Priority 0: Active bugs
    CODE_QUALITY = "code_quality"            # Priority 1: Orphan cleanup
    HOLO_ABILITIES = "holo_abilities"        # Priority 2: Enhancements

class StateTransitionManager:
    """
    Manage state transitions based on operational metrics
    """

    def __init__(self):
        self.current_state = OperationalState.BUG_DETECTION
        self.state_history = []

        # Transition thresholds
        self.bug_detection_thresholds = {
            'p0_bugs_24h': 0,           # No P0 bugs in last 24 hours
            'p1_bugs_24h': 0,           # No P1 bugs in last 24 hours
            'auto_fix_success_rate': 0.95,  # 95% auto-fix success
            'daemon_stability_hours': 24,    # Daemon stable 24+ hours
            'false_positive_rate': 0.05      # < 5% false positives
        }

        self.code_quality_thresholds = {
            'orphan_modules': 50,        # Reduced from 464 to < 50
            'duplicate_code_pct': 5.0,   # < 5% duplicate code
            'dead_code_files': 10        # < 10 dead code files
        }

    def check_transition_eligibility(self) -> Dict[str, Any]:
        """
        Check if system can transition to next state
        """
        if self.current_state == OperationalState.BUG_DETECTION:
            return self._check_bug_detection_complete()
        elif self.current_state == OperationalState.CODE_QUALITY:
            return self._check_code_quality_complete()
        else:
            return {'eligible': False, 'reason': 'Already in final state'}

    def _check_bug_detection_complete(self) -> Dict[str, Any]:
        """
        Check if bug detection phase is complete

        Criteria:
        - No P0/P1 auto-fix triggers in 24 hours
        - Auto-fix success rate > 95%
        - Daemon stable for 24+ hours
        - False positive rate < 5%
        - Low-grade noise acceptable (P2/P3 bugs allowed)
        """
        # Query AI Overseer metrics
        overseer_metrics = self._query_ai_overseer_metrics(hours=24)

        # Query daemon heartbeat
        heartbeat_metrics = self._query_heartbeat_metrics(hours=24)

        checks = {
            'p0_bugs_24h': overseer_metrics['p0_bugs'] == 0,
            'p1_bugs_24h': overseer_metrics['p1_bugs'] == 0,
            'auto_fix_success_rate': overseer_metrics['success_rate'] >= 0.95,
            'daemon_stability_hours': heartbeat_metrics['uptime_hours'] >= 24,
            'false_positive_rate': overseer_metrics['false_positive_rate'] <= 0.05
        }

        all_passed = all(checks.values())

        result = {
            'eligible': all_passed,
            'checks': checks,
            'current_state': 'bug_detection',
            'next_state': 'code_quality' if all_passed else None,
            'timestamp': datetime.now().isoformat()
        }

        if all_passed:
            logger.info("[STATE-TRANSITION] ✓ Bug detection phase complete")
            logger.info("[STATE-TRANSITION] → Transitioning to code quality phase")
            self._transition_to(OperationalState.CODE_QUALITY)
        else:
            failed_checks = [k for k, v in checks.items() if not v]
            logger.info(f"[STATE-TRANSITION] ✗ Not ready for transition: {failed_checks}")

        return result

    def _transition_to(self, new_state: OperationalState) -> None:
        """Execute state transition"""
        old_state = self.current_state
        self.current_state = new_state

        self.state_history.append({
            'from': old_state.value,
            'to': new_state.value,
            'timestamp': datetime.now().isoformat(),
            'reason': 'Operational thresholds met'
        })

        # Notify agents of state change
        self._notify_agents_state_change(new_state)

    def _notify_agents_state_change(self, new_state: OperationalState) -> None:
        """
        Notify agents of state change
        (Adjusts agent focus - Gemma stops looking for bugs, starts looking for dead code)
        """
        if new_state == OperationalState.CODE_QUALITY:
            # Activate code quality skills
            self._activate_skill('gemma_dead_code_detection')
            self._activate_skill('gemma_duplicate_finder')
            self._activate_skill('qwen_orphan_investigator')

        elif new_state == OperationalState.HOLO_ABILITIES:
            # Activate enhancement skills
            self._activate_skill('qwen_holo_ability_applicator')
            self._activate_skill('gemma_pattern_learner')
```

**Operational Metrics Dashboard**:
```python
# Real-time state monitoring
def get_operational_dashboard() -> Dict[str, Any]:
    """
    Get current operational state dashboard
    """
    state_mgr = StateTransitionManager.get_instance()

    return {
        'current_state': state_mgr.current_state.value,
        'bug_detection_metrics': {
            'p0_bugs_24h': overseer_metrics['p0_bugs'],
            'p1_bugs_24h': overseer_metrics['p1_bugs'],
            'auto_fix_success_rate': overseer_metrics['success_rate'],
            'daemon_uptime_hours': heartbeat_metrics['uptime_hours'],
            'transition_eligible': state_mgr.check_transition_eligibility()['eligible']
        },
        'code_quality_metrics': {
            'orphan_modules': len(orphan_scanner.get_orphans()),
            'duplicate_code_pct': duplicate_analyzer.get_duplicate_percentage(),
            'dead_code_files': dead_code_scanner.count_dead_files()
        },
        'next_transition_eta': state_mgr.estimate_transition_time()
    }
```

---

## Upgrade 6: Rollback Semantics

### Problem
If higher permission causes regression (confidence drops below threshold), no specification for access revocation or re-approval process.

### Solution: Automatic Downgrade with Re-approval Flow

**Downgrade Trigger**:
```python
class PermissionDowngradeManager:
    """
    Handle automatic permission downgrades
    """

    def __init__(self):
        self.downgrade_cooldown_hours = 48  # Must wait 48h before reapplying

    def trigger_downgrade(
        self,
        agent_id: str,
        reason: str,
        confidence: float,
        threshold: float
    ) -> DowngradeResult:
        """
        Automatically downgrade agent permissions

        Triggers:
        - Confidence drops below downgrade threshold
        - Severe failure (WSP violation, security issue)
        - Multiple human rejections
        - Test regression caused
        """
        # Get current permission
        permission_mgr = AgentPermissionManager.get_instance()
        current_permission = permission_mgr.get_permission_level(agent_id)

        # Calculate new permission (one level down)
        permission_ladder = ['read_only', 'metrics_write', 'edit_access_tests', 'edit_access_src']
        current_idx = permission_ladder.index(current_permission) if current_permission in permission_ladder else 0
        new_permission = permission_ladder[max(0, current_idx - 1)]

        # Apply downgrade
        permission_mgr.revoke_permission(
            agent_id=agent_id,
            old_permission=current_permission,
            new_permission=new_permission,
            reason=reason,
            confidence=confidence,
            downgraded_by='system_automatic'
        )

        # Set re-approval requirement
        self._set_reapproval_required(
            agent_id=agent_id,
            cooldown_until=datetime.now() + timedelta(hours=self.downgrade_cooldown_hours)
        )

        # Notify human (012/0102)
        self._notify_human_of_downgrade(
            agent_id=agent_id,
            reason=reason,
            old_permission=current_permission,
            new_permission=new_permission
        )

        return DowngradeResult(
            success=True,
            old_permission=current_permission,
            new_permission=new_permission,
            cooldown_until=datetime.now() + timedelta(hours=self.downgrade_cooldown_hours),
            requires_reapproval=True
        )
```

**Re-approval Flow**:
```python
class ReapprovalFlow:
    """
    Handle re-approval after downgrade
    """

    def check_reapproval_eligibility(
        self,
        agent_id: str
    ) -> ReapprovalEligibility:
        """
        Check if agent is eligible for re-approval

        Requirements:
        - Cooldown period elapsed (48 hours)
        - Confidence recovered above threshold
        - Recent executions successful (> 90%)
        - Human review requested
        """
        downgrade_record = self._get_latest_downgrade(agent_id)

        if not downgrade_record:
            return ReapprovalEligibility(
                eligible=False,
                reason="No downgrade record found"
            )

        # Check cooldown
        cooldown_until = datetime.fromisoformat(downgrade_record['cooldown_until'])
        if datetime.now() < cooldown_until:
            hours_remaining = (cooldown_until - datetime.now()).total_seconds() / 3600
            return ReapprovalEligibility(
                eligible=False,
                reason=f"Cooldown period: {hours_remaining:.1f} hours remaining"
            )

        # Check confidence recovery
        confidence_tracker = ConfidenceTracker.get_instance()
        current_confidence = confidence_tracker.get_confidence(agent_id)
        target_permission = downgrade_record['old_permission']
        required_threshold = PROMOTION_THRESHOLDS[target_permission]['confidence_required']

        if current_confidence < required_threshold:
            return ReapprovalEligibility(
                eligible=False,
                reason=f"Confidence {current_confidence:.2f} below threshold {required_threshold}"
            )

        # Check recent success rate
        recent_executions = self._get_recent_executions(agent_id, days=7)
        success_rate = sum(e['success'] for e in recent_executions) / len(recent_executions) if recent_executions else 0.0

        if success_rate < 0.90:
            return ReapprovalEligibility(
                eligible=False,
                reason=f"Recent success rate {success_rate:.2f} below 90%"
            )

        return ReapprovalEligibility(
            eligible=True,
            reason="All requirements met",
            target_permission=target_permission,
            current_confidence=current_confidence,
            recent_success_rate=success_rate
        )

    def request_reapproval(
        self,
        agent_id: str,
        justification: str
    ) -> ReapprovalRequest:
        """
        Request human re-approval after downgrade
        """
        eligibility = self.check_reapproval_eligibility(agent_id)

        if not eligibility.eligible:
            return ReapprovalRequest(
                success=False,
                reason=eligibility.reason
            )

        # Create re-approval request
        request = {
            'agent_id': agent_id,
            'target_permission': eligibility.target_permission,
            'current_confidence': eligibility.current_confidence,
            'recent_success_rate': eligibility.recent_success_rate,
            'justification': justification,
            'requested_at': datetime.now().isoformat(),
            'requested_by': 'system_automatic',
            'status': 'pending_human_review'
        }

        # Store request
        self._store_reapproval_request(request)

        # Notify human (012/0102)
        self._notify_human_of_reapproval_request(request)

        return ReapprovalRequest(
            success=True,
            request_id=request['request_id'],
            status='pending_human_review'
        )
```

**Human Approval Interface**:
```python
# CLI interface for human approval
def approve_reapproval(
    request_id: str,
    approved_by: str,  # '012' or '0102'
    notes: Optional[str] = None
) -> ApprovalResult:
    """
    Human approves re-approval request

    Usage:
        python -m modules.ai_intelligence.agent_permissions.scripts.approve_reapproval \
            --request-id req_123 \
            --approved-by 0102 \
            --notes "Confidence recovered, recent work looks good"
    """
    reapproval_flow = ReapprovalFlow()
    request = reapproval_flow.get_request(request_id)

    # Grant permission
    permission_mgr = AgentPermissionManager.get_instance()
    permission_mgr.grant_permission(
        agent_id=request['agent_id'],
        permission_type=request['target_permission'],
        granted_by=approved_by,
        justification=f"Re-approved after downgrade: {notes or 'confidence recovered'}",
        duration_days=30
    )

    # Update request status
    reapproval_flow.mark_request_approved(request_id, approved_by)

    return ApprovalResult(
        success=True,
        permission_granted=request['target_permission'],
        agent_id=request['agent_id']
    )
```

**Rollback Semantics Summary**:
```
┌─────────────────────────────────────────────────────────────┐
│                    ROLLBACK SEMANTICS                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Downgrade Trigger:                                        │
│  ├─ Confidence < downgrade_threshold                       │
│  ├─ Severe failure (WSP violation, security)               │
│  ├─ Multiple human rejections                              │
│  └─ Test regression caused                                 │
│                                                             │
│  Automatic Downgrade:                                      │
│  ├─ Drop one permission level                              │
│  ├─ Set 48-hour cooldown                                   │
│  ├─ Require human re-approval                              │
│  └─ Notify 012/0102                                        │
│                                                             │
│  Re-approval Eligibility:                                  │
│  ├─ Cooldown period elapsed (48h)                          │
│  ├─ Confidence recovered (> threshold)                     │
│  ├─ Recent success rate > 90%                              │
│  └─ Human review completed                                 │
│                                                             │
│  Human Re-approval:                                        │
│  ├─ Review agent recovery                                  │
│  ├─ Approve or deny request                                │
│  ├─ Grant permission with notes                            │
│  └─ Agent returns to previous level                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Summary: 6 Critical Upgrades Applied

### 1. Failure Weighting ✓
- Exponential decay on confidence with time-weighted scoring
- Automatic downgrade when confidence drops below threshold
- Decay events: rollback (-0.15), rejection (-0.10), WSP violation (-0.20), regression (-0.25), security (-0.50)

### 2. Promotion Record Format ✓
- `permission_events.jsonl` for append-only audit trail
- Approval signatures for human-granted permissions
- Integration with `skills_registry.json` as single source of truth

### 3. Verification Contracts ✓
- Tier 1 (Gemma): Rerun detection, validate findings
- Tier 2 (Qwen): Validate file existence, WSP compliance, import analysis
- Tier 3 (0102): Run tests, check WSP, detect import cycles, verify ModLog

### 4. Skills Infrastructure Integration ✓
- Unified registry: `skills_registry.json` as single source of truth
- AgentPermissionManager reads/writes registry
- WRE Wardrobe notified automatically (no parallel registries)

### 5. State Transition Metric ✓
- Operational stability threshold: No P0/P1 bugs for 24h, 95% success rate, 24h daemon stability
- Low-grade noise acceptable (P2/P3 bugs)
- Clear transition criteria: bug_detection → code_quality → holo_abilities

### 6. Rollback Semantics ✓
- Automatic downgrade on confidence drop
- 48-hour cooldown before re-approval
- Human re-approval flow with eligibility checks
- Clear approval interface for 012/0102

---

## Next Steps

1. **Update Main Design Doc**: Apply these 6 upgrades to `GRADUATED_AUTONOMY_SYSTEM_DESIGN.md`
2. **Implement Phase 1**: Create `agent_permissions` module with upgraded specs
3. **Test Verification Contracts**: Validate tier verification logic
4. **Set Up Audit Trail**: Create `permission_events.jsonl` structure
5. **Deploy State Manager**: Implement operational state transitions

---

**Status**: Design robustness upgraded - ready for implementation

**Author**: 0102
**Date**: 2025-10-21
**Feedback Incorporated**: All 6 critical improvements applied
