# WRE Core Components - Interface Documentation

**WSP 11 Compliance:** This document defines the public interfaces for all WRE core components, ensuring modular cohesion and clean integration.

## Component Overview

The WRE core follows a modular architecture with single-responsibility components that communicate through well-defined interfaces.

### Core Components

#### 1. `engine_core.py` - WRE Core Engine
**Purpose:** Minimal lifecycle coordinator and main event loop manager
**Lines:** 151
**Dependencies:** All other components

**Public Interface:**
```python
class WRECore:
    def __init__(self, project_root_path: str = None)
    def start() -> None
    def shutdown() -> None
    def get_component_manager() -> ComponentManager
    def get_session_manager() -> SessionManager
    def get_module_prioritizer() -> ModulePrioritizer
    def get_wsp30_orchestrator() -> WSP30Orchestrator
```

**Key Methods:**
- `start()`: Initialize and run the WRE engine
- `shutdown()`: Gracefully shutdown the engine
- `get_*()`: Accessor methods for component managers

#### 2. `menu_handler.py` - Menu Handler
**Purpose:** User interaction processing and menu selection routing
**Lines:** 249
**Dependencies:** ModuleDevelopmentHandler, UIInterface, SessionManager

**Public Interface:**
```python
class MenuHandler:
    def __init__(self, project_root: Path, ui_interface, session_manager)
    def handle_choice(self, choice: str, engine) -> None
```

**Key Methods:**
- `handle_choice()`: Process user menu selections and route to appropriate handlers
- Routes to: module development, WSP30 orchestration, system management, etc.

#### 3. `system_manager.py` - System Manager
**Purpose:** System operations management (git, ModLog, FMAS, compliance)
**Lines:** 409
**Dependencies:** SessionManager

**Public Interface:**
```python
class SystemManager:
    def __init__(self, project_root: Path, session_manager)
    def handle_system_management(self, engine) -> None
    def update_modlog(self, module_name: str) -> bool
    def git_push(self) -> bool
    def run_fmas_audit(self) -> bool
```

**Key Methods:**
- `handle_system_management()`: Display and handle system management menu
- `update_modlog()`: Update module ModLog files
- `git_push()`: Execute git push operations
- `run_fmas_audit()`: Run FMAS structural audit

#### 4. `module_analyzer.py` - Module Analyzer
**Purpose:** Module analysis operations and WSP compliance validation
**Lines:** 370
**Dependencies:** SessionManager

**Public Interface:**
```python
class ModuleAnalyzer:
    def __init__(self, project_root: Path, session_manager)
    def handle_module_analysis(self, engine) -> None
    def analyze_module_structure(self, module_path: str) -> Dict[str, Any]
    def validate_wsp_compliance(self, module_path: str) -> bool
```

**Key Methods:**
- `handle_module_analysis()`: Display and handle module analysis menu
- `analyze_module_structure()`: Analyze module structure and components
- `validate_wsp_compliance()`: Validate WSP compliance for a module

#### 5. `module_development_handler.py` - Module Development Handler
**Purpose:** Module development workflows and lifecycle management
**Lines:** 369
**Dependencies:** SessionManager

**Public Interface:**
```python
class ModuleDevelopmentHandler:
    def __init__(self, project_root: Path, session_manager)
    def handle_module_development(self, module_name: str, engine) -> None
    def enter_manual_mode(self, module_name: str, engine) -> None
    def create_module_scaffold(self, module_name: str) -> bool
```

**Key Methods:**
- `handle_module_development()`: Handle module-specific development workflow
- `enter_manual_mode()`: Enter manual development mode for a module
- `create_module_scaffold()`: Create WSP-compliant module scaffold

#### 6. `wsp30_orchestrator.py` - WSP30 Orchestrator
**Purpose:** WSP_30 Agentic Module Build Orchestration
**Lines:** 486
**Dependencies:** ModulePrioritizer

**Public Interface:**
```python
class WSP30Orchestrator:
    def __init__(self, project_root: Path, mps_calculator)
    def start_agentic_build(self, module_name: str) -> bool
    def orchestrate_new_module(self, module_name: str) -> bool
    def analyze_ecosystem(self) -> Dict[str, Any]
    def generate_build_strategy(self, module_name: str) -> Dict[str, Any]
```

**Key Methods:**
- `start_agentic_build()`: Start autonomous module build process
- `orchestrate_new_module()`: Orchestrate creation of new module
- `analyze_ecosystem()`: Analyze entire module ecosystem
- `generate_build_strategy()`: Generate build strategy for module

#### 7. `agentic_orchestrator/` - Agentic Orchestrator (Modular)
**Purpose:** WSP 54 Recursive Agentic Orchestration
**Lines:** ~800 (modularized)
**Dependencies:** Agent activation, WSP 54 agents

**Public Interface:**
```python
# Main entrypoints
async def orchestrate_wsp54_agents(trigger: OrchestrationTrigger, **kwargs) -> Dict[str, Any]
def get_orchestration_stats() -> Dict[str, Any]

# Core orchestrator class
class AgenticOrchestrator:
    async def orchestrate_recursively(self, context: OrchestrationContext) -> Dict[str, Any]
    def get_orchestration_stats(self) -> Dict[str, Any]
```

**Modular Components:**
- `orchestration_context.py`: Context dataclasses and enums
- `agent_task_registry.py`: Agent task specifications
- `agent_executor.py`: Agent execution logic
- `recursive_orchestration.py`: Main orchestrator class
- `entrypoints.py`: Public interface functions

**Key Methods:**
- `orchestrate_wsp54_agents()`: Main orchestration entrypoint
- `get_orchestration_stats()`: Get orchestration statistics
- `orchestrate_recursively()`: Recursive orchestration with zen coding

#### 8. `component_manager.py` - Component Manager
**Purpose:** Component lifecycle management and initialization
**Lines:** 122
**Dependencies:** None

**Public Interface:**
```python
class ComponentManager:
    def __init__(self, project_root: Path)
    def initialize_all_components(self) -> None
    def validate_components(self) -> bool
    def get_components(self) -> Tuple
```

**Key Methods:**
- `initialize_all_components()`: Initialize all windsurfing components
- `validate_components()`: Validate critical component availability
- `get_components()`: Get all initialized components

#### 9. `session_manager.py` - Session Manager
**Purpose:** Session tracking and logging
**Lines:** 126
**Dependencies:** None

**Public Interface:**
```python
class SessionManager:
    def __init__(self, project_root: Path)
    def start_session(self, session_type: str) -> str
    def end_session(self, session_id: str) -> None
    def log_operation(self, operation: str, data: Dict) -> None
    def log_achievement(self, achievement: str, description: str) -> None
    def log_module_access(self, module_name: str, access_type: str) -> None
```

**Key Methods:**
- `start_session()`: Start new session and return session ID
- `end_session()`: End session and log completion
- `log_*()`: Various logging methods for operations and achievements

#### 10. `module_prioritizer.py` - Module Prioritizer
**Purpose:** Module priority scoring and roadmap generation
**Lines:** 310
**Dependencies:** MPSCalculator

**Public Interface:**
```python
class ModulePrioritizer:
    def __init__(self, project_root: Path)
    def generate_development_roadmap(self) -> Dict[str, Any]
    def calculate_module_priority(self, module_name: str) -> float
    def get_prioritized_modules(self) -> List[Dict[str, Any]]
```

**Key Methods:**
- `generate_development_roadmap()`: Generate development roadmap
- `calculate_module_priority()`: Calculate priority for specific module
- `get_prioritized_modules()`: Get list of prioritized modules

#### 11. `roadmap_manager.py` - Roadmap Manager
**Purpose:** Roadmap parsing and management utilities
**Lines:** 92
**Dependencies:** None

**Public Interface:**
```python
def parse_roadmap(roadmap_dir: Path) -> List[Tuple[str, str]]
def extract_objectives(roadmap_content: str) -> List[Tuple[str, str]]
```

**Key Functions:**
- `parse_roadmap()`: Parse ROADMAP.md file and extract objectives
- `extract_objectives()`: Extract objectives from roadmap content

## Component Integration Patterns

### 1. **WRE Core Engine Integration**
All components are initialized and managed by the WRE Core Engine:

```python
class WRECore:
    def __init__(self):
        self.component_manager = ComponentManager()
        self.session_manager = SessionManager()
        self.module_prioritizer = ModulePrioritizer()
        self.wsp30_orchestrator = WSP30Orchestrator()
        # ... other components
```

### 2. **Menu Handler Routing**
Menu Handler routes user choices to appropriate components:

```python
def handle_choice(self, choice: str, engine):
    if choice == "1":  # Module Development
        module_handler.handle_module_development(module_name, engine)
    elif choice == "2":  # WSP30 Orchestration
        wsp30_orchestrator.start_agentic_build(module_name)
    elif choice == "3":  # System Management
        system_manager.handle_system_management(engine)
```

### 3. **Session Management Integration**
All components use SessionManager for logging:

```python
# In any component
self.session_manager.log_operation("module_build", {"module": module_name})
self.session_manager.log_achievement("build_complete", "Module built successfully")
```

### 4. **Agentic Orchestration Integration**
WSP30 Orchestrator integrates with Agentic Orchestrator:

```python
# In WSP30 Orchestrator
async def start_agentic_build(self, module_name: str):
    # Trigger WSP 54 agent orchestration
    from agentic_orchestrator import orchestrate_wsp54_agents
    result = await orchestrate_wsp54_agents(
        OrchestrationTrigger.MODULE_BUILD,
        module_name=module_name
    )
```

## Error Handling and Recovery

### 1. **Component Initialization Errors**
```python
try:
    component_manager.initialize_all_components()
except ComponentError as e:
    logger.error(f"Component initialization failed: {e}")
    # Fallback to minimal mode
```

### 2. **Orchestration Errors**
```python
try:
    result = await orchestrate_wsp54_agents(trigger)
except OrchestrationError as e:
    logger.error(f"Orchestration failed: {e}")
    # Fallback to deterministic mode
```

### 3. **Session Recovery**
```python
# SessionManager automatically handles session recovery
session_manager.recover_session(session_id)
```

## Performance Considerations

### 1. **Async Operations**
- Agentic Orchestrator uses async/await for non-blocking operations
- WSP30 Orchestrator supports async module building
- Session logging is non-blocking

### 2. **Memory Management**
- Components use lazy initialization
- Session data is periodically archived
- Agent results are cached for performance

### 3. **Scalability**
- Modular design supports horizontal scaling
- Agent orchestration can be distributed
- Component communication is decoupled

## Testing Interface

### 1. **Component Testing**
```python
# Test individual components
def test_menu_handler():
    handler = MenuHandler(project_root, ui_interface, session_manager)
    handler.handle_choice("1", engine)
    # Assert expected behavior

def test_agentic_orchestrator():
    result = await orchestrate_wsp54_agents(OrchestrationTrigger.TESTING_CYCLE)
    assert result["status"] == "success"
```

### 2. **Integration Testing**
```python
# Test component integration
def test_wre_core_integration():
    wre = WRECore()
    wre.start()
    # Test component interactions
    wre.shutdown()
```

## WSP Compliance Interface

### 1. **WSP 11 Interface Compliance**
All components implement WSP 11 interface requirements:
- Clear public interfaces
- Well-defined method signatures
- Comprehensive documentation

### 2. **WSP 54 Agent Integration**
Agentic Orchestrator integrates with all WSP 54 agents:
- ComplianceAgent
- ModularizationAuditAgent
- TestingAgent
- ScoringAgent
- DocumentationAgent
- JanitorAgent
- ChroniclerAgent

### 3. **WSP 48 Recursive Improvement**
Components support recursive self-improvement:
- Self-analysis capabilities
- Performance monitoring
- Automatic optimization

---

*This interface documentation ensures WSP 11 compliance and provides comprehensive guidance for component integration and usage.* 