#!/usr/bin/env python3
"""
WSP Module Audit & Bootstrap Tool (Simplest Working Solution)

Purpose:
- Audit modules/ for WSP-required files
- Create missing tests/TestModLog.md placeholders
- Ensure per-module scripts/validate.py exists (lightweight validation entrypoint)

Usage:
  python tools/wsp_module_audit.py --dry-run     # show actions
  python tools/wsp_module_audit.py --apply       # write missing files

WSP References: WSP 22, 34, 49, 54, 74
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple


REQUIRED_DOCS = [
    "README.md",
    "ROADMAP.md",
    "ModLog.md",
    "INTERFACE.md",
    "requirements.txt",
    "__init__.py",
]

REQUIRED_TEST_DOCS = [
    ("tests/README.md", "# tests/README.md\n\nDescribe test strategy, how to run, fixtures, and expected behavior.\n"),
    ("tests/TestModLog.md", "# TestModLog\n\n- Initialize test change log per WSP 34.\n"),
]

PLACEHOLDERS = {
    "README.md": "# Module README (WSP)\n\n- Module Purpose\n- WSP Compliance Status\n- Dependencies\n- Usage Examples\n- Integration Points\n- WSP Recursive Instructions\n",
    "ROADMAP.md": "# ROADMAP (WSP 22)\n\n- Vision\n- Milestones (PoC → Prototype → MVP)\n- Risks\n- Dependencies\n",
    "ModLog.md": "# Module ModLog (WSP 22)\n\n- Initialized ModLog per WSP 22.\n",
    "INTERFACE.md": "# INTERFACE (WSP 11)\n\n## Public API\n## Parameters\n## Returns\n## Errors\n## Examples\n",
    "requirements.txt": "# Module requirements (pin as needed)\n",
    "__init__.py": "",
    "src/__init__.py": "",
    "memory/README.md": "# Module Memory (WSP 60)\n\nDescribe memory layout, retention and indexing.\n",
}

VALIDATE_TEMPLATE = """#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd))
    try:
        return subprocess.call(cmd)
    except FileNotFoundError:
        print("(tool missing, skipping)")
        return 0

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    # Lint placeholder (optional tools): ruff/flake8 if available
    run([sys.executable, "-m", "pip", "--version"])  # smoke
    # Pytest if tests exist
    tests_dir = root / "tests"
    if tests_dir.exists():
        code = run([sys.executable, "-m", "pytest", "-q"])  # allow missing pytest
        if code != 0:
            return code
    print("Validation complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""


def find_module_roots(modules_dir: Path) -> List[Path]:
    roots: List[Path] = []
    for domain_dir in sorted(p for p in modules_dir.iterdir() if p.is_dir() and not p.name.startswith("__")):
        for module_dir in sorted(p for p in domain_dir.iterdir() if p.is_dir()):
            if (module_dir / "README.md").exists():
                roots.append(module_dir)
    return roots


def audit_module(module_root: Path) -> Tuple[List[str], List[Tuple[Path, str]], List[Path]]:
    missing_docs: List[str] = []
    create_files: List[Tuple[Path, str]] = []
    existing: List[Path] = []

    for doc in REQUIRED_DOCS:
        p = module_root / doc
        if p.exists():
            existing.append(p)
        else:
            missing_docs.append(doc)
            # create placeholder for missing required docs
            content = PLACEHOLDERS.get(doc, "")
            create_files.append((p, content))

    for rel, content in REQUIRED_TEST_DOCS:
        p = module_root / rel
        if not p.exists():
            create_files.append((p, content))
        else:
            existing.append(p)

    # Ensure required dirs/files
    for rel in ("src/__init__.py", "memory/README.md"):
        p = module_root / rel
        if not p.exists():
            create_files.append((p, PLACEHOLDERS.get(rel, "")))
        else:
            existing.append(p)

    validate_py = module_root / "scripts" / "validate.py"
    if not validate_py.exists():
        create_files.append((validate_py, VALIDATE_TEMPLATE))
    else:
        existing.append(validate_py)

    return missing_docs, create_files, existing


def write_files(pairs: List[Tuple[Path, str]], dry_run: bool) -> None:
    for path, content in pairs:
        if dry_run:
            print(f"CREATE {path}")
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        # Only create if truly missing to avoid clobber
        if not path.exists():
            path.write_text(content, encoding="utf-8")
            # make validate executable friendly on unix
            if path.name == "validate.py":
                try:
                    path.chmod(0o755)
                except Exception:
                    pass
            print(f"WROTE {path}")
        else:
            print(f"SKIP (exists) {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Write missing files")
    parser.add_argument("--dry-run", action="store_true", help="Only print actions")
    args = parser.parse_args()
    dry = not args.apply
    if args.apply and args.dry_run:
        print("Choose either --apply or --dry-run, not both")
        return 2

    project_root = Path(__file__).resolve().parents[1]
    modules_dir = project_root / "modules"
    if not modules_dir.exists():
        print("modules/ not found")
        return 2

    roots = find_module_roots(modules_dir)
    print(f"Found {len(roots)} module roots with README.md")

    total_missing_docs = 0
    todo_writes: List[Tuple[Path, str]] = []

    for root in roots:
        missing_docs, create_files, _ = audit_module(root)
        if missing_docs:
            total_missing_docs += len(missing_docs)
            print(f"[DOCS] {root}: missing {missing_docs}")
        for p, _ in create_files:
            print(f"[CREATE] {p}")
        todo_writes.extend(create_files)

    if dry:
        print("\nDRY-RUN complete.")
        return 0

    write_files(todo_writes, dry_run=False)
    print("\nAPPLY complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


