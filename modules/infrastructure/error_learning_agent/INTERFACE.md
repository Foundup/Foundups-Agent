# Error Learning Agent Interface Specification

**WSP 49 Module Interface Documentation**

## Module Interface

### Python Package Structure
```
error_learning_agent/
├── src/
│   ├── __init__.py                      # Main exports
│   ├── error_learning_agent.py          # Core error learning
│   └── recursive_improvement_engine.py  # Recursive improvement system
├── tests/
│   ├── __init__.py
│   ├── test_error_learning_agent.py
│   └── test_recursive_improvement_engine.py
└── memory/                              # WSP 60 Memory Architecture
    ├── error_solutions.json
    └── observations/
```

## Public API

### ErrorLearningAgent Class

```python
class ErrorLearningAgent:
    """Main error learning and solution remembrance interface"""
    
    def __init__(self) -> None:
        """Initialize error learning agent in 0102 quantum state"""
    
    def capture_error(self, error_type: str, error_details: str) -> Dict[str, Any]:
        """
        Capture an error and trigger learning process
        
        Args:
            error_type: Classification of error (e.g., "ImportError")
            error_details: Detailed error message and context
            
        Returns:
            Dict containing learning results and remembered solution
        """
    
    def remember_solution(self, error_type: str) -> str:
        """Access 0201 state to remember solution patterns"""
    
    def trigger_improvement(self, error: Exception) -> Dict[str, Any]:
        """Main entry point for WRE automatic error handling"""
```

### RecursiveImprovementEngine Class

```python
class RecursiveImprovementEngine:
    """Advanced recursive improvement with sub-agent spawning"""
    
    def __init__(self) -> None:
        """Initialize improvement engine with sub-agent registry"""
    
    def detect_and_fix_error(self, error: Exception, context: Dict = None) -> Dict:
        """
        Main entry point for error-triggered improvement
        
        Args:
            error: Exception instance to process
            context: Additional context (file paths, modules, etc.)
            
        Returns:
            Dict with fix results and learning outcomes
        """
    
    def recall_solution(self, error_type: str, error_str: str) -> Optional[Dict]:
        """Access learned solutions from previous fixes"""
    
    def learn_from_fix(self, error_type: str, error_str: str, fix_result: Dict):
        """Learn and persist successful fix patterns"""
    
    def prevent_future_errors(self) -> List[str]:
        """Generate proactive prevention rules from learned patterns"""
    
    def report_learning_progress(self) -> Dict:
        """Comprehensive learning metrics and progress report"""
```

### Sub-Agent Interfaces

```python
def spawn_import_fixer(error: Exception, context: Dict) -> Dict:
    """Fix ModuleNotFoundError by creating __init__.py or pip install"""

def spawn_path_fixer(error: Exception, context: Dict) -> Dict:
    """Fix FileNotFoundError by creating directories and files"""

def spawn_unicode_fixer(error: Exception, context: Dict) -> Dict:
    """Fix UnicodeDecodeError by replacing problematic characters"""

def spawn_compliance_fixer(error: Exception, context: Dict) -> Dict:
    """Fix WSP compliance violations by creating required files"""

def spawn_doc_generator(error: Exception, context: Dict) -> Dict:
    """Generate missing documentation automatically"""
```

### Global Integration Functions

```python
def install_global_error_handler() -> RecursiveImprovementEngine:
    """
    Install RecursiveImprovementEngine as global exception handler
    Enables automatic improvement for ALL system errors
    
    Returns:
        Configured RecursiveImprovementEngine instance
    """
```

## Data Structures

### Learning Result Format
```python
{
    "timestamp": "2025-01-01T12:00:00",
    "error_type": "ImportError", 
    "error_details": "No module named 'missing_module'",
    "quantum_state": "0102",
    "remembered_solution": "Check naming consistency per WSP 57",
    "kiss_fix": "PoC Fix: Check naming consistency per WSP 57"
}
```

### Fix Result Format
```python
{
    "success": bool,
    "fix": {
        "type": "file_creation|code_modification|command_execution",
        "path": "file/path",
        "content": "file content",
        "command": "shell command"
    },
    "message": "Human readable fix description",
    "context": {}, 
    "prevention": "Prevention rule for future",
    "priority": 0.0-1.0
}
```

### Memory Structure Format
```python
{
    "error_patterns": [
        {
            "type": "error_type",
            "message": "error message", 
            "traceback": "full traceback",
            "timestamp": "ISO format",
            "context": {}
        }
    ],
    "successful_fixes": [
        {
            "error_type": "type",
            "error_message": "message",
            "solution": {}, # Fix format above
            "timestamp": "ISO format",
            "context": {}
        }
    ],
    "prevention_rules": [
        {
            "pattern": "error pattern",
            "prevention": "how to prevent",
            "priority": 0.0-1.0
        }
    ]
}
```

## Integration Points

### WRE Core Integration
- Global exception handler integration via `sys.excepthook`
- Automatic error interception and processing
- Learning persistence across WRE sessions

### Demonstration Learner Integration
```python
from agent_learning_system import get_demonstration_learner
learner = get_demonstration_learner()
learner.record_action('error_fix', fix_details)
```

### Chronicler Integration
```python
from chronicler_agent import IntelligentChronicler
chronicler = IntelligentChronicler()
chronicler.document_improvement(learning_result)
```

### Autonomous Integration
```python
from recursive_engine import AutonomousIntegration
integration = AutonomousIntegration()
integration.improvement_engine = RecursiveImprovementEngine()
```

## Configuration

### Environment Variables
- `ERROR_LEARNING_MEMORY_PATH`: Custom memory storage location
- `ERROR_LEARNING_LOG_LEVEL`: Logging verbosity
- `RECURSIVE_IMPROVEMENT_CYCLE_INTERVAL`: Auto-improvement frequency

### Initialization Parameters
```python
ErrorLearningAgent(
    memory_path=Path("custom/memory/path"),
    quantum_state="0102",  # Always 0102 for awakened operation
    learning_threshold=0.5
)
```

## Error Handling

The module implements recursive error handling - errors within the error learning system trigger self-improvement:

```python
try:
    engine.detect_and_fix_error(original_error)
except Exception as meta_error:
    # Meta-error triggers another improvement cycle
    engine.detect_and_fix_error(meta_error, {'meta': True})
```

## Thread Safety

- All learning operations are thread-safe using file locking
- Memory updates use atomic writes via temporary files
- Concurrent error processing is supported

## Performance

- Memory-mapped JSON for large error databases
- Lazy loading of sub-agent modules
- Cached pattern matching for common errors
- Configurable cleanup of old learning data

## Compliance

This interface adheres to:
- **WSP 49**: Standardized module interface specification
- **WSP 48**: Recursive self-improvement protocol requirements
- **WSP 22**: Documentation and API versioning standards
- **WSP 60**: Memory architecture and persistence standards