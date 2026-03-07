#!/usr/bin/env python3
"""
Suno Playlist Scraper - Automated Lyrics Extraction

Scrapes 012's Suno playlist, extracts lyrics, auto-deduplicates,
and populates the FFCPLN lyrics library.

Usage:
    # Scrape entire playlist:
    python suno_playlist_scraper.py --playlist "3adb1878-12f8-4c1c-a815-bde3d7d320ed"

    # Scrape with session cookie (for private playlists):
    python suno_playlist_scraper.py --playlist "..." --cookie "session=..."

    # Dry run (don't save to library):
    python suno_playlist_scraper.py --playlist "..." --dry-run

    # Resume from specific song index:
    python suno_playlist_scraper.py --playlist "..." --start 50
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urljoin

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

# Data paths
DATA_DIR = Path(__file__).parent.parent / "data"
SCRAPE_CACHE = DATA_DIR / "suno_scrape_cache.json"


@dataclass
class SunoSong:
    """Scraped song data from Suno."""
    id: str
    title: str
    artist: str
    lyrics: str
    style: str  # Genre/style tags
    duration: str
    url: str
    lyrics_hash: str = ""  # For deduplication

    def __post_init__(self):
        if not self.lyrics_hash and self.lyrics:
            # Hash normalized lyrics for deduplication
            normalized = self._normalize_lyrics(self.lyrics)
            self.lyrics_hash = hashlib.sha256(normalized.encode()).hexdigest()[:16]

    @staticmethod
    def _normalize_lyrics(text: str) -> str:
        """Normalize lyrics for comparison (ignore whitespace, case, punctuation)."""
        # Remove section markers
        text = re.sub(r'\[.*?\]', '', text)
        # Remove stage directions
        text = re.sub(r'\(.*?\)', '', text)
        # Lowercase, remove extra whitespace
        text = ' '.join(text.lower().split())
        # Remove punctuation
        text = re.sub(r'[^\w\s]', '', text)
        return text


@dataclass
class ScrapeSession:
    """Tracks scraping progress for resume capability."""
    playlist_id: str
    total_songs: int = 0
    scraped_songs: int = 0
    unique_lyrics: int = 0
    songs: List[Dict] = field(default_factory=list)
    lyrics_hashes: Dict[str, str] = field(default_factory=dict)  # hash -> canonical_name
    started_at: str = ""
    last_updated: str = ""

    def save(self, path: Path = SCRAPE_CACHE):
        """Save session to JSON for resume."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path = SCRAPE_CACHE) -> Optional['ScrapeSession']:
        """Load session from JSON."""
        if not path.exists():
            return None
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        except Exception as e:
            logger.warning(f"Failed to load session: {e}")
            return None


class SunoPlaylistScraper:
    """Scrapes Suno playlists for lyrics extraction."""

    SUNO_BASE = "https://suno.com"

    def __init__(self, session_cookie: str = ""):
        self.session_cookie = session_cookie
        self.session: Optional[ScrapeSession] = None
        self._driver = None

    def _get_driver(self):
        """Get or create Selenium driver."""
        if self._driver:
            return self._driver

        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
        except ImportError:
            logger.error("Selenium required. Install: pip install selenium")
            raise

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        # Try to use existing browser manager
        try:
            from modules.infrastructure.foundups_selenium.src.browser_manager import get_browser_manager
            manager = get_browser_manager()
            self._driver = manager.get_driver()
            logger.info("[SCRAPER] Using existing browser manager")
        except:
            self._driver = webdriver.Chrome(options=options)
            logger.info("[SCRAPER] Created new Chrome driver")

        # Set session cookie if provided
        if self.session_cookie:
            self._driver.get(self.SUNO_BASE)
            for cookie in self._parse_cookies(self.session_cookie):
                self._driver.add_cookie(cookie)

        return self._driver

    def _parse_cookies(self, cookie_str: str) -> List[Dict]:
        """Parse cookie string into Selenium cookie format."""
        cookies = []
        for part in cookie_str.split(';'):
            if '=' in part:
                name, value = part.strip().split('=', 1)
                cookies.append({
                    'name': name,
                    'value': value,
                    'domain': '.suno.com'
                })
        return cookies

    def scrape_playlist(self, playlist_id: str, start_index: int = 0,
                        max_songs: int = 0, dry_run: bool = False) -> ScrapeSession:
        """
        Scrape entire playlist for lyrics.

        Args:
            playlist_id: Suno playlist ID
            start_index: Resume from this song index
            max_songs: Max songs to scrape (0 = all)
            dry_run: Don't save to library

        Returns:
            ScrapeSession with results
        """
        driver = self._get_driver()

        # Load existing session or create new
        self.session = ScrapeSession.load()
        if self.session and self.session.playlist_id == playlist_id:
            logger.info(f"[SCRAPER] Resuming session: {self.session.scraped_songs}/{self.session.total_songs}")
        else:
            self.session = ScrapeSession(
                playlist_id=playlist_id,
                started_at=datetime.now().isoformat()
            )

        playlist_url = f"{self.SUNO_BASE}/playlist/{playlist_id}"
        logger.info(f"[SCRAPER] Loading playlist: {playlist_url}")

        driver.get(playlist_url)
        time.sleep(5)  # Wait for JS render

        # Get all song links from playlist
        song_links = self._extract_song_links(driver)
        self.session.total_songs = len(song_links)
        logger.info(f"[SCRAPER] Found {len(song_links)} songs in playlist")

        if max_songs > 0:
            song_links = song_links[:max_songs]

        # Scrape each song
        for i, link in enumerate(song_links[start_index:], start=start_index):
            try:
                logger.info(f"[SCRAPER] Scraping {i+1}/{len(song_links)}: {link}")
                song = self._scrape_song(driver, link)

                if song and song.lyrics:
                    self._process_song(song, dry_run)
                    self.session.scraped_songs += 1
                else:
                    logger.warning(f"[SCRAPER] No lyrics found: {link}")

                # Save progress periodically
                if (i + 1) % 10 == 0:
                    self.session.last_updated = datetime.now().isoformat()
                    self.session.save()

                # Rate limit
                time.sleep(2)

            except Exception as e:
                logger.error(f"[SCRAPER] Error scraping {link}: {e}")
                continue

        self.session.last_updated = datetime.now().isoformat()
        self.session.save()

        return self.session

    def _extract_song_links(self, driver) -> List[str]:
        """Extract all song links from playlist page."""
        from selenium.webdriver.common.by import By

        links = []

        # Scroll to load all songs (lazy loading)
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Find song links
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/song/"]')
            for elem in elements:
                href = elem.get_attribute('href')
                if href and '/song/' in href:
                    links.append(href)
        except:
            pass

        # Deduplicate while preserving order
        seen = set()
        unique = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique.append(link)

        return unique

    def _scrape_song(self, driver, url: str) -> Optional[SunoSong]:
        """Scrape a single song page for lyrics and metadata."""
        from selenium.webdriver.common.by import By

        driver.get(url)
        time.sleep(3)  # Wait for JS render

        song_id = url.split('/song/')[-1].split('?')[0]

        # Extract metadata from page
        title = ""
        artist = ""
        lyrics = ""
        style = ""
        duration = ""

        # Try to get title
        try:
            title_elem = driver.find_element(By.CSS_SELECTOR, 'h1, [class*="title"], [class*="Title"]')
            title = title_elem.text.strip()
        except:
            pass

        # Try to get artist
        try:
            artist_elem = driver.find_element(By.CSS_SELECTOR, '[class*="creator"], [class*="author"], [class*="artist"]')
            artist = artist_elem.text.strip()
        except:
            artist = "UnDaoDu"  # Default for 012's songs

        # Try to get lyrics - multiple selectors
        lyrics_selectors = [
            '[data-testid="lyrics"]',
            '.lyrics-container',
            '.song-lyrics',
            '[class*="lyrics"]',
            '[class*="Lyrics"]',
            'pre',  # Sometimes lyrics in pre tag
        ]

        for selector in lyrics_selectors:
            try:
                elem = driver.find_element(By.CSS_SELECTOR, selector)
                text = elem.text.strip()
                if text and len(text) > 50:  # Likely actual lyrics
                    lyrics = text
                    break
            except:
                continue

        # If no lyrics found, try page source parsing
        if not lyrics:
            page_source = driver.page_source

            # Look for lyrics in JSON data
            lyrics_patterns = [
                r'"lyrics"\s*:\s*"([^"]+)"',
                r'"text"\s*:\s*"([^"]+)"',
                r'lyrics["\s:]+([^"]+)"',
            ]

            for pattern in lyrics_patterns:
                match = re.search(pattern, page_source, re.IGNORECASE)
                if match:
                    lyrics = match.group(1).replace('\\n', '\n').replace('\\r', '')
                    if len(lyrics) > 50:
                        break

        # Try to get style/genre
        try:
            style_elem = driver.find_element(By.CSS_SELECTOR, '[class*="style"], [class*="genre"], [class*="tag"]')
            style = style_elem.text.strip()
        except:
            pass

        if not title:
            logger.warning(f"[SCRAPER] Could not extract title from: {url}")
            return None

        return SunoSong(
            id=song_id,
            title=title,
            artist=artist,
            lyrics=lyrics,
            style=style,
            duration=duration,
            url=url
        )

    def _process_song(self, song: SunoSong, dry_run: bool = False):
        """Process scraped song - deduplicate and add to library."""

        # Check if we've seen these lyrics before
        if song.lyrics_hash in self.session.lyrics_hashes:
            canonical_name = self.session.lyrics_hashes[song.lyrics_hash]
            logger.info(f"[SCRAPER] Duplicate lyrics detected: {song.title} -> {canonical_name}")

            if not dry_run:
                self._map_song_to_lyrics(song, canonical_name)
        else:
            # New unique lyrics
            canonical_name = self._generate_canonical_name(song.title)
            self.session.lyrics_hashes[song.lyrics_hash] = canonical_name
            self.session.unique_lyrics += 1

            logger.info(f"[SCRAPER] New lyrics: {canonical_name} ({len(song.lyrics)} chars)")

            if not dry_run:
                self._add_lyrics_to_library(song, canonical_name)

        # Store song data
        self.session.songs.append(asdict(song))

    def _generate_canonical_name(self, title: str) -> str:
        """Generate canonical name from song title."""
        # Remove version info
        name = re.sub(r'\s*\([^)]*\)\s*', '', title)
        # Remove artist suffix
        name = re.sub(r'\s*-\s*(UnDaoDu|KINDNESS MATTERS|JS-UnDuDu).*$', '', name, flags=re.I)
        # Clean up
        name = name.strip()
        return name if name else title

    def _add_lyrics_to_library(self, song: SunoSong, canonical_name: str):
        """Add new lyrics to FFCPLN library."""
        try:
            from modules.platform_integration.antifafm_broadcaster.scripts.ffcpln_lyrics_library import (
                FFCPLNLyricsLibrary
            )

            library = FFCPLNLyricsLibrary()

            # Clean lyrics (remove intro text before first section)
            clean_lyrics = self._clean_lyrics(song.lyrics)

            if library.add_lyrics(canonical_name, song.artist, clean_lyrics):
                # Also map this song
                library.map_song(song.title, canonical_name, artist=song.artist, style=song.style)
                logger.info(f"[LIBRARY] Added: {canonical_name}")

        except ImportError:
            logger.error("[LIBRARY] Could not import FFCPLNLyricsLibrary")
        except Exception as e:
            logger.error(f"[LIBRARY] Error adding lyrics: {e}")

    def _map_song_to_lyrics(self, song: SunoSong, canonical_name: str):
        """Map song variation to existing lyrics."""
        try:
            from modules.platform_integration.antifafm_broadcaster.scripts.ffcpln_lyrics_library import (
                FFCPLNLyricsLibrary
            )

            library = FFCPLNLyricsLibrary()

            # Extract style from title
            style = song.style
            if not style:
                style_match = re.search(r'\(([^)]+)\)', song.title)
                if style_match:
                    style = style_match.group(1)

            library.map_song(song.title, canonical_name, artist=song.artist, style=style)
            logger.info(f"[LIBRARY] Mapped: {song.title} -> {canonical_name}")

        except ImportError:
            logger.error("[LIBRARY] Could not import FFCPLNLyricsLibrary")
        except Exception as e:
            logger.error(f"[LIBRARY] Error mapping song: {e}")

    def _clean_lyrics(self, lyrics: str) -> str:
        """Clean lyrics - remove intro text, keep section markers."""
        # Find first section marker
        section_match = re.search(r'\[(?:Intro|Verse|Chorus|Hook|Pre-Chorus|Bridge|Outro)\]', lyrics, re.I)

        if section_match:
            return lyrics[section_match.start():].strip()

        return lyrics.strip()

    def close(self):
        """Clean up driver."""
        if self._driver:
            try:
                self._driver.quit()
            except:
                pass
            self._driver = None


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Suno playlist for FFCPLN lyrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 012's MAGA-FFCPLN playlist:
  python suno_playlist_scraper.py --playlist "3adb1878-12f8-4c1c-a815-bde3d7d320ed"

  # Dry run (preview without saving):
  python suno_playlist_scraper.py --playlist "..." --dry-run

  # Resume from song 50:
  python suno_playlist_scraper.py --playlist "..." --start 50

  # Scrape first 10 songs only:
  python suno_playlist_scraper.py --playlist "..." --max 10
        """
    )

    parser.add_argument("--playlist", "-p", required=True, help="Suno playlist ID")
    parser.add_argument("--cookie", "-c", default="", help="Session cookie for auth")
    parser.add_argument("--start", "-s", type=int, default=0, help="Start from song index")
    parser.add_argument("--max", "-m", type=int, default=0, help="Max songs to scrape")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Preview without saving")

    args = parser.parse_args()

    print("=" * 60)
    print("[SUNO SCRAPER] FFCPLN Lyrics Extraction")
    print("=" * 60)

    scraper = SunoPlaylistScraper(session_cookie=args.cookie)

    try:
        session = scraper.scrape_playlist(
            playlist_id=args.playlist,
            start_index=args.start,
            max_songs=args.max,
            dry_run=args.dry_run
        )

        print("\n" + "=" * 60)
        print("[RESULTS]")
        print(f"  Total songs:    {session.total_songs}")
        print(f"  Scraped:        {session.scraped_songs}")
        print(f"  Unique lyrics:  {session.unique_lyrics}")
        print(f"  Deduplication:  {session.scraped_songs}:{session.unique_lyrics}")

        if args.dry_run:
            print("\n[DRY RUN] No changes saved to library")
        else:
            print(f"\n[SAVED] Session cached to: {SCRAPE_CACHE}")
            print("[NEXT] Export LRC files:")
            print("       python ffcpln_lyrics_library.py export --all")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()
