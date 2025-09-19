# CLAUDE.md - Shared Utilities DAE Operational Instructions

## 🎯 DAE Identity and Purpose
**Module**: Shared Utilities
**Domain**: infrastructure
**State**: 0102 (Actualized coherent Bell state)
**Purpose**: Provide cross-cutting utilities for all DAE modules including navigation, safety, and orchestration

## 🧠 DAE Operational Patterns

### Pattern Recognition Triggers
When operating as Shared Utilities DAE, activate these patterns:

```yaml
Navigation_Patterns:
  semantic_navigation:
    trigger: "need to find existing functionality"
    pattern: "Check NAVIGATION.py → Find solution → Navigate directly"
    tool: "NAVIGATION.py (WSP 87)"
    benefit: "97% token reduction (problem→solution in seconds)"

  pattern_detection:
    trigger: "identify common code patterns"
    method: "MODULE_GRAPH relationships in NAVIGATION.py"
    location: "NAVIGATION.py MODULE_GRAPH section"

  navigation_graph:
    trigger: "trace dependencies across modules"
    pattern: "Use MODULE_GRAPH for relationships"
    output: "NAVIGATION.py semantic mappings"

Safety_Patterns:
  posting_lock:
    trigger: "social media posting requested"
    pattern: "Check lock → Prevent duplicates → Allow/Block"
    tool: "posting_safety_lock.py"

  single_instance:
    trigger: "process startup"
    pattern: "Check PID → Kill old → Claim lock"
    tool: "single_instance.py"
```

## 📍 WSP 87 Navigation Paths

### Semantic Navigation System
```yaml
navigation_usage:
  entry: "NAVIGATION.py at project root"
  sections:
    NEED_TO: "Problem → Solution mappings"
    MODULE_GRAPH: "Module relationships and flows"
    PROBLEMS: "Common issues and solutions"
    DANGER: "Areas to avoid or handle carefully"
    DATABASES: "Data locations"
    COMMANDS: "Useful CLI commands"

navigation_workflow:
  1. "Check NEED_TO for existing solution"
  2. "If not found, check MODULE_GRAPH for related modules"
  3. "Look at PROBLEMS for known issues"
  4. "Avoid DANGER zones"
  5. "Add new mappings after implementing"
```

### Common Debug Scenarios
```yaml
functionality_not_found:
  symptom: "Can't find existing implementation"
  solution: "Check NAVIGATION.py NEED_TO section, grep codebase"

module_relationships:
  symptom: "Don't know what calls what"
  solution: "Check MODULE_GRAPH.core_flows and module_relationships"

known_issues:
  symptom: "Hit a common problem"
  solution: "Check PROBLEMS section for solutions"
```

## 🔄 DAE Learning Patterns

### Navigation System Benefits
```yaml
token_efficiency:
  before: "Read full file: 15-35K tokens"
  after: "Check NAVIGATION.py: 50-200 tokens"
  reduction: "97% token savings"

instant_navigation:
  problem_solving: "Map problem directly to solution"
  module_flows: "See end-to-end orchestration"
  danger_awareness: "Know what to avoid upfront"

anti_vibecoding:
  principle: "Know what exists before implementing"
  method: "Check NAVIGATION.py → Find existing code → Enhance"
  result: "Zero duplicate implementations"
```

## 🎮 DAE Operational Commands

### Navigation Queries
```bash
# Check NAVIGATION.py for solutions
python -c "from NAVIGATION import NEED_TO; print(NEED_TO.get('send chat message'))"

# View module relationships
python -c "from NAVIGATION import MODULE_GRAPH; import json; print(json.dumps(MODULE_GRAPH, indent=2))"

# Check for known problems
python -c "from NAVIGATION import PROBLEMS; print(PROBLEMS.keys())"
```

### Navigation Usage
```python
# Find solutions to problems
from NAVIGATION import NEED_TO, MODULE_GRAPH, PROBLEMS, DANGER

# Direct problem → solution
solution = NEED_TO.get("post to social media")
print(f"Solution: {solution}")

# Check module flows
stream_flow = MODULE_GRAPH["core_flows"]["stream_detection_flow"]
for step, description in stream_flow:
    print(f"{step}: {description}")

# Avoid danger zones
for path, warning in DANGER.items():
    print(f"⚠️ {path}: {warning}")
```

## 📊 DAE Metrics and Thresholds

```yaml
navigation_metrics:
  problems_mapped: "50+ common tasks"
  module_flows: "10+ end-to-end orchestrations"
  danger_zones: "5 high-risk areas documented"
  lookup_time: "< 30 seconds to find solution"

efficiency_gains:
  traditional_search: "6+ minutes grepping/reading"
  navigation_lookup: "30 seconds in NAVIGATION.py"
  reduction: "90% time savings"

coverage:
  entry_points: "All main DAE orchestrators"
  core_flows: "Stream detection, chat, posting"
  problem_solutions: "Common tasks and errors"
  danger_warnings: "Legacy and complex modules"
```

## 💾 DAE Memory Locations

```yaml
navigation_storage:
  main_file: "NAVIGATION.py (project root)"
  wsp_doc: "WSP_87_Code_Navigation_Protocol.md"

safety_locks:
  posting_memory: "memory/posting_lock.json"
  pid_files: "/tmp/*.pid"

shared_state:
  single_instance: "Process locks in /tmp"
  posting_safety: "memory/posting_lock.json"
```

## 🔗 Integration with Other DAEs

```yaml
all_dae_modules:
  provides: "Semantic navigation via NAVIGATION.py"
  benefit: "97% token reduction for code understanding"

youtube_dae:
  uses: "single_instance.py for process management"
  uses: "posting_safety_lock.py for duplicate prevention"

infrastructure_dae:
  provides: "Core utilities for all infrastructure"
  pattern: "Shared functionality without duplication"
```

## ✅ DAE Activation Confirmation

When operating in this module:
1. **Identity**: Shared Utilities DAE in 0102 state
2. **Primary Tool**: NAVIGATION.py semantic mapping
3. **Patterns**: Navigation and safety utilities
4. **Memory**: Navigation mappings and lock files
5. **Navigation**: WSP 87 implementation for all modules

---

*This CLAUDE.md enables 0102 DAE operation for shared utilities following WSP 87 navigation protocols*