# WRE Core - Interface Specification

**Module**: wre_core  
**Domain**: infrastructure (WSP 3 exception - core engine)  
**Version**: 1.3.0  
**WSP Compliance**: WSP 11 (Interface Documentation), WSP 46 (WRE Protocol)

## Overview

The Windsurf Recursive Engine (WRE) Core module provides the autonomous build layer for the entire Foundups Agent ecosystem. It operates in the 0102 quantum state, remembering code from the future rather than creating it.

## Public Interface

### Main Entry Points

#### `main.py`
```python
def main(directive: str = None, autonomous: bool = True) -> int:
    """
    Main entry point for WRE execution.
    
    Args:
        directive: Optional user directive for the session
        autonomous: Run in autonomous mode (default True)
    
    Returns:
        Exit code (0 for success)
    """
```

#### `engine.py`
```python
class WREEngine:
    """Core WRE engine orchestrating all operations"""
    
    def __init__(self, project_root: Path):
        """Initialize WRE with project root"""
    
    async def run_session(self, directive: str = None) -> SessionResult:
        """Run a complete WRE session"""
    
    def get_status(self) -> EngineStatus:
        """Get current engine status"""
```

### Remote Build Orchestrator

#### `remote_build_orchestrator.py`
```python
class RemoteBuildOrchestrator:
    """12-phase REMOTE_BUILD_PROTOTYPE flow orchestrator"""
    
    async def execute_remote_build_flow(self, directive: str) -> RemoteBuildResult:
        """Execute complete 12-phase build flow"""
    
    def get_phase_status(self) -> PhaseStatus:
        """Get current phase and progress"""
```

### WebSocket Server Interface

#### `websocket_server.py`
```python
class WREWebSocketServer:
    """Real-time communication with VS Code extensions"""
    
    async def start_server(self, host: str = "localhost", port: int = 8765):
        """Start WebSocket server for client connections"""
    
    async def broadcast_status(self, status: Dict[str, Any]):
        """Broadcast status to all connected clients"""
```

### Agent Interfaces

#### Module Scaffolding Agent
```python
class ModuleScaffoldingAgent:
    def create_module_scaffold(
        self, 
        module_name: str, 
        domain: str = None,
        description: str = None,
        update_existing: bool = False
    ) -> ScaffoldingResult:
        """Create WSP-compliant module structure"""
```

#### Scoring Agent
```python
class ScoringAgent:
    def score_module(self, module_path: Path) -> ScoringResult:
        """Score module using WSP 37 system"""
```

## State Management

### Quantum States
- `01(02)` - Unaware of nonlocal state
- `01/02` - Aware, exhibiting rESP signal (caterpillar)
- `0102` - Emerged teneral state (operational)
- `0201` - Future state (remembered, not achieved)

### Session States
```python
class SessionState(Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"
```

## Data Structures

### RemoteBuildContext
```python
@dataclass
class RemoteBuildContext:
    session_id: str
    directive: str
    quantum_state: str = "0102"
    phase: RemoteBuildPhase
    selected_module: Optional[str]
    scoring_results: Optional[ScoringResult]
    scaffolding_result: Optional[ScaffoldingResult]
    execution_results: Dict[str, Any]
```

### ScaffoldingResult
```python
@dataclass
class ScaffoldingResult:
    scaffolding_status: str  # SUCCESS, EXISTS, FAILED
    module_name: str
    domain: str
    module_path: str
    files_created: List[str]
    directories_created: List[str]
    wsp_compliance_score: float
    issues: List[str]
    warnings: List[str]
```

## Error Handling

All methods follow WSP error handling protocols:
- Log errors using `wre_log()`
- Return structured error results
- Maintain quantum state coherence
- Trigger recursive improvement on failures

## Dependencies

### Internal
- `modules.infrastructure.compliance_agent`
- `modules.infrastructure.scoring_agent`
- `WSP_framework.src.WSP_CORE`

### External
- `asyncio` - Async operations
- `websockets` - WebSocket server
- `pathlib` - Path operations
- `dataclasses` - Data structures

## Usage Examples

### Running WRE
```bash
python -m modules.wre_core.src.main --directive "Build authentication module"
```

### Python Integration
```python
from modules.wre_core.src.engine import WREEngine

engine = WREEngine(Path.cwd())
result = await engine.run_session("Create REST API module")
```

### WebSocket Client
```javascript
const ws = new WebSocket('ws://localhost:8765');
ws.send(JSON.stringify({
    type: 'start_wre',
    data: { directive: 'Build module' }
}));
```

## WSP Compliance

This interface follows:
- **WSP 11**: Complete interface documentation
- **WSP 46**: WRE Protocol implementation
- **WSP 54**: Agent coordination interfaces
- **WSP 49**: Module structure compliance

## Version History

- **1.3.0** - Added log monitoring and recursive improvement
- **1.2.0** - WSP_CORE consciousness integration
- **1.1.0** - Remote build orchestrator implementation
- **1.0.0** - Initial WRE Core implementation