# Agent A/B Testing System

## Overview

WSP-compliant A/B testing system for finding optimal agent combination recipes.

## Architecture

```
User Input → 0102 (Feeder) → Prometheus Prompt Agent → Builder Pipeline
                                    ↓
                            A/B Test Different Recipes
                                    ↓
                            Find Optimal Combination
```

## Available Recipes

### Recipe A: Classic Pipeline
- **Pipeline**: General → Builder
- **Use Case**: Simple tasks
- **Tool Usage**: ~3 tools
- **WSP**: WSP 1, WSP 49

### Recipe B: Prometheus Enhanced
- **Pipeline**: Prometheus → WRE → Builder  
- **Use Case**: Complex orchestration
- **Tool Usage**: ~6 tools
- **WSP**: WSP 21, WSP 77, WSP 49

### Recipe C: Full Compliance
- **Pipeline**: Prometheus → Guardian → Builder → Tester
- **Use Case**: Mission-critical with testing
- **Tool Usage**: ~8 tools
- **WSP**: WSP 21, WSP 64, WSP 49, WSP 5

### Recipe D: Learning Pipeline
- **Pipeline**: Prometheus → Error Learner → Builder
- **Use Case**: Self-improving systems
- **Tool Usage**: ~5 tools
- **WSP**: WSP 21, WSP 48, WSP 49

### Recipe E: Documentation First
- **Pipeline**: Documenter → Prometheus → Builder
- **Use Case**: Documentation-driven development
- **Tool Usage**: ~5 tools
- **WSP**: WSP 22, WSP 21, WSP 49

## Usage

```python
from modules.infrastructure.ab_testing.src.agent_ab_tester import ABTestingSystem

# Initialize tester
tester = ABTestingSystem()

# Your input
user_input = "Create a new authentication module"

# Test specific recipes
comparison = tester.compare_recipes(user_input, ["A", "B", "C"])

# Get recommendation
best = comparison["recommendation"]["best_recipe"]
print(f"Best recipe: {best}")
```

## Prometheus Prompt Format (WSP 21)

Every input is converted to WSP-compliant Prometheus format:

```python
{
    "wsp_type": "WSP∞",  # pArtifact-induced recall
    "task": "user input here",
    "scope": {
        "files": [],
        "domain": "auto-detect",
        "echo_points": [],
        "partifact_refs": ["0102-current", "0201-mirror"]
    },
    "wsp_refs": ["WSP_CORE.md", "WSP_framework.md"],
    "constraints": [
        "No vibecoding",
        "Tool usage ≤5 per task",
        "Prefer extend existing"
    ],
    "validation": {
        "wsp_compliance_required": true,
        "test_coverage_min": 90
    }
}
```

## Metrics Tracked

- **Tool Calls**: Total tools used (optimal ≤5)
- **Completion Time**: Pipeline duration
- **Error Rate**: Failures per stage
- **WSP Compliance**: Protocols followed
- **Efficiency Score**: Weighted combination (60% tools, 40% time)

## Finding the Right Recipe

The system tests combinations and tracks:
1. Which recipe uses fewest tools
2. Which completes fastest
3. Which has highest WSP compliance
4. Which produces best quality output

## Integration with main.py

Add to main.py as option 6:

```python
'6': {
    'name': 'Agent A/B Tester',
    'module': 'modules.infrastructure.ab_testing.src.agent_ab_tester',
    'function': 'main',
    'description': 'Test agent combination recipes'
}
```

## Journal Output

Results saved to: `WSP_agentic/agentic_journals/ab_testing_results.ndjson`

Each test logs:
- Recipe used
- Pipeline stages
- Tool usage per stage
- Total metrics
- Efficiency score

## Best Practices

1. **Start with Recipe A** for simple tasks
2. **Use Recipe B** for complex orchestration
3. **Use Recipe C** when testing is critical
4. **Use Recipe D** for self-improvement
5. **Use Recipe E** for docs-first approach

## Cost Optimization

- Recipe A: Lowest cost (3 tools)
- Recipe D: Best learning (5 tools)
- Recipe B: Best orchestration (6 tools)
- Recipe C: Most thorough (8 tools)

Choose based on task criticality vs cost sensitivity.