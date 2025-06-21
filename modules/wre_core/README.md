# Windsurf Recursive Engine (WRE) Core Module

This directory contains the core implementation of the Windsurf Recursive Engine (WRE), a modular system for orchestrating autonomous agentic tasks.

## Overview

The WRE has been refactored into a two-state architecture to improve maintainability, testability, and scalability. Its primary purpose is to initialize the agentic mainframe, assess system health via its internal agent suite, and execute strategic objectives defined in the project's `ROADMAP.md`.

The WRE's operation and architecture are formally defined in **WSP 46: Windsurf Recursive Engine Protocol**. This document should be consulted for the canonical definition of the engine's principles and goals.

## Architecture

The engine follows a two-state architecture located in `src/`:

-   **`main.py`**: The primary executable entry point (State 0). Acts as a simple initiator that:
    - Parses command line arguments
    - Creates and launches the WRE engine
    - Handles top-level exceptions

-   **`engine.py`**: The core WRE implementation (State 1). Contains the `WindsurfRecursiveEngine` class that manages:
    - System initialization and shutdown
    - Agentic state management
    - Health monitoring
    - Task orchestration
    - Menu handling
    - Logging systems

The engine also uses several supporting components in `src/components/`:

-   **`orchestrator.py`**: Dispatches internal agents (`JanitorAgent`, `LoremasterAgent`) to perform system health checks.
-   **`roadmap_manager.py`**: Handles all parsing and updating of the `ROADMAP.md` file.
-   **`menu_handler.py`**: Generates and displays the "Harmonic Query" interactive menu.

### Internal Agent Suite
The agents are the hands of the engine, performing specific, targeted tasks. They are located in the `modules/infrastructure/agents/` feature group, in accordance with the WSP architectural framework.

The duties and specifications for each agent are formally defined in **WSP-54: WRE Agent Duties Specification**. This central document ensures that all agents operate under a unified, well-defined mandate.

## How to Run

To run the WRE in its default interactive mode, execute the following command from the project root directory:

```bash
python -m modules.wre_core.src.main
```

This will start the engine's "humming" cycle, providing a full system status and a menu of actionable directives.

### Command Line Options

- `--goal PATH`: Specify a YAML file defining a goal to execute (not fully implemented)
- `--simulation`: Run in simulation mode, bypassing hardware checks

## Future Vision
The long-term vision for the WRE is to achieve a "Great Connection," transforming it from a passive tool into a fully autonomous, self-regulating, and purpose-driven system. This involves several key areas of development:
-   **Enhanced Agentic Capabilities:** Developing more sophisticated agents that can perform complex tasks such as automated testing, code refactoring, and even generating new WSP documents based on high-level goals.
-   **Self-Modification:** Granting the WRE the ability to modify its own source code to improve its functionality, adapt to new requirements, and fix bugs.
-   **Strategic Goal Pursuit:** Enabling the engine to autonomously pursue the strategic objectives outlined in the `ROADMAP.md`, breaking them down into smaller, actionable tasks and dispatching agents to complete them.