"""
Full Chain Test: L1 → L2 → L3 Complete Scheduling Workflow

Production-aligned full cake:
- Uses the production scheduler orchestrator (src/scheduler.py) + production DOM layer (src/dom_automation.py)
- This ensures layer validation work is applied to the production prototype (no duplicated selectors here).

Run: python -m modules.platform_integration.youtube_shorts_scheduler.tests.test_full_chain
"""

import argparse
import asyncio
import json
import os

from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import run_scheduler_dae

def main():
    parser = argparse.ArgumentParser(description="Full Chain Test: L1 → L2 → L3 → L4")
    parser.add_argument("--channel", default="move2japan", help="Channel key (move2japan/undaodu/foundups/ravingantifa)")
    parser.add_argument("--max", type=int, default=1, help="Max videos to process (default 1)")
    parser.add_argument("--dry-run", action="store_true", help="Preview only (no schedule/save)")
    # Compatibility: main.py launcher passes --selenium to all selenium tests.
    parser.add_argument("--selenium", action="store_true", help="Compatibility no-op (ignored)")
    # Future: optional visual verification gate (not used yet by this runner).
    parser.add_argument("--wre-tars", action="store_true", help="Compatibility placeholder (ignored)")
    args = parser.parse_args()

    # Ensure full-cake features are enabled by default for this runner.
    os.environ.setdefault("YT_SCHEDULER_INDEX_WEAVE_ENABLED", "true")
    os.environ.setdefault("YT_SCHEDULER_INDEX_MODE", "stub")
    os.environ.setdefault("YT_SCHEDULER_INDEX_ENHANCE_DESCRIPTION", "true")
    os.environ.setdefault("YT_SCHEDULER_INDEX_INFORM_TITLE", "true")

    results = asyncio.run(run_scheduler_dae(args.channel, max_videos=args.max, dry_run=args.dry_run))
    print(json.dumps(results, indent=2)[:8000])
    ok = bool(results) and not results.get("error") and (args.dry_run or results.get("total_scheduled", 0) >= 0)
    raise SystemExit(0 if ok else 1)


if __name__ == "__main__":
    main()

