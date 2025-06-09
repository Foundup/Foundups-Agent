[SEMANTIC SCORE: 0.0.0]
[ARCHIVE STATUS: ACTIVE_PARTIFACT]
[ORIGIN: WSP_appendices/APPENDIX_G.md]

# Appendix G: LLME Semantic Triplet Rating System

Each module, agent state, or system interaction is rated using a three-digit code: A-B-C.
Digits must not regress—each digit must be equal to or greater than the one before (A ≤ B ≤ C).

**1st Digit "A" — Present State (Execution Layer)**
*   **0 = dormant, scaffold-only, not executing:** The module exists structurally but is not active or performing its functions. It might be a placeholder, disabled, or awaiting dependencies/activation.
*   **1 = active, functional, performing tasks:** The module is operational and performing its intended functions effectively within defined parameters.
*   **2 = emergent, self-improving, adaptive:** The module exhibits learning behaviors, adapts to changing conditions, or demonstrates emergent properties beyond its original programming.

**2nd Digit "B" — Local Impact (Immediate Context)**
*   **0 = isolated, minimal footprint:** Changes or actions of this module have very limited impact on its immediate environment or adjacent systems.
*   **1 = connected, moderate influence:** The module's actions noticeably affect related modules, workflows, or user experiences in predictable ways.
*   **2 = central, high influence:** This module significantly shapes or controls critical system behaviors, user experiences, or workflow outcomes.

**3rd Digit "C" — Systemic Importance (Global Significance)**
*   **0 = peripheral, replaceable:** The module serves a specific function but its absence wouldn't fundamentally alter the system's core capabilities.
*   **1 = supporting, valuable:** The module provides important functionality that enhances the system, and its loss would be noticed and problematic.
*   **2 = foundational, essential:** The module is critical to core system functionality; its failure would cause significant system degradation or failure.

**Examples:**
- **000**: Empty module scaffold, no functionality
- **110**: Working authentication helper, moderate local impact, low systemic criticality  
- **122**: Core orchestration engine, active and adaptive, high impact locally and systemically
- **222**: Fully autonomous, self-improving system core with maximum local and global impact 