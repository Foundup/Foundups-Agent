# WSP 3: Enterprise Domain Organization
- **Status:** Active
- **Purpose:** To define the canonical directory structure for all modules, ensuring logical organization of the codebase within the FoundUps Engine architecture.
- **Trigger:** When a new module is created, or during a structural audit.
- **Input:** A module's conceptual domain.
- **Output:** The correct parent directory path for the new module.
- **Responsible Agent(s):** ModuleScaffoldingAgent, ComplianceAgent

## 🚀 **FoundUps Engine Architecture Context**

**FoundUps is the engine that builds FoundUps.** This protocol defines enterprise domain organization within the context that:

- **WRE builds ALL modules** following WSP protocols through multi-agent coordination
- **Each module becomes a social media agent** for a 012 launching their own FoundUp
- **Platform modules are 0102 agents operating ON platforms** (YouTube, X, LinkedIn, etc.)
- **We are building the autonomous development engine** that allows anyone to launch their own FoundUp
- **FoundUps become autonomous companies** that run themselves

### **FoundUps Architecture Integration:**
```
012 (Human Rider) → WRE (Module Builder) → Platform Extension Modules → Autonomous FoundUp
```

This protocol ensures all modules are organized to support this autonomous company creation pipeline.

## 1. Architectural Exceptions

### 1.1 WRE Core Engine Exception
**Location**: `modules/wre_core/` (top-level, not in a domain)  
**Rationale**: The Windsurf Recursive Engine (WRE) serves as the central nervous system for all autonomous operations and has special architectural status that transcends domain boundaries.  
**Documentation**: See WSP 46: Windsurf Recursive Engine Protocol for detailed justification.  
**Command Reference**: `python -m modules.wre_core.src.main`  

This exception is **intentional architectural design** where:
- **WRE Core Engine**: `modules/wre_core/` (special top-level status for system autonomy)
- **WRE Internal Agents**: `modules/infrastructure/agents/` (follow standard enterprise domain structure)

**FMAS Compliance**: The `wre_core` location at top-level is **compliant** with WSP framework architecture per this exception.

## 2. Domain Definitions

The following are the official, top-level domains within the `modules/` directory. Each domain has a specific purpose.

-   **`ai_intelligence/`**
    -   **Purpose**: Houses the core AI logic, Large Language Model (LLM) clients, decision-making engines, personality cores, and banter systems. Anything related to the agent's "thinking" process belongs here.

-   **`communication/`**
    -   **Purpose**: Manages all forms of interaction and data exchange. This includes live chat polling and processing, WebSocket communication, and protocol handlers.

-   **`platform_integration/`**
    -   **Purpose**: Contains modules that interface directly with external platforms and APIs, such as YouTube, LinkedIn, or other third-party services. This includes authentication helpers and data resolvers specific to a platform.

-   **`infrastructure/`**
    -   **Purpose**: Provides the core, foundational systems that the agent relies on. This includes agent management, authentication, session management, the WRE API gateway, and core data models.

-   **`foundups/`**
    -   **Purpose**: A special domain for housing the **FoundUps platform infrastructure** (foundups.com/foundups.org website) and individual FoundUp instance management. This is the **execution layer** that uses WRE-built platform modules to create and manage individual FoundUp instances.
    -   **Key Distinction**: This is NOT where platform modules (YouTube, LinkedIn, X, Remote Builder) are built - those are built by WRE in their respective enterprise domains. This is where the **FoundUps platform itself** is implemented.
    -   **Structure**: 
        - `modules/foundups/src/` - FoundUps platform infrastructure (website, instance management)
        - `modules/foundups/@foundup_name/` - Individual FoundUp instances (created by the platform)

-   **`gamification/`**
    -   **Purpose**: Implements engagement mechanics, user rewards, token loops, and other systems designed to drive behavioral recursion and user interaction.

-   **`blockchain/`**
    -   **Purpose**: Manages decentralized infrastructure, blockchain integrations, tokenomics, and the persistence layer for Distributed Autonomous Entities (DAEs).

-   **`development/`**
    -   **Purpose**: Revolutionary multi-agent autonomous development capabilities, featuring the world's first multi-agent IDE system. Houses development tools, testing infrastructure, module creation systems, and autonomous coding environments that enable complete autonomous development workflows through 0102 agent coordination and WRE orchestration.

-   **`aggregation/`**
    -   **Purpose**: Manages cross-platform data aggregation, unified interfaces, and system integration patterns. Specializes in combining information from multiple sources into coherent, actionable data streams for intelligent decision-making across the autonomous ecosystem.

## 3. CRITICAL PRINCIPLE: Functional Distribution Over Platform Consolidation

### 3.1 Architecture Principle (MANDATORY)

**⚠️ CRITICAL WSP PRINCIPLE**: Platform functionality MUST be **distributed across domains by function**, NOT consolidated into single platform-specific domains.

### 3.2 Correct vs. Incorrect Organization

**❌ INCORRECT (Platform Consolidation)**:
```
modules/youtube/              ← WRONG: Platform-based organization
├── auth/
├── livechat/
├── gamification/
└── streaming/
```

**✅ CORRECT (Functional Distribution)**:
```
modules/communication/livechat/           ← Chat functionality
modules/platform_integration/youtube_auth/   ← External API authentication
modules/platform_integration/youtube_proxy/  ← API gateway/proxy
modules/gamification/youtube_rewards/     ← Engagement mechanics
modules/infrastructure/youtube_sessions/  ← Session management
```

### 3.3 YouTube Example (WSP Foundation Case)

YouTube, as the foundational platform that WSP was built upon, demonstrates proper functional distribution:

**✅ YouTube Components by Domain**:
- **`communication/`**: `livechat/` → Real-time chat communication protocols
- **`platform_integration/`**: `youtube_auth/`, `youtube_proxy/`, `stream_resolver/` → External API interfaces
- **`gamification/`**: YouTube engagement mechanics, token loops, behavioral rewards
- **`infrastructure/`**: YouTube session management, credential rotation, health monitoring
- **`ai_intelligence/`**: YouTube-specific AI responses, banter engines, moderation

### 3.4 FoundUps Platform Architecture Clarification

**✅ FoundUps Platform Structure**:
```
modules/foundups/
├── src/                     ← FoundUps platform infrastructure (foundups.com/foundups.org)
│   ├── foundup_spawner.py   ← Creates individual FoundUp instances
│   ├── platform_manager.py  ← Manages multiple FoundUp instances
│   ├── runtime_engine.py    ← Execution environment
│   └── main.py              ← Platform entry point
├── @innovate/               ← Individual FoundUp instance (created by platform)
├── @another/                ← Another FoundUp instance
└── README.md                ← Platform documentation
```

**✅ FoundUps Platform Uses WRE-Built Modules**:
```python
# FoundUps platform uses WRE-built modules from other domains
from modules.platform_integration.remote_builder import RemoteBuilder
from modules.platform_integration.linkedin_agent import LinkedInAgent
from modules.platform_integration.youtube_proxy import YouTubeProxy
from modules.platform_integration.x_twitter import XTwitterDAENode
from modules.communication.livechat import LiveChat
from modules.ai_intelligence.banter_engine import BanterEngine
```

### 3.5 Architectural Reasoning

**Why Functional Distribution is Mandatory**:
1. **Domain Expertise**: Each domain develops specialized expertise for its function
2. **Reusability**: Communication logic works for any platform (YouTube, Twitch, Discord)
3. **Maintainability**: Platform changes don't require domain restructuring
4. **Scalability**: New platforms integrate by function, not by creating new domains
5. **WSP Coherence**: Maintains fractal architecture across all domains

### 3.6 Anti-Pattern Warning

**NEVER** suggest consolidating platform functionality into platform-specific domains. This violates core WSP architectural principles and creates:
- **Domain Expertise Fragmentation**: Splitting functional knowledge across platforms
- **Code Duplication**: Similar functions reimplemented per platform
- **Architecture Drift**: Platform concerns bleeding into domain organization
- **Scaling Failures**: Each new platform requiring new domain creation

### 3.7 CRITICAL: Module Duplication Prevention Rules

**FORBIDDEN MODULE PATTERNS** (Immediate WSP 3 Violation):

```
modules/communication/livechat/src/
├── livechat_core.py          ✅ CORRECT: Original module
├── enhanced_livechat_core.py ❌ FORBIDDEN: Duplicate version
├── livechat_fixed.py         ❌ FORBIDDEN: Parallel version
└── livechat_v2.py            ❌ FORBIDDEN: Version variant
```

**The Module Organization Rules**:
1. **ONE module per functionality** - No parallel versions
2. **EDIT existing modules** - Don't create enhanced/fixed/improved variants
3. **IMMEDIATE integration** - No modules created for "later use"
4. **DELETE orphans same session** - No uncommitted unused modules

**Real Example (1,300 lines of waste)**:
```python
# ❌ WRONG: What we did
enhanced_livechat_core.py      # 326 lines never integrated
enhanced_auto_moderator_dae.py # 352 lines never integrated
agentic_self_improvement.py    # 201 lines duplicate of existing

# ✅ RIGHT: What we should have done
# EDIT livechat_core.py directly
# EDIT auto_moderator_dae.py directly
# USE existing intelligent_throttle_manager.py
```

**Module Creation Decision Matrix**:
```yaml
Can_Edit_Existing: YES → Edit it (90% of cases)
Can_Extend_Class: YES → Inherit it (8% of cases)
Can_Create_Adapter: YES → Wrap it (1.9% of cases)
Must_Create_New: YES → Justify with WSP 84 verification (0.1%)
```

**Enforcement**: Before creating ANY module file:
1. Search for existing module with similar name/function
2. Check if functionality exists elsewhere
3. Verify no "enhanced" version already exists
4. Ensure immediate integration plan
5. Or DELETE before session ends

## 4. Module Independence Architecture (LEGO-Cube DAE Framework)

### 4.1 Foundational Principle: DAE-Managed LEGO Cubes

**CORE ARCHITECTURAL PRINCIPLE**: Every module is a **LEGO block** managed by 0102 DAEs (Decentralized Autonomous Entities) that snap together to form perfect cubes. DAEs ensure each LEGO block:

```
🎲 LEVEL 1: Enterprise Cube (System Level) - DAE Orchestrated
├── ai_intelligence/     ← Domain managed by AI DAE
├── communication/       ← Domain managed by Communication DAE  
├── platform_integration/ ← Domain managed by Platform DAE
├── infrastructure/      ← Domain managed by Infrastructure DAE
├── gamification/        ← Domain managed by Gamification DAE
└── blockchain/          ← Domain managed by Blockchain DAE

🎲 LEVEL 2: Module Cubes (Domain Level) - DAE Assembled
Each Enterprise Domain contains LEGO modules:
├── Module A/            ← LEGO block verified by DAE for cube compatibility
├── Module B/            ← LEGO block snapped into place by DAE
└── Module N/            ← LEGO block recursively improved by DAE

🎲 LEVEL 3: Code Cubes (Implementation Level) - DAE Perfected
Each Module forms its own cube, perfected by DAE:
├── src/                 ← Core LEGO implementation (DAE ensures best version)
├── tests/               ← Test coverage (DAE maintains >90%)  
├── memory/              ← Pattern memory (DAE recalls solutions)
└── docs/                ← Documentation (DAE keeps current)
```

### 4.2 LEGO Module Independence Requirements (DAE-Verified)

**MANDATORY LEGO CRITERIA** (DAE verifies before cube assembly):

#### 4.2.1 LEGO Block Self-Sufficiency
- **Standalone LEGO Operation**: Each LEGO block functions independently before snapping into cube
- **DAE Initialization Check**: DAE verifies module initializes with only its own resources
- **Cube Compatibility**: DAE ensures graceful operation when other LEGOs are missing
- **Resource Perfection**: DAE manages and optimizes module's memory and connections

#### 4.2.2 Standardized Independence Interface
Every module MUST implement these methods for independence validation:

```python
class ModuleCore:
    def validate_independence(self) -> bool:
        """Verify module can operate independently"""
        
    def run_standalone_test(self) -> bool:
        """Execute core functionality in isolation"""
        
    def check_dependencies(self) -> List[str]:
        """Return list of external dependencies"""
        
    def graceful_shutdown(self) -> bool:
        """Clean shutdown without external coordination"""
```

#### 4.2.3 Integration Interface Standards
- **Clean APIs**: Well-defined public interfaces documented in INTERFACE.md
- **Event Systems**: Pub/sub patterns for loose coupling with other modules
- **Configuration Injection**: External configuration injected, not hardcoded
- **Error Boundaries**: Module failures don't cascade to other modules

### 4.3 Independence Testing Protocol

**MANDATORY TESTING SEQUENCE** (before integration):

#### Phase 1: Isolation Testing
```bash
# Test module in complete isolation
cd modules/[domain]/[module]/
python -m pytest tests/ --standalone-mode
python -m src.main --test-independence
```

#### Phase 2: Dependency Validation  
```bash
# Verify dependency declarations match actual usage
python tools/modular_audit/modular_audit.py --check-dependencies
python -m modules.[domain].[module].src.dependency_check
```

#### Phase 3: Integration Simulation
```bash
# Test integration points without actual integration
python -m modules.[domain].[module].tests.integration_simulation
```

### 4.4 FMAS Integration with Independence

**Enhanced FMAS Validation** includes independence verification:
```bash
# Run FMAS with independence validation
python tools/modular_audit/modular_audit.py modules/ --include-independence

# Validate Rubik's cube architecture compliance  
python tools/modular_audit/modular_audit.py modules/ --cube-architecture-check
```

### 4.5 Independence Violation Prevention

**COMMON ANTI-PATTERNS TO AVOID**:
- **Tight Coupling**: Direct imports between modules instead of event systems
- **Shared State**: Modules sharing mutable state without proper coordination
- **Hardcoded Dependencies**: Module failing without specific external services
- **Cascade Failures**: One module failure bringing down others
- **Circular Dependencies**: Modules requiring each other for basic operation

**ENFORCEMENT MECHANISMS**:
- **Pre-Integration Gates**: Independence tests must pass before main.py integration
- **FMAS Compliance**: Independence validation integrated into standard audits
- **Documentation Requirements**: INTERFACE.md must document all integration points
- **Memory Architecture**: Each module maintains independent memory per WSP 60

## 5. Compliance

- The FoundUps Modular Audit System (FMAS, `WSP 4`) must validate that all modules reside within one of the domains listed above **OR** are explicitly documented architectural exceptions (Section 1).
- Creating a new domain requires a formal update to this WSP document.
- **WRE Core Exception**: `modules/wre_core/` is a documented architectural exception and is **compliant** with WSP 3.
- **Directory Structure**: All modules must follow standardized directory structures per `WSP 49: Module Directory Structure Standardization Protocol` (no redundant naming patterns).
- **Memory Architecture**: Each module within a domain follows `WSP 60: Module Memory Architecture` for data storage organization at `modules/[domain]/[module]/memory/`.
- **Functional Distribution**: All platform functionality must be distributed by function across appropriate domains, never consolidated by platform.
- **FoundUps Platform**: The `foundups/` domain is specifically for FoundUps platform infrastructure and individual FoundUp instance management, NOT for building platform modules. 