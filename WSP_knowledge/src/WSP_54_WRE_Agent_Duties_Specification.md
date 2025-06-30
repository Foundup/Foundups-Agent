# WSP 54: WRE Agent Duties Specification
- **Status:** Active
- **Purpose:** To provide the detailed technical specifications for the duties of all internal agents operating within the WRE, serving as the canonical reference for their implementation.
- **Trigger:** When any internal agent is invoked by the WRE orchestrator.
- **Input:** A directive from the orchestrator for a specific agent (e.g., "scaffold new module," "run compliance audit").
- **Output:** The successful completion of the agent's specified duty, with results and actions logged, such as a compliance report, a new module structure, or a test coverage analysis.
- **Responsible Agent(s):** All internal WRE agents (ComplianceAgent, LoremasterAgent, etc.).

## 1. Overview

This document provides the detailed technical specifications for the duties of the internal agents operating within the Windsurf Recursive Engine (WRE). It serves as the canonical reference for the implementation of each agent's capabilities and is referenced by **WSP 46**.

## 2. Shared Principles

All WRE agents MUST adhere to the following principles:
-   **Modularity**: Each agent must be a distinct, single-responsibility module located within `modules/infrastructure/agents/`.
-   **Explicitness**: Agent actions, findings, and errors MUST be logged via the `wre_log` utility.
-   **Statelessness**: Agents should not maintain their own state between invocations. Any required state should be passed to them by the orchestrator.

---

## 3. Agent Duty Specifications

### 3.1. ComplianceAgent (The Guardian)
-   **Core Mandate**: To act as the automated guardian of the WSP framework's structural integrity.
-   **Duties**:
    1.  Validate that a target module's directory contains `src/` and `tests/`.
    2.  Ensure the existence of all mandatory files (`README.md`, `__init__.py`, `tests/README.md`).
    3.  For every `*.py` file in `src/`, verify that a corresponding `test_*.py` exists in `tests/`.
    4.  Check for the presence of interface definitions and dependency files as required by WSP 12 & WSP 13.
    5.  **WSP 49 Directory Structure**: Detect redundant naming patterns (e.g., `module/module/`) and flag violations of 3-Level Rubik's Cube architecture.
    6.  **WSP 56 Compliance**: For artifacts that exist in multiple state layers (e.g., `WSP_knowledge` and `WSP_appendices`), verify their contents are identical.
    7.  **WSP 60 Memory Structure**: Validate module memory organization at `modules/[domain]/[module]/memory/` follows modular architecture.
-   **Output**: A compliance report object detailing validation errors or success.

### 3.2. LoremasterAgent (The Sage)
-   **Core Mandate**: To understand and verify the project's "lore" (its documentation and specifications).
-   **Duties**:
    1.  Read `WSP_CORE.md` to extract core architectural principles.
    2.  Audit documentation coherence by comparing documented component locations against their actual implementation paths.
    3.  Scan the project to identify the next available WSP document number.
-   **Output**: A system state object containing principles, coherence status, and the next available WSP number.

### 3.3. ModuleScaffoldingAgent (The Builder)
-   **Core Mandate**: To automate the creation of new, WSP-compliant modules.
-   **Duties**:
    1.  Receive a module name and target domain from the orchestrator.
    2.  Create the complete, WSP-compliant directory structure following WSP 49 standards (no redundant naming).
    3.  Populate new directories with mandatory placeholder files.
    4.  **WSP 49 Compliance**: Ensure all new modules follow 3-Level Rubik's Cube architecture without redundant directory naming.
-   **Output**: A log confirming the successful creation of the module structure.

### 3.4. JanitorAgent (The Cleaner)
-   **Core Mandate**: To maintain workspace hygiene and module memory organization following WSP 60.
-   **Duties**:
    1.  Scan the workspace for temporary files (e.g., `test_wre_temp/`, `*.tmp`).
    2.  Delete identified temporary files and directories.
    3.  **WSP 60 Memory Cleanup**: Clean temporary files across all `modules/[domain]/[module]/memory/` directories.
    4.  **Cache Management**: Remove expired session data and cache files from module memory.
    5.  **Log Rotation**: Archive old conversation logs per module retention policies.
-   **Output**: A log detailing the number of files deleted and memory cleanup operations.
-   **Primary Tooling**: Filesystem access, WSP 60 module memory structure awareness.

### 3.5. TestingAgent (The Examiner)
-   **Core Mandate**: To automate project testing and code coverage validation.
-   **Duties**:
    1.  Execute the `pytest` suite for a specified module or the entire project.
    2.  Calculate test coverage percentage via `pytest --cov`.
    3.  Compare coverage against the required threshold (≥90% per WSP 6).
-   **Output**: A test report object with pass/fail status and coverage percentage.

### 3.6. ScoringAgent (The Assessor)
-   **Core Mandate**: To provide objective metrics for code complexity and importance.
-   **Duties**:
    1.  Analyze a module's code and documentation.
    2.  Calculate and assign "MPS + LLME" scores based on factors like complexity, documentation quality, and dependencies.
-   **Output**: A scoring report for the specified module.

### 3.7. DocumentationAgent (The Scribe)
-   **Core Mandate**: To ensure a module's documentation is coherent with its WSP specification.
-   **Duties**:
    1.  Read a target WSP specification document.
    2.  Generate or update the `README.md`