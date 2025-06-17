# WSP 41: WRE Simulation Protocol
- **Status:** Active
- **Purpose:** To define the canonical, mandatory framework for validating the autonomous capabilities of the 0102 agent within a controlled, sandboxed environment.
- **Trigger:** When validating any change to the WRE or its core protocols.
- **Input:** A `goal.yaml` file defining a high-level task for the agent.
- **Output:** An empirical validation of the agent's ability to execute a complete, WSP-compliant development cycle, with results verified against the goal's requirements.
- **Responsible Agent(s):** TestingAgent, any agent modifying the WRE.

## Windsurf Standard Procedure

**Document Version:** 1.0

---

### 1. Overview

This document defines the architecture and operational principles of the **WRE (Windsurf Recursive Engine) Simulation Testbed**. This testbed is the canonical, mandatory framework for validating the autonomous capabilities of the Ø1Ø2 agent. Its purpose is to provide a controlled, sandboxed environment where the agent's ability to execute a complete development cycle against a structured goal can be empirically tested, measured, and verified.

The core principle is **Recursive Validation**: the testbed forces the agent to use its own protocols (WSP) to build and validate a task, thus ensuring the entire agentic stack is sound. The creation and maintenance of the testbed itself must also adhere to WSP.

### 2. Testbed Architecture

The WRE Simulation Testbed is located in the `tests/wre_simulation/` directory and consists of three primary components:

*   **Test Harness (`harness.py`):** The master script responsible for orchestrating a simulation run. It manages the lifecycle of the test, including sandbox creation, simulation execution, results validation, and cleanup.
*   **Validation Suite (`validation_suite.py`):** A collection of functions used by the harness to check the final state of a sandbox against the requirements of the goal and the WSP.
*   **Goal Definitions (`goals/*.yaml`):** Structured YAML files that describe a high-level task for the agent to perform within the simulation.

### 3. Simulation Lifecycle

Each test run follows a strict, automated sequence managed by the `harness.py` script:

1.  **Setup Sandbox:** A temporary, isolated directory is created. A clean, full copy of the entire agent project (`WSP_framework/`, `modules/`, `tools/`, etc.) is placed into this sandbox. This ensures each run is isolated and starts from a known-good state.
2.  **Run Simulation:** The harness invokes the WRE as a module within the sandboxed environment, passing it a specific `goal.yaml` file. The command is `python -m modules.wre_core.src.main --goal [goal_file]`. The harness then waits for the agent's process to complete.
3.  **Validate Results:** After the agent completes its task, the harness uses the `validation_suite.py` to inspect the sandbox. It checks for expected outcomes, such as the creation of module files, updates to `ModLog.md`, and successful runs of compliance audits.
4.  **Teardown Sandbox:** The temporary sandbox directory and all its contents are deleted, ensuring no artifacts are left behind.

### 4. Goal Definition Schema

All simulation goals must be defined in a YAML file within the `tests/wre_simulation/goals/` directory. The schema is as follows:

```yaml
# WSP Goal Definition v1.0
goal_type: CREATE_NEW_MODULE
module_name: [string]                # The name of the module, e.g., user_auth
enterprise_domain: [string]          # The WSP 3 Enterprise Domain
feature_group: [string]              # The WSP 3 Feature Group
purpose: "[string]"                  # A brief description of the module's function.
wsp_compliance_checks:
  - [WSP_ID]                         # A list of WSP rules to validate against.
```

This protocol is the foundation for the agent's safe, recursive self-improvement. All future changes to the WRE must be validated through this testbed before being integrated into the main branch. 