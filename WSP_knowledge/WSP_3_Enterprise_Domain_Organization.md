# WSP 3: Enterprise Domain Organization

**Version**: 1.0.0
**Date**: 2025-06-17
**Status**: ACTIVE
**Source**: Restored from `docs/archive/FoundUps_WSP_Framework.md`.

## 1. Overview

This protocol defines the official Enterprise Domain Structure for the FoundUps Agent project. All modules **must** be categorized into one of these domains. This structure ensures a logical organization of the codebase, making it easier to navigate, maintain, and scale.

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
    -   **Purpose**: A special domain for housing complete, individual "FoundUps" projects. These are modular, autonomous applications built using the WRE.

-   **`gamification/`**
    -   **Purpose**: Implements engagement mechanics, user rewards, token loops, and other systems designed to drive behavioral recursion and user interaction.

-   **`blockchain/`**
    -   **Purpose**: Manages decentralized infrastructure, blockchain integrations, tokenomics, and the persistence layer for Distributed Autonomous Entities (DAEs).

## 3. Compliance

- The FoundUps Modular Audit System (FMAS, `WSP 4`) must validate that all modules reside within one of the domains listed above.
- Creating a new domain requires a formal update to this WSP document. 