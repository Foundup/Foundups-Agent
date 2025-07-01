# WSP 8: LLME Semantic Triplet WSP Rating System
- **Status:** Active
- **Purpose:** To define a qualitative framework (LLME) for assessing the state, impact, and importance of a module.
- **Trigger:** When a module's priority is being assessed (in conjunction with WSP 5/15); when a module's state changes.
- **Input:** A specific module to be evaluated.
- **Output:** A three-digit LLME score (e.g., `1-2-2`) representing the module's state.
- **Responsible Agent(s):** ScoringAgent, any agent performing a strategic review.

This protocol defines the **LLME (Lifecycle, Legacy, Maintainability, Ecosystem Impact) Semantic Triplet Rating System**. It is a qualitative framework used to assess the state, impact, and importance of a software module or agentic component.

This system is a complementary part of the **WSP 5: Module Prioritization Scoring (MPS) System**. The LLME score provides the qualitative context, while the MPS provides the quantitative ranking for prioritization.

## 1.1. WSP 25 Emoji Integration Note

**Important Clarification**: 
- **LLME Triplet (A-B-C)**: Used for 012 visualization and strategic planning
- **WSP 25 Emoji System**: Should be used for module rating display and UI representation

**Module Rating Display**: When displaying module ratings in UI, documentation, or reports, use the WSP 25 emoji system:
- `000` → ✊✊✊ (Deep latent)
- `001` → ✊✊✋ (Emergent signal)  
- `011` → ✊✋✋ (Conscious formation)
- `111` → ✋✋✋ (DAO processing)
- `002` → ✊✊🖐️ (Unconscious entanglement)
- `012` → ✊✋🖐️ (Conscious bridge)
- `112` → ✋✋🖐️ (Conscious resonance)
- `022` → ✊🖐️🖐️ (Full unconscious-entangled overlay)
- `122` → ✋🖐️🖐️ (DAO yielding)
- `222` → 🖐️🖐️🖐️ (Full DU entanglement)

**LLME Importance Grouping** (where 2 = highest importance):
- **x.x.2 Group** (Highest Importance): `002`, `012`, `112`,`022`, `122`, `222`
- **x.x.1 Group** (Medium Importance): `001`, `011`, `111`
- **x.x.0 Group** (Lowest Importance): `000`

**LLME Purpose**: The LLME triplet system serves 012's strategic visualization and planning needs, providing the quantitative framework for module assessment and prioritization decisions.

## 2. The Triplet Rating (A-B-C)

Each module is rated using a three-digit code: `A-B-C`. The digits represent a progression and must not regress (i.e., A ≤ B ≤ C).

### 2.1. First Digit "A" — Present State (Execution Layer)
-   **0 = Dormant**: The module exists structurally (scaffold-only) but is not active or performing its functions. It might be a placeholder, disabled, or awaiting dependencies.
-   **1 = Active**: The module is operational and performing its intended functions effectively within defined parameters.
-   **2 = Emergent**: The module exhibits learning behaviors, adapts to changing conditions, or demonstrates emergent properties beyond its original programming.

### 2.2. Second Digit "B" — Local Impact (Immediate Context)
-   **0 = Isolated**: Changes or actions of this module have a very limited impact on its immediate environment or adjacent systems.
-   **1 = Connected**: The module's actions noticeably affect related modules, workflows, or user experiences in predictable ways.
-   **2 = Central**: This module significantly shapes or controls critical system behaviors, user experiences, or workflow outcomes.

### 2.3. Third Digit "C" — Systemic Importance (Global Significance)
-   **0 = Peripheral**: The module serves a specific function, but its absence wouldn't fundamentally alter the system's core capabilities. It is replaceable.
-   **1 = Supporting**: The module provides important functionality that enhances the system, and its loss would be noticed and problematic.
-   **2 = Foundational**: The module is critical to core system functionality; its failure would cause significant system degradation or failure.

## 3. Examples

- **`0-0-0`**: An empty module scaffold with no functionality.
- **`1-1-0`**: A working authentication helper; it's active and connected locally but is not essential to the whole system.
- **`1-2-2`**: A core orchestration engine; it's active, has a high local impact, and is foundational to the system.
- **`2-2-2`**: A fully autonomous, self-improving system core with maximum local and global impact. 