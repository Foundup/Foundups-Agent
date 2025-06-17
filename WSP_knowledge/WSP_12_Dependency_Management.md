# WSP 12: Dependency Management

**Version**: 1.0.0
**Date**: 2025-06-17
**Status**: ACTIVE
**Source**: Defined based on `WSP_CORE.md` requirements.

## 1. Overview

This protocol governs the management of external dependencies. `WSP_CORE.md` requires that dependencies are declared explicitly to ensure reproducibility and stability.

## 2. Dependency Declaration

1.  **Module-Level `requirements.txt`**: As per the "Implementation Checklist" in `WSP_CORE.md`, each module with external Python dependencies **must** declare them in a `requirements.txt` file at the module's root (e.g., `modules/<domain>/<module_name>/requirements.txt`).

2.  **Explicit Versioning**: To ensure deterministic builds, all dependencies listed in a module's `requirements.txt` **must** be pinned to a specific version using the `==` operator (e.g., `requests==2.28.1`).

3.  **Global `requirements.txt`**: A global `requirements.txt` file at the project root serves as the single source of truth for the entire project's environment. It is an aggregation of all module-level dependency files.

## 3. Workflow

1.  **Adding a Dependency**: Add the pinned dependency to the specific module's `requirements.txt` and then update the global `requirements.txt` accordingly.
2.  **Installation**: All project dependencies should be installed by running `pip install -r requirements.txt` from the project root.

## 4. Enforcement

- **CI/CD Pipeline:** The CI/CD pipeline should verify that the global `requirements.txt` is a valid superset of all module-level requirements files.
- **Audit Script:** The FMAS (`WSP 4`) can be extended to check that `import` statements for non-standard libraries have a corresponding entry in a `requirements.txt` file. 