#!/usr/bin/env python3
"""
Suno Lyrics Extractor for FFCPLN Songs

Extract lyrics from Suno AI for 012's original songs.
Since the songs were created in Suno, the lyrics exist there.

Options:
1. Suno API (if available) - use song IDs
2. Suno webpage scrape - parse song pages
3. YouTube captions - extract from 012's channel

Usage:
    # From Suno song URL:
    python suno_lyrics_extractor.py --url "https://suno.com/song/xxxx"

    # From list of Suno URLs:
    python suno_lyrics_extractor.py --urls-file "suno_songs.txt"

    # From YouTube video (extract captions):
    python suno_lyrics_extractor.py --youtube "VIDEO_ID" --artist "UnDaoDu" --title "fuck trump"

    # From YouTube playlist:
    python suno_lyrics_extractor.py --youtube-playlist "PLAYLIST_ID"
"""

import argparse
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse, parse_qs

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DEFAULT_OUTPUT_DIR = Path("data/lrc_files")


def extract_suno_song_id(url: str) -> Optional[str]:
    """Extract song ID from Suno URL."""
    # Format: https://suno.com/song/xxxx or https://suno.ai/song/xxxx
    patterns = [
        r'suno\.com/song/([a-zA-Z0-9-]+)',
        r'suno\.ai/song/([a-zA-Z0-9-]+)',
        r'suno\.com/s/([a-zA-Z0-9-]+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None


def scrape_suno_page(url: str) -> Optional[Dict]:
    """
    Scrape Suno song page for lyrics and metadata.

    Note: Suno pages are JS-rendered, so this uses Selenium.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        logger.error("Selenium not installed. Run: pip install selenium")
        return None

    logger.info(f"[SUNO] Scraping: {url}")

    try:
        # Use existing browser manager if available
        from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
        manager = get_browser_manager()
        driver = manager.get_driver()
    except ImportError:
        # Fallback to basic Chrome
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        driver = webdriver.Chrome(options=options)

    try:
        driver.get(url)

        # Wait for page to load (Suno uses React)
        time.sleep(5)

        # Try to find lyrics section
        # Suno typically has lyrics in a specific container
        lyrics_selectors = [
            '[data-testid="lyrics"]',
            '.lyrics-container',
            '.song-lyrics',
            '[class*="lyrics"]',
            '[class*="Lyrics"]',
        ]

        lyrics_text = None
        for selector in lyrics_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                lyrics_text = elem.text
                if lyrics_text:
                    break
            except:
                continue

        # Try to get title and artist
        title = None
        artist = None

        try:
            # Look for song title
            title_elem = driver.find_element(By.CSS_SELECTOR, 'h1, [class*="title"], [class*="Title"]')
            title = title_elem.text.strip()
        except:
            pass

        try:
            # Look for artist/creator
            artist_elem = driver.find_element(By.CSS_SELECTOR, '[class*="creator"], [class*="author"], [class*="artist"]')
            artist = artist_elem.text.strip()
        except:
            pass

        if not lyrics_text:
            # Try getting page source and parsing
            page_source = driver.page_source

            # Look for lyrics in page source (often in JSON data)
            lyrics_match = re.search(r'"lyrics"\s*:\s*"([^"]+)"', page_source)
            if lyrics_match:
                lyrics_text = lyrics_match.group(1).replace('\\n', '\n')

        if lyrics_text:
            return {
                'title': title or 'Unknown',
                'artist': artist or 'Unknown',
                'lyrics': lyrics_text,
                'url': url,
                'source': 'suno-scrape'
            }
        else:
            logger.warning(f"[SUNO] No lyrics found on page: {url}")
            return None

    except Exception as e:
        logger.error(f"[SUNO] Scrape error: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass


def extract_youtube_captions(video_id: str, artist: str = "", title: str = "") -> Optional[Dict]:
    """
    Extract captions/subtitles from YouTube video using yt-dlp.

    For 012's Suno songs uploaded to YouTube, auto-captions may have lyrics.
    """
    logger.info(f"[YOUTUBE] Extracting captions: {video_id}")

    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "%(id)s"

        cmd = [
            "yt-dlp",
            "--skip-download",
            "--write-auto-subs",
            "--sub-lang", "en",
            "--sub-format", "vtt",
            "-o", str(output_path),
            f"https://www.youtube.com/watch?v={video_id}"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                logger.warning(f"[YOUTUBE] yt-dlp failed: {result.stderr[:200]}")
                return None

            # Find the VTT file
            vtt_files = list(Path(tmpdir).glob("*.vtt"))

            if not vtt_files:
                logger.warning(f"[YOUTUBE] No captions found for: {video_id}")
                return None

            # Parse VTT file
            vtt_path = vtt_files[0]
            lyrics = parse_vtt_to_lyrics(vtt_path)

            if lyrics:
                # Get video title if not provided
                if not title:
                    title_cmd = ["yt-dlp", "--get-title", f"https://www.youtube.com/watch?v={video_id}"]
                    title_result = subprocess.run(title_cmd, capture_output=True, text=True, timeout=30)
                    if title_result.returncode == 0:
                        title = title_result.stdout.strip()

                return {
                    'title': title or video_id,
                    'artist': artist or 'antifaFM',
                    'lyrics': lyrics,
                    'video_id': video_id,
                    'source': 'youtube-captions'
                }

        except subprocess.TimeoutExpired:
            logger.warning("[YOUTUBE] Timeout extracting captions")
        except Exception as e:
            logger.error(f"[YOUTUBE] Error: {e}")

    return None


def parse_vtt_to_lyrics(vtt_path: Path) -> List[Tuple[int, str]]:
    """
    Parse VTT subtitle file to (timestamp_ms, text) tuples.

    Cleans up auto-generated captions (removes duplicates, timing artifacts).
    """
    lyrics = []
    seen_text = set()

    with open(vtt_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # VTT format: 00:00:05.000 --> 00:00:08.000
    #             Caption text
    pattern = r'(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s*-->\s*\d{2}:\d{2}:\d{2}\.\d{3}\s*\n(.+?)(?=\n\n|\n\d{2}:|$)'

    for match in re.finditer(pattern, content, re.DOTALL):
        hours, mins, secs, millis = match.groups()[:4]
        text = match.group(5).strip()

        # Clean up caption text
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'\[.*?\]', '', text)  # Remove [Music] etc.
        text = text.strip()

        if not text or text in seen_text:
            continue

        seen_text.add(text)

        timestamp_ms = (int(hours) * 3600 + int(mins) * 60 + int(secs)) * 1000 + int(millis)
        lyrics.append((timestamp_ms, text))

    return lyrics


def lyrics_to_lrc_format(data: Dict) -> str:
    """Convert extracted data to LRC format string."""
    lines = []

    # Metadata
    if data.get('artist'):
        lines.append(f"[ar:{data['artist']}]")
    if data.get('title'):
        lines.append(f"[ti:{data['title']}]")
    lines.append(f"[by:Extracted from {data.get('source', 'unknown')}]")
    lines.append("")

    lyrics = data.get('lyrics', [])

    if isinstance(lyrics, str):
        # Plain text lyrics - add simple timing
        for i, line in enumerate(lyrics.split('\n')):
            line = line.strip()
            if line:
                # Estimate timing: 3 seconds per line
                timestamp_ms = i * 3000
                mins = timestamp_ms // 60000
                secs = (timestamp_ms % 60000) // 1000
                centis = (timestamp_ms % 1000) // 10
                lines.append(f"[{mins:02d}:{secs:02d}.{centis:02d}] {line}")
    else:
        # Timed lyrics
        for timestamp_ms, text in lyrics:
            mins = timestamp_ms // 60000
            secs = (timestamp_ms % 60000) // 1000
            centis = (timestamp_ms % 1000) // 10
            lines.append(f"[{mins:02d}:{secs:02d}.{centis:02d}] {text}")

    return '\n'.join(lines)


def save_lrc_file(data: Dict, output_dir: Path) -> Optional[Path]:
    """Save extracted lyrics as LRC file."""
    if not data or not data.get('lyrics'):
        return None

    lrc_content = lyrics_to_lrc_format(data)

    output_dir.mkdir(parents=True, exist_ok=True)

    artist = data.get('artist', 'Unknown')
    title = data.get('title', 'Unknown')
    safe_filename = "".join(c if c.isalnum() or c in " -_" else "_" for c in f"{artist}_{title}")

    lrc_path = output_dir / f"{safe_filename[:60]}.lrc"

    with open(lrc_path, 'w', encoding='utf-8') as f:
        f.write(lrc_content)

    logger.info(f"[SAVE] Created: {lrc_path}")
    return lrc_path


def batch_extract_youtube_playlist(playlist_id: str, output_dir: Path) -> List[Path]:
    """
    Extract lyrics from all videos in a YouTube playlist.

    For 012's 11 hours of music, this processes the entire playlist.
    """
    logger.info(f"[PLAYLIST] Processing: {playlist_id}")

    # Get video IDs from playlist
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--print", "%(id)s|%(title)s",
        f"https://www.youtube.com/playlist?list={playlist_id}"
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if result.returncode != 0:
            logger.error(f"[PLAYLIST] Failed to get videos: {result.stderr[:200]}")
            return []

        videos = []
        for line in result.stdout.strip().split('\n'):
            if '|' in line:
                video_id, title = line.split('|', 1)
                videos.append((video_id, title))

        logger.info(f"[PLAYLIST] Found {len(videos)} videos")

        generated = []
        for i, (video_id, title) in enumerate(videos):
            logger.info(f"[PLAYLIST] Processing {i+1}/{len(videos)}: {title}")

            # Try to parse artist from title (format: "Artist - Title")
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                artist, song_title = parts
            else:
                artist = "antifaFM"
                song_title = title

            data = extract_youtube_captions(video_id, artist=artist, title=song_title)

            if data:
                lrc_path = save_lrc_file(data, output_dir)
                if lrc_path:
                    generated.append(lrc_path)

            # Rate limit
            time.sleep(2)

        return generated

    except subprocess.TimeoutExpired:
        logger.error("[PLAYLIST] Timeout getting playlist")
        return []
    except Exception as e:
        logger.error(f"[PLAYLIST] Error: {e}")
        return []


def main():
    parser = argparse.ArgumentParser(
        description="Extract lyrics from Suno AI songs or YouTube captions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From Suno song URL:
  python suno_lyrics_extractor.py --url "https://suno.com/song/xxxx"

  # From YouTube video (captions):
  python suno_lyrics_extractor.py --youtube "dQw4w9WgXcQ" --artist "UnDaoDu" --title "fuck trump"

  # From YouTube playlist (batch - for 11hrs of music):
  python suno_lyrics_extractor.py --youtube-playlist "PLxxxxx" --output "data/lrc_files"

  # Import generated LRC files:
  python generate_lrc_files.py --import-folder "data/lrc_files"
        """
    )

    # Input options
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--url", help="Suno song URL to scrape")
    input_group.add_argument("--urls-file", type=Path, help="File with Suno URLs (one per line)")
    input_group.add_argument("--youtube", help="YouTube video ID to extract captions from")
    input_group.add_argument("--youtube-playlist", dest="playlist", help="YouTube playlist ID")

    # Metadata for single video
    parser.add_argument("--artist", "-a", default="", help="Artist name")
    parser.add_argument("--title", "-t", default="", help="Song title")

    # Output
    parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for LRC files")

    args = parser.parse_args()

    print("=" * 60)
    print("[SUNO EXTRACTOR] Lyrics extraction for FFCPLN songs")
    print("=" * 60)

    if args.url:
        # Single Suno URL
        data = scrape_suno_page(args.url)
        if data:
            lrc_path = save_lrc_file(data, args.output)
            if lrc_path:
                print(f"\n[DONE] Created: {lrc_path}")
        else:
            print("\n[FAILED] Could not extract lyrics from Suno page")
            print("[TIP] Try YouTube captions instead: --youtube VIDEO_ID")

    elif args.urls_file:
        # Multiple Suno URLs from file
        if not args.urls_file.exists():
            print(f"[ERROR] File not found: {args.urls_file}")
            return

        urls = [line.strip() for line in args.urls_file.read_text().split('\n') if line.strip()]
        print(f"[BATCH] Processing {len(urls)} URLs")

        generated = []
        for url in urls:
            data = scrape_suno_page(url)
            if data:
                lrc_path = save_lrc_file(data, args.output)
                if lrc_path:
                    generated.append(lrc_path)
            time.sleep(2)  # Rate limit

        print(f"\n[DONE] Generated {len(generated)}/{len(urls)} LRC files")

    elif args.youtube:
        # Single YouTube video
        data = extract_youtube_captions(args.youtube, artist=args.artist, title=args.title)
        if data:
            lrc_path = save_lrc_file(data, args.output)
            if lrc_path:
                print(f"\n[DONE] Created: {lrc_path}")
        else:
            print("\n[FAILED] Could not extract captions")
            print("[TIP] Video may not have auto-captions enabled")

    elif args.playlist:
        # YouTube playlist (batch)
        generated = batch_extract_youtube_playlist(args.playlist, args.output)
        print(f"\n[DONE] Generated {len(generated)} LRC files in: {args.output}")

    print("\n[NEXT] Review/edit files, then import:")
    print(f"       python generate_lrc_files.py --import-folder {args.output}")


if __name__ == "__main__":
    main()
