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

- **`AgentRegistry`**: A persistence layer that maintains a record of known agents and their status in the `memory/` directory, allowing for stateful awareness across system restarts.

## 3. Orchestration Role

In the "Conductor and the Orchestra" model, this module acts as the Orchestra's Librarian. It doesn't play an instrument but is responsible for providing the correct sheet music (the `AgentIdentity`) to the Conductor (`_proxy` modules) before the performance begins. The proxy then uses this identity to interact with other services. 