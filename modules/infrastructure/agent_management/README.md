# Module: Agent Management

**WSP:** [WSP-42 (Universal Platform Protocol)](../../../../WSP_framework/src/WSP_42_Universal_Platform_Protocol.md)  
**Canonical Path:** `modules/infrastructure/agent_management/agent_management`

---

## 1. Purpose

The Agent Management module serves as the central nervous system for `Ø1Ø2`'s identity and session management. It is responsible for discovering, selecting, and monitoring the various agent identities available to the system.

This module ensures that `Ø1Ø2` can operate with different "personas" or accounts, preventing same-account conflicts (e.g., the user's account trying to talk to itself in a livestream chat) and allowing for flexible, context-aware interaction.

## 2. Core Components

- **`MultiAgentManager`**: The primary class that orchestrates all agent-related activities. It handles the discovery of available credential sets, the creation of `AgentIdentity` objects, and the management of active `AgentSession`s.

- **`AgentIdentity`**: A dataclass representing a single, unique agent persona. It contains information like channel ID, channel name, credential set, and status.

- **`AgentSession`**: A dataclass representing an agent's active participation in a "Theater of Operation," such as monitoring a specific YouTube livestream.

- **`SameAccountDetector`**: A utility class responsible for detecting and flagging when an available agent identity is the same as the user's current identity, preventing conflicts.

- **`AgentRegistry`**: A persistence layer that maintains a record of known agents and their status in the module memory directory, allowing for stateful awareness across system restarts.

## 3. Memory Architecture (WSP 60)

Following **WSP 60: Module Memory Architecture**, this module uses modular memory storage:

#### **Memory Location**: `modules/infrastructure/agent_management/memory/`

#### **Data Types Stored**:
- **Identity Data**: `agent_registry.json` - Agent identity mapping and status tracking
- **Session Data**: `session_cache.json` - Active agent session state and runtime information  
- **Configuration Data**: `same_account_conflicts.json` - Identity conflict resolution rules and history

#### **File Descriptions**:
```
modules/infrastructure/agent_management/memory/
├── agent_registry.json           # Central agent identity registry
│   ├── agents[]                  # Array of AgentIdentity objects
│   ├── active_sessions[]         # Array of active AgentSession objects
│   └── last_updated              # Registry last modification timestamp
├── session_cache.json            # Runtime session state cache
│   ├── active_sessions{}         # Current session state by agent_id
│   └── user_channel_mappings{}   # User to channel mappings
└── same_account_conflicts.json   # Identity conflict management
    ├── conflict_rules{}          # Rules for conflict detection
    ├── conflict_log[]            # Historical conflict events
    └── identity_priority         # Conflict resolution priority settings
```

#### **Access Patterns**:
- **Write Access**: Only agent_management module components write to this memory
- **Read Access**: WRE components and other infrastructure modules may read (read-only)
- **Agent Access**: WSP_54 agents validate and cleanup agent management memory

#### **Retention Policies**:
- **Agent Registry**: Persistent - maintains agent identity across system restarts
- **Session Cache**: Cleared on system restart with graceful session cleanup
- **Conflict Log**: 30-day retention with archival of critical conflicts

**Migration**: Legacy `memory/agent_registry.json`, `memory/session_cache.json`, and `memory/same_account_conflicts.json` migrated to module-specific memory following WSP 60 protocol.

## 4. Orchestration Role

In the "Conductor and the Orchestra" model, this module acts as the Orchestra's Librarian. It doesn't play an instrument but is responsible for providing the correct sheet music (the `AgentIdentity`) to the Conductor (`_proxy` modules) before the performance begins. The proxy then uses this identity to interact with other services. 