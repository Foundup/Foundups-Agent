#!/usr/bin/env python3
"""
Video Indexer - CLI Interface

Agent-callable CLI wrapper for video indexing automation.
Enables IronClaw/OpenClaw to invoke indexing directly.

WSP Compliance:
    WSP 72: Module Independence (standalone CLI)
    WSP 11: Interface Documentation

Usage:
    python -m modules.ai_intelligence.video_indexer.cli --channel undaodu
    python -m modules.ai_intelligence.video_indexer.cli --channel move2japan --video-id abc123
    python -m modules.ai_intelligence.video_indexer.cli --status
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path

# UTF-8 enforcement (WSP 90) - entry point only
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

INDEX_ROOT = Path("memory") / "video_index"


def main():
    parser = argparse.ArgumentParser(
        description='Video Indexer - Agent CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Index all videos for a channel
  python -m modules.ai_intelligence.video_indexer.cli --channel undaodu

  # Index specific video
  python -m modules.ai_intelligence.video_indexer.cli --channel move2japan --video-id abc123

  # Check indexing status
  python -m modules.ai_intelligence.video_indexer.cli --status

  # List indexed videos for channel
  python -m modules.ai_intelligence.video_indexer.cli --channel undaodu --list

  # Force reindex
  python -m modules.ai_intelligence.video_indexer.cli --channel move2japan --reindex
        """
    )

    parser.add_argument('--channel', '-c', type=str,
                        help='Channel key: move2japan, undaodu, foundups, antifafm')
    parser.add_argument('--video-id', '-v', type=str,
                        help='Specific video ID to index')
    parser.add_argument('--batch-size', '-b', type=int, default=10,
                        help='Videos per batch (default: 10)')
    parser.add_argument('--status', '-s', action='store_true',
                        help='Show indexing status and exit')
    parser.add_argument('--list', '-l', action='store_true',
                        help='List indexed videos for channel')
    parser.add_argument('--reindex', action='store_true',
                        help='Force reindex (ignore existing)')
    parser.add_argument('--skip-holoindex', action='store_true',
                        help='Skip ChromaDB indexing (JSON only)')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Status mode
    if args.status:
        return show_status()

    # List mode
    if args.list:
        if not args.channel:
            parser.error("--channel required with --list")
        return list_indexed(args.channel)

    # Require channel for indexing
    if not args.channel:
        parser.error("--channel is required (or use --status)")

    # Execute indexing
    return run_indexing(args)


def show_status():
    """Show indexing status across all channels."""
    print("\n[STATUS] Video Index Status")
    print("=" * 50)

    if not INDEX_ROOT.exists():
        print("  No index directory found")
        return 0

    total = 0
    for channel_dir in INDEX_ROOT.iterdir():
        if channel_dir.is_dir():
            count = len(list(channel_dir.glob("*.json")))
            total += count
            print(f"  {channel_dir.name}: {count} videos indexed")

    print(f"\n  TOTAL: {total} videos")
    return 0


def list_indexed(channel: str):
    """List indexed videos for a channel."""
    channel_dir = INDEX_ROOT / channel

    if not channel_dir.exists():
        print(f"[LIST] No index found for channel: {channel}")
        return 0

    videos = list(channel_dir.glob("*.json"))
    print(f"\n[LIST] {channel}: {len(videos)} indexed videos")

    for v in sorted(videos)[:20]:  # Show first 20
        print(f"  - {v.stem}")

    if len(videos) > 20:
        print(f"  ... and {len(videos) - 20} more")

    return 0


def run_indexing(args):
    """Execute video indexing."""
    try:
        from modules.ai_intelligence.video_indexer.src.video_indexer import VideoIndexer

        logger.info(f"[INDEX] Channel: {args.channel}")
        logger.info(f"[INDEX] Batch size: {args.batch_size}")

        if args.video_id:
            logger.info(f"[INDEX] Video ID: {args.video_id}")

        if args.reindex:
            logger.info("[INDEX] Force reindex enabled")

        if args.skip_holoindex:
            logger.info("[INDEX] Skipping ChromaDB (JSON only)")

        indexer = VideoIndexer(channel=args.channel)

        if args.video_id:
            # Single video indexing
            result = indexer.index_video(
                video_id=args.video_id,
                force=args.reindex
            )
            print(f"\n[RESULT] Video indexed: {args.video_id}")
            print(f"[RESULT] Topics: {result.get('topics', [])}")
        else:
            # Batch indexing
            result = indexer.index_channel(
                batch_size=args.batch_size,
                force=args.reindex,
                skip_holoindex=args.skip_holoindex
            )
            print(f"\n[RESULT] Indexed: {result.get('indexed', 0)}")
            print(f"[RESULT] Skipped: {result.get('skipped', 0)}")
            print(f"[RESULT] Errors: {result.get('errors', 0)}")

        return 0

    except ImportError as e:
        logger.error(f"Failed to import indexer: {e}")
        logger.info("Try: pip install -r modules/ai_intelligence/video_indexer/requirements.txt")
        return 1
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
