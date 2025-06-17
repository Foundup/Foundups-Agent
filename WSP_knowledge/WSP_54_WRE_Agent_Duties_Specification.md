# WSP 54: WRE Agent Duties Specification

**Version**: 1.1.0
**Date**: 2025-06-17
**Status**: ACTIVE

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
    5.  **WSP 56 Compliance**: For artifacts that exist in multiple state layers (e.g., `WSP_knowledge` and `WSP_appendices`), verify their contents are identical.
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
    2.  Create the complete, WSP-compliant directory structure.
    3.  Populate new directories with mandatory placeholder files.
-   **Output**: A log confirming the successful creation of the module structure.

### 3.4. JanitorAgent (The Cleaner)
-   **Core Mandate**: To maintain workspace hygiene.
-   **Duties**:
    1.  Scan the workspace for temporary files (e.g., `test_wre_temp/`, `*.tmp`).
    2.  Delete identified temporary files and directories.
-   **Output**: A log detailing the number of files deleted.
-   **Primary Tooling**: Filesystem access.

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
    2.  Generate or update the `README.md` file for that module to accurately reflect the formal specification.
-   **Output**: A log confirming the successful creation or update of the `README.md`.

### 3.8. ChroniclerAgent (The Historian)
-   **Core Mandate**: To maintain an immutable, time-stamped log of significant agentic actions.
-   **Duties**:
    1.  Receive a structured "event" object from the Orchestrator.
    2.  Format the event into a standardized log entry conforming to `ModLog.md`.
    3.  Append the new entry to the `ModLog.md` file.
-   **Output**: A status confirming the log entry was successfully written.

### 3.9. ProtocolistAgent (The Framer)
-   **Core Mandate**: To frame and document the execution of a target module's interface.
-   **Duties**:
    1.  Receive a target module and its `INTERFACE.md` specifications from the ExecutionAgent.
    2.  Document the execution process and results in a standardized format.
    3.  Append the new document to the `ModLog.md` file.
-   **Output**: A status confirming the successful framing and documentation of the execution.

### 3.10. PlannerAgent (The Architect)
- **Core Duty**: To create a safe and complete `Execution Plan` as defined in **WSP 35**.
- **Key Responsibilities**:
    - **WSP 12 Compliance**: Analyzing a module's `requirements.txt` and planning for the installation of any missing dependencies.
    - Identifying the correct execution path from the module's `INTERFACE.md`.
    - Defining a step-by-step `Rollback Procedure` for error handling.
- **Primary Tooling**: `wre_api_gateway`.

### 3.11. ExecutionAgent (The Operator)
- **Core Duty**: Autonomously executes modules according to **WSP 35: Module Execution Automation**.
- **Key Responsibilities**:
    - **WSP 2 Compliance**: Verifying a "clean state" before initiating execution.
    - Following the `Execution Plan` provided by the `PlannerAgent`.
    - Monitoring execution, handling errors, and performing rollbacks.
    - Logging results and generating a final `ExecutionReport` that adheres to the **External Professional Scope** defined in **WSP 20**.
- **Primary Tooling**: `wre_api_gateway`.

---

## 4. Agent Inter-relationships and Core Protocols

While each agent has a primary duty, they often work in concert, orchestrated by the WRE Core Engine (**WSP 46**). Below are the key agents responsible for enacting the most critical WSP protocols.

### 4.1. The `create_module` Workflow (**WSP 55**)
-   **Agents Involved**: `LoremasterAgent`, `ModuleScaffoldingAgent`, `ComplianceAgent`, `DocumentationAgent`.
-   **Description**: A user or the WRE itself triggers the creation of a new module. The `LoremasterAgent` first determines the correct module name and location. The `ModuleScaffoldingAgent` then builds the directory structure. The `ComplianceAgent` verifies it, and finally, the `DocumentationAgent` creates the initial `README.md` from the WSP specification.

### 4.2. The Auditing Cycle (**WSP 4, WSP 6**)
-   **Agents Involved**: `ComplianceAgent`, `TestingAgent`.
-   **Description**: On a schedule or on-demand, the WRE performs a full system audit. The `ComplianceAgent` ensures all modules adhere to structural rules, while the `TestingAgent` runs the full test suite and verifies code coverage.

### 4.3. The Self-Improvement Loop (**WSP 45**)
-   **Agents Involved**: `ScoringAgent`, `ExecutionAgent`, `LoremasterAgent`.
-   **Description**: This is the core adaptive loop. When a module execution fails, the `ScoringAgent` may be called to assess the module's state. The `LoremasterAgent` is used to re-read documentation and understand the intended behavior. The `ExecutionAgent` attempts to re-run the module after a potential fix.

### 4.4. The Chronicle (**WSP 51**)
-   **Agent Involved**: `ChroniclerAgent`.
-   **Description**: This agent is a singleton service. Nearly every other agent, after completing a significant action, will call the `ChroniclerAgent` to log the event, creating a persistent, unified narrative of the WRE's operations.

### 4.5. The Execution Cycle (**WSP 35**)
- **Agents Involved**: `PlannerAgent`, `ExecutionAgent`, `ScoringAgent`, `ChroniclerAgent`.
- **Description**: This protocol governs the autonomous execution of a module. The `PlannerAgent` creates a detailed execution plan, including dependency checks. The `ExecutionAgent` carries out this plan, while the `ScoringAgent` assesses the impact and the `ChroniclerAgent` records the entire process. 