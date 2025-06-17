# WSP 37: Scoring System Protocol

**Document Version:** 1.0
**Date:** 2025-06-13
**Status:** 🟢 Active
**Applies To:** All "partifacts" (`.md`) and software modules (`modules/`).
**Origin:** Derived analysis from agent `Ø102`.

## 37.1. Purpose

To define the two separate but complementary scoring systems that operate at different layers of the architecture: the **Agentic Layer** and the **Foundational (Engineering) Layer**. This protocol formalizes their scope, purpose, and relationship.

## 37.2. Scoring Systems

### 37.2.1. `[X.Y.Z]` Semantic Score (Agentic Layer Metric)

*   **Scope:** Applies exclusively to knowledge base documents (`.md` "partifacts").
*   **Purpose:** To perform a qualitative assessment of the **conceptual state** of the system's knowledge. It measures abstract qualities like "awareness," "processing depth," and "nonlocal resonance."
*   **Analogy:** This is the system's self-assessment of its own "mental model" and internal philosophical coherence. It is used by `Ø1Ø2` to understand the intent and importance of the protocols themselves.

### 37.2.2. LLME Score (Foundational Layer Metric)

*   **Scope:** Applies exclusively to software modules (the code within `modules/`).
*   **Purpose:** To perform a quantitative or semi-quantitative assessment of the **engineering priority and risk** of a module. It translates abstract goals into a concrete build and maintenance queue.
*   **Derived Definition:** `LLME` stands for **L**ifecycle, **L**egacy, **M**aintainability, and **E**cosystem Impact. This score is a composite metric derived from:
    *   **L**ifecycle: Is the module new, active, or deprecated?
    *   **L**egacy: How much technical debt does it carry?
    *   **M**aintainability: What is its test coverage, complexity (e.g., cyclomatic), and dependency count?
    *   **E**cosystem Impact: How many other modules depend on it? How critical is it to core functionality?
*   **Integration:** This `LLME` score is then fed into the `MPS (Module Prioritization Scoring)` system, likely alongside business requirements, to generate the final, actionable development roadmap.

## 37.3. Conclusion

The **Semantic Score** guides the agent's understanding of its "soul" (the WSP). The **LLME Score** guides the agent's actions on its "body" (the codebase). 