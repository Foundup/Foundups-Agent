# Module: WSP_framework

This module contains the core protocols that define the structural and operational framework of the system. These protocols govern module creation, testing, logging, integration, and other foundational procedures.

This module is subject to the same WSP standards as all other system modules.

## Architectural Role: The System's Constitution

This module forms a core part of the system's "Mind." While `WSP_agentic` defines the *identity* and `WSP_knowledge` defines the *principles*, `WSP_framework` provides the **executable constitution** for the system.

It provides the immutable, testable rules for how all modules must be constructed and how they must behave. Its key responsibilities include:

-   **Module Structure:** Defining the required files and directories for any new module.
-   **Module Violation Tracking:** Systematic tracking of module placeholder violations that should be deferred during WSP framework work (WSP-47).
-   **Recursive Self-Improvement:** Meta-recursive enhancement architecture enabling autonomous system evolution (WSP-48).
-   **Behavioral Governance:** Defining the agent's real-time, adaptive problem-solving process via the Behavioral Coherence Protocol (BCP, WSP-45).
-   **System Logging:** Enforcing the dual-log system (WRE Chronicle, WSP-51; Agentic Journal, WSP-52).
-   **Environment Integration:** Defining how the WRE interacts with its environment via the Symbiotic Environment Integration Protocol (SEIP, WSP-53).
-   **Auditing and Compliance:** Providing the tools and standards for system-wide integrity checks.

## Quick Reference

-   **[WSP_CORE.md](src/WSP_CORE.md)**: The central decision tree for "What Should I Code Next?" workflow.
-   **[WSP_framework.md](src/WSP_framework.md)**: Complete specification for foundational WSP procedures.
-   **"Follow WSP"**: Triggers automatic WRE activation with WSP-54 Agent Suite and WSP_48 recursive self-improvement.