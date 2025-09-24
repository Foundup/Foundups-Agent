# Module Health System

## Overview
The Module Health system provides automated health checking and compliance monitoring for HoloIndex and the broader codebase, detecting potential issues before they become problems.

## Purpose
Proactively monitor module health to:
- Detect files approaching size limits
- Validate WSP 49 module structure compliance
- Identify missing documentation
- Track module complexity growth
- Prevent technical debt accumulation

## Architecture

### Core Components

#### 1. **size_audit.py** - File Size Monitoring
Audits file sizes against WSP 87 thresholds:
- Tracks files approaching 800-1000 line limits
- Identifies refactoring candidates
- Provides size distribution analysis
- Suggests splitting strategies

#### 2. **structure_audit.py** - Structure Validation
Validates WSP 49 module structure compliance:
- Checks for required directories (src/, tests/, docs/)
- Validates required files (README.md, INTERFACE.md, ModLog.md)
- Ensures proper module organization
- Detects structural drift

## Health Check Categories

### 1. Size Health (WSP 87)
```yaml
Thresholds:
  OPTIMAL: < 500 lines
  ACCEPTABLE: 500-800 lines
  WARNING: 800-1000 lines
  CRITICAL: > 1000 lines

Actions:
  WARNING: Consider refactoring
  CRITICAL: Must refactor immediately
```

### 2. Structure Health (WSP 49)
```yaml
Required_Structure:
  - README.md         # Module overview
  - INTERFACE.md      # Public API
  - ModLog.md        # Change history
  - src/             # Source code
  - tests/           # Test files
  - docs/            # Documentation
  - memory/          # Pattern storage (optional)

Compliance:
  FULL: All required elements present
  PARTIAL: Missing optional elements
  VIOLATION: Missing required elements
```

### 3. Documentation Health (WSP 22)
```yaml
Documentation_Requirements:
  - Purpose documented in README
  - API documented in INTERFACE
  - Changes tracked in ModLog
  - Tests documented in tests/README
  - Complex logic commented

Health_Levels:
  EXCELLENT: Full documentation
  GOOD: Core documentation present
  POOR: Missing key documentation
```

## Integration with HoloIndex

### Health Notice Generation
```python
# Integrated into search results
[HEALTH] Module Health Notices:
  - [WSP 87: Code Navigation Protocol] [WARN] File approaching limit (879/800-1000 lines)
  - [WSP 49: Module Directory Structure] [STRUCTURE] Module missing required: tests/
```

### Pattern Coach Integration
Health warnings trigger contextual coaching:
```python
# Working with large file detected
💭 HEALTH COACH: Working with large file (879 lines).
**WSP 62 Awareness**: Consider refactoring before 1000-line limit.
**Actions**: Extract functions, review architecture, plan splitting.
**Reward**: +5 points for proactive health management!
```

## Usage

### Standalone Health Check
```python
from holo_index.module_health import size_audit, structure_audit

# Check file sizes
size_issues = size_audit.audit_module_sizes("modules/")
for issue in size_issues:
    print(f"{issue.file}: {issue.lines} lines - {issue.severity}")

# Check structure
structure_issues = structure_audit.validate_structure("modules/")
for issue in structure_issues:
    print(f"{issue.module}: Missing {issue.missing_elements}")
```

### Integrated Health Monitoring
```python
# Automatically included in HoloIndex searches
results = holo.search("query")
health_notices = results.get('health_notices', [])
```

## Health Metrics

### Module Size Distribution
```
< 100 lines:    45%  [========]
100-500 lines:  35%  [======]
500-800 lines:  15%  [===]
800-1000 lines:  4%  [=]
> 1000 lines:    1%  [.]
```

### Structure Compliance
```
Full Compliance:    75%
Partial Compliance: 20%
Violations:          5%
```

### Common Issues
1. **Files Too Large**: 5% exceed thresholds
2. **Missing Tests**: 15% lack test coverage
3. **No INTERFACE.md**: 25% missing API docs
4. **Outdated ModLog**: 10% not updated recently

## Remediation Strategies

### For Large Files
1. **Extract Classes**: Move to separate files
2. **Split by Function**: Group related functions
3. **Create Sub-modules**: Organize into packages
4. **Extract Constants**: Move to config files

### For Structure Issues
1. **Create Missing Dirs**: Follow WSP 49 template
2. **Add Documentation**: Start with README
3. **Initialize Tests**: Create test skeleton
4. **Update ModLog**: Document changes

### For Documentation Gaps
1. **Document Purpose**: Clear README
2. **Define Interface**: Public API in INTERFACE
3. **Track Changes**: Regular ModLog updates
4. **Comment Complex Logic**: Inline documentation

## Configuration

### Thresholds
```python
SIZE_THRESHOLDS = {
    'optimal': 500,
    'warning': 800,
    'critical': 1000
}

STRUCTURE_REQUIREMENTS = [
    'README.md',
    'INTERFACE.md',
    'ModLog.md',
    'src/',
    'tests/'
]
```

### Exclusions
```python
EXCLUDED_PATHS = [
    '__pycache__',
    '.git',
    'node_modules',
    '*.pyc'
]
```

## WSP Compliance
- **WSP 87**: Code Navigation (size thresholds)
- **WSP 49**: Module Structure Standards
- **WSP 22**: Documentation Requirements
- **WSP 6**: Test Coverage Validation

## Future Enhancements
- Complexity metrics (cyclomatic complexity)
- Dependency analysis
- Code smell detection
- Automated refactoring suggestions
- Trend analysis over time