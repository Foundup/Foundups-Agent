# -*- coding: utf-8 -*-
"""
Batch Video Indexer - Index all UnDaoDu videos via Gemini API

Usage:
    python scripts/batch_index_videos.py --batch-size 50 --delay 1.5

Features:
    - Skips already indexed videos
    - Progress tracking with JSON state file
    - Rate limiting with configurable delay
    - Graceful error handling
    - Resume from where you left off

WSP Compliance:
    WSP 72: Module Independence
    WSP 91: DAE Observability
"""

import argparse
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

os.environ['PYTHONIOENCODING'] = 'utf-8'
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


def get_indexed_videos_from_files(channel: str = 'undaodu') -> set:
    """
    Get set of already indexed video IDs from JSON files.

    This uses file-based deduplication instead of ChromaDB to avoid
    WSL/SQLite cross-filesystem issues that cause segfaults.
    """
    video_index_dir = Path(f'memory/video_index/{channel}')

    if not video_index_dir.exists():
        return set()

    # Get video IDs from JSON filenames (stem = video_id)
    indexed = set()
    for json_file in video_index_dir.glob('*.json'):
        indexed.add(json_file.stem)

    return indexed


def get_indexed_videos() -> set:
    """
    Get set of already indexed video IDs from HoloIndex.

    WARNING: This may cause segfaults when run via WSL due to ChromaDB/SQLite
    cross-filesystem issues. Use get_indexed_videos_from_files() instead.
    """
    try:
        from holo_index.core.video_search import VideoContentIndex

        index = VideoContentIndex()
        count = index.collection.count()

        # Get all video IDs from collection
        if count == 0:
            return set()

        # Fetch in batches to get all
        all_metas = []
        offset = 0
        batch = 100

        while offset < count:
            sample = index.collection.get(
                limit=batch,
                offset=offset,
                include=['metadatas']
            )
            all_metas.extend(sample.get('metadatas', []))
            offset += batch

        return set(m.get('video_id', '') for m in all_metas if m.get('video_id'))
    except Exception as e:
        logger.warning(f"HoloIndex unavailable ({e}), falling back to file-based dedup")
        return get_indexed_videos_from_files()


def load_video_ids(video_file: str) -> list:
    """Load video IDs from file, oldest first."""
    with open(video_file) as f:
        all_ids = [line.strip() for line in f if line.strip()]

    # Reverse to get oldest first
    return list(reversed(all_ids))


def save_progress(state_file: str, indexed: list, failed: list):
    """Save progress to state file."""
    state = {
        'last_updated': datetime.now().isoformat(),
        'indexed_count': len(indexed),
        'failed_count': len(failed),
        'last_indexed': indexed[-10:] if indexed else [],
        'failed': failed[-20:] if failed else [],
    }

    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)


def analyze_with_retry(analyzer, video_id: str, max_retries: int = 3, base_delay: float = 30.0):
    """Analyze video with exponential backoff retry on 429 errors."""
    import re

    for attempt in range(max_retries):
        result = analyzer.analyze_video(video_id)

        # Check for rate limit error
        if result.error and '429' in str(result.error):
            # Parse retry delay from error message
            match = re.search(r"retryDelay['\"]:\s*['\"](\d+)s", str(result.error))
            if match:
                delay = int(match.group(1)) + 5  # Add buffer
            else:
                delay = base_delay * (2 ** attempt)  # Exponential backoff

            logger.warning(f'Rate limited, waiting {delay}s before retry {attempt + 1}/{max_retries}')
            time.sleep(delay)
            continue

        return result

    return result  # Return last result after all retries


def main():
    parser = argparse.ArgumentParser(description='Batch index YouTube videos via Gemini')
    parser.add_argument('--batch-size', type=int, default=50, help='Videos per batch')
    parser.add_argument('--delay', type=float, default=1.5, help='Seconds between API calls')
    parser.add_argument('--video-file', default='data/undaodu_video_ids.txt', help='Video IDs file')
    parser.add_argument('--channel', default='undaodu', help='Channel name')
    parser.add_argument('--state-file', default='memory/batch_index_state.json', help='Progress state file')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be indexed')
    parser.add_argument('--max-retries', type=int, default=3, help='Max retries on rate limit')
    parser.add_argument('--use-holoindex', action='store_true',
                        help='Use HoloIndex for dedup (may cause segfaults via WSL)')
    parser.add_argument('--skip-holoindex', action='store_true',
                        help='Skip HoloIndex segment indexing (JSON only, faster)')
    args = parser.parse_args()

    # Ensure paths exist
    Path(args.state_file).parent.mkdir(parents=True, exist_ok=True)

    print('=' * 70)
    print(f'BATCH VIDEO INDEXER - {args.channel.upper()} Channel')
    print('=' * 70)

    # Get current state - use file-based dedup by default to avoid WSL/ChromaDB issues
    logger.info('Checking already indexed videos...')
    if args.use_holoindex:
        logger.info('Using HoloIndex for deduplication (--use-holoindex)')
        indexed_set = get_indexed_videos()
    else:
        logger.info('Using file-based deduplication (faster, WSL-safe)')
        indexed_set = get_indexed_videos_from_files(args.channel)
    logger.info(f'Already indexed: {len(indexed_set)} videos')

    # Load video list
    video_ids = load_video_ids(args.video_file)
    logger.info(f'Total videos in channel: {len(video_ids)}')

    # Filter to unindexed
    to_index = [vid for vid in video_ids if vid not in indexed_set]
    logger.info(f'Remaining to index: {len(to_index)} videos')

    if not to_index:
        logger.info('All videos already indexed!')
        return

    # Limit to batch size
    batch = to_index[:args.batch_size]
    logger.info(f'This batch: {len(batch)} videos')

    if args.dry_run:
        print('\n[DRY RUN] Would index these videos:')
        for i, vid in enumerate(batch[:10], 1):
            print(f'  {i}. {vid}')
        if len(batch) > 10:
            print(f'  ... and {len(batch) - 10} more')
        return

    # Import indexer
    from modules.ai_intelligence.video_indexer.src.gemini_video_analyzer import (
        GeminiVideoAnalyzer,
        save_analysis_result,
    )

    analyzer = GeminiVideoAnalyzer()

    print('')
    print('=' * 70)
    print(f'Starting batch: {len(batch)} videos')
    print('=' * 70)

    indexed = []
    failed = []
    start_time = time.time()

    for i, vid in enumerate(batch, 1):
        try:
            result = analyze_with_retry(analyzer, vid, max_retries=args.max_retries)

            if result.success:
                save_analysis_result(result, channel=args.channel, index_to_holoindex=not args.skip_holoindex)
                title = (result.title or '?')[:45]
                logger.info(f'[{i:03d}/{len(batch)}] OK {vid} | {len(result.segments):2d} seg | {title}')
                indexed.append(vid)
            else:
                logger.warning(f'[{i:03d}/{len(batch)}] FAIL {vid} | {result.error[:50]}')
                failed.append({'id': vid, 'error': result.error})

        except Exception as e:
            logger.error(f'[{i:03d}/{len(batch)}] ERR {vid} | {str(e)[:50]}')
            failed.append({'id': vid, 'error': str(e)})

        # Rate limit
        if i < len(batch):
            time.sleep(args.delay)

        # Save progress every 10 videos
        if i % 10 == 0:
            save_progress(args.state_file, indexed, [f['id'] for f in failed])

    # Final progress save
    save_progress(args.state_file, indexed, [f['id'] for f in failed])

    elapsed = time.time() - start_time

    print('')
    print('=' * 70)
    print(f'BATCH COMPLETE')
    print('=' * 70)
    print(f'Indexed:    {len(indexed)} videos')
    print(f'Failed:     {len(failed)} videos')
    print(f'Time:       {elapsed:.1f}s ({elapsed/len(batch):.1f}s per video)')
    print(f'Remaining:  {len(to_index) - len(indexed)} videos')
    print('')

    # Summary
    final_count = len(indexed_set) + len(indexed)
    total = len(video_ids)
    pct = (final_count / total) * 100
    print(f'Progress: {final_count}/{total} ({pct:.1f}%)')


if __name__ == '__main__':
    main()
