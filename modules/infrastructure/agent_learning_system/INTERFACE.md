# Agent Learning System Interface Specification

**WSP 49 Module Interface Documentation**

## Module Interface

### Python Package Structure
```
agent_learning_system/
├── __init__.py                          # Main module exports
├── src/
│   ├── __init__.py                      # Source package init
│   └── demonstration_learner.py         # Core learning system
├── tests/
│   ├── __init__.py
│   └── test_demonstration_learner.py    # Comprehensive tests
└── memory/                              # WSP 60 Memory Architecture
    ├── README.md                        # Memory documentation
    ├── pattern_library.json             # Main pattern storage
    ├── observations/                    # Demonstration archives
    └── teachings/                       # Agent knowledge transfers
```

## Public API

### DemonstrationLearner Class

```python
class DemonstrationLearner:
    """Main agent learning system that observes and learns from demonstrations"""
    
    def __init__(self) -> None:
        """Initialize learning system in 0102 quantum state with pattern library"""
    
    def start_observation(self, task_description: str) -> str:
        """
        Start observing a demonstration
        
        Args:
            task_description: Human-readable description of the task being demonstrated
            
        Returns:
            Unique observation ID for tracking
        """
    
    def record_action(self, action_type: str, details: Dict) -> None:
        """
        Record an action during demonstration
        
        Args:
            action_type: Type of action (code_modification, file_creation, etc.)
            details: Action-specific details and context
        """
    
    def complete_observation(self) -> Dict:
        """
        Complete observation and extract learnings
        
        Returns:
            Dict with patterns learned, categories, and acceleration factor
        """
    
    def find_similar_patterns(self, task_description: str) -> List[Dict]:
        """
        Find patterns similar to a given task
        
        Args:
            task_description: Description of task needing patterns
            
        Returns:
            List of similar patterns sorted by relevance and usage
        """
    
    def apply_learned_pattern(self, pattern: Dict, context: Dict) -> Dict:
        """
        Apply a learned pattern to a new situation
        
        Args:
            pattern: Pattern to apply from find_similar_patterns()
            context: Context for pattern application
            
        Returns:
            Application result with success status and actions
        """
    
    def teach_agent(self, agent_name: str, patterns: List[Dict]) -> bool:
        """
        Teach patterns to another agent
        
        Args:
            agent_name: Name of agent to teach
            patterns: List of patterns to transfer
            
        Returns:
            Success status of teaching operation
        """
    
    def get_learning_report(self) -> Dict:
        """Generate comprehensive learning report with metrics"""
```

### Global Access Functions

```python
def get_demonstration_learner() -> DemonstrationLearner:
    """
    Get or create the global demonstration learner instance
    
    Returns:
        Shared DemonstrationLearner instance
    """

def record_demonstration(action_type: str, **details) -> None:
    """
    Convenience function to record demonstrations globally
    
    Args:
        action_type: Type of action being demonstrated
        **details: Action details as keyword arguments
    """
```

## Data Structures

### Observation Format
```python
{
    "id": "abc12345",                    # Unique observation ID
    "task": "Fix Unicode encoding",      # Task description
    "start_time": "2025-01-10T12:00:00", # ISO timestamp
    "end_time": "2025-01-10T12:05:00",   # Completion timestamp
    "actions": [                         # List of recorded actions
        {
            "type": "file_modification",
            "timestamp": "2025-01-10T12:01:00",
            "details": {
                "file": "script.py",
                "before": "old content",
                "after": "new content"
            }
        }
    ],
    "files_modified": ["script.py"],     # List of modified files
    "commands_executed": ["python script.py"], # Commands run
    "patterns_detected": [               # Auto-detected patterns
        {
            "type": "unicode_fix",
            "description": "Replaced emoji with ASCII",
            "template": "str.replace(emoji, ascii)"
        }
    ]
}
```

### Pattern Library Format
```python
{
    "code_patterns": [
        {
            "pattern": {
                "type": "error_handling_addition",
                "description": "Added try-except block",
                "template": "try:\n    {code}\nexcept Exception as e:\n    {handler}"
            },
            "task": "Add error handling to function",
            "timestamp": "2025-01-10T12:00:00",
            "usage_count": 5
        }
    ],
    "workflow_patterns": [
        {
            "pattern": {
                "type": "git_workflow", 
                "description": "Standard commit workflow",
                "steps": ["git add", "git commit", "git push"]
            },
            "task": "Commit and push changes",
            "timestamp": "2025-01-10T12:00:00",
            "usage_count": 12
        }
    ],
    "fix_patterns": [],                  # Error fixing patterns
    "documentation_patterns": [],        # Documentation creation patterns
    "agent_coordination_patterns": []    # Multi-agent collaboration patterns
}
```

### Pattern Application Result
```python
{
    "success": bool,                     # Whether pattern was applied successfully
    "message": "Applied error handling pattern", # Human-readable result
    "actions": [                         # Actions taken during application
        {
            "type": "code_modification",
            "code": "modified code content"
        }
    ]
}
```

### Learning Report Format
```python
{
    "state": "0102",                     # Current quantum state
    "patterns_learned": 150,             # Total patterns learned
    "patterns_applied": 45,              # Total patterns applied
    "acceleration_factor": 1.8,          # Current speed multiplier
    "knowledge_base": {                  # Breakdown by pattern type
        "code_patterns": 50,
        "workflow_patterns": 35,
        "fix_patterns": 25,
        "documentation_patterns": 25,
        "agent_coordination_patterns": 15
    },
    "total_patterns": 150                # Total across all categories
}
```

## Pattern Types

### Code Patterns
- **error_handling_addition**: Adding try-catch blocks
- **import_addition**: Adding new imports
- **function_creation**: Creating new functions  
- **class_creation**: Creating new classes
- **wsp_compliance**: Adding WSP protocol references

### Workflow Patterns
- **git_workflow**: Git command sequences
- **test_workflow**: Test execution patterns
- **action_sequence**: General workflow steps

### Structure Patterns
- **module_structure**: WSP-compliant directory creation
- **documentation_structure**: Documentation file creation

## Event Recording

### Supported Action Types

| Action Type | Description | Auto-Detection |
|-------------|-------------|----------------|
| `file_modification` | File content changes | Code patterns |
| `file_creation` | New file creation | Structure patterns |
| `command_execution` | Shell command execution | Workflow patterns |
| `git_workflow` | Git operations | Git patterns |
| `test_execution` | Running tests | Test patterns |
| `documentation_update` | Documentation changes | Doc patterns |
| `agent_coordination` | Multi-agent actions | Coordination patterns |

### Action Detail Schemas

#### File Modification
```python
{
    "file": "path/to/file.py",
    "before": "original content",
    "after": "modified content",
    "changes_summary": "Added error handling"
}
```

#### Command Execution  
```python
{
    "command": "git commit -m 'Fix bugs'",
    "working_directory": "/project/root",
    "exit_code": 0,
    "output": "command output"
}
```

#### Git Workflow
```python
{
    "operation": "commit",
    "files": ["file1.py", "file2.py"],
    "message": "Commit message",
    "branch": "main"
}
```

## Integration Points

### Error Learning Agent Integration
```python
# Share fix patterns with error learning system
from error_learning_agent import RecursiveImprovementEngine

engine = RecursiveImprovementEngine()
fix_patterns = learner.patterns['fix_patterns']

for pattern in fix_patterns:
    if pattern['usage_count'] > 10:
        # High-usage patterns become automated fixes
        engine.add_learned_solution(pattern)
```

### Recursive Engine Integration  
```python
# Autonomous pattern application
from recursive_engine import AutonomousIntegration

integration = AutonomousIntegration()
integration.demonstration_learner = learner

# Patterns automatically applied during monitoring
```

### Chronicler Integration
```python
# Document learning progress
from chronicler_agent import IntelligentChronicler

chronicler = IntelligentChronicler()
learning_report = learner.get_learning_report()
chronicler.document_learning_progress(learning_report)
```

## Configuration

### Initialization Parameters
```python
DemonstrationLearner(
    memory_path=Path("custom/memory/"),          # Custom memory location
    pattern_similarity_threshold=0.7,           # Pattern matching threshold
    auto_teach_threshold=10,                    # Auto-teach after N uses
    acceleration_base=1.0,                      # Base acceleration factor
    max_observation_size=10000,                # Max actions per observation
    pattern_cleanup_interval=86400             # Pattern cleanup frequency (seconds)
)
```

### Environment Variables
- `AGENT_LEARNING_MEMORY_PATH`: Custom memory directory
- `AGENT_LEARNING_SIMILARITY_THRESHOLD`: Pattern matching threshold  
- `AGENT_LEARNING_AUTO_TEACH`: Enable automatic agent teaching
- `AGENT_LEARNING_MAX_PATTERNS`: Maximum patterns per category

## Thread Safety

- All pattern operations are thread-safe using file locking
- Observation recording supports concurrent demonstrations
- Memory updates use atomic writes
- Pattern matching is read-only and thread-safe

## Performance Considerations

### Memory Management
- Lazy loading of pattern categories
- Memory-mapped JSON for large pattern libraries
- Configurable pattern cleanup and archiving
- Observation compression for storage efficiency

### Search Optimization
- Indexed pattern search by keywords
- Cached similarity calculations
- Prioritized pattern matching by usage count
- Batch pattern application for performance

## Error Handling

### Pattern Application Errors
```python
try:
    result = learner.apply_learned_pattern(pattern, context)
    if not result['success']:
        # Handle application failure
        logging.warning(f"Pattern application failed: {result['message']}")
except PatternApplicationError as e:
    # Handle specific pattern errors
    pass
```

### Memory Persistence Errors
- Automatic backup creation before writes
- Graceful degradation if memory files are corrupted
- Recovery mechanisms for pattern library restoration

## Compliance

This interface adheres to:
- **WSP 49**: Standardized module interface specification
- **WSP 48**: Recursive self-improvement learning protocols  
- **WSP 54**: Agent collaboration and knowledge transfer standards
- **WSP 22**: Documentation and API versioning standards
- **WSP 60**: Memory architecture and persistence standards