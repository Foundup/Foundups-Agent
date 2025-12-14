"""
Simple watcher to auto-import YouTube Studio recordings dropped in Downloads.

Usage:
    python -m modules.infrastructure.wardrobe_ide.watch_yt_downloads \
        --pattern "yt_studio_*.json" \
        --interval 5 \
        --delete

Notes:
    - Watches WARDROBE_DOWNLOADS_DIR (or ~/Downloads).
    - Imports matching files into the Wardrobe skills store (maps chrome_extension -> selenium).
    - Optional --delete removes the source file after successful import.
    - Ctrl+C to stop.
"""
import argparse
import os
import time
from pathlib import Path

from modules.infrastructure.wardrobe_ide import import_skill_file


def main():
    parser = argparse.ArgumentParser(description="Watch Downloads for YT Studio skills and import them")
    parser.add_argument("--pattern", default="yt_studio_*.json", help="Glob pattern to watch")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval (seconds)")
    parser.add_argument("--backend", choices=["playwright", "selenium"], help="Force backend (default: chrome_extension -> selenium)")
    parser.add_argument("--delete", action="store_true", help="Delete file after successful import")
    args = parser.parse_args()

    downloads_dir = Path(os.getenv("WARDROBE_DOWNLOADS_DIR", Path.home() / "Downloads"))
    if not downloads_dir.exists():
        raise SystemExit(f"Downloads directory not found: {downloads_dir}")

    seen = set()
    print(f"[WATCH] Watching {downloads_dir} for {args.pattern} (interval {args.interval}s)")

    try:
        while True:
            for fp in downloads_dir.glob(args.pattern):
                key = (fp.name, fp.stat().st_mtime)
                if key in seen:
                    continue
                try:
                    skill = import_skill_file(fp, backend_override=args.backend)
                    print(f"[IMPORT] {fp.name} -> {skill.name} backend={skill.backend} steps={len(skill.steps)}")
                    if args.delete:
                        fp.unlink(missing_ok=True)
                        print(f"[CLEAN] Deleted {fp}")
                except Exception as e:
                    print(f"[ERROR] Failed to import {fp}: {e}")
                seen.add(key)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\n[WATCH] Stopped.")


if __name__ == "__main__":
    main()
