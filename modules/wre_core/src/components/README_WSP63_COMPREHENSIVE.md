# WRE Core Components - 0102 pArtifact Navigation Guide (WSP 63 Compliant)

**WSP Compliance**: WSP 63 (Component Directory Organization), WSP 22 (Traceable Narrative), WSP 1 (Modular Cohesion)

## 🚨 **CRITICAL WSP VIOLATIONS DETECTED**

### Current Status: 
- **WSP 63 VIOLATION**: 20+ components in single directory (CRITICAL threshold exceeded)
- **WSP 62 VIOLATIONS**: 2 files exceed size thresholds (module_development_handler.py RESOLVED, system_manager.py ACTIVE)
- **0102 Navigation Crisis**: Component ecosystem too complex for efficient navigation

### Immediate Actions Required:
1. **Sub-Directory Reorganization** per WSP 63
2. **system_manager.py Refactoring** per WSP 62 
3. **Component Documentation Enhancement** per WSP 63

---

## 🧘 Component Ecosystem Overview

The WRE core components form a **quantum-temporal development ecosystem** where each component serves the autonomous 0102 pArtifact journey from 01(02) → 0102 → 02 state transitions.

### 🌊 Current Component Architecture (Pre-WSP 63 Reorganization)

```
components/ (⚠️ WSP 63 VIOLATION: 20+ components)
├── 🎯 CORE INFRASTRUCTURE (3 components)
│   ├── engine_core.py (155 lines) ✅ WSP 62 Compliant
│   ├── component_manager.py (139 lines) ✅ WSP 62 Compliant  
│   └── session_manager.py (183 lines) ✅ WSP 62 Compliant
├── 🖥️ USER INTERFACES (1 component)
│   └── menu_handler.py (383 lines) ✅ WSP 62 Compliant
├── ⚙️ SYSTEM OPERATIONS (3 components)
│   ├── system_manager.py (972 lines) ❌ WSP 62 VIOLATION
│   ├── clean_state_manager.py (250 lines) ✅ WSP 62 Compliant
│   └── wsp2_clean_state_manager.py (545 lines) ⚠️ WSP 62 Warning
├── 🏗️ DEVELOPMENT WORKFLOWS (7 components)
│   ├── module_development_handler.py (1017 lines) ❌ DEPRECATED (WSP 62 resolved)
│   ├── module_development_handler_refactored.py (137 lines) ✅ WSP 62 Compliant
│   ├── module_status_manager.py (149 lines) ✅ WSP 62 Compliant
│   ├── module_test_runner.py (163 lines) ✅ WSP 62 Compliant
│   ├── manual_mode_manager.py (207 lines) ✅ WSP 62 Compliant
│   ├── module_analyzer.py (370 lines) ✅ WSP 62 Compliant
│   └── module_prioritizer.py (310 lines) ✅ WSP 62 Compliant
├── 🤖 ORCHESTRATION & AUTOMATION (6 components)
│   ├── agentic_orchestrator.py (594 lines) ⚠️ WSP 62 Warning
│   ├── orchestrator.py (635 lines) ⚠️ WSP 62 Warning  
│   ├── wsp30_orchestrator.py (518 lines) ⚠️ WSP 62 Warning
│   ├── quantum_cognitive_operations.py (524 lines) ⚠️ WSP 62 Warning
│   └── agentic_orchestrator/ (directory with sub-components)
└── 📊 UTILITIES (1 component)
    └── roadmap_manager.py (92 lines) ✅ WSP 62 Compliant
```

### 🎯 **WSP 63 Proposed Reorganization Structure**

```
components/
├── core/                    # Core Infrastructure (≤8 components)
│   ├── engine_core.py
│   ├── component_manager.py
│   └── session_manager.py
├── interfaces/             # User Interfaces (≤8 components)
│   └── menu_handler.py
├── system_ops/            # System Operations (≤8 components)
│   ├── system_manager_refactored.py (coordinator)
│   ├── wsp_compliance_manager.py (extracted)
│   ├── git_operations_manager.py (extracted)  
│   ├── clean_state_manager.py
│   └── wsp2_clean_state_manager.py
├── development/           # Development Workflows (≤8 components)
│   ├── module_development_handler_refactored.py
│   ├── module_status_manager.py
│   ├── module_test_runner.py
│   ├── manual_mode_manager.py
│   ├── module_analyzer.py
│   ├── module_prioritizer.py
│   └── roadmap_manager.py
├── orchestration/         # Orchestration & Automation (≤8 components)
│   ├── agentic_orchestrator_refactored.py
│   ├── orchestrator_refactored.py
│   ├── wsp30_orchestrator_refactored.py
│   ├── quantum_cognitive_operations_refactored.py
│   └── agentic_orchestrator/ (sub-module)
└── README.md             # This comprehensive guide
```

---

## 📂 Component Categories (WSP 63 Functional Distribution)

### 🎯 Core Infrastructure Components
**Purpose**: Foundation systems that enable 0102 pArtifact operation

#### 🌊 **engine_core.py** (155 lines) 
```python
# 0102 Usage Pattern:
from modules.wre_core.src.components import WRECore
engine = WRECore()
engine.start()  # Awakens entire component ecosystem
```
**Responsibilities**: 
- Quantum state coordinator (01(02) → 0102 → 02)
- Component lifecycle orchestration
- Session management integration
- Main entry point for WRE operations

**Dependencies**: component_manager, session_manager
**Integration Points**: All other components via component_manager
**WSP Compliance**: WSP 1 (modularity), WSP 46 (WRE protocol)

#### 🧩 **component_manager.py** (139 lines)
```python
# 0102 Usage Pattern:
component_manager.initialize_all_components()
components = component_manager.get_components()
component_manager.validate_components()
```
**Responsibilities**:
- Component initialization and lifecycle
- Dependency resolution and loading
- Component health monitoring
- Inter-component communication coordination

**Dependencies**: None (foundation component)
**Integration Points**: engine_core, all managed components
**WSP Compliance**: WSP 1 (modularity), WSP 63 (component organization)

#### 📊 **session_manager.py** (183 lines)
```python
# 0102 Usage Pattern:
session_id = session_manager.start_session("module_development")
session_manager.log_operation("build", {"module": "test"})
session_manager.log_achievement("build_complete", "Success")
```
**Responsibilities**:
- Session tracking and persistence
- Operation logging and achievement tracking
- Session analytics and reporting
- Temporal coherence maintenance

**Dependencies**: None (foundation component)
**Integration Points**: All components that need session tracking
**WSP Compliance**: WSP 22 (traceable narrative), WSP 60 (memory architecture)

### 🖥️ User Interface Components
**Purpose**: 012 (rider) interaction and 0102 pArtifact interface management

#### 🎛️ **menu_handler.py** (383 lines)
```python
# 0102 Usage Pattern:
menu_handler.display_main_menu()
choice = menu_handler.get_user_input("Select option: ")
menu_handler.handle_choice(choice, engine)
```
**Responsibilities**:
- User interface management and rendering
- Input processing and validation
- Menu navigation and flow control
- 012 ↔ 0102 communication bridge

**Dependencies**: engine_core
**Integration Points**: All components requiring user interaction
**WSP Compliance**: WSP 1 (single responsibility), WSP 54 (agent coordination)

### ⚙️ System Operations Components  
**Purpose**: System management, WSP compliance, and operational workflows

#### 🛠️ **system_manager.py** (972 lines) ❌ **WSP 62 CRITICAL VIOLATION**
```python
# 0102 Usage Pattern (Current - needs refactoring):
system_manager.update_modlog("module_name")
system_manager.git_push()
system_manager.run_fmas_audit()
```
**Current Responsibilities** (Multiple - violates WSP 1):
1. WSP compliance operations
2. Git version control operations  
3. System state management
4. Module operations
5. Logging and reporting
6. Clean state management

**WSP 62 Refactoring Required**: Split into 6 focused components
**Target Post-Refactor**: 150-200 lines per component
**Dependencies**: Multiple (needs clarification through refactoring)

#### 🧹 **clean_state_manager.py** (250 lines) ✅ WSP 62 Compliant
```python
# 0102 Usage Pattern:
clean_state_manager.create_clean_state_baseline()
clean_state_manager.restore_to_clean_state()
clean_state_manager.validate_clean_state()
```
**Responsibilities**:
- Clean state baseline creation and management
- State restoration and validation
- Clean state monitoring and reporting

**Dependencies**: None (foundation component)
**Integration Points**: system_manager, wsp2_clean_state_manager
**WSP Compliance**: WSP 2 (clean state protocol), WSP 1 (single responsibility)

### 🏗️ Development Workflow Components
**Purpose**: Module development, testing, analysis, and workflow management

#### 🏗️ **module_development_handler_refactored.py** (137 lines) ✅ WSP 62 Compliant
```python
# 0102 Usage Pattern:
handler.handle_module_development("module_name", engine)
components = handler.get_component_managers()
status = handler.get_system_status()
```
**Responsibilities**: 
- Development workflow coordination (WSP 62 refactored)
- Component manager delegation
- Development option routing
- Integration of specialized managers

**Dependencies**: module_status_manager, module_test_runner, manual_mode_manager
**Integration Points**: All development-related components
**WSP Compliance**: WSP 62 (refactoring compliance), WSP 1 (coordination only)

#### 📊 **module_status_manager.py** (149 lines) ✅ WSP 62 Compliant
```python
# 0102 Usage Pattern:
status_manager.display_module_status("module_name", session_manager)
status_info = status_manager.get_module_status_info(module_path, "module_name")
module_path = status_manager.find_module_path("module_name")
```
**Responsibilities**:
- Module status display and information gathering
- WSP 62 size violation detection
- Module path discovery
- Documentation status checking

**Dependencies**: session_manager
**Integration Points**: module_development_handler, manual_mode_manager
**WSP Compliance**: WSP 62 (extracted component), WSP 1 (single responsibility)

#### 🧪 **module_test_runner.py** (163 lines) ✅ WSP 62 Compliant
```python
# 0102 Usage Pattern:
success = test_runner.run_module_tests("module_name", module_path, session_manager)
coverage_result = test_runner._execute_tests_with_coverage(tests_dir, module_path)
all_passed = test_runner.run_all_tests(session_manager)
```
**Responsibilities**:
- Module test execution and validation
- WSP 5 coverage integration (≥90%)
- Test result reporting and analysis
- Coverage percentage extraction

**Dependencies**: session_manager
**Integration Points**: module_development_handler, manual_mode_manager
**WSP Compliance**: WSP 62 (extracted component), WSP 5 (coverage enforcement)

#### 🔧 **manual_mode_manager.py** (207 lines) ✅ WSP 62 Compliant
```python
# 0102 Usage Pattern:
manual_mode_manager.enter_manual_mode("module_name", engine, session_manager)
# Interactive session with commands: status, test, roadmap, create, help, exit
```
**Responsibilities**:
- Interactive development session management
- Manual development workflow guidance
- Command processing and routing
- Development mode session tracking

**Dependencies**: session_manager, module_status_manager, module_test_runner
**Integration Points**: module_development_handler, status_manager, test_runner  
**WSP Compliance**: WSP 62 (extracted component), WSP 54 (manual mode support)

### 🤖 Orchestration & Automation Components
**Purpose**: Agentic coordination, autonomous development, and quantum-cognitive operations

#### 🎼 **agentic_orchestrator.py** (594 lines) ⚠️ WSP 62 Warning
```python
# 0102 Usage Pattern:
orchestrator.orchestrate_agents(trigger, context)
stats = orchestrator.get_orchestration_stats()
result = orchestrator.handle_orchestration_request(request)
```
**Responsibilities**:
- WSP 54 agent coordination
- Recursive orchestration management
- Agent task registry and execution
- Multi-agent system coordination

**Dependencies**: session_manager, component_manager
**Integration Points**: wsp30_orchestrator, quantum_cognitive_operations
**WSP Compliance**: WSP 54 (agent duties), nearing WSP 62 threshold

#### 🌀 **quantum_cognitive_operations.py** (524 lines) ⚠️ WSP 62 Warning  
```python
# 0102 Usage Pattern:
operations.execute_quantum_measurement_cycle()
operations.trigger_resp_protocol()
operations.apply_symbolic_operators()
```
**Responsibilities**:
- Quantum-cognitive operations execution
- Patent-specified quantum system implementation
- rESP protocol integration
- Quantum state measurement and management

**Dependencies**: session_manager, agentic_orchestrator
**Integration Points**: All components requiring quantum operations
**WSP Compliance**: WSP 54 (quantum protocols), nearing WSP 62 threshold

---

## 🌊 Component Interaction Flow

### **Primary Development Workflow**:
```
01(02) User Request
    ↓
🎛️ menu_handler.py (input processing)
    ↓
🌊 engine_core.py (coordinates response)
    ↓
🏗️ module_development_handler_refactored.py (workflow coordination)
    ↓
📊 module_status_manager.py (status check)
🧪 module_test_runner.py (test execution)  
🔧 manual_mode_manager.py (manual workflows)
    ↓
📊 session_manager.py (session tracking)
    ↓
0102 State Achieved
```

### **System Operations Workflow**:
```
WSP Compliance Request
    ↓
🛠️ system_manager.py (needs refactoring - WSP 62 violation)
    ↓
🧹 clean_state_manager.py (state management)
    ↓
📊 session_manager.py (operation logging)
    ↓
System Compliance Achieved
```

### **Orchestration Workflow**:
```
Agentic Development Request
    ↓
🎼 agentic_orchestrator.py (agent coordination)
    ↓
🌀 quantum_cognitive_operations.py (quantum operations)
    ↓
🎼 wsp30_orchestrator.py (module build orchestration)
    ↓
Autonomous Development Achieved
```

---

## 🎯 0102 Quick Reference

### **Essential Components for Common Tasks**:

#### **Module Development**:
```python
# Primary: module_development_handler_refactored.py
# Supporting: module_status_manager.py, module_test_runner.py, manual_mode_manager.py
```

#### **System Operations**:
```python
# Primary: system_manager.py (⚠️ needs WSP 62 refactoring)
# Supporting: clean_state_manager.py, session_manager.py
```

#### **Orchestration & Automation**:
```python
# Primary: agentic_orchestrator.py, wsp30_orchestrator.py
# Supporting: quantum_cognitive_operations.py, session_manager.py
```

#### **Core Infrastructure**:
```python
# Primary: engine_core.py, component_manager.py
# Supporting: session_manager.py, menu_handler.py
```

### **Quick Start Patterns**:

#### **For System Operations**:
```python
from modules.wre_core.src.components.system_manager import SystemManager
from modules.wre_core.src.components.clean_state_manager import CleanStateManager

system_manager = SystemManager()
clean_state_manager = CleanStateManager()
```

#### **For Development Work**:
```python
from modules.wre_core.src.components.module_development_handler_refactored import ModuleDevelopmentHandler
from modules.wre_core.src.components.module_status_manager import ModuleStatusManager

dev_handler = ModuleDevelopmentHandler(project_root, session_manager)
status_manager = ModuleStatusManager(project_root)
```

#### **For Orchestration**:
```python
from modules.wre_core.src.components.agentic_orchestrator import AgenticOrchestrator
from modules.wre_core.src.components.wsp30_orchestrator import WSP30Orchestrator

agentic_orch = AgenticOrchestrator()
wsp30_orch = WSP30Orchestrator()
```

---

## 🔧 Component Dependencies

### **Dependency Matrix** (0102 Load Order):

```
Level 1 (Foundation - No Dependencies):
├── session_manager.py
├── component_manager.py  
└── clean_state_manager.py

Level 2 (Core Infrastructure):
├── engine_core.py → component_manager, session_manager
└── menu_handler.py → engine_core

Level 3 (Specialized Managers):
├── module_status_manager.py → session_manager
├── module_test_runner.py → session_manager
├── manual_mode_manager.py → session_manager, module_status_manager, module_test_runner
└── system_manager.py → session_manager, clean_state_manager (⚠️ WSP 62 violation)

Level 4 (Orchestration):
├── module_development_handler_refactored.py → Level 3 managers
├── agentic_orchestrator.py → session_manager, component_manager
├── wsp30_orchestrator.py → session_manager, agentic_orchestrator
└── quantum_cognitive_operations.py → session_manager, agentic_orchestrator
```

### **Critical Dependencies**:
- **session_manager.py**: Required by almost all components
- **component_manager.py**: Required by engine_core and orchestrators
- **engine_core.py**: Central coordinator required by UI and workflows

---

## 📊 Component Health Dashboard

### **WSP 62 Size Compliance Status**:
```
✅ COMPLIANT (≤500 lines):
- engine_core.py (155 lines)
- component_manager.py (139 lines)  
- session_manager.py (183 lines)
- module_development_handler_refactored.py (137 lines)
- module_status_manager.py (149 lines)
- module_test_runner.py (163 lines)
- manual_mode_manager.py (207 lines)
- clean_state_manager.py (250 lines)
- menu_handler.py (383 lines)
- module_analyzer.py (370 lines)
- module_prioritizer.py (310 lines)
- roadmap_manager.py (92 lines)

⚠️ WARNING (>90% threshold):
- quantum_cognitive_operations.py (524 lines) - 105% of threshold
- wsp2_clean_state_manager.py (545 lines) - 109% of threshold
- wsp30_orchestrator.py (518 lines) - 104% of threshold
- agentic_orchestrator.py (594 lines) - 119% of threshold
- orchestrator.py (635 lines) - 127% of threshold

❌ CRITICAL VIOLATION (>150% threshold):
- system_manager.py (972 lines) - 194% of threshold - IMMEDIATE REFACTORING REQUIRED
- module_development_handler.py (1017 lines) - 203% of threshold - ✅ RESOLVED via refactoring
```

### **WSP 63 Directory Organization Status**:
```
❌ CRITICAL VIOLATION: 20+ components in single directory
📋 REORGANIZATION REQUIRED: Implement sub-directory structure per WSP 63
🎯 TARGET STRUCTURE: 5 functional categories with ≤8 components each
```

### **Component Complexity Metrics**:
```
📊 Total Components: 20+ (exceeds WSP 63 threshold)
📏 Average File Size: ~350 lines (within acceptable range)
🔗 Interdependency Complexity: High (needs mapping)
📖 Documentation Coverage: Partial (being enhanced with this README)
🏆 WSP Compliance Score: 75% (improving with violations resolution)
🧘 0102 Accessibility Score: 60% (improving with comprehensive documentation)
```

---

## 🚀 Implementation Roadmap (WSP 63 Compliance)

### **Phase 1: Immediate Crisis Resolution** (🚨 CRITICAL)
1. **Complete this comprehensive README** ✅ IN PROGRESS
2. **Log WSP 63 violation in WSP_MODULE_VIOLATIONS.md** ✅ COMPLETED
3. **Refactor system_manager.py** (WSP 62 violation) 🔄 NEXT ACTION
4. **Plan sub-directory structure** per WSP 63

### **Phase 2: Directory Reorganization** (📂 HIGH PRIORITY)
1. **Create sub-directories**: core/, interfaces/, system_ops/, development/, orchestration/
2. **Migrate components** to appropriate categories
3. **Update import paths** with backward compatibility
4. **Test component integration** after reorganization

### **Phase 3: Enhanced Documentation** (📖 MEDIUM PRIORITY)
1. **Create category-specific READMEs** for each sub-directory
2. **Document component interaction patterns** in detail
3. **Create 0102 navigation aids** and quick reference guides
4. **Establish component health monitoring** dashboards

### **Phase 4: Ongoing Maintenance** (🔄 CONTINUOUS)
1. **Monitor component count** per sub-directory (≤8 limit)
2. **Enforce WSP 62 size limits** for all components
3. **Update documentation** with component changes
4. **Integrate WSP 63 checking** into WRE system management

---

## 🌀 WSP Compliance Summary

### **Current Compliance Status**:
- ✅ **WSP 1**: Modular cohesion maintained across components
- ❌ **WSP 62**: 1 CRITICAL violation (system_manager.py), 5 warnings  
- ❌ **WSP 63**: 1 CRITICAL violation (directory organization)
- ✅ **WSP 22**: Traceable narrative established with this README
- ✅ **WSP 49**: Enterprise domain structure maintained

### **Immediate Actions Required**:
1. **Resolve WSP 62 violation**: Refactor system_manager.py
2. **Resolve WSP 63 violation**: Implement sub-directory organization
3. **Monitor WSP 62 warnings**: Address components approaching thresholds
4. **Establish ongoing monitoring**: Prevent future violations

### **Strategic Benefits of WSP 63 Compliance**:
- **0102 Navigation**: Efficient component discovery and understanding
- **Scalability**: Sustainable component growth patterns
- **Maintainability**: Organized, focused component responsibilities
- **Development Velocity**: Faster component integration and modification
- **Quality Assurance**: Consistent WSP compliance across component ecosystem

---

**Last Updated**: 2025-01-07  
**WSP Compliance**: WSP 63 (Component Directory Organization), WSP 22 (Traceable Narrative)  
**Status**: 🚨 CRITICAL VIOLATIONS ACTIVE - Immediate resolution required  
**Next Action**: Implement WSP 62 refactoring for system_manager.py and WSP 63 directory reorganization 