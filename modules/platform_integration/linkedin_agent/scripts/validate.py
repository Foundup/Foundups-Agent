#!/usr/bin/env python3
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
