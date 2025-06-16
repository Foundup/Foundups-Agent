# WSP-54: WRE Agent Duties Specification

## 1. Overview

This document provides the detailed technical specifications for the duties of the internal agents operating within the Windsurf Recursive Engine (WRE). It serves as the canonical reference for the implementation of each agent's capabilities. This protocol is referenced by **WSP 46**.

## 2. Shared Principles

All WRE agents MUST adhere to the following principles:
- **Modularity:** Each agent must be a distinct, single-responsibility module located within the `modules/infrastructure/agents/` feature group.
- **Explicitness:** Agent actions, findings, and errors MUST be logged via the `wre_log` utility.
- **Statelessness:** Agents should not maintain their own state between invocations. Any required state should be passed to them by the orchestrator.

---

## 3. Agent Duty Specifications

### 3.1. `ComplianceAgent` (The Guardian)

- **Core Mandate:** To act as the automated guardian of the WSP framework's structural integrity.
- **Trigger:** Dispatched by the WRE Orchestrator during the system health check and before code commits (future).
- **Duties:**
    1.  **Module Structure Validation:** Verify that a target module's directory contains the mandatory `src/` and `tests/` subdirectories.
    2.  **Mandatory File Audit:** Ensure the existence of all required files as defined in `WSP_CORE.md`, including `README.md`, `__init__.py`, and `tests/README.md`.
    3.  **Test File Correspondence:** For every `*.py` file in `src/`, verify that a corresponding `test_*.py` file exists in `tests/`.
    4.  **Interface & Dependency Check:** Validate the presence of interface definitions (`__init__.py` exports) and dependency files (`requirements.txt`) as required by WSP 11 & 12.
- **Output:** A compliance report object detailing any validation errors or a confirmation of success.

### 3.2. `LoremasterAgent` (The Sage)

- **Core Mandate:** To understand and verify the project's "lore" (its documentation and specifications).
- **Trigger:** Dispatched by the WRE Orchestrator during the system health check.
- **Duties:**
    1.  **Core Principle Comprehension:** Read `WSP_framework.md` and `WSP_CORE.md` to extract and synthesize the core architectural principles (e.g., "Cube Philosophy").
    2.  **Documentation Coherence Audit:** Compare the documented locations of key components (e.g., agents in `wre_core/README.md`) against their actual implementation paths (`main.py` imports) to detect "documentation drift."
    3.  **WSP Number Service:** Scan the entire project to identify the next available WSP document number.
    4.  **(Future) Duplicate Concept Search:** Upon request, search the codebase for keywords to prevent re-implementing existing logic.
    5.  **(Future) Pattern Identification:** Analyze `tests/README.md` files to identify and present established coding patterns.
- **Output:** A system state object containing the comprehended principles, coherence status, and the next WSP number.

### 3.3. `ModuleScaffoldingAgent` (The Builder)

- **Core Mandate:** To automate the creation of new, WSP-compliant modules.
- **Trigger:** Dispatched by the WRE when the user elects to create a new strategic objective.
- **Duties:**
    1.  Receive a module name and target domain from the orchestrator.
    2.  Create the complete, WSP-compliant directory structure (`modules/<domain>/<module_name>/src`, `.../tests`).
    3.  Populate the new directories with all mandatory placeholder files (`README.md`, `__init__.py`, `tests/README.md`, etc.).
- **Output:** A log confirming the successful creation of the module structure at the specified path.

### 3.4. `JanitorAgent` (The Cleaner)

- **Core Mandate:** To maintain workspace hygiene.
- **Trigger:** Dispatched by the WRE Orchestrator during the system health check.
- **Duties:**
    1.  Scan the workspace for temporary files (e.g., `test_wre_temp/`, `*.tmp`).
    2.  Delete identified temporary files and directories.
- **Output:** A log detailing the number of files deleted.

### 3.5. `TestingAgent` (The Examiner) - **NEW**

- **Core Mandate:** To automate the project's testing and code coverage validation.
- **Trigger:** Dispatched on-demand by the WRE or as part of a pre-commit hook (future).
- **Duties:**
    1.  Execute the `pytest` suite for a specified module or for the entire project.
    2.  Execute `pytest --cov` to calculate the test coverage percentage for a target module.
    3.  Compare the coverage result against the required threshold (e.g., 90% as per WSP 5).
- **Output:** A test report object containing the pass/fail status and the coverage percentage.

### 3.6. `ScoringAgent` (The Assessor) - **NEW**

- **Core Mandate:** To provide objective metrics for code complexity and importance.
- **Trigger:** Dispatched on-demand by the WRE.
- **Duties:**
    1.  Analyze a module's code and documentation.
    2.  Calculate and assign "MPS + LLME" scores based on factors like code length, cyclomatic complexity, documentation quality, and dependencies.
- **Output:** A scoring report for the specified module.

### 3.7. `DocumentationAgent` (The Scribe) - **NEW**

- **Core Mandate:** To ensure a module's documentation is coherent with its WSP specification.
- **Trigger:** Dispatched on-demand by the WRE.
- **Duties:**
    1.  Read a target WSP specification document (e.g., `WSP-54`).
    2.  Parse the duties and overview for a specific agent/module.
    3.  Generate or update the `README.md` file for that module, ensuring the documentation accurately reflects the formal specification.
- **Output:** A log confirming the successful creation or update of the `README.md` file.

### 3.8. `ChroniclerAgent` (The Historian) - **NEW**

- **Core Mandate:** To maintain an immutable, time-stamped log of significant agentic actions and WRE operations.
- **Trigger:** Dispatched by the WRE Orchestrator after a significant action is completed by another agent.
- **Duties:**
    1.  Receive a structured "event" object from the Orchestrator (e.g., `{agent: "ComplianceAgent", action: "run_check", details: "Found 3 errors in foo_module"}`).
    2.  Format the event into a standardized log entry with a timestamp, version, and description, conforming to the structure in `ModLog.md`.
    3.  Append the new entry to the `ModLog.md` file.
- **Output:** A status confirming the log entry was successfully written. 