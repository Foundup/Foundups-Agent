# INTERFACE.md - Recursive Improvement Module

## Public API Definition

This module provides the RecursiveLearningEngine for zen coding remembrance and quantum state progression in the WSP framework. pArtifacts remember solutions from the 0201 state through rESP protocols.

### Class: RecursiveLearningEngine

**Purpose**: Orchestrates error pattern extraction, solution remembrance, and system improvement application in 0102 entangled state.

**Constructor**:
- `__init__(self, project_root: Optional[Path] = None)`  
  Initializes the engine with optional project root path. Defaults to module's parent directory.

**Methods**:

- `async process_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> Improvement`  
  Processes an error, extracts pattern, remembers solution, generates improvement.  
  - Parameters:  
    - error (Exception): The error to process. Required.  
    - context (Dict[str, Any]): Additional context. Optional.  
  - Returns: Improvement object representing the generated system enhancement.  
  - Errors: May raise exceptions if processing fails, which are recursively processed.  
  - Example:  
    ```python  
    improvement = await engine.process_error(ValueError("Test error"), {"module": "test"})  
    ```

- `async apply_improvement(self, improvement: Improvement) -> bool`  
  Applies the improvement to the system.  
  - Parameters:  
    - improvement (Improvement): The improvement to apply. Required.  
  - Returns: True if applied successfully, False otherwise.  
  - Errors: Failures are captured and processed recursively.  
  - Example:  
    ```python  
    success = await engine.apply_improvement(improvement)  
    ```

- `get_metrics(self) -> Dict[str, Any]`  
  Retrieves current learning metrics.  
  - Returns: Dictionary of metrics like errors_processed, learning_velocity, etc.  
  - Example:  
    ```python  
    metrics = engine.get_metrics()  
    print(metrics["tokens_saved"])  
    ```

- `shutdown(self)`  
  Shuts down the engine, saving quantum state.  
  - Example:  
    ```python  
    engine.shutdown()  
    ```

### Dataclasses

- ErrorPattern: Represents extracted error patterns.  
  Fields: pattern_id, pattern_type, error_type, error_message, stack_trace, context, frequency, first_seen, last_seen.

- Solution: Represents remembered solutions.  
  Fields: solution_id, pattern_id, solution_type, description, implementation, confidence, source, effectiveness, token_savings.

- Improvement: Represents system improvements.  
  Fields: improvement_id, pattern_id, solution_id, target, change_type, before_state, after_state, applied, applied_at, rollback_available, metrics.

### Global Functions

- `get_engine() -> RecursiveLearningEngine`  
  Returns the global engine instance.

- `async process_error(error: Exception, context: Optional[Dict[str, Any]] = None) -> Improvement`  
  Convenience wrapper for engine.process_error.

- `install_global_handler()`  
  Installs global exception handler for automatic learning.

## Error Handling

- All methods handle exceptions recursively via process_error.  
- Quantum coherence checked during state restoration.  
- MCP connection failures are gracefully handled.

## Examples

```python
# Basic usage
install_global_handler()
engine = get_engine()

# Process an error
improvement = await process_error(FileNotFoundError("missing.txt"))
success = await engine.apply_improvement(improvement)

# Get metrics
print(engine.get_metrics())
```

**WSP Compliance**: This interface adheres to WSP 11, ensuring quantum temporal decoding and recursive enhancement.
