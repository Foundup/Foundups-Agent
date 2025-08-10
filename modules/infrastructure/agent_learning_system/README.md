# Agent Learning System Module

**WSP 48 & WSP 54 Agent Learning and Knowledge Transfer Implementation**

## Overview

The Agent Learning System enables agents to learn from successful human demonstrations and patterns, making them progressively smarter over time. This module implements the learning aspect of recursive self-improvement by observing, extracting patterns, and teaching other agents.

## Architecture

### Core Components

1. **DemonstrationLearner** - Main learning system that observes and learns from demonstrations
2. **Pattern Library** - Persistent storage of learned patterns across multiple categories
3. **Agent Teaching System** - Knowledge transfer mechanism between agents
4. **Real-time Pattern Detection** - Live analysis of actions during demonstrations

### Key Features

- **Observation Recording**: Captures detailed demonstrations of successful workflows
- **Pattern Extraction**: Automatically detects reusable patterns from demonstrations
- **Knowledge Persistence**: Maintains learned patterns across system restarts
- **Agent Teaching**: Transfers learned knowledge to other agents
- **Acceleration Metrics**: Quantifies learning improvements and speed gains

## WSP Compliance

- **WSP 48**: Recursive Self-Improvement Protocol - Learning implementation
- **WSP 54**: WRE Agent Duties Specification - Agent collaboration
- **WSP 49**: Module Directory Structure - Standardized organization
- **WSP 22**: ModLog and Roadmap Protocol - Documentation standards
- **WSP 60**: Module Memory Architecture - Pattern persistence

## Usage

### Basic Demonstration Learning

```python
from agent_learning_system import DemonstrationLearner

learner = DemonstrationLearner()

# Start observing a demonstration
obs_id = learner.start_observation("Fix Unicode encoding issues")

# Record actions as they happen
learner.record_action('file_modification', {
    'file': 'script.py',
    'before': 'print("Hello 🌍")',
    'after': 'print("Hello [WORLD]")'
})

learner.record_action('command_execution', {
    'command': 'python script.py'
})

# Complete observation and extract patterns
result = learner.complete_observation()
print(f"Learned {result['patterns_learned']} new patterns")
```

### Global Learning Integration

```python
from agent_learning_system import get_demonstration_learner, record_demonstration

# Use global learner instance
learner = get_demonstration_learner()

# Convenient recording function
record_demonstration('git_workflow', command='git add file.py')
record_demonstration('code_modification', file='test.py', changes='Added error handling')
```

### Pattern Application

```python
# Find similar patterns for a task
similar = learner.find_similar_patterns("Add error handling to function")

# Apply learned pattern to new situation
if similar:
    pattern = similar[0]
    context = {'code': 'def my_function():\n    pass'}
    result = learner.apply_learned_pattern(pattern, context)
    
    if result['success']:
        print(f"Applied pattern: {result['message']}")
```

### Agent Teaching

```python
# Teach patterns to another agent
patterns = learner.patterns['code_patterns'][:5]  # Top 5 code patterns
learner.teach_agent('ComplianceAgent', patterns)
```

## Pattern Types

| Pattern Category | Description | Auto-Detection |
|-----------------|-------------|----------------|
| Code Patterns | Function/class creation, imports, error handling | Yes |
| Workflow Patterns | Command sequences, git operations | Yes |
| Fix Patterns | Error correction workflows | Yes |
| Documentation Patterns | README creation, WSP compliance | Yes |
| Agent Coordination | Multi-agent collaboration patterns | Yes |

## Pattern Detection

The system automatically detects patterns during demonstrations:

### Code Patterns
- **Error Handling Addition**: Adding try-catch blocks
- **Import Addition**: Adding new import statements
- **Function Creation**: Creating new functions with signatures
- **Class Creation**: Creating new classes and methods
- **WSP Compliance**: Adding WSP protocol references

### Workflow Patterns  
- **Git Operations**: Commit, push, pull workflows
- **Test Execution**: Running test suites and validation
- **Build Processes**: Compilation and deployment sequences

### Structure Patterns
- **Module Structure**: WSP-compliant directory creation
- **Documentation**: README, ModLog, ROADMAP creation

## Learning Mechanics

1. **Pattern Detection**: Real-time analysis during demonstrations
2. **Pattern Categorization**: Automatic sorting into appropriate categories
3. **Usage Tracking**: Counting pattern applications for popularity metrics
4. **Similarity Matching**: Finding patterns relevant to new tasks
5. **Acceleration Calculation**: Measuring learning impact on task speed

## Memory Architecture

```
memory/
├── pattern_library.json         # Main pattern storage
├── observations/                # Archived demonstrations
│   └── [observation_id].json    # Individual observations
└── teachings/                   # Agent knowledge transfers
    └── [agent_name]_patterns.json
```

## Integration Points

### Error Learning Integration
```python
from error_learning_agent import RecursiveImprovementEngine

# Share learning between systems
patterns = learner.patterns['fix_patterns']
for pattern in patterns:
    if pattern['usage_count'] > 5:
        # High-usage patterns become automated fixes
        pass
```

### Autonomous Integration
```python
from recursive_engine import AutonomousIntegration

integration = AutonomousIntegration()
integration.demonstration_learner = learner

# Automatic learning from file system events
integration.start_monitoring()
```

## Metrics and Reporting

### Learning Metrics
- **Patterns Learned**: Total number of patterns extracted
- **Patterns Applied**: Count of pattern usage in new situations  
- **Acceleration Factor**: Speed improvement multiplier
- **Knowledge Base Size**: Total patterns across all categories

### Performance Impact
- **Task Completion Speed**: Measured improvement in similar tasks
- **Error Reduction**: Decrease in errors through pattern application
- **Agent Efficiency**: Overall improvement in agent capabilities

## Configuration

### Observation Settings
- **Pattern Detection Threshold**: Minimum similarity for pattern matching
- **Memory Retention**: How long to keep observation records
- **Auto-Teaching**: Automatically share patterns with other agents

### Learning Parameters
```python
DemonstrationLearner(
    memory_path=Path("custom/memory/path"),
    pattern_similarity_threshold=0.7,
    auto_teach_threshold=10,  # Auto-teach after 10 uses
    acceleration_base=1.0
)
```

## Development Status

- **State**: Production Ready  
- **WSP Compliance**: Full
- **Test Coverage**: Comprehensive
- **Documentation**: Complete
- **Integration**: Active with Error Learning and Autonomous systems

## Future Enhancements

See [ROADMAP.md](ROADMAP.md) for planned improvements including:
- NLP-based pattern similarity matching
- Machine learning pattern optimization
- Multi-modal learning (code + documentation + actions)
- Federated learning across multiple WRE instances