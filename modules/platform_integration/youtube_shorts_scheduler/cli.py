#!/usr/bin/env python3
"""
YouTube Shorts Scheduler - CLI Interface

Agent-callable CLI wrapper for scheduling automation.
Enables IronClaw/OpenClaw to invoke scheduling directly.

WSP Compliance:
    WSP 72: Module Independence (standalone CLI)
    WSP 11: Interface Documentation

Usage:
    python -m modules.platform_integration.youtube_shorts_scheduler.cli --channel move2japan
    python -m modules.platform_integration.youtube_shorts_scheduler.cli --channel undaodu --max-videos 5
    python -m modules.platform_integration.youtube_shorts_scheduler.cli --list-channels
"""

import argparse
import asyncio
import logging
import sys

# UTF-8 enforcement (WSP 90) - entry point only
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(
        description='YouTube Shorts Scheduler - Agent CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Schedule videos for Move2Japan channel
  python -m modules.platform_integration.youtube_shorts_scheduler.cli --channel move2japan

  # Schedule with limit
  python -m modules.platform_integration.youtube_shorts_scheduler.cli --channel undaodu --max-videos 5

  # List available channels
  python -m modules.platform_integration.youtube_shorts_scheduler.cli --list-channels

  # Dry run (show what would be scheduled)
  python -m modules.platform_integration.youtube_shorts_scheduler.cli --channel move2japan --dry-run
        """
    )

    parser.add_argument('--channel', '-c', type=str,
                        help='Channel key: move2japan, undaodu, foundups')
    parser.add_argument('--max-videos', '-m', type=int, default=10,
                        help='Maximum videos to schedule (default: 10)')
    parser.add_argument('--list-channels', action='store_true',
                        help='List available channels and exit')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be scheduled without executing')
    parser.add_argument('--browser', '-b', type=str, default='chrome',
                        choices=['chrome', 'edge'],
                        help='Browser to use (default: chrome)')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # List channels mode
    if args.list_channels:
        try:
            from modules.infrastructure.shared_utilities.youtube_channel_registry import get_channels
            channels = get_channels()
            print("\n[CHANNELS] Available for scheduling:")
            for ch in channels:
                print(f"  - {ch['key']}: {ch['name']} ({ch['id']})")
            return 0
        except ImportError as e:
            logger.error(f"Failed to load channel registry: {e}")
            return 1

    # Require channel for scheduling
    if not args.channel:
        parser.error("--channel is required (or use --list-channels)")

    # Execute scheduling
    try:
        from modules.platform_integration.youtube_shorts_scheduler.src.scheduler import YouTubeShortsScheduler

        logger.info(f"[SCHEDULE] Channel: {args.channel}")
        logger.info(f"[SCHEDULE] Max videos: {args.max_videos}")
        logger.info(f"[SCHEDULE] Browser: {args.browser}")

        if args.dry_run:
            logger.info("[SCHEDULE] DRY RUN - no changes will be made")

        scheduler = YouTubeShortsScheduler(channel=args.channel)

        if args.dry_run:
            # Just show unlisted videos
            unlisted = scheduler.get_unlisted_videos()
            print(f"\n[DRY-RUN] Found {len(unlisted)} unlisted videos:")
            for v in unlisted[:args.max_videos]:
                print(f"  - {v.get('title', 'Unknown')} ({v.get('video_id', '?')})")
            return 0

        result = scheduler.run_scheduling_workflow(max_videos=args.max_videos)

        print(f"\n[RESULT] Scheduled: {result.get('scheduled', 0)}")
        print(f"[RESULT] Errors: {result.get('errors', 0)}")

        return 0 if result.get('errors', 0) == 0 else 1

    except ImportError as e:
        logger.error(f"Failed to import scheduler: {e}")
        return 1
    except Exception as e:
        logger.error(f"Scheduling failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
