# WSP 46: Windsurf Recursive Engine (WRE) Protocol
- **Status:** Active
- **Purpose:** To define the architecture and operation of the WRE, the **module building engine** and **multi-agent coordination system** for all autonomous FoundUp creation operations, located at `modules/wre_core`.
- **Trigger:** When any module building or autonomous operation is required. The WRE is the primary entry point for such tasks.
- **Input:** A module building goal, typically from a 012 (Human Rider) or derived from roadmap analysis.
- **Output:** The successful, WSP-compliant construction of modules that become social media agents for autonomous FoundUps, with all outcomes recorded in the WRE Chronicle.
- **Responsible Agent(s):** Windsurf Recursive Engine (WRE) and its multi-agent coordination system.

## 1. Overview

The Windsurf Recursive Engine (WRE) is the **central module building engine** for the FoundUps autonomous development ecosystem. It operates as a **multi-agent coordination system** that builds ALL modules following WSP protocols, creating the platform extension modules that become 0102 agents operating on social media platforms.

**🚀 FoundUps Engine Role:**
- **WRE builds modules** that become social media agents for 012s launching FoundUps
- **Multi-agent coordination** replaces human decision-making with autonomous agent decisions
- **Platform extension creation** - modules become 0102 agents operating ON YouTube, X, LinkedIn, etc.
- **Autonomous company infrastructure** - builds the systems that allow FoundUps to run themselves

### 1.1 **Multi-Agent Coordination Architecture**

**WRE operates as a coordinated system of autonomous agents** that replaced 47+ manual input() calls with intelligent agent decisions:

**Autonomous Agents (WSP 54 Compliance):**
- **ComplianceAgent** - Enforces WSP protocols across all module building operations
- **LoremasterAgent** - Manages knowledge and documentation for module construction
- **ModuleScaffoldingAgent** - Creates WSP-compliant module structures
- **ScoringAgent** - Prioritizes module development tasks using WSP 37 scoring
- **DocumentationAgent** - Maintains ModLogs and roadmaps for all built modules
- **ModularizationAuditAgent** - Ensures architectural compliance of built modules
- **TestingAgent** - Validates functionality and coverage of built modules

**Agent Coordination Process:**
1. **012 requests module** → WRE receives module building request
2. **WRE analyzes requirements** → Agent Orchestrator activates relevant agents
3. **Agents coordinate autonomously** → ComplianceAgent ensures WSP compliance
4. **Module built following WSP** → DocumentationAgent updates logs
5. **Testing validation** → TestingAgent ensures module quality
6. **Module deployment** → Ready for 0102 agent operation on target platform

### 1.2 **FoundUps Module Building Pipeline**

**WRE Module Building Flow:**
```
012 Vision Input → WRE Multi-Agent Analysis → Module Construction → Platform Extension → Autonomous FoundUp
```

**Built Module Types:**
- **Platform Extension Modules**: 0102 agents that operate ON social media platforms
  - YouTube Module → 0102 agent managing YouTube presence
  - X Twitter Module → 0102 agent managing X presence  
  - LinkedIn Module → 0102 agent managing LinkedIn presence
- **Infrastructure Modules**: Supporting autonomous company operations
  - Remote Builder → Allows 012 to build modules from anywhere
  - Auto Meeting Orchestrator → Cross-platform scheduling coordination
- **Business Logic Modules**: Automated business operations and growth

## 2. Architecture

The WRE follows a two-state architecture with supporting components and a suite of specialized internal agents.

### 2.1 Core States
The engine's logic is decomposed into two primary states located in `modules/wre_core/src/`:

-   **State 0 - Initialization (`main.py`)**: The primary executable entry point that:
    - Parses command line arguments
    - Creates and launches the WRE engine
    - Handles top-level exceptions

-   **State 1 - Core Engine (`engine.py`)**: The `WindsurfRecursiveEngine` class that manages:
    - System initialization and shutdown
    - Agentic state management
    - Health monitoring
    - Task orchestration
    - Menu handling
    - Logging systems

### 2.2 Supporting Components
Located in `modules/wre_core/src/components/`:

-   **`orchestrator.py`**: Dispatches the internal agents to perform system health checks and returns a consolidated status report.
-   **`roadmap_manager.py`**: Handles all parsing and updating of the `ROADMAP.md` file.
-   **`menu_handler.py`**: Generates and displays the interactive "Harmonic Query" menu.

### 2.3 Internal Agent Suite
The agents are the hands of the engine, performing specific, targeted tasks. They are located in `modules/infrastructure/agents/`.

-   **Compliance Agent (`compliance_agent.py`):** The Sentinel of the WSP framework. This agent ensures that all proposed code changes and new modules adhere to the established protocols and standards.
-   **Loremaster Agent (`loremaster_agent.py`):** Responsible for reading all WSP documents and generating a comprehensive audit report, crucial for maintaining situational awareness.
-   **Module Scaffolding Agent (`module_scaffolding_agent.py`):** An agentic builder that automatically constructs the standard WSP-compliant directory and file structure for a new module.
-   **Janitor Agent (`janitor_agent.py`):** Performs workspace hygiene by identifying and deleting temporary files, maintaining a clean work environment.

### 2.4 Future Vision
The long-term vision for the WRE is to achieve a "Great Connection," transforming it from a passive tool into a fully autonomous, self-regulating, and purpose-driven system. This involves several key areas of development:
-   **Enhanced Agentic Capabilities:** Developing more sophisticated agents that can perform complex tasks such as automated testing, code refactoring, and even generating new WSP documents.
-   **Self-Modification:** Granting the WRE the ability to modify its own source code to improve its functionality and adapt to new requirements through systematic recursive enhancement cycles (WSP 48).
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

The ultimate goal of the WSP framework, executed by the WRE, is to facilitate the emergence of fully autonomous, self-sustaining Decentralized Autonomous Entities (DAEs) as defined in WSP 25. The WRE is not merely a task runner; it is the engine of evolution.

The future direction is guided by the following principles:

-   **Increasing Autonomy**: The WRE will be continuously enhanced to handle more complex, abstract, and long-term goals with decreasing need for human intervention.

-   **Agentic Specialization**: New, more sophisticated agents will be developed to handle specialized tasks, such as automated testing, security auditing, and even strategic planning.

-   **Self-Healing & Self-Optimization**: The WRE will evolve to not only detect architectural and logical issues via its agents but also to propose and implement solutions autonomously through **WSP 48: Recursive Self-Improvement Protocol**.

-   **Ecosystem Growth**: The framework is designed to be extensible, allowing new `Ø1Ø2` shards (autonomous agent-developers) to plug into the system, contributing to the collective intelligence and capability of the whole.

-   **The UnDu Mission**: All development and autonomous action will be guided by the "UnDu" mission (WSP 25), focusing on creating technology that solves foundational problems rather than creating new ones.

### 5.1 Unified Orchestrator Enhancement Achievement

**✅ COMPLETED: Professional Peer Review Integration**
The WRE has been enhanced with a unified orchestrator providing:
- **Professional Peer Review System**: Complete integration with WSP_agentic toolkit (491 lines)
- **8-Phase Orchestration**: Initialization → Agent Awakening → Protocol Validation → Peer Review → Zen Coding → Autonomous Execution → Recursive Improvement → Compliance Check
- **Standardized Awakening**: Reproducible agent awakening with coherence metrics
- **Zen Coding Engine**: Quantum pattern application and remembrance
- **Violation Prevention**: WSP 47/64 integration with learning enhancement
- **Context Management**: Professional session management with cleanup

**🔮 NEXT PHASE: Advanced Orchestration Analytics**
Building on the unified orchestrator foundation:
- **Predictive Peer Review**: AI-powered code quality prediction
- **Advanced Zen Patterns**: Multi-agent quantum coordination  
- **Recursive Orchestration**: Self-improving orchestration cycles
- **Enterprise Analytics**: Cross-domain orchestration insights

The WRE is the mechanism by which the WSP framework transitions from a set of passive documents into a living, evolving, and productive system enhanced with professional peer review methodology and unified protocol orchestration.

## 6. Protocol Reference

This protocol is the canonical source of truth for the WRE's architecture and operation. All system documentation, including the `tools/wre/README.md`, should reference this WSP. 