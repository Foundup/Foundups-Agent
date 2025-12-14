"""
Import Wardrobe skills from the Downloads folder into the skills store.

Usage:
    python -m modules.infrastructure.wardrobe_ide.import_from_downloads \
        --pattern "*.json" \
        --backend selenium \
        --delete

Notes:
    - By default scans ~/Downloads (override with WARDROBE_DOWNLOADS_DIR).
    - Maps chrome_extension -> selenium unless backend is explicitly provided.
    - Optionally deletes source files after successful import.
"""
import argparse
import os
from pathlib import Path

from modules.infrastructure.wardrobe_ide import import_skill_file


def main():
    parser = argparse.ArgumentParser(description="Import Wardrobe skills from Downloads")
    parser.add_argument(
        "--pattern",
        default="*.json",
        help="Glob pattern to match (default: *.json)",
    )
    parser.add_argument(
        "--backend",
        choices=["playwright", "selenium"],
        help="Force backend (default: chrome_extension -> selenium mapping)",
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Delete source files after successful import",
    )
    args = parser.parse_args()

    downloads_dir = Path(os.getenv("WARDROBE_DOWNLOADS_DIR", Path.home() / "Downloads"))
    if not downloads_dir.exists():
        raise SystemExit(f"Downloads directory not found: {downloads_dir}")

    files = sorted(downloads_dir.glob(args.pattern))
    if not files:
        print(f"[IMPORT] No files matched pattern '{args.pattern}' in {downloads_dir}")
        return

    for fp in files:
        try:
            skill = import_skill_file(
                fp,
                backend_override=args.backend,
                name_override=None,
            )
            print(
                f"[IMPORT] {fp.name} -> {skill.name} backend={skill.backend} "
                f"steps={len(skill.steps)} url={skill.meta.get('target_url')}"
            )
            if args.delete:
                fp.unlink(missing_ok=True)
                print(f"[IMPORT] Deleted source file {fp}")
        except Exception as e:
            print(f"[IMPORT] Failed on {fp}: {e}")


if __name__ == "__main__":
    main()
