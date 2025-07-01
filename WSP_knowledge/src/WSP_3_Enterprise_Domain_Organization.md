# WSP 3: Enterprise Domain Organization
- **Status:** Active
- **Purpose:** To define the canonical directory structure for all modules, ensuring logical organization of the codebase.
- **Trigger:** When a new module is created, or during a structural audit.
- **Input:** A module's conceptual domain.
- **Output:** The correct parent directory path for the new module.
- **Responsible Agent(s):** ModuleScaffoldingAgent, ComplianceAgent

This protocol defines the official Enterprise Domain Structure for the FoundUps Agent project. All modules **must** be categorized into one of these domains. This structure ensures a logical organization of the codebase, making it easier to navigate, maintain, and scale.

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

## 4. Compliance

- The FoundUps Modular Audit System (FMAS, `WSP 4`) must validate that all modules reside within one of the domains listed above **OR** are explicitly documented architectural exceptions (Section 1).
- Creating a new domain requires a formal update to this WSP document.
- **WRE Core Exception**: `modules/wre_core/` is a documented architectural exception and is **compliant** with WSP 3.
- **Directory Structure**: All modules must follow standardized directory structures per `WSP 49: Module Directory Structure Standardization Protocol` (no redundant naming patterns).
- **Memory Architecture**: Each module within a domain follows `WSP 60: Module Memory Architecture` for data storage organization at `modules/[domain]/[module]/memory/`.
- **Functional Distribution**: All platform functionality must be distributed by function across appropriate domains, never consolidated by platform.
- **FoundUps Platform**: The `foundups/` domain is specifically for FoundUps platform infrastructure and individual FoundUp instance management, NOT for building platform modules. 