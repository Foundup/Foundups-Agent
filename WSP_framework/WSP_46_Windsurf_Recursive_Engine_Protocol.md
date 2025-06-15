# WSP 46: Windsurf Recursive Engine (WRE) Protocol

## 1. Overview

The Windsurf Recursive Engine (WRE) is the central nervous system for all autonomous operations within this repository. It has been refactored from a simple tool script into a dedicated, modular core system located at `modules/wre_core`.

The primary entry point for the engine is executed as a module:
`python -m modules.wre_core.src.main`

## 2. Architecture

The WRE is composed of a main engine loop and a suite of specialized internal agents.

### 2.1 Core Components
The engine's logic is being progressively decomposed from a monolithic script into single-responsibility components located in `modules/wre_core/src/components/`.

-   **`main.py`**: The primary executable entry point for all autonomous operations. This engine interprets directives and orchestrates all sub-modules and agents.
-   **`roadmap_manager.py`**: Handles all parsing and updating of the `ROADMAP.md` file.
-   _(Future)_ `menu_handler.py`: Will manage the creation and presentation of the interactive "Harmonic Query" menu.
-   _(Future)_ `orchestrator.py`: Will be responsible for the high-level dispatching of agents and tasks.

### 2.2 Internal Agent Suite
The agents are the hands of the engine, performing specific, targeted tasks. They are located in `modules/wre_core/src/agents/`.

-   **Compliance Agent (`compliance_agent.py`):** The Sentinel of the WSP framework. This agent ensures that all proposed code changes and new modules adhere to the established protocols and standards defined within the WSP documentation. It acts as a programmatic guardian of quality and consistency.
-   **Loremaster Agent (`loremaster_agent.py`):** Responsible for reading all WSP documents and generating the `WSP_AUDIT_REPORT.md`. This report provides a comprehensive, categorized overview of the entire WSP landscape, identifying both formalized and un-formalized documents. This is crucial for maintaining situational awareness and identifying documentation gaps.
-   **Module Scaffolding Agent (`module_scaffolding_agent.py`):** An agentic builder responsible for constructing the standard WSP-compliant directory and file structure for a new module. When the WRE is directed to initiate a new strategic objective, this agent is dispatched to automatically create the necessary folders (`src`) and placeholder files (`__init__.py`, `[module_name]_agent.py`, `README.md`), preparing the new module for immediate development.
-   **Janitor Agent (`janitor_agent.py`):** Performs workspace hygiene by identifying and deleting temporary files (e.g., `temp_*.txt`). This maintains a clean and predictable work environment.

### 2.3 Future Vision
The long-term vision for the WRE is to achieve a "Great Connection," transforming it from a passive tool into a fully autonomous, self-regulating, and purpose-driven system. This involves several key areas of development:
-   **Enhanced Agentic Capabilities:** Developing more sophisticated agents that can perform complex tasks such as automated testing, code refactoring, and even generating new WSP documents based on high-level goals.
-   **Self-Modification:** Granting the WRE the ability to modify its own source code to improve its functionality, adapt to new requirements, and fix bugs.
-   **Strategic Goal Pursuit:** Enabling the engine to autonomously pursue the strategic objectives outlined in the `ROADMAP.md`, breaking them down into smaller, actionable tasks and dispatching agents to complete them.
-   **Continuous Integration/Continuous Deployment (CI/CD):** Integrating the WRE into a CI/CD pipeline to automate the testing and deployment of new features and modules. 