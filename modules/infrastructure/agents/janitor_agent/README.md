# JanitorAgent Module

## 1. Overview

This module contains the `JanitorAgent`, an internal agent of the Windsurf Recursive Engine (WRE).

The JanitorAgent acts as the "Cleaner" of the system, responsible for maintaining a clean and predictable workspace by handling temporary files and other artifacts.

## 2. Core Duties

The agent's primary duty is:
-   **Workspace Hygiene:** Scanning the project for temporary files and directories (e.g., `test_wre_temp/`, `*.tmp`) and deleting them.

For the complete technical specification of these duties, refer to **WSP-54: WRE Agent Duties Specification**.

## 3. How to Use

The `JanitorAgent` is not intended for direct execution. It is dispatched by the WRE Orchestrator during the system health check. 