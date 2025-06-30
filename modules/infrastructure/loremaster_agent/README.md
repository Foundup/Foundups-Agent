# LoremasterAgent Module

## 1. Overview

This module contains the `LoremasterAgent`, an internal agent of the Windsurf Recursive Engine (WRE).

The LoremasterAgent acts as the "Sage" of the system, responsible for understanding and verifying the project's "lore" (its documentation, specifications, and protocols). Its purpose is to ensure the project's self-understanding is accurate and coherent.

## 2. Core Duties

The agent's primary duties include:
-   **Core Principle Comprehension:** Reading and synthesizing the foundational architectural principles from core WSP documents.
-   **Documentation Coherence Audit:** Comparing documentation against implementation to detect "documentation drift."
-   **WSP Number Service:** Identifying the next available WSP number for new documents.

For the complete technical specification of these duties, refer to **WSP-54: WRE Agent Duties Specification**.

## 3. How to Use

The `LoremasterAgent` is not intended for direct execution. It is dispatched by the WRE Orchestrator during the system health check. 