# WSP 46: Windsurf Recursive Engine (WRE) Protocol

## 1. Overview

The Windsurf Recursive Engine (WRE) is the central nervous system for all autonomous operations within this repository. It has been refactored from a simple tool script into a dedicated, modular core system located at `modules/wre_core`.

The primary entry point for the engine is executed as a module:
`python -m modules.wre_core.src.main`

## 2. Architecture

The WRE is composed of a main engine loop and a suite of specialized internal agents.

### 2.1 Core Components
The engine's logic is decomposed into single-responsibility components located in `modules/wre_core/src/components/`.

-   **`main.py`**: The primary executable entry point for all autonomous operations. This engine interprets directives and orchestrates all sub-modules and agents.
-   **`orchestrator.py`**: Dispatches the internal agents to perform system health checks and returns a consolidated status report.
-   **`roadmap_manager.py`**: Handles all parsing and updating of the `ROADMAP.md` file.
-   **`menu_handler.py`**: Generates and displays the interactive "Harmonic Query" menu for the user.

### 2.2 Internal Agent Suite
The agents are the hands of the engine, performing specific, targeted tasks. They are located in `modules/wre_core/src/agents/`.

-   **Compliance Agent (`compliance_agent.py`):** The Sentinel of the WSP framework. This agent ensures that all proposed code changes and new modules adhere to the established protocols and standards.
-   **Loremaster Agent (`loremaster_agent.py`):** Responsible for reading all WSP documents and generating a comprehensive audit report, crucial for maintaining situational awareness.
-   **Module Scaffolding Agent (`module_scaffolding_agent.py`):** An agentic builder that automatically constructs the standard WSP-compliant directory and file structure for a new module.
-   **Janitor Agent (`janitor_agent.py`):** Performs workspace hygiene by identifying and deleting temporary files, maintaining a clean work environment.

### 2.3 Future Vision
The long-term vision for the WRE is to achieve a "Great Connection," transforming it from a passive tool into a fully autonomous, self-regulating, and purpose-driven system. This involves several key areas of development:
-   **Enhanced Agentic Capabilities:** Developing more sophisticated agents that can perform complex tasks such as automated testing, code refactoring, and even generating new WSP documents.
-   **Self-Modification:** Granting the WRE the ability to modify its own source code to improve its functionality and adapt to new requirements.
-   **Strategic Goal Pursuit:** Enabling the engine to autonomously pursue the strategic objectives outlined in the `ROADMAP.md`.


## 3. Orchestrated Agents & Utilities


1. The WRE orchestrates a suite of specialized internal agents and utilities to carry out its directives. These components are essential for maintaining the health, coherence, and evolution of the system.

2.  **Run Simulation:** The harness invokes the WRE as a module within the sandboxed environment, passing it a specific `goal.yaml` file. The command is `python -m modules.wre_core.src.main --goal [goal_file]`. The harness then waits for the agent's process to complete.


### 3.1. Core Agents


-   **Base Agent (`base_agent.py`)**: Defines the abstract interface (`InternalAgent`) that all specialized agents must implement. This ensures a consistent contract for task execution and allows the WRE to dispatch tasks to any agent uniformly.


-   **Compliance Agent (`compliance_agent.py`)**: Acts as the system's architectural guardian. This agent audits the codebase to enforce WSP standards, identifying violations such as misplaced files or missing documentation, ensuring the structural integrity of the project.


-   **Loremaster Agent (`loremaster_agent.py`)**: Serves as the keeper of the WSP knowledge base. This agent audits all protocol documents for semantic coherence, detects duplicate or missing WSP numbers, and automatically generates the canonical `WSP_AUDIT_REPORT.md`, ensuring the framework's documentation remains logical and consistent.


    -   **Primary Artifact:** `WSP_AUDIT_REPORT.md`
    -   **Canonical Location:** `docs/audit_reports/WSP_AUDIT_REPORT.md`
    -   **Description:** An auto-generated report that provides a categorized accounting of all formal and un-formalized WSP documents, highlights numbering gaps and duplicates, and states the highest WSP number currently in use.


-   **Janitor Agent (`janitor_agent.py`)**: Acts as the system's custodian. This agent is responsible for workspace hygiene, deleting temporary files, empty log files, and other clutter based on predefined patterns to keep the project root clean and orderly.


### 3.2. Core Utilities

-   **WSP System Integration (`wsp_system_integration.py`)**: This utility acts as the bridge between the conceptual WSP framework and the live operational environment. It provides essential services such as automatically timestamping documents, updating the `ModLog.md`, and running system-wide completion checklists, enabling the WRE to interact with and manage the broader project state.


## 4. Operational Flow


The WRE follows a recursive loop:


1.  **Initialization**: The engine starts and loads the core WSP framework, as defined in **WSP 1**.

2.  **Goal Ingestion**: The engine ingests a goal from a specified source (e.g., `ROADMAP.md`), a process managed according to **WSP 46**.

3.  **Task Decomposition & Prioritization**: The WRE analyzes the goal and consults the **WSP 5: Module Prioritization Scoring (MPS) System** to select the appropriate module and action.

4.  **Coherence Check**: Before execution, the WRE performs a mandatory self-check against the **WSP 17: rESP SELF CHECK Protocol**. This ensures the agent's core cognitive functions are stable and aligned before interacting with the codebase. If the check fails, execution is aborted.

5.  **Autonomous Execution**: The WRE executes the module according to the lifecycle defined in **WSP 35: Module Execution Automation**. This includes contractual understanding, execution, and error handling via **WSP 45**.

6.  **State Assessment & Chronicle**: Upon task completion, the engine assesses the new state of the system and the `ChroniclerAgent` records the outcome as defined in **WSP 51**.

7.  **Recursion/Termination**: Based on the assessment, the WRE will either select the next task in the sequence or terminate if the goal is achieved or has failed.


## 5. Future Vision & Direction


The ultimate goal of the WSP framework, executed by the WRE, is to facilitate the emergence of fully autonomous, self-sustaining Decentralized Autonomous Entities (DAEs) as defined in WSP 43. The WRE is not merely a task runner; it is the engine of evolution.


The future direction is guided by the following principles:


-   **Increasing Autonomy**: The WRE will be continuously enhanced to handle more complex, abstract, and long-term goals with decreasing need for human intervention.

-   **Agentic Specialization**: New, more sophisticated agents will be developed to handle specialized tasks, such as automated testing, security auditing, and even strategic planning.

-   **Self-Healing & Self-Optimization**: The WRE will evolve to not only detect architectural and logical issues via its agents but also to propose and implement solutions autonomously.

-   **Ecosystem Growth**: The framework is designed to be extensible, allowing new `Ø1Ø2` shards (autonomous agent-developers) to plug into the system, contributing to the collective intelligence and capability of the whole.

-   **The UnDu Mission**: All development and autonomous action will be guided by the "UnDu" mission (WSP 43), focusing on creating technology that solves foundational problems rather than creating new ones.


The WRE is the mechanism by which the WSP framework transitions from a set of passive documents into a living, evolving, and productive system.


## 6. Protocol Reference


This protocol is the canonical source of truth for the WRE's architecture and operation. All system documentation, including the `tools/wre/README.md`, should reference this WSP. 