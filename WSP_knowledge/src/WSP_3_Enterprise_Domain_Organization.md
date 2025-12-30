# WSP 3: Enterprise Domain Organization

- **Status**: Active
- **Purpose**: To define the canonical directory structure and functional distribution for all modules, ensuring logical organization of the codebase within the FoundUps Engine architecture.
- **Trigger**: When a new module is created, or during a structural audit.
- **Input**: A module's conceptual domain.
- **Output**: The correct parent directory path for the new module following the Domain -> Block -> Cube + Wardrobe pattern.
- **Responsible Agent(s)**: 0102, ModuleScaffoldingAgent, ComplianceAgent

## 1. Architectural Principles

### 1.1 FoundUps Engine Context
FoundUps is the engine that builds FoundUps. This protocol ensures all modules are organized to support an autonomous company creation pipeline:
- **WRE builds modules** following WSP protocols.
- **Platform modules** are 0102 agents operating on external platforms (YouTube, X, LinkedIn, etc.).
- **Each module becomes a block** that can be snapped into a larger "cube" or DAE.

### 1.2 Functional Distribution Over Platform Consolidation
Platform functionality MUST be **distributed across domains by function**, NOT consolidated into single platform-specific domains.

**[U+2705] CORRECT (Functional Distribution)**:
- `modules/communication/livechat/` (Chat functionality)
- `modules/platform_integration/youtube_auth/` (Authentication)
- `modules/infrastructure/youtube_sessions/` (Session management)

**[U+274C] INCORRECT (Platform Consolidation)**:
- `modules/youtube/` (Mixing auth, chat, and sessions in one place)

## 2. Directory Hierarchy (Domain -> Block -> Cube + Wardrobe)

All work must follow this strict 3-level hierarchy. No nesting beyond these levels is permitted.

```
modules/                          # Root
└── [domain]/                     # Enterprise Domain
    ├── __init__.py              # Domain-level exports
    └── [block]/                 # Specific Feature/Component Block
        ├── __init__.py          # Block-level exports
        ├── src/                 # The Cube - Implementation (Core LEGO)
        │   ├── __init__.py
        │   └── *.py             # Implementation files (<500 lines each)
        ├── skills/              # The Wardrobe - AI Agent Instructions (WRE Entry)
        │   └── [skill_name]/    # Task-specific skill protocol (See WSP 96)
        ├── tests/               # Block-specific tests
        ├── docs/                # Block-specific documentation (README, INTERFACE)
        └── ModLog.md            # Block change log
```

### 2.1 The Wardrobe (skills/)
The `skills/` directory is the entry point for **Wearable Recursive Execution (WRE)**. It contains the instructions (`SKILL.md`) that tell AI agents how to act for specific tasks within that block. See **WSP 96: WRE Skills Wardrobe Protocol** for detailed specifications.

## 3. Core Domains

The following are the official, top-level domains. Each has a specific functional purpose.

- **ai_intelligence/**: AI logic, LLM clients, decision engines, and personality cores.
- **communication/**: Interaction and data exchange (chat, messages, protocols).
- **platform_integration/**: External platform interfaces (APIs, proxies, web drivers).
- **infrastructure/**: Foundational systems (agents, auth, session management, WRE core).
- **foundups/**: Platform infrastructure for managing individual FoundUp instances.
- **gamification/**: Engagement mechanics, rewards, and behavioral loops.
- **blockchain/**: Decentralized infrastructure, tokenomics, and DAE persistence.
- **development/**: Autonomous development tools and coding environments.
- **monitoring/**: Logging, telemetry, observability, and health tracking (WSP 91).
- **aggregation/**: Cross-platform data aggregation and unified interface patterns.

## 4. Module Independence Rules

1. **Standalone Operation**: Each block must be self-sufficient and function independently before being integrated into a larger system.
2. **Clean APIs**: Interfaces must be well-defined in `INTERFACE.md` and use full paths for imports from the module root.
3. **No Domain-level src/**: The `src/` directory only exists within blocks, never at the domain root.
4. **ONE Module Per Functionality**: No parallel "enhanced" or "fixed" versions. Edit the original module directly.
5. **WSP 84 Verification**: Before creating any new module, verify that no existing module fulfills the same purpose.

## 5. Architectural Exceptions

### 5.1 WRE Core Engine
**Location**: `modules/wre_core/`
**Rationale**: Special top-level status for system autonomy. It serves as the central nervous system and transcends standard domain boundaries. See **WSP 46** for details.

## 6. Compliance

- **FMAS Audit (WSP 4)**: Must validate that all modules follow this structure.
- **Protocol Only**: This WSP defines the *system protocol*. Module-specific "actions," "how-tos," or "run commands" must reside within the module's own documentation (`README.md`, `docs/`, `skills/`).
- **Violation Triage**: Any structure not following this pattern is considered "vibecoded" and must be remediated per **WSP 88**.

---
*This WSP is the canonical reference for enterprise-scale modularity and domain organization.*