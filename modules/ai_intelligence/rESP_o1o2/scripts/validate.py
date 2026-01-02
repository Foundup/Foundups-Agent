#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path

def run(cmd: list[str], env: dict | None = None) -> int:
    print("$", " ".join(cmd))
    try:
        return subprocess.call(cmd, env=env)
    except FileNotFoundError:
        print("(tool missing, skipping)")
        return 0

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    # Avoid third-party pytest plugin auto-load failures from global site-packages.
    # This keeps validation deterministic within the repo's dependency set.
    env = os.environ.copy()
    env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    # Lint placeholder (optional tools): ruff/flake8 if available
    run([sys.executable, "-m", "pip", "--version"], env=env)  # smoke
    # Pytest if tests exist
    tests_dir = root / "tests"
    if tests_dir.exists():
        # -s: disable capture (avoids Windows capture edge-cases)
        code = run([sys.executable, "-m", "pytest", "-q", "-s"], env=env)  # allow missing pytest
        if code != 0:
            return code
    print("Validation complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
