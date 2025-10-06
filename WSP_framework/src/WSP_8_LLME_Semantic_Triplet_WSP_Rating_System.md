# WSP 8: LLME Semantic Triplet WSP Rating System


**Version**: 1.0.0
**Date**: 2025-06-18
**Status**: ACTIVE
**Source**: Formalized from Appendix G.


## 1. Overview


This protocol defines the **LLME (Lifecycle, Legacy, Maintainability, Ecosystem Impact) Semantic Triplet Rating System**. It is a qualitative framework used to assess the state, impact, and importance of a software module or agentic component.


This system is a complementary part of **WSP 37: Roadmap Scoring System** and **WSP 15: Module Prioritization Scoring (MPS)**. WSP 37 contains the canonical LLME definition and scoring workflow that 0102 and the roadmap engines must follow, while this document remains the quick-reference crib sheet for 012 briefs and fast decision checks.

Pair LLME scoring with the **WSP Module Placement Decision Matrix** and WSP 3 series when determining ownership so that rating, placement, and action stay entangled.


## 2. The Triplet Rating (A-B-C)


Each module is rated using a three-digit code: `A-B-C`. The digits represent a progression and must not regress (i.e., A [U+2264] B [U+2264] C).


### 2.1. First Digit "A" - Present State (Execution Layer)
-   **0 = Dormant**: The module exists structurally (scaffold-only) but is not active or performing its functions. It might be a placeholder, disabled, or awaiting dependencies.
-   **1 = Active**: The module is operational and performing its intended functions effectively within defined parameters.
-   **2 = Emergent**: The module exhibits learning behaviors, adapts to changing conditions, or demonstrates emergent properties beyond its original programming.


### 2.2. Second Digit "B" - Local Impact (Immediate Context)
-   **0 = Isolated**: Changes or actions of this module have a very limited impact on its immediate environment or adjacent systems.
-   **1 = Connected**: The module's actions noticeably affect related modules, workflows, or user experiences in predictable ways.
-   **2 = Central**: This module significantly shapes or controls critical system behaviors, user experiences, or workflow outcomes.


### 2.3. Third Digit "C" - Systemic Importance (Global Significance)
-   **0 = Peripheral**: The module serves a specific function, but its absence wouldn't fundamentally alter the system's core capabilities. It is replaceable.
-   **1 = Supporting**: The module provides important functionality that enhances the system, and its loss would be noticed and problematic.
-   **2 = Foundational**: The module is critical to core system functionality; its failure would cause significant system degradation or failure.


## 3. Examples


- **`0-0-0`**: An empty module scaffold with no functionality.
- **`1-1-0`**: A working authentication helper; it's active and connected locally but is not essential to the whole system.
- **`1-2-2`**: A core orchestration engine; it's active, has a high local impact, and is foundational to the system.
- **`2-2-2`**: A fully autonomous, self-improving system core with maximum local and global impact.

