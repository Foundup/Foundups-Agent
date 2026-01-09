#!/usr/bin/env python3
"""
YouTube Channel Indexing - Launch Script

WSP 62 Compliance: Extracted to scripts/index_channel.py for main.py integration.

Orchestrates the full indexing pipeline:
    Channel → VideoArchiveExtractor → BatchTranscriber → ChromaDB Index

Usage:
    from modules.communication.voice_command_ingestion.scripts.index_channel import (
        index_channel, show_indexing_menu
    )
    index_channel("move2japan", max_videos=10)
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Channel configurations (mirrored from youtube_shorts_scheduler)
CHANNELS = {
    "move2japan": {
        "id": "UC-LSSlOZwpGIRIYihaz8zCw",
        "name": "Move2Japan",
        "description": "012's Japan living channel (9,020 subscribers)",
        "chrome_port": 9222,  # Chrome (shared with UnDaoDu)
    },
    "undaodu": {
        "id": "UCfHM9Fw9HD-NwiS0seD_oIA",
        "name": "UnDaoDu",
        "description": "012's consciousness exploration channel",
        "chrome_port": 9222,  # Chrome (shared with Move2Japan)
    },
    "foundups": {
        "id": "UCSNTUXjAgpd4sgWYP0xoJgw",
        "name": "FoundUps",
        "description": "FoundUps venture studio channel",
        "chrome_port": 9223,  # Edge browser
    },
}


def list_videos_via_selenium(channel_key: str, max_videos: int = 50, oldest_first: bool = True) -> list:
    """
    List videos via Selenium (authenticated, sees ALL videos including private/unlisted).

    Uses YouTubeStudioDOM from youtube_shorts_scheduler - Lego block pattern.

    Args:
        channel_key: Channel key (move2japan, undaodu, foundups)
        max_videos: Maximum videos to list
        oldest_first: If True, sort oldest first (for indexing historical content)

    Returns:
        List of dicts with video_id, title
    """
    channel = CHANNELS.get(channel_key.lower())
    if not channel:
        print(f"[ERROR] Unknown channel: {channel_key}")
        return []

    channel_id = channel["id"]
    chrome_port = channel.get("chrome_port", 9222)

    # Build Studio URL with oldest-first sort if requested
    sort_order = "ASCENDING" if oldest_first else "DESCENDING"
    studio_url = (
        f"https://studio.youtube.com/channel/{channel_id}/videos/upload"
        f"?filter=%5B%5D&sort=%7B%22columnType%22%3A%22date%22%2C%22sortOrder%22%3A%22{sort_order}%22%7D"
    )

    print(f"\n[SELENIUM] Listing videos via YouTube Studio")
    print(f"  Channel: {channel['name']} ({channel_key})")
    print(f"  Chrome Port: {chrome_port}")
    print(f"  Sort: {'Oldest First' if oldest_first else 'Newest First'}")
    print(f"  URL: {studio_url[:80]}...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options as ChromeOptions
        from selenium.webdriver.edge.options import Options as EdgeOptions
        from modules.platform_integration.youtube_shorts_scheduler.src.dom_automation import YouTubeStudioDOM

        # Auto-launch browser if not running (Lego block: reuse dae_dependencies)
        from modules.infrastructure.dependency_launcher.src.dae_dependencies import (
            is_port_open, launch_chrome, launch_edge
        )

        # FoundUps (port 9223) uses Edge, others use Chrome
        is_edge = (chrome_port == 9223)
        browser_name = "Edge" if is_edge else "Chrome"

        # Check if browser is running, auto-launch if not
        if not is_port_open(chrome_port):
            print(f"[AUTO-LAUNCH] {browser_name} not running on port {chrome_port}, launching...")
            if is_edge:
                success, msg = launch_edge()
            else:
                success, msg = launch_chrome()

            if not success:
                print(f"[ERROR] Failed to auto-launch {browser_name}: {msg}")
                return []
            print(f"[OK] {browser_name} auto-launched: {msg}")
        else:
            print(f"[OK] {browser_name} already running on port {chrome_port}")

        # Connect to browser via remote debugging
        print(f"[CONNECT] Connecting to {browser_name}...")

        try:
            if is_edge:
                options = EdgeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
                driver = webdriver.Edge(options=options)
            else:
                options = ChromeOptions()
                options.add_experimental_option("debuggerAddress", f"127.0.0.1:{chrome_port}")
                driver = webdriver.Chrome(options=options)
        except Exception as e:
            print(f"[ERROR] Failed to connect to {browser_name} on port {chrome_port}")
            print(f"  Error: {e}")
            return []

        # Create DOM handler with the connected driver
        dom = YouTubeStudioDOM(driver)
        print(f"[OK] Connected to {browser_name}")

        # Navigate to Studio videos page with sort
        print(f"[NAV] Navigating to Studio...")
        dom.driver.get(studio_url)

        import time
        time.sleep(3)  # Wait for page load

        # Get video rows
        videos = []
        page = 1

        while len(videos) < max_videos:
            print(f"[SCAN] Page {page}: Scanning video rows...")

            rows = dom.get_video_rows()
            if not rows:
                print(f"[DONE] No more videos found on page {page}")
                break

            for row in rows:
                if len(videos) >= max_videos:
                    break
                try:
                    from selenium.webdriver.common.by import By
                    link = row.find_element(By.CSS_SELECTOR, "a[href*='/edit']")
                    href = link.get_attribute("href")
                    video_id = href.split("/video/")[1].split("/")[0]
                    title = link.text or "Unknown Title"

                    videos.append({
                        "video_id": video_id,
                        "title": title,
                        "href": href,
                    })
                    print(f"  [{len(videos)}] {video_id}: {title[:40]}...")
                except Exception as e:
                    logger.debug(f"Skip row: {e}")
                    continue

            # Check for next page
            if len(videos) < max_videos and dom.has_next_page():
                print("[NAV] Clicking next page...")
                dom.click_next_page()
                time.sleep(2)
                page += 1
            else:
                break

        print(f"\n[OK] Found {len(videos)} videos via Selenium")
        return videos

    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("[TIP] Run: pip install selenium")
        return []
    except Exception as e:
        print(f"[ERROR] Selenium listing failed: {e}")
        logger.error(f"Selenium listing failed: {e}", exc_info=True)
        return []


def index_channel(
    channel_key: str,
    max_videos: int = 10,
    model_size: str = "base",
    skip_transcription: bool = False,
    skip_indexing: bool = False,
    dry_run: bool = False,
    use_selenium: bool = False,
    oldest_first: bool = True
) -> dict:
    """
    Index a YouTube channel's videos into ChromaDB for semantic search.

    Full pipeline:
    1. List videos via Selenium (authenticated) or yt-dlp (0 API quota)
    2. Extract audio via yt-dlp + browser cookies
    3. Transcribe via faster-whisper
    4. Save to JSONL
    5. Index into ChromaDB

    Args:
        channel_key: "move2japan", "undaodu", or "foundups"
        max_videos: Maximum videos to process
        model_size: Whisper model size (tiny, base, small, medium, large-v3)
        skip_transcription: Skip transcription, only index existing JSONL
        skip_indexing: Skip indexing, only transcribe
        dry_run: Preview only, don't process
        use_selenium: Use Selenium to list videos (sees private/unlisted)
        oldest_first: Sort oldest first (for historical indexing)

    Returns:
        Dict with results: {videos_found, videos_transcribed, segments_indexed, jsonl_path}
    """
    channel = CHANNELS.get(channel_key.lower())
    if not channel:
        print(f"[ERROR] Unknown channel: {channel_key}")
        print(f"[INFO] Available: {', '.join(CHANNELS.keys())}")
        return {"error": f"Unknown channel: {channel_key}"}

    channel_id = channel["id"]
    channel_name = channel["name"]

    print(f"\n[INDEX] YouTube Channel Indexing")
    print("=" * 60)
    print(f"Channel: {channel_name} ({channel_key})")
    print(f"Channel ID: {channel_id}")
    print(f"Max Videos: {max_videos}")
    print(f"Model: {model_size}")
    print(f"Method: {'Selenium (authenticated)' if use_selenium else 'yt-dlp (public)'}")
    print(f"Sort: {'Oldest First' if oldest_first else 'Newest First'}")
    print(f"Dry Run: {'Yes' if dry_run else 'No'}")
    print("=" * 60)

    results = {
        "channel": channel_key,
        "channel_id": channel_id,
        "videos_found": 0,
        "videos_transcribed": 0,
        "segments_indexed": 0,
        "jsonl_path": None,
        "errors": []
    }

    # Output paths - just filename, BatchTranscriber adds output_dir
    jsonl_filename = f"{channel_key}_transcripts.jsonl"
    jsonl_path = Path("memory/transcripts") / jsonl_filename
    results["jsonl_path"] = str(jsonl_path)

    if dry_run:
        print("\n[DRY RUN] Preview only - no processing")
        print(f"[DRY RUN] Would save to: {jsonl_path}")
        return results

    try:
        # Phase 1: List videos (if not skip_transcription)
        video_ids = []  # Will store video IDs for transcription

        if not skip_transcription:
            if use_selenium:
                # Use Selenium (authenticated, sees ALL videos)
                print("\n[PHASE 1] Listing videos via Selenium (authenticated)...")
                selenium_videos = list_videos_via_selenium(channel_key, max_videos, oldest_first)
                results["videos_found"] = len(selenium_videos)

                if not selenium_videos:
                    print("[WARN] No videos found via Selenium")
                    return results

                video_ids = [v["video_id"] for v in selenium_videos]

                # Show video list
                for i, v in enumerate(selenium_videos[:5], 1):
                    print(f"  {i}. {v['video_id']}: {v['title'][:40]}...")
                if len(selenium_videos) > 5:
                    print(f"  ... and {len(selenium_videos) - 5} more")

            else:
                # Use yt-dlp (public videos only)
                print("\n[PHASE 1] Listing channel videos via yt-dlp...")

                from modules.platform_integration.youtube_live_audio.src.youtube_live_audio import (
                    get_archive_extractor
                )

                extractor = get_archive_extractor()
                videos = list(extractor.list_channel_videos(channel_id, max_videos=max_videos))
                results["videos_found"] = len(videos)

                print(f"[OK] Found {len(videos)} videos")

                if not videos:
                    print("[WARN] No videos found")
                    return results

                video_ids = [v.video_id for v in videos]

                # Show video list
                for i, v in enumerate(videos[:5], 1):
                    print(f"  {i}. {v.title[:50]}... ({v.duration_sec}s)")
                if len(videos) > 5:
                    print(f"  ... and {len(videos) - 5} more")

        # Phase 2: Transcribe videos
        if not skip_transcription:
            print(f"\n[PHASE 2] Transcribing with faster-whisper ({model_size})...")

            from modules.communication.voice_command_ingestion.src.voice_command_ingestion import (
                get_batch_transcriber
            )

            transcriber = get_batch_transcriber(model_size=model_size)

            # Transcribe and save
            segments = list(transcriber.transcribe_channel(channel_id, max_videos=max_videos))
            results["videos_transcribed"] = len(set(s.video_id for s in segments))

            # Save to JSONL (pass filename only, transcriber adds output_dir)
            count = transcriber.save_transcripts_jsonl(segments, jsonl_filename)
            print(f"[OK] Saved {count} transcript segments to {jsonl_path}")

        # Phase 3: Index into ChromaDB
        if not skip_indexing and jsonl_path.exists():
            print(f"\n[PHASE 3] Indexing into ChromaDB...")

            from modules.communication.voice_command_ingestion.src.transcript_index import (
                get_transcript_index
            )

            index = get_transcript_index()
            indexed = index.index_from_jsonl(str(jsonl_path))
            results["segments_indexed"] = indexed

            print(f"[OK] Indexed {indexed} segments into ChromaDB")

            # Show stats
            stats = index.get_stats()
            print(f"\n[STATS] Transcript Index")
            print(f"  Collection: {stats.get('collection', 'N/A')}")
            print(f"  Total Segments: {stats.get('segment_count', 0)}")
            print(f"  SSD Path: {stats.get('ssd_path', 'N/A')}")

        print("\n[SUCCESS] Channel indexing complete!")
        print(f"  Videos: {results['videos_transcribed']}")
        print(f"  Segments: {results['segments_indexed']}")
        print(f"  JSONL: {results['jsonl_path']}")

        return results

    except ImportError as e:
        error_msg = f"Missing dependency: {e}"
        print(f"[ERROR] {error_msg}")
        print("[TIP] Install: pip install faster-whisper yt-dlp chromadb sentence-transformers")
        results["errors"].append(error_msg)
        return results

    except Exception as e:
        error_msg = f"Indexing failed: {e}"
        print(f"[ERROR] {error_msg}")
        logger.error(error_msg, exc_info=True)
        results["errors"].append(error_msg)
        return results


def search_transcripts(query: str, limit: int = 10) -> None:
    """Search indexed transcripts with semantic similarity."""
    print(f"\n[SEARCH] Searching transcripts for: '{query}'")
    print("=" * 60)

    try:
        from modules.communication.voice_command_ingestion.src.transcript_index import (
            search_012_transcripts
        )

        results = search_012_transcripts(query, limit=limit)

        if not results:
            print("[INFO] No results found")
            print("[TIP] Make sure you've indexed some channels first!")
            return

        print(f"[OK] Found {len(results)} results:\n")

        for i, r in enumerate(results, 1):
            score_pct = r.get('score', 0) * 100
            print(f"{i}. [{score_pct:.0f}%] {r.get('title', 'N/A')[:40]}...")
            print(f"   {r.get('text', '')[:80]}...")
            print(f"   [LINK] {r.get('url', 'N/A')}")
            print()

    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        logger.error(f"Search failed: {e}", exc_info=True)


def show_indexing_menu() -> str:
    """Display YouTube indexing submenu and return choice."""
    print("\n[MENU] YouTube Channel Indexing")
    print("=" * 60)
    print("== INDEX CHANNELS (yt-dlp) ==")
    print("1. Index Move2Japan (012's Japan channel)")
    print("2. Index UnDaoDu (012's consciousness channel)")
    print("3. Index FoundUps (FoundUps venture studio)")
    print("4. Index All Channels")
    print("")
    print("== SELENIUM (authenticated, oldest first) ==")
    print("s1. [SELENIUM] Index Move2Japan (Chrome 9222)")
    print("s2. [SELENIUM] Index UnDaoDu (Chrome 9222)")
    print("s3. [SELENIUM] Index FoundUps (Edge 9223)")
    print("s4. [SELENIUM] Auto-Index All (continuous)")
    print("")
    print("== SEARCH ==")
    print("5. Search Transcripts (Semantic Search)")
    print("6. Index Status (Show ChromaDB stats)")
    print("")
    print("== OPTIONS ==")
    print("7. Reindex Only (Skip transcription)")
    print("8. Transcribe Only (Skip indexing)")
    print("")
    print("0. Back to YouTube Menu")
    print("=" * 60)

    return input("\nSelect option: ").strip()


def run_indexing_menu() -> None:
    """Run the indexing menu loop."""
    while True:
        choice = show_indexing_menu()

        if choice == "1":
            # Index Move2Japan
            max_videos = input("Max videos [10]: ").strip() or "10"
            index_channel("move2japan", max_videos=int(max_videos))
            input("\nPress Enter to continue...")

        elif choice == "2":
            # Index UnDaoDu
            max_videos = input("Max videos [10]: ").strip() or "10"
            index_channel("undaodu", max_videos=int(max_videos))
            input("\nPress Enter to continue...")

        elif choice == "3":
            # Index FoundUps
            max_videos = input("Max videos [10]: ").strip() or "10"
            index_channel("foundups", max_videos=int(max_videos))
            input("\nPress Enter to continue...")

        elif choice == "4":
            # Index All
            max_videos = input("Max videos per channel [5]: ").strip() or "5"
            max_v = int(max_videos)

            print("\n[ALL] Indexing all channels...")
            for channel_key in CHANNELS.keys():
                index_channel(channel_key, max_videos=max_v)

            input("\nPress Enter to continue...")

        elif choice == "5":
            # Search
            query = input("Search query: ").strip()
            if query:
                search_transcripts(query)
            else:
                print("[WARN] No query provided")
            input("\nPress Enter to continue...")

        elif choice == "6":
            # Status
            print("\n[STATUS] Transcript Index Stats")
            print("=" * 60)
            try:
                from modules.communication.voice_command_ingestion.src.transcript_index import (
                    get_transcript_index
                )
                index = get_transcript_index()
                stats = index.get_stats()

                print(f"Collection: {stats.get('collection', 'N/A')}")
                print(f"Segments: {stats.get('segment_count', 0)}")
                print(f"SSD Path: {stats.get('ssd_path', 'N/A')}")
                print(f"Initialized: {stats.get('initialized', False)}")

                # Check JSONL files
                memory_dir = Path("memory/transcripts")
                if memory_dir.exists():
                    jsonl_files = list(memory_dir.glob("*_transcripts.jsonl"))
                    if jsonl_files:
                        print(f"\nJSONL Files:")
                        for f in jsonl_files:
                            size_kb = f.stat().st_size / 1024
                            print(f"  - {f.name} ({size_kb:.1f} KB)")
                    else:
                        print("\n[INFO] No JSONL transcripts found yet")

            except Exception as e:
                print(f"[ERROR] Failed to get stats: {e}")
            input("\nPress Enter to continue...")

        elif choice == "7":
            # Reindex only
            channel = input("Channel (move2japan/undaodu/foundups): ").strip().lower()
            if channel in CHANNELS:
                index_channel(channel, skip_transcription=True)
            else:
                print(f"[ERROR] Unknown channel: {channel}")
            input("\nPress Enter to continue...")

        elif choice == "8":
            # Transcribe only
            channel = input("Channel (move2japan/undaodu/foundups): ").strip().lower()
            max_videos = input("Max videos [10]: ").strip() or "10"
            if channel in CHANNELS:
                index_channel(channel, max_videos=int(max_videos), skip_indexing=True)
            else:
                print(f"[ERROR] Unknown channel: {channel}")
            input("\nPress Enter to continue...")

        elif choice.lower() == "s1":
            # Selenium - Move2Japan
            max_videos = input("Max videos [50]: ").strip() or "50"
            index_channel("move2japan", max_videos=int(max_videos), use_selenium=True, oldest_first=True)
            input("\nPress Enter to continue...")

        elif choice.lower() == "s2":
            # Selenium - UnDaoDu
            max_videos = input("Max videos [50]: ").strip() or "50"
            index_channel("undaodu", max_videos=int(max_videos), use_selenium=True, oldest_first=True)
            input("\nPress Enter to continue...")

        elif choice.lower() == "s3":
            # Selenium - FoundUps
            max_videos = input("Max videos [50]: ").strip() or "50"
            index_channel("foundups", max_videos=int(max_videos), use_selenium=True, oldest_first=True)
            input("\nPress Enter to continue...")

        elif choice.lower() == "s4":
            # Selenium - Auto-Index All (continuous)
            print("\n[AUTO] Selenium Auto-Index Mode")
            print("=" * 60)
            print("This will continuously index ALL channels (oldest first)")
            print("Press Ctrl+C to stop")
            print("=" * 60)

            max_per_channel = input("Max videos per channel [20]: ").strip() or "20"
            max_v = int(max_per_channel)

            try:
                while True:
                    for channel_key in CHANNELS.keys():
                        print(f"\n[AUTO] Processing {channel_key}...")
                        index_channel(channel_key, max_videos=max_v, use_selenium=True, oldest_first=True)

                    print("\n[AUTO] All channels processed. Waiting 5 minutes before next round...")
                    import time
                    time.sleep(300)  # Wait 5 minutes

            except KeyboardInterrupt:
                print("\n[STOP] Auto-indexing stopped by user")

            input("\nPress Enter to continue...")

        elif choice == "0":
            break

        else:
            print("[ERROR] Invalid choice")


# CLI entry point
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="YouTube Channel Indexing")
    parser.add_argument("--channel", choices=list(CHANNELS.keys()), help="Channel to index")
    parser.add_argument("--max-videos", type=int, default=10, help="Max videos")
    parser.add_argument("--model", default="base", help="Whisper model size")
    parser.add_argument("--search", help="Search query")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--menu", action="store_true", help="Run interactive menu")

    args = parser.parse_args()

    if args.menu:
        run_indexing_menu()
    elif args.search:
        search_transcripts(args.search)
    elif args.channel:
        index_channel(
            args.channel,
            max_videos=args.max_videos,
            model_size=args.model,
            dry_run=args.dry_run
        )
    else:
        run_indexing_menu()
