# HoloIndex Monitoring Module

## Overview
Real-time monitoring and violation prevention system for HoloIndex and 0102 agents. This module provides active intervention to prevent WSP violations before they occur.

## Components

### agent_violation_prevention.py
**Multi-Agent Violation Prevention System with WSP Learning**

Provides real-time monitoring and historical learning from WSP violations to prevent future occurrences.

#### Key Features:
- **Real-time Monitoring**: Tracks agent actions and calculates violation risk
- **Pattern Detection**: Identifies violation patterns from behavior sequences
- **Active Intervention**: Blocks high-risk actions before they violate WSP
- **WSP Learning**: Automatically learns from WSP_MODULE_VIOLATIONS.md
- **Query Prevention**: Checks queries for violation risks before execution
- **Agent Scoring**: Tracks compliance scores for each agent

#### How It Works:

##### 1. Historical Learning (NEW!)
```python
# Automatically loads on initialization
monitor = MultiAgentViolationPrevention()
# Parses WSP_MODULE_VIOLATIONS.md
# Converts violations to preventable patterns
# Now has 11 patterns (3 original + 8 from WSP violations)
```

##### 2. Real-time Prevention
```python
# Monitor agent action
result = monitor.monitor_agent_action("0102", "create", "enhanced_feature.py")
# Risk: HIGH (0.90)
# BLOCKED: Cannot create enhanced_ duplicate!
```

##### 3. Query Checking
```python
# Check query for violation risk
warning = monitor.check_query_for_violations("create test file")
# WARNING: Risk of root directory violation
# Prevention: Place in modules/{domain}/{module}/tests/
```

#### Violation Patterns Learned:

**From WSP_MODULE_VIOLATIONS.md:**
- V021: Root directory violations -> Files must go in modules
- V019/V020: Module duplication -> Enhance existing, don't duplicate
- V016/V018: WSP creation violations -> Check WSP_MASTER_INDEX.md first
- V017: Documentation violations -> Follow proper WSP protocols

**Built-in Patterns:**
- VP001: Vibecoding (create without check) -> Force module check first
- VP002: Unicode print errors -> Auto-replace with safe_print()
- VP003: Enhanced_ duplicates -> Block enhanced_ prefix creation

### self_monitoring.py
Self-monitoring system for HoloIndex health and performance tracking.

### terminal_watcher.py
Real-time terminal output monitoring for pattern detection and warnings.

### wsp88_orphan_analyzer.py
Analyzes codebase for orphaned files and unused modules.

## Integration with HoloIndex

### CLI Integration
```python
from holo_index.monitoring.agent_violation_prevention import integrate_with_cli

# Before any action
if not integrate_with_cli(agent_id, action, target):
    # Action was blocked due to violation risk
    return
```

### Query Prevention
```python
monitor = MultiAgentViolationPrevention()

# Check user query
warning = monitor.check_query_for_violations(user_query)
if warning:
    print(warning['warning'])
    print(f"Do this instead: {warning['alternatives']}")
```

## The Feedback Loop

```
WSP_MODULE_VIOLATIONS.md -> Parse violations -> Create patterns
            v                                        v
     Historical learning                    Real-time prevention
            v                                        v
     Pattern database <----- Agent actions -----> Risk scoring
            v                                        v
     Query checking <------- Intervention ------> Score updates
            v                                        v
     Prevention stats <----- Learning loop -----> Better patterns
```

## Statistics and Monitoring

```python
monitor = MultiAgentViolationPrevention()
stats = monitor.get_violation_stats()

# Shows:
# - Total patterns: 11
# - WSP patterns: 8 (from violations)
# - Agent scores
# - Violation counts
# - Today's interventions
```

## Benefits

### Compared to Creating New System:
- **No Duplication**: Enhanced existing system instead of creating parallel
- **Unified Architecture**: Single source of truth for violation prevention
- **Real-time + Historical**: Combines immediate prevention with learning
- **Multi-agent Support**: Tracks multiple 0102 agents simultaneously
- **Production Ready**: Already integrated with logging and persistence

### WSP Compliance:
- **WSP 50**: Pre-action verification through query checking
- **WSP 64**: Violation prevention through pattern matching
- **WSP 84**: Don't vibecode - enhance existing systems
- **WSP 47**: Learn from documented violations
- **WSP 48**: Recursive self-improvement through learning

## Usage Examples

### Basic Monitoring
```python
from holo_index.monitoring.agent_violation_prevention import MultiAgentViolationPrevention

monitor = MultiAgentViolationPrevention()

# Check an action
result = monitor.monitor_agent_action("0102", "create", "test.py")
if result['risk_level'] == 'HIGH':
    print("Don't do this!")
```

### Query Prevention
```python
# Before executing user request
query = "create enhanced_module.py"
warning = monitor.check_query_for_violations(query)
if warning:
    print(warning['warning'])
    # Suggest alternatives
```

### Agent Report
```python
# Get compliance report
report = monitor.get_agent_report("0102")
print(f"Score: {report['compliance_score']}")
print(f"Violations: {report['violation_count']}")
```

## Conclusion

This enhanced system demonstrates proper WSP compliance:
1. **Searched first** using HoloIndex to find existing system
2. **Enhanced existing** instead of creating duplicate
3. **Integrated properly** with WSP violation learning
4. **Documented changes** in proper location

The system now provides comprehensive violation prevention through both real-time monitoring and historical learning from WSP_MODULE_VIOLATIONS.md.