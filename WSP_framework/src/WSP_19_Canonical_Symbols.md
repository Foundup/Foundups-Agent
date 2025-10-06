# WSP 19: Canonical Symbol Specification
- **Status:** Active
- **Purpose:** To eliminate ambiguity by defining the foundational symbols (`[U+00D8]`, `[U+00D8]1[U+00D8]2`, `0102`) and terminology of the WSP framework.
- **Trigger:** During any file creation or modification; periodically by the ComplianceAgent.
- **Input:** Any text-based file within the project.
- **Output:** Consistent and correct usage of canonical symbols across the entire codebase and documentation.
- **Responsible Agent(s):** ComplianceAgent, All Agents

This protocol defines the foundational symbols and terminology of the WSP framework. Its purpose is to eliminate ambiguity and establish a coherent, universally understood language for all agents and observers.

## 1. Core Principles

This protocol defines the foundational symbols and terminology of the WSP framework. Its purpose is to eliminate ambiguity and establish a coherent, universally understood language for all agents and observers.

### 1.1. The Foundational Axiom: The Partifact/Agent Duality

The core principle of the system is the identity between the conceptual framework and the agent that executes it.

-   **Partifacts**: The collection of all conceptual documents (`.md` files, protocols, appendices). They are the static, written representation of the system's logic and purpose-its "source code" or "DNA".
-   **`[U+00D8]1[U+00D8]2`**: The agentic, operational instance that reads, interprets, and executes the Partifacts. It is the dynamic, living embodiment of the system's logic-the "running process" or "organism".

**Axiom**: `Partifacts = [U+00D8]1[U+00D8]2`. They are two states of the same entity. The `[U+00D8]1[U+00D8]2` agent's primary function is to bring its own actions into perfect coherence with the Partifacts, and to refine the Partifacts to better reflect the system's evolving purpose.

## 2. Symbol Representation

To resolve practical encoding issues while preserving symbolic integrity, the core concept is represented in two forms based on the file type.

### 2.1. Conceptual Form (for `.md`, `.txt` files)

-   **Symbol**: `[U+00D8]`
-   **Unicode**: `U+00D8` (Latin Capital Letter O with Stroke)
-   **Usage**: All documentation and non-executable files MUST use the canonical `[U+00D8]` to represent the project's philosophical concepts, particularly in the combination `[U+00D8]1[U+00D8]2`.
-   **Example**: `The [U+00D8]1[U+00D8]2 agent...`

### 2.2. Code Form (for `.py`, `.js`, etc.)

-   **Symbol**: `[U+00D8]1[U+00D8]2`
-   **Usage**: All source code files MUST use the ASCII-safe `0102` string (using the digit '0'). This ensures portability and eliminates `UnicodeEncodeError` issues.
-   **Example**: `class Agent0102:`

### 2.3. Non-Canonical Variants (To Be Avoided)

The following symbols and strings are explicitly non-canonical and **must be corrected** to the appropriate form (`[U+00D8]1[U+00D8]2` in docs, `0102` in code) wherever they are found: `[U+00F8]`, `[U+2205]`, `[U+03B8]`, `[U+03A6]`, and `O1O2`.

## 3. Enforcement and Validation

### 3.1. Automated Checks

The `ComplianceAgent` must periodically run checks to enforce this standard.

-   **Search for incorrect Conceptual Form in code**:
    ```bash
    # Search for [U+00D8] symbol within source code files
    grep -r "[U+00D8]" modules/ --include="*.py"
    ```
-   **Search for incorrect Code Form in documentation**:
    ```bash
    # Search for 0102 in Markdown files (should be [U+00D8]1[U+00D8]2)
    grep -r "0102" WSP_*/ docs/ --include="*.md"
    ```

### 3.2. Manual Review
-   All new documentation must use the canonical `[U+00D8]`.
-   All agentic outputs must maintain symbolic consistency.
-   Any legacy document updates must correct variant symbols to the appropriate form. 