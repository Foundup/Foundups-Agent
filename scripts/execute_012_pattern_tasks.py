#!/usr/bin/env python3
"""
Replay pattern tasks exported from ingest_012_patterns.py:
- Loads holo_index/memory/012_pattern_tasks.json
- Runs HoloIndex search for each suggested_query (--verbose)
- Stores the CLI output back into PatternMemory so AI Overseer/Qwen
  can analyze the observed outcome.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

from holo_index.qwen_advisor.pattern_memory import PatternMemory  # noqa: E402

PATTERN_TASKS = REPO_ROOT / "holo_index" / "memory" / "012_pattern_tasks.json"
PYTHON_EXE = REPO_ROOT / ".venv" / "Scripts" / "python.exe"


def run_holo_search(query: str, limit: int = 5) -> subprocess.CompletedProcess[str]:
    cmd = [
        str(PYTHON_EXE),
        "holo_index.py",
        "--search",
        query,
        "--limit",
        str(limit),
        "--verbose",
    ]
    return subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def main():
    parser = argparse.ArgumentParser(description="Execute stored 012 pattern tasks via HoloIndex.")
    parser.add_argument("--file", type=Path, default=PATTERN_TASKS, help="Task JSON file path.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of tasks to run.")
    parser.add_argument("--skip", type=int, default=0, help="Number of tasks to skip (offset).")
    parser.add_argument("--dry-run", action="store_true", help="Print commands without executing.")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"[ERROR] Task file not found: {args.file}")
        sys.exit(1)

    tasks = json.loads(args.file.read_text(encoding="utf-8"))
    if args.skip:
        tasks = tasks[args.skip :]
    if args.limit:
        tasks = tasks[: args.limit]

    if not tasks:
        print("[WARN] No pattern tasks to run.")
        return

    pattern_memory = PatternMemory()
    success = 0

    for task in tasks:
        pattern_id = task.get("pattern_id", "unknown")
        query = task.get("suggested_query", "")
        module = task.get("module", "unknown")
        print(f"\n[RUN] {pattern_id} -> '{query}'")

        if args.dry_run:
            print("  (dry-run) skipping execution.")
            continue

        result = run_holo_search(query)
        stdout = result.stdout or ""
        stderr = result.stderr or ""
        output = stdout + "\n" + stderr
        ok = result.returncode == 0
        if ok:
            success += 1
            print("  [OK] HoloIndex completed.")
        else:
            print(f"  [FAIL] HoloIndex returned {result.returncode}")

        pattern_memory.store_pattern(
            {
                "id": f"{pattern_id}_run_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
                "context": f"Query: {query}\nModule: {module}\n---\n{output.strip()}",
                "decision": {
                    "query": query,
                    "module": module,
                },
                "outcome": {
                    "result": "success" if ok else "failure",
                    "return_code": result.returncode,
                },
                "module": module,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "verified": ok,
                "source": "012_pattern_task_runner",
            }
        )

    print(f"\n[SUMMARY] Executed {len(tasks)} tasks ({success} succeeded).")


if __name__ == "__main__":
    main()
