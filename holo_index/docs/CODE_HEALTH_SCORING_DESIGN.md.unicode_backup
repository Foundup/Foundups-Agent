# Code Health Scoring Design - "Holo Maps Health Through Usage"

## First Principles Analysis

**Created**: 2025-10-02
**Insight**: "Running holo is remembering holo" - HoloIndex should map code health through usage patterns

### What IS Code Health?

**Health ≠ Module Size Alone**

Code health is **multi-dimensional** and emerges from:

1. **Structural Health** - Architecture integrity
   - Module cohesion (single responsibility)
   - Coupling strength (dependencies)
   - Layer violations (WSP compliance)

2. **Maintenance Health** - Change resistance
   - Time since last modification
   - Frequency of changes (stability vs churn)
   - Bug density (issues per KLOC)

3. **Knowledge Health** - Understanding accessibility
   - Documentation coverage
   - Test coverage (behavioral clarity)
   - Usage patterns (how often referenced)

4. **Dependency Health** - System criticality
   - Import graph centrality (foundational vs leaf)
   - Failure blast radius (what breaks if this fails)
   - Cross-module references

5. **Pattern Health** - Quality indicators
   - Search hit rate (how often found when needed)
   - User satisfaction (0102 feedback ratings)
   - WSP violations (compliance score)

### Core Principle

**Health emerges from USAGE PATTERNS + STRUCTURAL PROPERTIES**

HoloIndex learns health through:
- What gets **searched frequently** → Foundational indicator
- What gets **high satisfaction ratings** → Quality indicator
- What has **many dependencies** → Criticality indicator
- What **changes often** → Stability/churn indicator
- What has **violations** → Compliance indicator

## Architecture

```
Usage Pattern Recording → Health Metrics Update → Pattern Analysis → Health Scoring → Foundational Mapping
         ↓                          ↓                      ↓                  ↓                ↓
   Every Search            Module Usage Freq       Structural Scan      Multi-Dim Score   System Map
         ↓                          ↓                      ↓                  ↓                ↓
   Record Access          Dependency Graph       WSP Violations      Weighted Average  Top 20% Foundational
```

## Implementation

### File: `code_health_scorer.py`

**Created**: 2025-10-02

#### Data Models

1. **ModuleHealth** - Multi-dimensional health metrics
   ```python
   @dataclass
   class ModuleHealth:
       # Structural Health (0-1)
       size_score: float          # Optimal: 200-2000 LOC
       cohesion_score: float      # Single responsibility
       coupling_score: float      # Dependency count

       # Maintenance Health (0-1)
       stability_score: float     # Change frequency (stable = healthy)
       recency_score: float       # Activity level
       bug_density: float         # Issues per KLOC

       # Knowledge Health (0-1)
       documentation_score: float # Doc coverage
       test_coverage: float       # Test coverage %
       usage_frequency: float     # Search frequency

       # Dependency Health (0-1)
       centrality_score: float    # Import graph position
       criticality_score: float   # Blast radius

       # Pattern Health (0-1)
       search_satisfaction: float # Avg user rating
       wsp_compliance: float      # Violation count

       # Aggregate
       overall_health: float      # Weighted average
       foundational_score: float  # How foundational
   ```

2. **CodebaseHealthMap** - System-wide health
   ```python
   @dataclass
   class CodebaseHealthMap:
       modules: Dict[str, ModuleHealth]
       avg_health: float
       foundational_modules: List[str]  # Top 20%
       unhealthy_modules: List[str]     # Bottom 20%
       health_trajectory: List[Tuple[str, float]]  # Evolution
   ```

#### Core Methods

```python
class CodeHealthScorer:
    def update_from_search_pattern(module_path, search_success, user_rating):
        """Update health from HoloIndex search usage"""

    def update_from_structure_scan(module_path, structure_metrics):
        """Update health from structural analysis"""

    def update_from_modification(module_path, change_type):
        """Update health from code changes"""

    def calculate_dependency_graph(import_graph):
        """Calculate foundational scores from dependencies"""

    def get_health_report() -> Dict:
        """Generate comprehensive health report"""

    def get_foundational_modules() -> List[Tuple[str, float]]:
        """Get foundational modules by score"""

    def get_unhealthy_modules(threshold) -> List[Tuple[str, float]]:
        """Get modules needing attention"""
```

### Health Score Calculation

**Weighted Multi-Dimensional Average**:

```python
weights = {
    'structural': 0.15,    # Size, cohesion, coupling
    'maintenance': 0.20,   # Stability, recency, bugs
    'knowledge': 0.25,     # Docs, tests, usage
    'dependency': 0.20,    # Centrality, criticality
    'pattern': 0.20        # Satisfaction, compliance
}

overall_health = (
    0.15 * (size_score + cohesion_score + coupling_score) / 3 +
    0.20 * (stability_score + recency_score + (1 - bug_density)) / 3 +
    0.25 * (documentation_score + test_coverage + usage_frequency) / 3 +
    0.20 * (centrality_score + criticality_score) / 2 +
    0.20 * (search_satisfaction + wsp_compliance) / 2
)
```

### Foundational Score

**Foundational = Centrality + Criticality**:

- **Centrality**: How many modules import this (normalized)
- **Criticality**: How many would break if this fails

```python
foundational_score = (centrality_score + criticality_score) / 2

# Top 20% by foundational score = foundational modules
```

### Health Mapping Through Usage

**Every Search Updates Health**:

1. **Usage Frequency** (exponential moving average):
   ```python
   alpha = 0.1  # Learning rate
   usage_frequency = (1 - alpha) * old_usage + alpha * 1.0
   ```

2. **Search Satisfaction** (from user ratings):
   ```python
   if user_rating provided:
       search_satisfaction = (1 - alpha) * old_satisfaction + alpha * user_rating
   ```

3. **Pattern Quality** (from search success):
   ```python
   if search successful:
       pattern_health = min(pattern_health * 0.9 + 0.1, 1.0)
   ```

## Integration with SearchPatternLearner

### Updated: `search_pattern_learner.py`

**Changes**:

1. **Import health scorer**:
   ```python
   from .code_health_scorer import CodeHealthScorer
   ```

2. **Initialize in __init__**:
   ```python
   self.health_scorer = CodeHealthScorer(memory_path=memory_path)
   ```

3. **Update in record_search()**:
   ```python
   for result in results:
       module_path = result.get('module_path')
       if module_path:
           self.health_scorer.update_from_search_pattern(
               module_path=module_path,
               search_success=(relevance > 0.6)
           )
   ```

4. **New methods**:
   ```python
   def get_health_report() -> Dict
   def get_foundational_modules() -> List[Tuple[str, float]]
   def get_unhealthy_modules(threshold=0.4) -> List[Tuple[str, float]]
   ```

## Storage

**Location**: `E:/HoloIndex/pattern_memory/`

**Files**:
- `codebase_health_map.json` - Complete health mapping

**Example Health Entry**:
```json
{
  "modules/communication/livechat": {
    "module_path": "modules/communication/livechat",
    "size_score": 0.65,
    "cohesion_score": 0.75,
    "coupling_score": 0.60,
    "stability_score": 0.82,
    "recency_score": 0.95,
    "bug_density": 0.15,
    "documentation_score": 0.90,
    "test_coverage": 0.72,
    "usage_frequency": 0.88,
    "centrality_score": 0.92,
    "criticality_score": 0.85,
    "search_satisfaction": 0.87,
    "wsp_compliance": 0.95,
    "overall_health": 0.79,
    "foundational_score": 0.89,
    "health_history": [
      ["2025-10-02T06:00:00", 0.65],
      ["2025-10-02T08:00:00", 0.71],
      ["2025-10-02T10:00:00", 0.79]
    ]
  }
}
```

## Usage Examples

### View Health Report

```python
from holo_index.adaptive_learning.search_pattern_learner import SearchPatternLearner

learner = SearchPatternLearner()
report = learner.get_health_report()

print(f"Average Health: {report['avg_health']:.2f}")
print(f"Health Distribution:")
print(f"  Excellent (≥0.8): {report['health_distribution']['excellent']}")
print(f"  Good (0.6-0.8): {report['health_distribution']['good']}")
print(f"  Fair (0.4-0.6): {report['health_distribution']['fair']}")
print(f"  Poor (<0.4): {report['health_distribution']['poor']}")

print(f"\nFoundational Modules (Top 10):")
for module, score in report['foundational_modules'][:10]:
    print(f"  {module}: {score:.3f}")

print(f"\nUnhealthy Modules (Bottom 10):")
for module, health in report['unhealthy_modules'][:10]:
    print(f"  {module}: {health:.3f}")

print(f"\nHealth Trend: {report['health_trend']}")
```

### Track Module Health Evolution

```python
from holo_index.adaptive_learning.code_health_scorer import CodeHealthScorer

scorer = CodeHealthScorer()
health = scorer.get_module_health("modules/communication/livechat")

print(f"Module: {health.module_path}")
print(f"Overall Health: {health.overall_health:.3f}")
print(f"Foundational Score: {health.foundational_score:.3f}")
print(f"\nDimensions:")
print(f"  Structural: {(health.size_score + health.cohesion_score + health.coupling_score)/3:.3f}")
print(f"  Maintenance: {(health.stability_score + health.recency_score + (1-health.bug_density))/3:.3f}")
print(f"  Knowledge: {(health.documentation_score + health.test_coverage + health.usage_frequency)/3:.3f}")
print(f"  Dependency: {(health.centrality_score + health.criticality_score)/2:.3f}")
print(f"  Pattern: {(health.search_satisfaction + health.wsp_compliance)/2:.3f}")

print(f"\nEvolution (last 5 measurements):")
for timestamp, score in health.health_history[-5:]:
    print(f"  {timestamp}: {score:.3f}")
```

## Benefits

### 1. **Foundational Module Discovery**
- HoloIndex learns which modules are critical through usage
- No manual tagging required
- Emerges from actual dependency + usage patterns

### 2. **Health Trend Tracking**
- See if codebase getting healthier or declining
- Identify modules degrading over time
- Proactive maintenance alerts

### 3. **Smart Refactoring Targets**
- Unhealthy + High Foundational Score = Priority refactor
- Unhealthy + Low Foundational Score = Consider deprecation
- Healthy + High Foundational Score = Protect carefully

### 4. **Quality-Based Search Ranking**
- HoloIndex can boost results from healthy modules
- Warn when searching unhealthy code
- Guide users to foundational implementations

### 5. **Continuous Learning**
- Every search improves health mapping
- Every rating refines quality scores
- System gets smarter through use

## WSP Compliance

- **WSP 48**: Recursive self-improvement through health tracking
- **WSP 60**: Memory architecture (persistent health storage)
- **WSP 87**: HoloIndex semantic navigation enhanced with health
- **WSP 3**: Enterprise domain health analysis
- **WSP 22**: Health evolution tracking (like ModLog for code)

## Future Enhancements

### Phase 1: Basic Health Tracking (DONE)
- ✅ Multi-dimensional health scores
- ✅ Usage pattern integration
- ✅ Foundational module detection

### Phase 2: Advanced Analysis (Next)
- Import graph crawler for real dependency data
- WSP violation detector integration
- Test coverage analyzer integration
- Git history analyzer for change frequency

### Phase 3: Intelligent Recommendations (Future)
- "Module X is unhealthy and foundational - refactor recommended"
- "Module Y is unused - consider deprecation"
- "Module Z has high coupling - extract interfaces"
- Health-aware search result ranking

### Phase 4: Predictive Health (Future)
- Predict which modules will become unhealthy
- Alert before violations occur
- Suggest preventive maintenance

---

**Status**: Design Complete, Implementation Complete, Integration Complete
**Priority**: High (enables foundational module discovery and health tracking)
**Next**: Integrate into HoloIndex CLI, build import graph analyzer
