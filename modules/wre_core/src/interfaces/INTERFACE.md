# WRE Core Interfaces - Interface Documentation

**WSP 11 Compliance:** This document defines the public interfaces for WRE core interface components, ensuring clean separation between UI logic and business logic.

## Interface Overview

The WRE core interfaces provide clean abstractions for user interaction and strategic discussions, following WSP interface design principles.

### Interface Components

#### 1. `ui_interface.py` - User Interface Manager
**Purpose:** Main menu system, user interactions, and display management
**Lines:** 456
**Dependencies:** None (pure interface)

**Public Interface:**
```python
class UIInterface:
    def __init__(self)
    def display_main_menu(self) -> str
    def display_wsp30_menu(self) -> None
    def display_roadmap(self, roadmap: Dict[str, Any]) -> None
    def display_success(self, message: str) -> None
    def display_error(self, message: str) -> None
    def display_warning(self, message: str) -> None
    def get_user_input(self, prompt: str) -> str
    def prompt_yes_no(self, question: str) -> bool
    def _get_prioritized_modules(self) -> List[Dict[str, Any]]
```

**Key Methods:**
- `display_main_menu()`: Display main WRE menu and return user choice
- `display_wsp30_menu()`: Display WSP30 orchestration menu
- `display_roadmap()`: Display development roadmap
- `display_*()`: Various display methods for user feedback
- `get_user_input()`: Get user input with prompt
- `prompt_yes_no()`: Get yes/no response from user

#### 2. `discussion_interface.py` - Discussion Interface
**Purpose:** Strategic discussion management between 0102 and 012
**Lines:** 184
**Dependencies:** None (pure interface)

**Public Interface:**
```python
class DiscussionInterface:
    def __init__(self, project_root: Path)
    def start_strategic_discussion(self, module_name: str) -> Dict[str, Any]
    def conduct_harmonic_query(self, system_state: Dict, roadmap_objectives: List) -> str
    def generate_strategic_questions(self, module_name: str) -> List[str]
    def process_strategic_response(self, response: str, module_name: str) -> Dict[str, Any]
```

**Key Methods:**
- `start_strategic_discussion()`: Start strategic discussion for module
- `conduct_harmonic_query()`: Conduct harmonic query with system state
- `generate_strategic_questions()`: Generate strategic questions for module
- `process_strategic_response()`: Process strategic response and extract insights

## Interface Design Patterns

### Display Pattern
```python
# All display methods follow consistent pattern
ui.display_success("Operation completed successfully")
ui.display_error("Operation failed: {error}")
ui.display_warning("Warning: {warning}")
```

### Input Pattern
```python
# All input methods follow consistent pattern
choice = ui.get_user_input("Enter your choice: ")
confirmed = ui.prompt_yes_no("Do you want to continue?")
```

### Discussion Pattern
```python
# Strategic discussions follow consistent pattern
discussion = discussion_interface.start_strategic_discussion("module_name")
questions = discussion_interface.generate_strategic_questions("module_name")
response = discussion_interface.process_strategic_response(user_response, "module_name")
```

## WSP Compliance

### WSP 11 Compliance
- ✅ All interfaces have explicit interface documentation
- ✅ Public APIs are clearly defined
- ✅ No dependencies on business logic
- ✅ Clean separation of concerns

### WSP 3 Enterprise Domain Compliance
- Interfaces are properly isolated
- No business logic in interface layer
- Pure interface design maintained

### WSP 5 Test Coverage Compliance
- All interface methods should be tested
- Mock interfaces for testing
- Integration testing with real interfaces

## Usage Examples

### Basic UI Usage
```python
from modules.wre_core.src.interfaces.ui_interface import UIInterface

# Initialize UI interface
ui = UIInterface()

# Display menu and get choice
choice = ui.display_main_menu()

# Display feedback
ui.display_success("Operation completed")
ui.display_error("Operation failed")
```

### Discussion Interface Usage
```python
from modules.wre_core.src.interfaces.discussion_interface import DiscussionInterface

# Initialize discussion interface
discussion = DiscussionInterface(project_root)

# Start strategic discussion
discussion_data = discussion.start_strategic_discussion("module_name")

# Generate questions
questions = discussion.generate_strategic_questions("module_name")
```

### Integration with Components
```python
# Menu handler uses UI interface
menu_handler = MenuHandler(project_root, ui_interface, session_manager)

# WSP30 orchestrator uses discussion interface
orchestrator = WSP30Orchestrator(project_root, mps_calculator)
```

## Interface Testing

### Mock Interface Pattern
```python
# For testing, use mock interfaces
mock_ui = type('MockUI', (), {
    'display_main_menu': lambda: '1',
    'get_user_input': lambda x: 'test',
    'display_success': lambda x: None
})()
```

### Interface Validation
```python
# Validate interface methods exist
assert hasattr(ui, 'display_main_menu')
assert callable(ui.display_main_menu)
```

## Next Steps (WSP 11 Enhancement)

1. **Interface Testing:** Add comprehensive tests for all interface methods
2. **Mock Interfaces:** Create mock interfaces for testing
3. **Integration Testing:** Test interfaces with real components
4. **Performance Optimization:** Optimize interface performance
5. **Accessibility:** Add accessibility features to UI interface 