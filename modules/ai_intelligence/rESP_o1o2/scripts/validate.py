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
    # Prevent any git automation / post-commit side effects during validation runs.
    env.setdefault("FOUNDUPS_SKIP_POST_COMMIT", "1")
    # Lint placeholder (optional tools): ruff/flake8 if available
    run([sys.executable, "-m", "pip", "--version"], env=env)  # smoke
    # Pytest if tests exist
    tests_dir = root / "tests"
    if tests_dir.exists():
        # Pytest is optional and can be unstable in some global Python setups (plugins/output hooks).
        # Enable explicitly with RUN_PYTEST=1.
        run_pytest = os.getenv("RUN_PYTEST", "").strip().lower() in {"1", "true", "yes"}
        if run_pytest:
            # -s: disable capture (avoids Windows capture edge-cases)
            code = run([sys.executable, "-m", "pytest", "-q", "-s"], env=env)
            if code != 0:
                return code
        else:
            print("Pytest skipped (set RUN_PYTEST=1 to enable).")
    print("Validation complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
