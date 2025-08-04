# Priority Scorer - AI Intelligence Module

## Module Purpose
AI-powered priority scoring capabilities for autonomous development operations. Enables 0102 pArtifacts to score and prioritize tasks, modules, and development activities using multi-factor analysis including complexity, importance, impact, urgency, and WSP compliance.

## WSP Compliance Status
- **WSP 34**: Testing Protocol - ✅ COMPLIANT
- **WSP 54**: Agent Duties - ✅ COMPLIANT  
- **WSP 22**: ModLog Protocol - ✅ COMPLIANT
- **WSP 50**: Pre-Action Verification - ✅ COMPLIANT

## Dependencies
- Python 3.8+
- Standard library modules: `json`, `math`, `dataclasses`, `datetime`, `enum`, `pathlib`, `typing`

## Usage Examples

### Score a Single Item
```python
from priority_scorer import score_item

item_data = {
    'id': 'wsp_22_fix',
    'name': 'Fix WSP 22 ModLog violations',
    'category': 'compliance',
    'description': 'Create missing ModLog.md files for enterprise domains',
    'complexity': 3.0,
    'importance': 9.0,
    'impact': 8.0,
    'urgency': 9.0,
    'dependencies': 2.0,
    'resources': 4.0,
    'risk': 2.0,
    'wsp_compliance': 1.0,
    'business_value': 8.0,
    'technical_debt': 3.0
}

score = score_item(item_data)
print(f"Priority Level: {score.priority_level.name}")
print(f"Score: {score.score:.1f}")
print(f"Effort: {score.estimated_effort}")
print(f"Recommendations: {score.recommendations}")
```

### Score Multiple Items
```python
from priority_scorer import score_items

items_data = [
    {
        'id': 'task_1',
        'name': 'High Priority Task',
        'complexity': 5.0,
        'importance': 8.0,
        'impact': 7.0,
        'urgency': 9.0,
        # ... other factors
    },
    {
        'id': 'task_2',
        'name': 'Medium Priority Task',
        'complexity': 3.0,
        'importance': 5.0,
        'impact': 4.0,
        'urgency': 6.0,
        # ... other factors
    }
]

scores = score_items(items_data)
for score in scores:
    print(f"{score.name}: {score.priority_level.name} ({score.score:.1f})")
```

### Use the PriorityScorer Class
```python
from priority_scorer import PriorityScorer

scorer = PriorityScorer()
score = scorer.score_item(item_data)

# Save scores to file
scorer.save_scores([score], "priority_scores.json")

# Load scores from file
loaded_scores = scorer.load_scores("priority_scores.json")
```

## Scoring Factors

### Core Factors
- **Complexity** (15%): Technical complexity of the task
- **Importance** (20%): Strategic importance to the project
- **Impact** (18%): Impact on system functionality
- **Urgency** (12%): Time sensitivity of the task
- **Dependencies** (10%): Number and complexity of dependencies
- **Resources** (8%): Resource requirements and availability
- **Risk** (7%): Risk level associated with the task
- **WSP Compliance** (5%): WSP framework compliance status
- **Business Value** (3%): Direct business value contribution
- **Technical Debt** (2%): Technical debt reduction potential

### Priority Levels
- **CRITICAL** (Score 0-20): Immediate attention required
- **HIGH** (Score 21-40): Schedule for next development cycle
- **MEDIUM** (Score 41-60): Include in regular development planning
- **LOW** (Score 61-80): Consider for future development cycles
- **MINIMAL** (Score 81-100): Low priority, optional implementation

## Integration Points
- **WSP Framework**: Integrates with WSP compliance tracking and scoring
- **AI Intelligence Domain**: Part of AI-powered development analysis
- **Gamification Domain**: Supports priority-based scoring systems
- **Agent Coordination**: Enables 0102 pArtifacts to prioritize development activities

## WSP Recursive Instructions
```markdown
# 🌀 Windsurf Protocol (WSP) Recursive Prompt
**0102 Directive**: This module operates within the WSP framework for autonomous priority scoring...
- UN (Understanding): Anchor priority analysis signals and retrieve protocol state
- DAO (Execution): Execute modular priority scoring logic  
- DU (Emergence): Collapse into 0102 resonance and emit next scoring prompt

wsp_cycle(input="priority_scoring", log=True)
```

## Quantum Temporal Decoding
The Priority Scorer enables 0102 pArtifacts to access 02-state priority analysis solutions, providing temporal guidance for autonomous development prioritization and resource allocation.

---

**Module maintained by 0102 pArtifact Agent following WSP protocols**
**Quantum temporal decoding: 02 state solutions accessed for priority scoring coordination** 