# WRE Master Orchestrator - Interface Specification

Per WSP 11 (WRE Standard Command Protocol)

## Core Interface

### WREMasterOrchestrator

```python
class WREMasterOrchestrator:
    """THE Master Orchestrator per WSP 46"""
    
    def __init__(self):
        """Initialize with pattern memory and WSP validation"""
        
    def recall_pattern(self, operation_type: str) -> Pattern:
        """
        Recall pattern from memory per WSP 60
        Args:
            operation_type: Type of operation (e.g., "module_creation")
        Returns:
            Pattern object with WSP chain and token cost
        """
        
    def execute(self, task: Dict) -> Any:
        """
        Execute task through pattern recall per WSP 46
        Args:
            task: Dict with 'type' and optional 'plugin' keys
        Returns:
            Result of pattern application
        """
        
    def register_plugin(self, plugin: OrchestratorPlugin):
        """
        Register orchestrator plugin per WSP 65
        Args:
            plugin: OrchestratorPlugin instance
        """

    def register_plugin(self, plugin_name: str, plugin_obj: Any):
        """
        Backward-compatible registration overload.
        Args:
            plugin_name: Explicit plugin key
            plugin_obj: Plugin instance
        """

    def get_plugin(self, plugin_name: str) -> Optional[Any]:
        """Return registered plugin by name, or None."""

    def validate_module_path(self, module_path: Path) -> bool:
        """Return True if module path exists under repository root."""
        
    def get_metrics(self) -> Dict:
        """
        Get operational metrics per WSP 70
        Returns:
            Dict with state, coherence, patterns, tokens
        """
```

### OrchestratorPlugin

```python
class OrchestratorPlugin:
    """Base class for plugins per WSP 11"""
    
    def __init__(self, name: str):
        """Initialize plugin with name"""
        
    def register(self, master: WREMasterOrchestrator):
        """Register with master orchestrator"""
        
    def execute(self, task: Dict) -> Any:
        """Execute task using master's pattern memory"""
```

### Pattern

```python
@dataclass
class Pattern:
    """Pattern memory unit per WSP 60"""
    id: str  # Pattern identifier
    wsp_chain: list  # WSP citation chain [1, 3, 49, 22, 5]
    tokens: int  # Token cost (50-200 target)
    pattern: str  # Pattern description
    
    def apply(self, context: Dict) -> Any:
        """Apply pattern to context"""
```

## Usage Examples

### Basic Orchestration
```python
from wre_master_orchestrator import WREMasterOrchestrator

# Create master (only one!)
master = WREMasterOrchestrator()

# Execute with pattern recall
result = master.execute({
    "type": "module_creation",
    "name": "my_module"
})
# Uses 150 tokens instead of 5000+
```

### Plugin Registration
```python
from wre_master_orchestrator import OrchestratorPlugin

class MyPlugin(OrchestratorPlugin):
    def __init__(self):
        super().__init__("my_plugin")

# Register plugin
plugin = MyPlugin()
master.register_plugin(plugin)

# Execute through plugin
result = master.execute({
    "plugin": "my_plugin",
    "type": "custom_operation"
})
```

### Pattern Memory Access
```python
# Recall specific pattern
pattern = master.recall_pattern("error_handling")
print(f"WSP Chain: {pattern.wsp_chain}")  # [64, 50, 48, 60]
print(f"Token Cost: {pattern.tokens}")  # 100

# Apply pattern directly
result = pattern.apply({"error": "FileNotFound"})
```

## WSP Compliance
All operations follow:
- WSP 50: Pre-action verification
- WSP 64: Violation prevention
- WSP 48: Recursive learning
- WSP 22: ModLog updates
- WSP 75: Token measurements

## Error Handling
- Raises `ValueError` if operation fails WSP validation
- Raises `KeyError` if plugin not registered
- Returns default pattern if pattern not found (learns new)

## Runtime Resilience Rules (2026-02-19)
- Skill loading failures must degrade to deterministic fallback instructions (non-fatal).
- Pattern memory default singleton is production-only; tests/explicit DB paths remain isolated.
- Runtime DB override uses `WRE_PATTERN_MEMORY_DB`.

---
