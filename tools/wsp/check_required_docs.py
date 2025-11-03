# -*- coding: utf-8 -*-
import io


import sys
from pathlib import Path


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

REQUIRED_FILES = [
    "README.md",
    "INTERFACE.md",
    "ModLog.md",
    "ROADMAP.md",
    "requirements.txt",
]


def scan_modules(repo_root: Path):
    base = repo_root / "modules"
    missing = {}
    if not base.exists():
        return missing
    for domain in base.iterdir():
        if not domain.is_dir():
            continue
        for module in domain.iterdir():
            if not module.is_dir():
                continue
            misses = []
            for f in REQUIRED_FILES:
                if not (module / f).exists():
                    misses.append(f)
            if not (module / "tests" / "README.md").exists():
                misses.append("tests/README.md")
            if not (module / "memory" / "README.md").exists():
                misses.append("memory/README.md")
            if misses:
                rel = module.relative_to(repo_root)
                missing[str(rel)] = misses
    return missing


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    missing = scan_modules(root)
    if not missing:
        print("WSP doc check: all modules pass required docs.")
        sys.exit(0)
    print("WSP doc check: missing artifacts")
    for module, items in sorted(missing.items()):
        print(f"- {module}:")
        for it in items:
            print(f"  - {it}")
    sys.exit(1)




