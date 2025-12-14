"""
Minimal recording trigger (no UI) for 012/automation to start a Wardrobe recording.

Usage:
    python -m modules.infrastructure.wardrobe_ide.record_trigger --name demo --url https://example.com --duration 15
Environment overrides:
    WARDROBE_DEFAULT_BACKEND (playwright|selenium) - playwright is required for recording.
"""
import argparse
import sys

from .src.recorder import record_new_skill
from .src.config import DEFAULT_BACKEND, DEFAULT_RECORD_DURATION


def main():
    parser = argparse.ArgumentParser(description="Wardrobe recording trigger")
    parser.add_argument("--name", required=True, help="Skill name")
    parser.add_argument("--url", required=True, help="Target URL to record")
    parser.add_argument("--duration", type=int, default=DEFAULT_RECORD_DURATION, help="Recording duration (seconds)")
    parser.add_argument("--backend", default=DEFAULT_BACKEND, choices=["playwright", "selenium"], help="Backend (use playwright to record)")
    args = parser.parse_args()

    record_new_skill(
        name=args.name,
        target_url=args.url,
        backend=args.backend,
        duration_seconds=args.duration,
        tags=None,
        notes="Triggered via record_trigger.py",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
