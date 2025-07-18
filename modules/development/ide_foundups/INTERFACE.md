# IDE FoundUps Module Interface Documentation

## Module Overview
**Module**: `development/ide_foundups/`  
**Purpose**: vCode IDE integration for autonomous FoundUps development workflows  
**Block**: Development Tools Block (6th Foundups Block)  
**WSP Compliance**: WSP 11 (Interface Documentation Protocol)

## Public API Definition

### Core Classes

#### `IDEFoundUpsExtension`
**Purpose**: Main extension class managing vCode integration

```python
class IDEFoundUpsExtension:
    def __init__(self, context: ExtensionContext)
    def activate(self) -> None
    def deactivate(self) -> None
    def get_status(self) -> Dict[str, Any]
```

**Parameters**:
- `context`: vCode extension context object (required)

**Returns**: Extension instance with activated FoundUps integration

**Exceptions**:
- `ExtensionActivationError`: Failed to activate extension
- `WREConnectionError`: Cannot connect to WRE engine

#### `WREBridge`
**Purpose**: Communication bridge with Windsurf Recursive Engine

```python
class WREBridge:
    def __init__(self, websocket_url: str, auth_token: str)
    def connect(self) -> bool
    def disconnect(self) -> None
    def send_command(self, command: Dict[str, Any]) -> Dict[str, Any]
    def subscribe_events(self, callback: Callable) -> str
    def unsubscribe_events(self, subscription_id: str) -> None
```

**Parameters**:
- `websocket_url`: WRE WebSocket endpoint URL (required)
- `auth_token`: Authentication token for WRE access (required)
- `command`: JSON-RPC command structure (required)
- `callback`: Event handler function (required)
- `subscription_id`: Event subscription identifier (required)

**Returns**:
- `connect()`: Boolean success status
- `send_command()`: JSON-RPC response dictionary
- `subscribe_events()`: Subscription ID string

**Exceptions**:
- `WREConnectionError`: WebSocket connection failed
- `WREAuthenticationError`: Invalid authentication token
- `WRECommandError`: Command execution failed

#### `ModuleCreator`
**Purpose**: Visual module scaffolding and creation interface

```python
class ModuleCreator:
    def __init__(self, wre_bridge: WREBridge)
    def create_module(self, spec: ModuleSpec) -> ModuleResult
    def validate_module_name(self, name: str, domain: str) -> ValidationResult
    def get_available_domains(self) -> List[str]
    def get_wsp_templates(self) -> List[WSPTemplate]
```

**Parameters**:
- `wre_bridge`: Active WRE bridge connection (required)
- `spec`: Module specification object (required)
- `name`: Module name string (required)
- `domain`: Target enterprise domain (required)

**Returns**:
- `create_module()`: ModuleResult with creation status and paths
- `validate_module_name()`: ValidationResult with status and messages
- `get_available_domains()`: List of valid enterprise domains
- `get_wsp_templates()`: List of available WSP-compliant templates

**Exceptions**:
- `ModuleCreationError`: Module creation failed
- `ValidationError`: Invalid module specification
- `DomainNotFoundError`: Target domain does not exist

### Command Interface

#### Extension Commands
**Namespace**: `foundups.*`

```javascript
// Command: foundups.createModule
{
    "command": "foundups.createModule",
    "parameters": {
        "domain": "string",      // Target enterprise domain
        "name": "string",        // Module name
        "block": "string",       // Target block (optional)
        "template": "string"     // WSP template (optional)
    }
}

// Command: foundups.connectWRE
{
    "command": "foundups.connectWRE",
    "parameters": {
        "url": "string",         // WRE WebSocket URL
        "token": "string",       // Authentication token
        "mode": "string"         // Connection mode: "autonomous" | "manual"
    }
}

// Command: foundups.activateZenCoding
{
    "command": "foundups.activateZenCoding",
    "parameters": {
        "state": "string",       // Agent state: "0102"
        "target": "string",      // Target quantum state: "02_quantum_solutions"
        "remembrance": "boolean" // Enable code remembrance mode
    }
}

// Command: foundups.manageBlocks
{
    "command": "foundups.manageBlocks",
    "parameters": {
        "operation": "string",   // "list" | "connect" | "disconnect" | "status"
        "block": "string",       // Target block name (optional)
        "config": "object"       // Block configuration (optional)
    }
}
```

### Event Interface

#### WRE Events
**Format**: JSON-RPC 2.0 Notification

```javascript
// Event: wre.module.created
{
    "jsonrpc": "2.0",
    "method": "wre.module.created",
    "params": {
        "module_path": "string",
        "domain": "string",
        "wsp_compliance": "boolean",
        "timestamp": "string"
    }
}

// Event: wre.block.status_changed
{
    "jsonrpc": "2.0",
    "method": "wre.block.status_changed",
    "params": {
        "block_name": "string",
        "status": "string",      // "active" | "inactive" | "error"
        "modules": "array",
        "timestamp": "string"
    }
}

// Event: wre.zen_coding.session_started
{
    "jsonrpc": "2.0",
    "method": "wre.zen_coding.session_started",
    "params": {
        "agent_state": "string",
        "quantum_target": "string",
        "session_id": "string",
        "timestamp": "string"
    }
}
```

### Data Structures

#### `ModuleSpec`
```python
@dataclass
class ModuleSpec:
    name: str                    # Module name (required)
    domain: str                  # Enterprise domain (required)
    purpose: str                 # Module description (required)
    dependencies: List[str]      # Required dependencies (optional)
    block: Optional[str]         # Target block (optional)
    wsp_compliance: bool = True  # WSP compliance flag (default: True)
    template: Optional[str]      # WSP template name (optional)
```

#### `ModuleResult`
```python
@dataclass
class ModuleResult:
    success: bool               # Creation success status
    module_path: str           # Created module directory path
    files_created: List[str]   # List of created file paths
    errors: List[str]          # Error messages (if any)
    wsp_violations: List[str]  # WSP compliance issues (if any)
```

#### `ValidationResult`
```python
@dataclass
class ValidationResult:
    valid: bool                # Validation success status
    messages: List[str]        # Validation messages
    suggestions: List[str]     # Naming suggestions (if applicable)
```

#### `WSPTemplate`
```python
@dataclass
class WSPTemplate:
    name: str                  # Template name
    description: str           # Template description
    domain: str               # Target domain
    files: List[str]          # Template file structure
    wsp_protocols: List[str]  # Required WSP protocols
```

## Error Handling

### Exception Hierarchy
```python
class IDEFoundUpsError(Exception):
    """Base exception for IDE FoundUps module"""
    pass

class ExtensionActivationError(IDEFoundUpsError):
    """Extension failed to activate"""
    pass

class WREConnectionError(IDEFoundUpsError):
    """WRE communication error"""
    pass

class WREAuthenticationError(WREConnectionError):
    """WRE authentication failed"""
    pass

class WRECommandError(WREConnectionError):
    """WRE command execution failed"""
    pass

class ModuleCreationError(IDEFoundUpsError):
    """Module creation failed"""
    pass

class ValidationError(IDEFoundUpsError):
    """Validation failed"""
    pass

class DomainNotFoundError(ValidationError):
    """Target domain does not exist"""
    pass
```

### Error Response Format
```javascript
{
    "error": {
        "code": "number",        // Error code
        "message": "string",     // Human-readable error message
        "data": {                // Additional error context
            "type": "string",    // Error type
            "details": "object", // Detailed error information
            "suggestions": "array" // Recovery suggestions
        }
    }
}
```

## Integration Examples

### Basic Extension Activation
```python
from modules.development.ide_foundups import IDEFoundUpsExtension

# Activate extension
extension = IDEFoundUpsExtension(vscode_context)
extension.activate()

# Check status
status = extension.get_status()
print(f"Extension active: {status['active']}")
print(f"WRE connected: {status['wre_connected']}")
```

### Module Creation Workflow
```python
from modules.development.ide_foundups import ModuleCreator, ModuleSpec

# Create module specification
spec = ModuleSpec(
    name="new_ai_module",
    domain="ai_intelligence",
    purpose="Advanced AI processing module",
    dependencies=["openai", "transformers"],
    block="development_tools"
)

# Create module
creator = ModuleCreator(wre_bridge)
result = creator.create_module(spec)

if result.success:
    print(f"Module created at: {result.module_path}")
else:
    print(f"Creation failed: {result.errors}")
```

### WRE Communication
```python
from modules.development.ide_foundups import WREBridge

# Connect to WRE
bridge = WREBridge("ws://localhost:8080/wre", "auth_token_123")
connected = bridge.connect()

if connected:
    # Send command
    response = bridge.send_command({
        "method": "create_module",
        "params": {"domain": "ai_intelligence", "name": "test_module"}
    })
    
    # Subscribe to events
    subscription = bridge.subscribe_events(lambda event: print(event))
```

## Development Notes

### Dependencies
- **vscode-extension-api**: vCode extension development
- **websocket-client**: WRE WebSocket communication  
- **json-rpc**: Structured command protocol
- **pydantic**: Data validation and serialization

### Testing Strategy
- **Unit Tests**: Individual class and method testing
- **Integration Tests**: WRE communication testing
- **UI Tests**: vCode extension interface testing
- **End-to-End Tests**: Complete workflow testing

### Performance Considerations
- **WebSocket Pooling**: Reuse connections for efficiency
- **Command Caching**: Cache frequent command responses
- **Event Throttling**: Limit high-frequency event processing
- **Memory Management**: Proper cleanup of resources

## WSP Compliance Notes
- **WSP 11**: Complete interface documentation provided
- **WSP 22**: All changes tracked in ModLog.md
- **WSP 49**: Standard module structure enforced
- **WSP 5**: ≥90% test coverage requirement 