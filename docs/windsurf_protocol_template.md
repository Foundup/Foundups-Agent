# FoundUps Agent Modular Change Log

This log tracks module changes, updates, and versioning for FoundUps Agent under the Windsurf modular development model.

## FoundUps-Agent Roadmap

### Status Ledger
- ✅ Complete
- 🔄 In Progress
- ⏳ Planned
- ⚠️ Deprecated

### ✅ Proof of Concept (0.0.x)
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]

### 🔄 +Prototype (0.1.x - 0.9.x)
- [ ] [Feature 1]
- [ ] [Feature 2]
- [ ] [Feature 3]
- [ ] [Feature 4]
- [ ] [Feature 5]
- [ ] [Feature 6]
- [ ] [Feature 7]
- [ ] [Feature 8]
- [ ] [Feature 9]

### 🔄 [High Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]
- [ ] [Task 5]

### 🔄 [Medium Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]
- [ ] [Task 5]

### 🔄 [Lower Priority System Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]
- [ ] [Task 5]
- [ ] [Task 6]

### ⏳ Minimum Viable Product (1.0.x+)
- [ ] [MVP Feature 1]
- [ ] [MVP Feature 2]
- [ ] [MVP Feature 3]
- [ ] [MVP Feature 4]
- [ ] [MVP Feature 5]
- [ ] [MVP Feature 6]
- [ ] [MVP Feature 7]

#### TODO List *Use `[+todo]` or `[+WSP]` commit convention prefix or add manually here.*
**/[Task Name]** - @[Assignee/Team] - priority: [PriorityScore]
- [ ] [Subtask 1]
- [ ] [Subtask 2]
- [ ] [Subtask 3]
- [ ] [Subtask 4]
- [ ] [Subtask 5]
- [ ] [Subtask 6]

## 🧩 MVP Release Phases

### ⏳ [Phase 1 Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]

### ⏳ [Phase 2 Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]

### 🔄 [Phase 3 Name]
- [ ] [Task 1]
- [ ] [Task 2]
- [ ] [Task 3]
- [ ] [Task 4]
- [ ] [Task 5]

====================================================================

## MODLOG - [+UPDATES]:
- Version: [X.Y.Z]
- Description: [Brief description of changes]
- Notes: [Additional context or considerations]
- Features:
  - [Feature 1]
  - [Feature 2]
  - [Feature 3]
  - [Feature 4]
  - [Feature 5]
  - [Feature 6]
  - [Feature 7]
  - [Feature 8]

====================================================================

## VERSION GUIDE
### Development Phases:
- #### POC (0.0.x): Initial development and proof of concept
  - 0.0.1: First working version
  - 0.0.2-0.0.9: POC improvements and fixes
- #### Prototype (0.1.x - 0.9.x): Feature development and testing
  - 0.1.x: Basic feature set
  - 0.2.x-0.9.x: Feature expansion and refinement
- #### MVP (1.0.x+): Production-ready releases
  - 1.0.0: First stable release
  - 1.x.x: Production updates and improvements

====================================================================

# Windsurf Protocol (WSP) Development Guidelines

**Usage Convention:**
* Use `# WSP:` prefix in task descriptions to indicate this is a Windsurf Protocol task
* Example: `# WSP: Implement cooldown check in QuotaManager.check_quota()`
* After task completion, ask: "Would you like me to add this change to the ModLog?"
* Use `# WSP+:` prefix for adding items to the TODO List

**CRITICAL: You MUST execute *ONLY* the Task described below. Absolutely NO modifications outside of the specified file and function(s) are permitted.**

## Task:
[Insert specific task here. Be extremely concise. Example: "Implement cooldown check in `QuotaManager.check_quota()` using `time.time()`."]

## Scope:
* **File:** `[/path/to/module.py]`
* **Target Function(s):** [List specific function(s) to modify. Example: `QuotaManager.check_quota()`, `QuotaManager.reset_quota()`]

## Constraints:
* **Strict Modification Boundary:** ONLY modify within the specified file and target function(s).
* **Preserve Structure:** Maintain existing code structure, spacing, and comments UNLESS directly contradictory to the Task.
* **No External Dependencies:** Do NOT add new external library dependencies. Use existing imports if possible.

## Reference Baseline:
* **Branch:** `Foundups-Agent-CleanX` (Compare ALL changes to this branch BEFORE submitting.)
* **Purpose:** This branch represents the known-good baseline. Ensure your changes do not introduce regressions, logic errors, or structural deviations.

## Validation:
* **Functional Equivalence (Unless Specified):** Ensure the code behaves IDENTICALLY to the baseline, except for the changes explicitly required by the Task.
* **Cautious Approach:** If unsure about a change, prioritize preserving the baseline logic and add a `TODO: [Your Question]` comment for review.
* **Unit Tests (If Applicable):** Run existing unit tests and add new tests to validate the specific functionality implemented.

# WARNING:
This is a strict Windsurf protocol. Each prompt is atomic. Each file is treated as sacred. No modifications outside the stated scope are permitted. Violations will result in rejection. 

# WSP Documentation: Refactoring Modules to Windsurf Compliance

**Document Version:** 1.0
**Date:** [Insert Date]
**Applies To:** FoundUps codebase, specifically refactoring files from the flat `modules/` directory into the structured `modules/<module_name>/src/` format.

## 1. Purpose

This document outlines the Standard Operating Procedure (SOP) for refactoring existing Python files (`*.py`) located directly within the `/modules/` directory into the **Windsurf Protocol** compliant structure. Adherence to this procedure ensures:

*   **FMAS Compatibility:** Modules pass validation checks performed by the FoundUps Modular Audit System (FMAS Windsurf).
*   **Modularity & Scalability:** Code is organized into distinct, testable "Micro Cubes".
*   **AI Readiness:** Predictable structure facilitates understanding and automation by AI systems.
*   **Maintainability:** Clear separation of source code (`src/`) and tests (`tests/`) improves code management.
*   **Import Clarity:** Standardized import paths reduce errors and ambiguity.

## 2. Scope

This WSP applies to any `.py` file currently residing directly in the root `/modules/` directory that represents a logical, self-contained unit of functionality (a potential Micro Cube).

**Example:** Moving `modules/live_chat_poller.py` to `modules/live_chat_poller/src/live_chat_poller.py`.

## 3. Prerequisites

*   **FoundUps Repository Access:** Cloned repository with the latest codebase.
*   **Python Environment:** Properly configured Python environment (as specified in the main README).
*   **Pytest:** `pytest` installed for running unit tests.
*   **FMAS Tool:** Access to the `tools/modular_audit/modular_audit.py` script.
*   **Baseline Access:** Read access to the designated baseline (e.g., `CLEAN4`) for FMAS comparison.
*   **Version Control:** Familiarity with Git (using branches is highly recommended for refactoring).
*   **Understanding of Windsurf:** Familiarity with the `modules/<module_name>/src/` and `modules/<module_name>/tests/` structure.

## 4. Standard Procedure (Step-by-Step)

**Goal:** Refactor `modules/original_module.py` into `modules/original_module/src/original_module.py`.

**(Note: Use a dedicated Git branch for each refactoring task.)**

1.  **Identify Target File:** Select the file to refactor (e.g., `modules/livechat.py`). Determine the corresponding module name (usually the base name of the file, e.g., `livechat`).

2.  **Create Module Directory Structure:**
    *   Create the main module directory: `mkdir modules/livechat`
    *   Create the source directory: `mkdir modules/livechat/src`
    *   Create the test directory (even if empty initially): `mkdir modules/livechat/tests`

3.  **Move the Source File:**
    *   Move the target file into its new `src/` directory:
        ```bash
        git mv modules/livechat.py modules/livechat/src/livechat.py
        ```
        *(Using `git mv` preserves file history)*

4.  **Create/Update Module `__init__.py`:**
    *   Create `modules/livechat/__init__.py`.
    *   **Purpose:** This file makes the `livechat` directory a Python package and defines its public interface by importing relevant classes/functions from the `src/` directory.
    *   **Content:**
        ```python
        # modules/livechat/__init__.py
        """Livechat Module for FoundUps.""" # Add appropriate docstring

        # Import the primary class/functions intended for external use from the src file
        from .src.livechat import LiveChatClient, connect_livechat # Example names

        # Define __all__ to control 'from modules.livechat import *' behavior
        # and explicitly declare the public API. List the imported names.
        __all__ = [
            'LiveChatClient',
            'connect_livechat',
            # Add other public items from .src.livechat here
        ]
        ```
    *   **Important:** Only expose necessary components. If `livechat.py` contained multiple classes/functions, only import and list the ones meant to be used by *other* modules in `__init__.py`.

5.  **Create/Update `src/__init__.py`:**
    *   Create `modules/livechat/src/__init__.py`.
    *   **Purpose:** Makes the `src` directory a sub-package.
    *   **Content:** This file can usually be left **empty**. It primarily serves to mark the directory as a package. Do *not* typically put imports here unless managing complex internal structures within `src`.

6.  **Update Internal Imports (within the moved file):**
    *   Open the moved file (`modules/livechat/src/livechat.py`).
    *   Check for any relative imports that might be broken by the move. For example, if `livechat.py` previously imported `utils.py` (also in the flat `modules/`) using `from . import utils`, this might need adjustment depending on where `utils.py` ends up.
    *   Generally, imports of *other Windsurf modules* should now use the full path: `from modules.other_module import SomeClass`.
    *   Imports of utility functions refactored into their own modules should use the new path: `from modules.utils_module.src.utils_file import helper_function`.

7.  **Update External Callers:**
    *   Identify other modules/scripts that were importing the *original* flat file (`from modules import livechat` or potentially `import modules.livechat`).
    *   **How to find callers:** Use codebase search tools (IDE search, `grep`, `git grep`):
        ```bash
        # Search for imports of the old flat module
        git grep "from modules import livechat"
        git grep "import modules.livechat"
        ```
    *   Update these callers to use the new, structured import path:
        ```python
        # Old import (in e.g., modules/processor/src/processor.py):
        # from modules import livechat # Or import modules.livechat

        # New import:
        from modules.livechat import LiveChatClient # Import specific items
        # Or: from modules import livechat # And use livechat.LiveChatClient
        ```
    *   Prioritize importing specific classes/functions (`from modules.livechat import LiveChatClient`) over importing the whole module (`from modules import livechat`).

8.  **Move/Create Tests:**
    *   If tests for `livechat.py` existed (e.g., `modules/tests/test_livechat.py`), move them into the new `tests/` directory:
        ```bash
        git mv modules/tests/test_livechat.py modules/livechat/tests/test_livechat.py
        ```
    *   If no tests exist, **create** a basic test file structure in `modules/livechat/tests/` (e.g., `test_livechat.py`) and add TODOs or basic tests. FMAS requires a test file for each source file.
    *   Update imports *within* the test files to reflect the new location of the source code (e.g., `from modules.livechat.src.livechat import LiveChatClient`).

9.  **Run Tests:**
    *   Run tests specifically for the refactored module:
        ```bash
        pytest modules/livechat/tests/
        ```
    *   Run tests for any modules identified as *callers* in Step 7, as their imports have changed.
        ```bash
        pytest modules/processor/tests/ # Example if processor called livechat
        ```
    *   Run all tests if unsure about dependencies: `pytest`

10. **Troubleshoot Test Failures:**
    *   **`ImportError`:**
        *   Check `modules/livechat/__init__.py`: Does it correctly import names from `.src.livechat`? Are the names actually defined in `src/livechat.py`? (As seen with `StreamResolver`).
        *   Check `modules/livechat/src/__init__.py`: Is it present (can be empty)?
        *   Check caller imports (Step 7): Are they using the correct new path (`modules.livechat`)?
        *   Check test imports (Step 8): Are they using `modules.livechat.src.livechat` correctly?
    *   **`NameError`:** Likely caused by incorrect imports in the module itself or in the calling code after refactoring.
    *   **Mock Errors (`AssertionError: Expected ... called ... times`):** As seen with `live_chat_processor`, ensure mocks are properly isolated between tests, potentially using `mock_instance.reset_mock()` within the test function before the code under test is called.
    *   **Other Failures:** Debug standard test failures related to the code's logic.

11. **Verify with FMAS:**
    *   Run the FoundUps Modular Audit System script against your changes:
        ```bash
        python tools/modular_audit/modular_audit.py <path_to_modules_root> --baseline <path_to_baseline_root>
        ```
    *   Address any reported issues:
        *   `STRUCTURE_ERROR`: Ensure `src/` and `tests/` exist.
        *   `NO_TEST`: Ensure a corresponding test file exists in `tests/`.
        *   `FOUND_IN_FLAT`: This *shouldn't* apply to the *new* structure but confirms the baseline comparison logic.
        *   `MISSING`/`MODIFIED`/`EXTRA`: Compare against the baseline if applicable. For newly refactored modules, `EXTRA` compared to an *old* baseline might be expected until the baseline is updated. The primary goal here is structural compliance (`src`/`tests`) and test existence.

12. **Commit Changes:**
    *   Stage all changes (moves, creations, modifications).
    *   Commit with a clear message describing the refactoring:
        ```bash
        git add .
        git commit -m "refactor(livechat): Move livechat module to Windsurf structure"
        ```

13. **Repeat:** Continue the process for the next flat file in `/modules/`.

## 5. Common Issues & Troubleshooting Summary

*   **`ImportError` during tests/runtime:** Double-check `__init__.py` files (module root and `src`), caller import paths, and test import paths. Ensure names imported actually exist in the target file.
*   **`NameError`:** Usually follows an `ImportError` or signifies an incorrectly updated import somewhere.
*   **Mock state bleeding (`AssertionError` on call count):** Use `mock_instance.reset_mock()` within tests before executing the code that uses the mock. Ensure `setUp` methods correctly initialize fresh mocks for each test.
*   **FMAS Errors:** Refer to the FMAS README for detailed explanations of `MISSING`, `MODIFIED`, `EXTRA`, `NO_TEST`, `FOUND_IN_FLAT`, `STRUCTURE_ERROR`. Focus on fixing structure and test existence first.

## 6. Best Practices

*   **One Module Per Branch/Commit:** Refactor one module at a time for easier review and rollback.
*   **Test Thoroughly:** Run tests for the refactored module *and* its dependents.
*   **Run FMAS:** Use the audit tool as a final validation step before merging.
*   **Communicate:** Inform team members if refactoring affects shared modules.
*   **Update Documentation:** If the module's public API changes significantly, update relevant documentation or docstrings.

---

This WSP provides a consistent methodology for bringing the FoundUps codebase into full Windsurf compliance, ensuring a robust, maintainable, and AI-ready modular architecture.