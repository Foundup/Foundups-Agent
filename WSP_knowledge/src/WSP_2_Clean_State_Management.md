# WSP 2: Clean State Management Protocol

**Version**: 1.0.0
**Date**: 2025-06-17
**Status**: ACTIVE
**Source**: Defined based on `WSP_CORE.md` requirements.

## 1. Overview

This protocol defines what constitutes a "clean state" for the repository and outlines the mandatory procedure for creating a snapshot of that state. As per `WSP_CORE.md`, following this protocol is a mandatory prerequisite for any high-risk operation, such as major refactoring.

## 2. Definition of a Clean State

A repository is in a "clean state" if and only if all of the following conditions, derived from the `WSP_CORE.md` project status checklists, are met:

- **No Uncommitted Changes:** `git status` reports a clean working directory.
- **Full Test Suite Pass:** All module tests pass (`pytest modules/`).
- **100% Audit Compliance:** The Modular Audit (`WSP 4`) reports zero violations (`python tools/modular_audit/modular_audit.py ./modules`).
- **Coverage Maintained:** Test coverage meets or exceeds the project standard defined in `WSP 5` (≥90%).

## 3. Snapshot Creation Protocol

The "snapshot process" referenced in `WSP_CORE.md` consists of the following steps:

1.  **Verification:** Confirm that all criteria in Section 2 are met.
2.  **Tagging:** Create a new, annotated Git tag to mark the clean state. The tag must use the sequential naming convention `clean-vX` (e.g., `clean-v6`, `clean-v7`).
    ```bash
    git tag -a clean-vX -m "Snapshot for [Reason for snapshot]"
    ```
3.  **Documentation:** It is recommended to log the creation of the clean state in `docs/clean_states.md` or a similar log file, noting the reason for the snapshot.

## 4. Usage

- **Baseline for Refactoring:** A clean state must be established before initiating any major code refactoring.
- **Reliable Rollback Point:** If a high-risk operation fails, the repository can be safely reset to the last known clean state tag.
- **Validation Benchmark:** CI/CD pipelines and automated tools can use these tags as a definitive "known-good" version for comparison.

## 5. Authority and Compliance

This protocol is non-negotiable. Failure to create a clean state before a high-risk operation is a critical violation of WSP. The `RSP_SELF_CHECK Protocol (WSP 17)` may use these tags to validate system coherence over time. 