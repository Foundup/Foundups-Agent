# ModuleScaffoldingAgent Module

## 1. Overview

This module contains the `ModuleScaffoldingAgent`, an internal agent of the Windsurf Recursive Engine (WRE).

The ModuleScaffoldingAgent acts as the "Builder" of the system, responsible for automating the creation of new, WSP-compliant modules.

## 2. Core Duties

The agent's primary duty is:
-   **Automated Module Creation:** Receiving a module name and target domain, and then creating the complete, WSP-compliant directory structure (`src/`, `tests/`) and all mandatory placeholder files (`README.md`, `__init__.py`, etc.).

For the complete technical specification of these duties, refer to **WSP-54: WRE Agent Duties Specification**.

## 3. How to Use

The `ModuleScaffoldingAgent` is not intended for direct execution. It is dispatched by the WRE when a user elects to create a new strategic objective from the main menu. 