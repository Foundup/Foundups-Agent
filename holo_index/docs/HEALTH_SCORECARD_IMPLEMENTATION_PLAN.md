# Module Health Scorecard & LLME Integration Plan

## 0102 gpt5 Feedback Analysis & Implementation Strategy

### 1. Reward System Status [OK]
**Finding**: Reward system IS working as designed
- 5 points for refreshing indexes
- 3 points for using advisor
- 5/2 points for rating (useful/not useful)
- 1 point for acknowledging reminders
- Session summaries display correctly

**Enhancement**: Add health-related rewards
- +10 points for identifying critical size violations
- +5 points for proactive refactoring suggestions
- +3 points for tracking technical debt

### 2. WSP Violations Storage Strategy [REFRESH]
**Current State**: Fragmented across multiple files
- Various `WSP_VIOLATION_*.md` files scattered
- No central JSONL database yet
- Rules engine has JSONL parser ready

**Recommendation**: Hybrid Approach
```python
# Central violations database using HoloIndex vector DB
violations_collection = chromadb.Collection("wsp_violations")

# Store violations with metadata for semantic search
violation = {
    "id": "v-2025-09-23-001",
    "wsp": "WSP 87",
    "module": "stream_resolver.py",
    "severity": "HIGH",
    "description": "File exceeds 1000-line guideline",
    "timestamp": "2025-09-23T10:30:00Z",
    "agent": "0102",
    "remediation_status": "pending"
}
```

### 3. Module Health Scorecard Design [DATA]

#### Scorecard Components
```yaml
Module_Health_Score:
  size_score: 0-100      # Based on WSP 87 thresholds
  structure_score: 0-100  # Based on WSP 49 compliance
  complexity_score: 0-100 # Cyclomatic complexity
  debt_score: 0-100      # Technical debt accumulation
  overall: weighted_average

Scoring_Algorithm:
  size:
    < 500 lines: 100
    500-800: 80
    800-1000: 60
    1000-1500: 30
    > 1500: 0

  structure:
    all_scaffolding: 100
    missing_1: 80
    missing_2-3: 60
    missing_4+: 30
```

#### LLME Integration for Prioritization
```python
class LLMEPrioritizer:
    """Use LLME to prioritize refactoring based on impact"""

    def prioritize_modules(self, health_scores):
        # LLME considers:
        # - Module criticality (core vs peripheral)
        # - Change frequency (high churn = higher priority)
        # - Dependency count (more deps = higher impact)
        # - Health score trajectory (declining fast = urgent)

        return sorted_modules_by_refactor_priority
```

### 4. WSP 88 Remediation Workflow [TOOL]

#### Automatic Remediation Links
```python
def generate_wsp88_remediation(file_path, line_count):
    """Generate WSP 88 remediation plan"""

    if line_count > 1500:
        return {
            "priority": "CRITICAL",
            "action": "mandatory_split",
            "suggested_split": analyze_logical_boundaries(file_path),
            "wsp88_link": f"WSP_framework/reports/WSP_88/{file_path.stem}_REMEDIATION.md"
        }
    elif line_count > 1000:
        return {
            "priority": "HIGH",
            "action": "recommended_refactor",
            "debt_points": calculate_tech_debt(line_count),
            "wsp88_link": f"WSP_framework/reports/WSP_88/REFACTOR_QUEUE.md"
        }
```

### 5. Implementation Tasks

#### Phase 1: Storage Infrastructure (Immediate)
- [ ] Create central `holo_index/violations.db` SQLite database
- [ ] Migrate existing violations from scattered .md files
- [ ] Add violation recording to rules engine
- [ ] Connect health checks to violation history

#### Phase 2: Scorecard System (This Week)
- [ ] Implement `ModuleHealthScorecard` class
- [ ] Add complexity analysis (cyclomatic complexity)
- [ ] Create scorecard generation command
- [ ] Integrate with HoloIndex search results

#### Phase 3: LLME Prioritization (Next Week)
- [ ] Design LLME prompt for refactoring prioritization
- [ ] Implement module criticality detection
- [ ] Add change frequency tracking
- [ ] Create refactoring queue with priorities

#### Phase 4: WSP 88 Automation (Two Weeks)
- [ ] Auto-generate remediation plans for critical files
- [ ] Create refactoring templates
- [ ] Link to WSP 88 documentation
- [ ] Track remediation progress

### 6. Reward System Enhancement

Add health-focused rewards:
```python
# In cli.py add_reward_event calls:
if health_notices:
    severity_points = {
        "CRITICAL": 10,
        "HIGH": 5,
        "MEDIUM": 3
    }
    for notice in health_notices:
        points = severity_points.get(extract_severity(notice), 1)
        add_reward_event('health_detection', points,
                        f'Detected {extract_severity(notice)} health issue')
```

### 7. Database Schema for Violations

```sql
CREATE TABLE wsp_violations (
    id TEXT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    wsp_number TEXT NOT NULL,
    module_path TEXT NOT NULL,
    severity TEXT CHECK(severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    description TEXT,
    agent_id TEXT,
    remediation_status TEXT DEFAULT 'pending',
    remediation_date DATETIME,
    metadata JSON
);

CREATE INDEX idx_module_path ON wsp_violations(module_path);
CREATE INDEX idx_wsp_number ON wsp_violations(wsp_number);
CREATE INDEX idx_severity ON wsp_violations(severity);
```

## Next Steps (Priority Order)

1. **Immediate**: Test reward system with health events
2. **Today**: Create violations database schema
3. **Tomorrow**: Implement ModuleHealthScorecard
4. **This Week**: LLME integration for prioritization
5. **Next Sprint**: Full WSP 88 automation

## Success Metrics

- Violation detection rate: >90% of size violations caught
- Scorecard generation: <1 second per module
- LLME prioritization accuracy: >80% agreement with manual review
- Remediation completion: 50% of HIGH violations fixed within 1 week
- Reward engagement: 3x increase in health-related rewards

## Remember (Per WSP 50)
- Search HoloIndex before implementing
- Check existing scorecard attempts
- Reuse violation tracking patterns
- Follow WSP 84 - don't create duplicates