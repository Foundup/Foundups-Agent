# WSP 15: Module Prioritization Scoring (MPS) System
- **Status:** Active
- **Purpose:** To provide a consistent, objective methodology for evaluating and ranking modules to guide development priorities.
- **Trigger:** When planning a new development cycle; when a new module is proposed.
- **Input:** A module or list of modules to be evaluated.
- **Output:** A priority score (P0-P4) for each module, documented in `modules_to_score.yaml`.
- **Responsible Agent(s):** ScoringAgent

The **Module Prioritization Scoring (MPS) System** provides a consistent, objective methodology for evaluating and ranking modules based on their strategic importance and implementation considerations. This is augmented by the **LLME Semantic Triplet Rating** (see `WSP 11`), which provides a qualitative layer for understanding a module's state, local impact, and systemic importance. This combined approach enables the development team to:

-   Focus efforts on the highest-value modules first.
-   Make informed decisions about resource allocation.
-   Create a defensible, transparent roadmap.
-   Balance immediate needs with long-term architectural goals.
-   Communicate priorities clearly to all stakeholders.
-   Align development effort with desired semantic states of modules (as defined by LLME).

## 2. Scoring Criteria (MPS Dimensions)

Each module receives a score from 1 (lowest) to 5 (highest) in four dimensions. The LLME score provides qualitative context for these dimensions.

### A. Complexity (1-5)

-   **Definition**: How difficult is the module to implement or refactor correctly?
-   **LLME Influence**: A module's 'Present State' (Digit A) can influence this. A dormant module (`A=0`) might be more complex to activate.

| Score | Complexity Level | Description                                                      |
| ----- | ---------------- | ---------------------------------------------------------------- |
| 1     | Trivial          | Simple code, few dependencies, well-understood patterns          |
| 2     | Low              | Straightforward implementation with minimal challenges           |
| 3     | Moderate         | Requires careful design, some complex logic or integration       |
| 4     | High             | Significant challenges, complex algorithms or interactions       |
| 5     | Very High        | Extremely complex, cutting-edge techniques, major integration work |

### B. Importance (1-5)

-   **Definition**: How essential is this module to the system's core functions?
-   **LLME Influence**: 'Local Impact' (Digit B) and 'Systemic Importance' (Digit C) directly inform this. A module with `B=2` or `C=2` is inherently important.

| Score | Importance Level | Description                                                      |
| ----- | ---------------- | ---------------------------------------------------------------- |
| 1     | Optional         | Nice-to-have, system works without it                            |
| 2     | Helpful          | Enhances system but not required for core operations             |
| 3     | Important        | System functions suboptimally without it                         |
| 4     | Critical         | System faces significant limitations without it                  |
| 5     | Essential        | System cannot function in a meaningful way without it            |

### C. Deferability (1-5)

-   **Definition**: How urgent is the development of this module? (A lower score means it is *more* deferrable).
-   **LLME Influence**: An active module (`A=1` or `A=2`) may be less deferrable than a dormant one (`A=0`), unless activating it is the urgent task.

| Score | Deferability Level   | Description                                                      |
| ----- | -------------------- | ---------------------------------------------------------------- |
| 1     | Highly Deferrable    | Can be postponed indefinitely with minimal impact                |
| 2     | Deferrable           | Can be delayed for several release cycles                        |
| 3     | Moderate             | Should be implemented within next 1-2 releases                   |
| 4     | Difficult to Defer   | Needed in the next release to maintain progress                  |
| 5     | Cannot Defer         | Blocking further progress; must be implemented immediately       |

### D. Impact (1-5)

-   **Definition**: How much value will this module deliver to users or the system?
-   **LLME Influence**: 'Local Impact' (Digit B) and 'Systemic Importance' (Digit C) directly inform this. An 'emergent' state (`A=2`) could also signify high impact.

| Score | Impact Level     | Description                                                      |
| ----- | ---------------- | ---------------------------------------------------------------- |
| 1     | Minimal          | Little noticeable improvement to users or system                 |
| 2     | Minor            | Some value, but limited in scope or effect                       |
| 3     | Moderate         | Clear benefits visible to users or significant internal improvements |
| 4     | Major            | Substantial value enhancement, highly visible improvements       |
| 5     | Transformative   | Game-changing capability that redefines system value             |

## 3. Scoring Process

1.  **Assess MPS**: For each module, assign scores (1-5) for Complexity, Importance, Deferability, and Impact.
2.  **Assign LLME**: Assign or review the module's current and target LLME score (e.g., "112").
3.  **Calculate Score**: Sum the four MPS dimensions: `MPS Score = Complexity + Importance + Deferability + Impact`.
4.  **Document**: Maintain scores and rationale in `modules_to_score.yaml`.

## 4. Priority Classification

The total MPS score (range: 4-20) and the LLME score determine priority.

| MPS Score Range | Priority | Action Guideline & LLME Considerations                                                                     |
| --------------- | -------- | ---------------------------------------------------------------------------------------------------------- |
| 16-20           | P0       | **Critical**. Work begins immediately. Modules with LLME `X22` or target `X22` are paramount.                |
| 13-15           | P1       | **High**. Important for near-term roadmap. Use LLME to sequence P1s (e.g., prioritize a `011` -> `122` evolution). |
| 10-12           | P2       | **Medium**. Valuable but not urgent. LLME can help differentiate P2s.                                      |
| 7-9             | P3       | **Low**. Can be deferred. Typically low current and target LLME.                                           |
| 4-6             | P4       | **Backlog**. Reconsidered in future planning. Candidates for deprecation if LLME remains `000`.            | 