"""
Wardrobe IDE CLI - Command-line interface for recording and replaying skills

Usage:
    python -m modules.infrastructure.wardrobe_ide record --name "skill_name" --url "https://..." [options]
    python -m modules.infrastructure.wardrobe_ide replay --name "skill_name" [options]
    python -m modules.infrastructure.wardrobe_ide list [options]

Examples:
    # Record a new skill
    python -m modules.infrastructure.wardrobe_ide record \\
        --name "yt_like_and_reply" \\
        --url "https://studio.youtube.com/..." \\
        --backend playwright \\
        --duration 20

    # Replay a skill
    python -m modules.infrastructure.wardrobe_ide replay \\
        --name "yt_like_and_reply"

    # List all skills
    python -m modules.infrastructure.wardrobe_ide list
"""
import argparse
import sys

from .src.recorder import record_new_skill, replay_skill_by_name, show_skills_library
from .src.skills_store import import_skill_file
from .src.config import DEFAULT_BACKEND, DEFAULT_RECORD_DURATION


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Wardrobe IDE - Record and replay browser interactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Record command
    record_parser = subparsers.add_parser(
        "record",
        help="Record a new Wardrobe Skill"
    )
    record_parser.add_argument(
        "--name",
        required=True,
        help="Skill name (e.g. 'yt_like_and_reply')"
    )
    record_parser.add_argument(
        "--url",
        required=True,
        help="Target URL to record interaction"
    )
    record_parser.add_argument(
        "--backend",
        default=DEFAULT_BACKEND,
        choices=["playwright", "selenium"],
        help=f"Backend to use for recording (default: {DEFAULT_BACKEND})"
    )
    record_parser.add_argument(
        "--duration",
        type=int,
        default=DEFAULT_RECORD_DURATION,
        help=f"Recording duration in seconds (default: {DEFAULT_RECORD_DURATION})"
    )
    record_parser.add_argument(
        "--tags",
        nargs="*",
        help="Tags for categorization (e.g. youtube engagement)"
    )
    record_parser.add_argument(
        "--notes",
        help="Notes about the skill"
    )

    # Replay command
    replay_parser = subparsers.add_parser(
        "replay",
        help="Replay a recorded Wardrobe Skill"
    )
    replay_parser.add_argument(
        "--name",
        required=True,
        help="Skill name to replay"
    )
    replay_parser.add_argument(
        "--backend",
        choices=["playwright", "selenium"],
        help="Backend to use for replay (uses skill's backend if not specified)"
    )

    # List command
    list_parser = subparsers.add_parser(
        "list",
        help="List all recorded skills"
    )
    list_parser.add_argument(
        "--backend",
        choices=["playwright", "selenium"],
        help="Filter by backend"
    )

    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Import a downloaded skill JSON into the Wardrobe library"
    )
    import_parser.add_argument(
        "--file",
        required=True,
        help="Path to the JSON skill file (e.g., downloaded from the Chrome extension)"
    )
    import_parser.add_argument(
        "--backend",
        choices=["playwright", "selenium"],
        help="Force backend (maps chrome_extension -> selenium by default)"
    )
    import_parser.add_argument(
        "--name",
        help="Optional new name for the skill"
    )

    # Parse args
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Execute command
    try:
        if args.command == "record":
            record_new_skill(
                name=args.name,
                target_url=args.url,
                backend=args.backend,
                duration_seconds=args.duration,
                tags=args.tags,
                notes=args.notes
            )

        elif args.command == "replay":
            replay_skill_by_name(
                name=args.name,
                backend=args.backend
            )

        elif args.command == "list":
            show_skills_library(backend_filter=args.backend)

        elif args.command == "import":
            skill = import_skill_file(
                file_path=args.file,
                backend_override=args.backend,
                name_override=args.name,
            )
            print(f"[WARDROBE-IDE] Imported skill '{skill.name}' (backend={skill.backend})")

    except KeyboardInterrupt:
        print("\n[WARDROBE-IDE] Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[WARDROBE-IDE] Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
