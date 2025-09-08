# WSP 10: DAE State Save Protocol
- **Status:** Active
- **Purpose:** To establish when and how DAEs must save their cube state to Git, ensuring backup recovery for refactoring operations and error scenarios.
- **Trigger:** Before any major DAE operation (cube refactoring, module consolidation, architectural changes); when DAE detects potential risk scenarios.
- **Input:** Current cube state, operation type, risk assessment.
- **Output:** Verified Git backup with rollback capability, documented state save in ModLog.
- **Responsible Agent(s):** All DAEs, ComplianceAgent for validation.

## 1. Overview

This protocol ensures that DAEs automatically save their functional cube state to Git before performing high-risk operations. This creates recoverable backup points, preventing data loss during refactoring, consolidation, or error scenarios. DAEs must know when to trigger state saves and follow the standardized backup procedure.

## 2. State Save Triggers

DAEs **MUST** trigger a state save before any of the following operations:

### 2.1 High-Risk Cube Operations
- **Module Consolidation**: When merging multiple modules into a unified cube
- **Cube Refactoring**: Major architectural changes to module relationships
- **Dependency Updates**: Significant changes to module dependencies
- **Memory Architecture Changes**: Modifications to WSP 60 memory structures

### 2.2 Risk-Based Triggers
- **Complexity Threshold**: When operation complexity score > 0.7 (from WSP 75 token analysis)
- **Multi-Module Impact**: Operations affecting 3+ modules simultaneously
- **Core Infrastructure Changes**: Modifications to foundational cube components

### 2.3 Error Recovery Triggers
- **Pre-Error Backup**: When DAE detects potential failure scenarios
- **Before Major Refactoring**: Automatic save before code cube cleanup operations

## 3. State Save Procedure

### 3.1 Pre-Save Verification
```bash
# DAE must verify clean state before saving
git status --porcelain
if [ $? -ne 0 ]; then
    echo "ERROR: Working directory not clean"
    exit 1
fi
```

### 3.2 Automated State Tagging
```bash
# Generate timestamped backup tag
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DAE_ID=$(echo $DAE_CUBE_NAME | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g')
TAG_NAME="dae-backup-${DAE_ID}-${TIMESTAMP}"

# Create annotated tag
git tag -a "$TAG_NAME" -m "DAE State Save: $DAE_CUBE_NAME
Operation: $OPERATION_TYPE
Risk Level: $RISK_LEVEL
Timestamp: $TIMESTAMP"
```

### 3.3 Documentation Requirements
DAE **MUST** document the state save in its ModLog:

```markdown
## [Timestamp] DAE State Save
**Tag:** dae-backup-[cube-name]-[timestamp]
**Operation:** [operation type]
**Risk Assessment:** [high/medium/low]
**Backup Files:** [list of critical files backed up]
**Recovery Point:** [git commit hash]
```

## 4. Recovery Procedures

### 4.1 Rollback Process
```bash
# List available DAE backups
git tag | grep "dae-backup-${DAE_ID}"

# Rollback to specific backup
git checkout "dae-backup-${DAE_ID}-20241201_143000"

# Create recovery branch
git checkout -b "recovery-${DAE_ID}-$(date +%Y%m%d)"
```

### 4.2 Post-Recovery Validation
After rollback, DAE must:
1. Run full test suite (WSP 5/6)
2. Verify module integrity (WSP 4)
3. Check dependency consistency (WSP 12)
4. Document recovery in ModLog

## 5. Integration with Other WSPs

### 5.1 WSP 2 Clean State Management
- State saves complement clean state snapshots
- Use clean state as baseline for DAE backups

### 5.2 WSP 34 Git Operations
- Follow conventional commit format for backup tags
- Integrate with branching strategy

### 5.3 WSP 60 Module Memory Architecture
- Backup includes memory state and persistent data
- Recovery restores memory architecture integrity

## 6. DAE Implementation Requirements

### 6.1 State Detection Logic
DAE must implement:
```python
def should_save_state(operation_type: str, complexity_score: float) -> bool:
    """Determine if operation requires state save"""
    high_risk_ops = ['refactor', 'consolidate', 'dependency_update']
    return (operation_type in high_risk_ops or
            complexity_score > 0.7 or
            self.risk_assessment() == 'high')
```

### 6.2 Automated Backup Integration
```python
async def execute_with_backup(self, operation_func, *args, **kwargs):
    """Execute operation with automatic state backup"""
    if self.should_save_state(operation_func.__name__, self.complexity_score):
        await self.save_state_to_git(operation_func.__name__)

    try:
        result = await operation_func(*args, **kwargs)
        return result
    except Exception as e:
        await self.rollback_to_last_backup()
        raise e
```

## 7. Monitoring and Compliance

### 7.1 Compliance Validation
- ComplianceAgent verifies DAE state save implementation
- Audit trail maintained in WSP_knowledge/logs/
- Regular compliance checks during FMAS validation (WSP 4)

### 7.2 Performance Tracking
- Track backup frequency and success rates
- Monitor recovery time and effectiveness
- Optimize backup procedures based on usage patterns

## 8. Emergency Recovery Protocol

### 8.1 Critical Failure Response
If DAE encounters critical failure:
1. **Immediate State Save**: Force save current state (even if corrupted)
2. **Emergency Tag Creation**: Use `emergency-` prefix for tags
3. **Notification**: Alert other DAEs in the ecosystem
4. **Isolation**: Prevent further operations until recovery

### 8.2 Ecosystem Coordination
- Failed DAE notifies ecosystem coordinator
- Backup DAEs assume critical functions
- Recovery coordinated across cube ecosystem

## 9. Future Enhancements

### 9.1 Intelligent Backup Selection
- AI-driven determination of what to backup
- Incremental backup strategies
- Compressed backup formats

### 9.2 Cross-Cube Recovery
- Backup sharing between related cubes
- Ecosystem-wide recovery orchestration
- Distributed backup strategies

This protocol ensures DAEs maintain recoverable state throughout their evolution, enabling safe refactoring and error recovery in the autonomous development ecosystem.