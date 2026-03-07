#!/usr/bin/env python3
"""
Suno LRC Downloader - Playwright Automation

Automatically downloads LRC files from Suno playlist using browser automation.
No extension needed - scrapes lyrics directly and generates LRC files.

Usage:
    # Download from 012's playlist:
    python suno_lrc_downloader.py --playlist "3adb1878-12f8-4c1c-a815-bde3d7d320ed"

    # With login (for private playlists):
    python suno_lrc_downloader.py --playlist "..." --login

    # Limit songs:
    python suno_lrc_downloader.py --playlist "..." --max 10

    # Resume from index:
    python suno_lrc_downloader.py --playlist "..." --start 50

Requirements:
    pip install playwright
    playwright install chromium
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Setup paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Paths
DATA_DIR = Path(__file__).parent.parent / "data"
LRC_OUTPUT_DIR = DATA_DIR / "lrc_downloads"
SESSION_FILE = DATA_DIR / "suno_session.json"
PROGRESS_FILE = DATA_DIR / "suno_download_progress.json"


@dataclass
class SongData:
    """Extracted song data."""
    id: str
    title: str
    artist: str
    lyrics: str
    style: str
    duration_sec: int
    url: str


class SunoLRCDownloader:
    """Downloads LRC files from Suno using Playwright."""

    SUNO_BASE = "https://suno.com"

    def __init__(self, headless: bool = False):
        self.headless = headless
        self.browser = None
        self.context = None
        self.page = None
        self.progress = {"completed": [], "failed": []}

    async def setup(self, login: bool = False):
        """Initialize Playwright browser."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            logger.error("Playwright not installed. Run:")
            logger.error("  pip install playwright")
            logger.error("  playwright install chromium")
            raise

        self.playwright = await async_playwright().start()

        # Use persistent context for login state
        user_data_dir = DATA_DIR / "playwright_profile"
        user_data_dir.mkdir(parents=True, exist_ok=True)

        self.browser = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(user_data_dir),
            headless=self.headless,
            viewport={"width": 1920, "height": 1080},
        )

        self.page = await self.browser.new_page()

        if login:
            await self._do_login()

        logger.info("[SETUP] Browser ready")

    async def _do_login(self):
        """Interactive login to Suno."""
        logger.info("[LOGIN] Opening Suno login page...")
        await self.page.goto(f"{self.SUNO_BASE}/signin")

        print("\n" + "=" * 60)
        print("[LOGIN] Please log in to Suno in the browser window.")
        print("Press ENTER when done...")
        print("=" * 60)
        input()

        # Wait for login to complete
        await asyncio.sleep(2)
        logger.info("[LOGIN] Login complete")

    async def close(self):
        """Clean up browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

    async def get_playlist_songs(self, playlist_id: str) -> List[str]:
        """Get all song URLs from playlist."""
        playlist_url = f"{self.SUNO_BASE}/playlist/{playlist_id}"
        logger.info(f"[PLAYLIST] Loading: {playlist_url}")

        await self.page.goto(playlist_url)
        await self.page.wait_for_load_state("networkidle")
        await asyncio.sleep(3)

        # Scroll to load all songs
        song_urls = set()
        last_count = 0
        scroll_attempts = 0

        while scroll_attempts < 20:  # Max 20 scroll attempts
            # Get current song links
            links = await self.page.query_selector_all('a[href*="/song/"]')
            for link in links:
                href = await link.get_attribute('href')
                if href and '/song/' in href:
                    # Clean URL
                    song_id = href.split('/song/')[-1].split('?')[0]
                    song_urls.add(f"{self.SUNO_BASE}/song/{song_id}")

            current_count = len(song_urls)
            logger.info(f"[PLAYLIST] Found {current_count} songs...")

            if current_count == last_count:
                scroll_attempts += 1
            else:
                scroll_attempts = 0
                last_count = current_count

            # Scroll down
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(1)

        logger.info(f"[PLAYLIST] Total: {len(song_urls)} unique songs")
        return list(song_urls)

    async def extract_song_data(self, url: str) -> Optional[SongData]:
        """Extract song data from song page."""
        logger.info(f"[EXTRACT] {url}")

        song_id = url.split('/song/')[-1].split('?')[0]

        # Method 0: Try Suno's public API first (faster, more reliable)
        try:
            import urllib.request
            api_url = f"https://studio-api.suno.ai/api/external/clips/?ids={song_id}"
            req = urllib.request.Request(api_url, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'application/json',
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            if data and len(data) > 0:
                clip = data[0]
                metadata = clip.get('metadata', {})
                lyrics = metadata.get('prompt', '') or clip.get('metadata', {}).get('concat_history', [{}])[0].get('prompt', '')

                if lyrics and len(lyrics) > 30:
                    logger.info(f"[EXTRACT] Found lyrics via API ({len(lyrics)} chars)")
                    return SongData(
                        id=song_id,
                        title=clip.get('title', '') or metadata.get('title', ''),
                        artist=clip.get('display_name', 'UnDaoDu'),
                        lyrics=lyrics,
                        style=metadata.get('tags', ''),
                        duration_sec=int(clip.get('metadata', {}).get('duration', 180)),
                        url=url
                    )
        except Exception as e:
            logger.debug(f"[EXTRACT] API extraction failed: {e}")

        # Fall back to browser scraping if API fails
        try:
            await self.page.goto(url)
            await self.page.wait_for_load_state("networkidle")
            await asyncio.sleep(3)  # Extra wait for JS to render

            # Extract title
            title = ""
            title_selectors = ['h1', '[class*="title"]', '[class*="Title"]', '[data-testid="song-title"]']
            for sel in title_selectors:
                try:
                    elem = await self.page.query_selector(sel)
                    if elem:
                        title = await elem.inner_text()
                        title = title.strip()
                        if title:
                            break
                except:
                    continue

            # Extract artist
            artist = "UnDaoDu"  # Default for 012's songs
            artist_selectors = ['[class*="creator"]', '[class*="author"]', '[class*="artist"]', '[class*="username"]']
            for sel in artist_selectors:
                try:
                    elem = await self.page.query_selector(sel)
                    if elem:
                        artist = await elem.inner_text()
                        artist = artist.strip()
                        if artist:
                            break
                except:
                    continue

            # Extract lyrics - try multiple methods
            lyrics = ""

            # Method 0: Extract from __NEXT_DATA__ JSON (Next.js SSR data)
            try:
                next_data = await self.page.evaluate('''() => {
                    const script = document.getElementById('__NEXT_DATA__');
                    if (script) {
                        const data = JSON.parse(script.textContent);
                        // Navigate to song data - Suno uses different paths
                        const props = data?.props?.pageProps;
                        if (props?.clip?.metadata?.prompt) return props.clip.metadata.prompt;
                        if (props?.song?.metadata?.prompt) return props.song.metadata.prompt;
                        if (props?.clip?.lyrics) return props.clip.lyrics;
                        if (props?.song?.lyrics) return props.song.lyrics;
                        // Try to find any lyrics field
                        const str = JSON.stringify(props);
                        const match = str.match(/"(?:lyrics|prompt)":"([^"]+)"/);
                        if (match) return match[1].replace(/\\\\n/g, '\\n');
                    }
                    return null;
                }''')
                if next_data and len(next_data) > 30:
                    lyrics = next_data.replace('\\n', '\n').replace('\\r', '')
                    logger.info(f"[EXTRACT] Found lyrics in __NEXT_DATA__ ({len(lyrics)} chars)")
            except Exception as e:
                logger.debug(f"[EXTRACT] __NEXT_DATA__ extraction failed: {e}")

            # Method 1: Direct selectors (if Method 0 didn't work)
            if not lyrics:
                lyrics_selectors = [
                    '[data-testid="lyrics"]',
                    '.lyrics-container',
                    '.song-lyrics',
                    '[class*="lyrics"]',
                    '[class*="Lyrics"]',
                    '[class*="prompt"]',
                    '[class*="Prompt"]',
                    'pre',
                ]

                for sel in lyrics_selectors:
                    try:
                        elem = await self.page.query_selector(sel)
                        if elem:
                            text = await elem.inner_text()
                            if text and len(text) > 50:
                                lyrics = text.strip()
                                break
                    except:
                        continue

            # Method 2: Find lyrics in page content via regex
            if not lyrics:
                try:
                    content = await self.page.content()

                    # Look for lyrics in JSON data embedded in page
                    patterns = [
                        r'"prompt"\s*:\s*"([^"]{50,})"',  # Suno uses "prompt" for lyrics
                        r'"lyrics"\s*:\s*"([^"]{50,})"',
                        r'"text"\s*:\s*"([^"]{50,})"',
                    ]

                    for pattern in patterns:
                        match = re.search(pattern, content)
                        if match:
                            lyrics = match.group(1)
                            lyrics = lyrics.replace('\\n', '\n').replace('\\r', '').replace('\\"', '"')
                            if len(lyrics) > 50:
                                logger.info(f"[EXTRACT] Found lyrics via regex ({len(lyrics)} chars)")
                                break
                except:
                    pass

            # Method 3: Try clicking "Show lyrics" or expand button
            if not lyrics:
                try:
                    expand_btns = await self.page.query_selector_all('button, [role="button"]')
                    for btn in expand_btns[:10]:
                        btn_text = await btn.inner_text()
                        if 'lyric' in btn_text.lower() or 'show' in btn_text.lower() or 'expand' in btn_text.lower():
                            await btn.click()
                            await asyncio.sleep(1)
                            break
                    # Try selectors again after clicking
                    for sel in ['[class*="lyrics"]', '[class*="Lyrics"]', '[class*="prompt"]', 'pre']:
                            elem = await self.page.query_selector(sel)
                            if elem:
                                text = await elem.inner_text()
                                if text and len(text) > 50:
                                    lyrics = text.strip()
                                    break
                except:
                    pass

            # Extract style/genre
            style = ""
            try:
                style_elem = await self.page.query_selector('[class*="style"], [class*="genre"], [class*="tag"]')
                if style_elem:
                    style = await style_elem.inner_text()
                    style = style.strip()
            except:
                pass

            # Get duration if possible
            duration_sec = 180  # Default 3 min
            try:
                dur_elem = await self.page.query_selector('[class*="duration"], [class*="time"]')
                if dur_elem:
                    dur_text = await dur_elem.inner_text()
                    # Parse "3:45" format
                    if ':' in dur_text:
                        parts = dur_text.split(':')
                        duration_sec = int(parts[0]) * 60 + int(parts[1])
            except:
                pass

            if not title:
                logger.warning(f"[EXTRACT] No title found: {url}")
                return None

            return SongData(
                id=song_id,
                title=title,
                artist=artist,
                lyrics=lyrics,
                style=style,
                duration_sec=duration_sec,
                url=url
            )

        except Exception as e:
            logger.error(f"[EXTRACT] Error: {e}")
            return None

    def create_lrc(self, song: SongData) -> str:
        """Generate LRC file content from song data."""
        lines = []

        # Metadata
        lines.append(f"[ar:{song.artist}]")
        lines.append(f"[ti:{song.title}]")
        lines.append(f"[by:Suno Downloader / antifaFM]")
        lines.append(f"[length:{song.duration_sec // 60}:{song.duration_sec % 60:02d}]")
        lines.append("")

        if not song.lyrics:
            lines.append("[00:00.00] (No lyrics available)")
            return '\n'.join(lines)

        # Parse and time lyrics
        lyrics_lines = song.lyrics.split('\n')
        total_lines = len([l for l in lyrics_lines if l.strip()])
        time_per_line = (song.duration_sec * 1000) / max(total_lines, 1)

        current_ms = 0
        for line in lyrics_lines:
            line = line.strip()
            if not line:
                current_ms += 500  # Half second for empty lines
                continue

            # Format timestamp
            mins = int(current_ms // 60000)
            secs = int((current_ms % 60000) // 1000)
            centis = int((current_ms % 1000) // 10)

            lines.append(f"[{mins:02d}:{secs:02d}.{centis:02d}] {line}")

            # Estimate duration for this line
            if line.startswith('[') and line.endswith(']'):
                current_ms += 1000  # Section marker
            else:
                word_count = len(line.split())
                current_ms += max(2000, int(word_count / 2.5 * 1000))

        return '\n'.join(lines)

    def save_lrc(self, song: SongData, output_dir: Path) -> Optional[Path]:
        """Save LRC file."""
        if not song.lyrics:
            logger.warning(f"[SAVE] No lyrics for: {song.title}")
            return None

        lrc_content = self.create_lrc(song)

        output_dir.mkdir(parents=True, exist_ok=True)

        # Safe filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in f"{song.artist}_{song.title}")
        lrc_path = output_dir / f"{safe_name[:80]}.lrc"

        with open(lrc_path, 'w', encoding='utf-8') as f:
            f.write(lrc_content)

        logger.info(f"[SAVE] Created: {lrc_path.name}")
        return lrc_path

    def load_progress(self):
        """Load download progress."""
        if PROGRESS_FILE.exists():
            with open(PROGRESS_FILE, 'r') as f:
                self.progress = json.load(f)

    def save_progress(self):
        """Save download progress."""
        PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress, f, indent=2)

    async def download_playlist(self, playlist_id: str, output_dir: Path,
                                 start_index: int = 0, max_songs: int = 0) -> dict:
        """Download LRC files for entire playlist."""

        self.load_progress()

        # Get song list
        song_urls = await self.get_playlist_songs(playlist_id)

        if max_songs > 0:
            song_urls = song_urls[:max_songs]

        stats = {"total": len(song_urls), "downloaded": 0, "no_lyrics": 0, "errors": 0, "skipped": 0}

        for i, url in enumerate(song_urls[start_index:], start=start_index):
            # Skip already completed
            if url in self.progress["completed"]:
                stats["skipped"] += 1
                continue

            logger.info(f"[{i+1}/{len(song_urls)}] Processing...")

            try:
                song = await self.extract_song_data(url)

                if song:
                    if song.lyrics:
                        lrc_path = self.save_lrc(song, output_dir)
                        if lrc_path:
                            stats["downloaded"] += 1
                            self.progress["completed"].append(url)
                        else:
                            stats["no_lyrics"] += 1
                    else:
                        stats["no_lyrics"] += 1
                        logger.warning(f"[SKIP] No lyrics: {song.title}")
                else:
                    stats["errors"] += 1
                    self.progress["failed"].append(url)

            except Exception as e:
                logger.error(f"[ERROR] {url}: {e}")
                stats["errors"] += 1
                self.progress["failed"].append(url)

            # Save progress periodically
            if (i + 1) % 5 == 0:
                self.save_progress()

            # Rate limit
            await asyncio.sleep(2)

        self.save_progress()
        return stats


async def main_async(args):
    """Async main function."""
    downloader = SunoLRCDownloader(headless=args.headless)

    try:
        await downloader.setup(login=args.login)

        stats = await downloader.download_playlist(
            playlist_id=args.playlist,
            output_dir=Path(args.output),
            start_index=args.start,
            max_songs=args.max
        )

        print("\n" + "=" * 60)
        print("[DOWNLOAD COMPLETE]")
        print("=" * 60)
        print(f"  Total songs:    {stats['total']}")
        print(f"  Downloaded:     {stats['downloaded']}")
        print(f"  No lyrics:      {stats['no_lyrics']}")
        print(f"  Errors:         {stats['errors']}")
        print(f"  Skipped:        {stats['skipped']}")
        print(f"\n  Output dir: {args.output}")
        print(f"\n[NEXT] Import to library:")
        print(f"  python ffcpln_lyrics_library.py bulk-import --folder {args.output}")

    finally:
        await downloader.close()


def main():
    parser = argparse.ArgumentParser(
        description="Download LRC files from Suno playlist",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download 012's playlist:
  python suno_lrc_downloader.py --playlist "3adb1878-12f8-4c1c-a815-bde3d7d320ed"

  # With login (for private playlists):
  python suno_lrc_downloader.py --playlist "..." --login

  # First 10 songs only:
  python suno_lrc_downloader.py --playlist "..." --max 10

  # Headless mode:
  python suno_lrc_downloader.py --playlist "..." --headless
        """
    )

    parser.add_argument("--playlist", "-p", required=True, help="Suno playlist ID")
    parser.add_argument("--output", "-o", type=str, default=str(LRC_OUTPUT_DIR), help="Output directory")
    parser.add_argument("--login", "-l", action="store_true", help="Interactive login first")
    parser.add_argument("--start", "-s", type=int, default=0, help="Start from song index")
    parser.add_argument("--max", "-m", type=int, default=0, help="Max songs to download")
    parser.add_argument("--headless", action="store_true", help="Run headless (no browser window)")

    args = parser.parse_args()

    print("=" * 60)
    print("[SUNO LRC DOWNLOADER] Playwright Automation")
    print("=" * 60)

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
