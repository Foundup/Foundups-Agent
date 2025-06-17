# WSP 14: Modular Audit Protocol (FMAS)

**Version**: 1.0.0
**Date**: 2025-06-17
**Status**: ACTIVE
**Source**: Defined based on `WSP_CORE.md` requirements.

## 1. Overview

This protocol defines the FoundUps Modular Audit System (FMAS), the automated system for enforcing structural and organizational compliance across the repository. The FMAS is referenced in `WSP_CORE.md` as a mandatory check for ensuring the structural integrity of the codebase.

The canonical implementation of this protocol is the `tools/modular_audit/modular_audit.py` script.

## 2. Core Audit Checks

The FMAS script must be capable of validating the following compliance points, as derived from the checklists in `WSP_CORE.md`:

- **`WSP 1` (Module Structure):** Verify that all modules adhere to the mandatory `src/` and `tests/` directory structure.
- **`WSP 3` (Enterprise Domain Organization):** Ensure all modules are located within a valid enterprise domain directory.
- **`WSP 13` (Test Documentation):** Confirm that every `tests/` directory contains a `README.md` file.

## 3. Usage

As outlined in `WSP_CORE.md`, the FMAS is a critical component of the development lifecycle:

- **New Module Workflow:** The audit must be run before starting work on a new module.
- **Existing Code Workflow:** The audit must be run to verify a clean system state after bug fixes or refactoring.
- **Clean State Validation:** A successful FMAS audit is a mandatory requirement for establishing a "clean state" as defined in `WSP 2`.

## 4. Extensibility

The FMAS is designed to be extensible. New checks should be added to the `modular_audit.py` script as new WSP standards are ratified. Each check within the script should clearly reference the WSP number it is enforcing. 