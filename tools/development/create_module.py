#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

WSP 35: Module Creation Automation Tool

This script automates the creation of new, WSP-compliant modules.
It scaffolds the required directory structure and placeholder files,
ensuring immediate compliance with the FoundUps workspace standards.
"""

import argparse
import os
import sys
from pathlib import Path

# --- Placeholder Content Templates ---

README_TEMPLATE = """
# Module: {module_name}

**WSP Compliance:** 🟢 **Active**

## 1. Purpose

[Describe the module's primary responsibility and function.]

## 2. Usage

[Provide code examples and instructions on how to use the module's public interface.]

## 3. WSP Compliance Status

| Protocol | Status | Notes |
|----------|--------|-------|
| WSP 1    | [OK]      | `src/` and `tests/` structure is present. |
| WSP 3    | [OK]      | Located in a valid Enterprise Domain and Feature Group. |
| WSP 13   | [OK]      | `requirements.txt` and `tests/README.md` are present. |

"""

INIT_TEMPLATE = """
# __init__.py for {module_name}
#
# Per WSP 11, this file defines the public API of the module.
# All functions and classes intended for external use should be imported here.
#
# Example:
# from .src.{module_name} import MyPublicClass, my_public_function

"""

SRC_INIT_TEMPLATE = "# __init__.py for src directory"

TESTS_README_TEMPLATE = """
# Module Tests: {module_name}

This document lists the test files for this module and their primary responsibilities,
as required by WSP 13.

| Test File | Description |
|-----------|-------------|
| `test_...`| [Describe the focus of this test file.] |

"""

SRC_MODULE_TEMPLATE = """
#!/usr/bin/env python3
\"\"\"
Core source code for the {module_name} module.
\"\"\"

class {class_name}:
    \"\"\"Example class for the {module_name} module.\"\"\"
    def __init__(self):
        pass

    def hello_world(self):
        \"\"\"An example method.\"\"\"
        print("Hello from {module_name}!")
        return "Hello from {module_name}!"

"""

# --- Enterprise Domains (from WSP 3) ---
# This should be kept in sync with the audit tool.
ENTERPRISE_DOMAINS = {
    "ai_intelligence",
    "communication",
    "platform_integration",
    "infrastructure",
    "data_processing",
    "monitoring",
    "development",
    "user_experience",
    "foundups",
    "gamification",
    "blockchain",
}


def create_module(module_path: str):
    """
    Validates the path and creates the module structure.
    """
    print(f"[TOOL] Initializing creation for module: {module_path}")

    # 1. --- Validation Steps ---
    try:
        path = Path(module_path)
        if path.parts[0].lower() != "modules":
            raise ValueError("Path must start with 'modules/'.")

        if len(path.parts) != 4:
            raise ValueError("Path must be in the format: modules/<domain>/<group>/<module_name>")

        domain, group, module_name = path.parts[1], path.parts[2], path.parts[3]

        if domain.lower() not in ENTERPRISE_DOMAINS:
            raise ValueError(f"'{domain}' is not a recognized Enterprise Domain.")

        if path.exists():
            raise ValueError(f"Module path '{module_path}' already exists.")

    except ValueError as e:
        print(f"[FAIL] Validation Failed: {e}")
        sys.exit(1)

    print("[OK] Path validation successful.")
    print(f"   - Enterprise Domain: {domain}")
    print(f"   - Feature Group:     {group}")
    print(f"   - Module Name:       {module_name}")

    # 2. --- Scaffolding Process ---
    print("\n[U+1F3D7]️  Creating directory structure...")
    src_path = path / "src"
    tests_path = path / "tests"
    src_path.mkdir(parents=True, exist_ok=False)
    tests_path.mkdir(exist_ok=False)
    print(f"   - Created: {path}/")
    print(f"   - Created: {src_path}/")
    print(f"   - Created: {tests_path}/")

    # 3. --- Placeholder File Generation ---
    print("\n[U+1F4C4] Generating placeholder files...")
    files_to_create = {
        path / "README.md": README_TEMPLATE.format(module_name=module_name),
        path / "__init__.py": INIT_TEMPLATE.format(module_name=module_name),
        path / "requirements.txt": "",
        src_path / "__init__.py": SRC_INIT_TEMPLATE,
        src_path / f"{module_name}.py": SRC_MODULE_TEMPLATE.format(
            module_name=module_name,
            class_name=f"{''.join(word.capitalize() for word in module_name.split('_'))}"
        ),
        tests_path / "__init__.py": SRC_INIT_TEMPLATE,
        tests_path / "README.md": TESTS_README_TEMPLATE.format(module_name=module_name),
    }

    for file_path, content in files_to_create.items():
        try:
            file_path.write_text(content.strip())
            print(f"   - Created: {file_path}")
        except IOError as e:
            print(f"[FAIL] Error writing to {file_path}: {e}")
            sys.exit(1)

    print("\n[U+2728] Module scaffolding complete!")

    # 4. --- Post-Creation Hook ---
    print("\n[SEARCH] Running compliance audit on the new module...")
    os.system(f"python tools/modular_audit/modular_audit.py {module_path}")


def main():
    parser = argparse.ArgumentParser(
        description="WSP 35: Module Creation Automation Tool",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "module_path",
        type=str,
        help="The fully-qualified path for the new module.\n"
             "Format: modules/<enterprise_domain>/<feature_group>/<module_name>"
    )

    args = parser.parse_args()
    create_module(args.module_path)


if __name__ == "__main__":
    main() 