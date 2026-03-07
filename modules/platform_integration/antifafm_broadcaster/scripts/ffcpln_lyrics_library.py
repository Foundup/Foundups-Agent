#!/usr/bin/env python3
"""
FFCPLN Lyrics Library CLI

Manages 012's original song lyrics with deduplication.
Many songs share the same lyrics in different styles/languages.

Usage:
    # Add lyrics from clipboard/file:
    python ffcpln_lyrics_library.py add --name "FFCPLN" --file lyrics.txt
    python ffcpln_lyrics_library.py add --name "FFCPLN" --paste  # Interactive paste

    # Map song variations to lyrics:
    python ffcpln_lyrics_library.py map --lyrics "FFCPLN" --song "Fake Fuck Christian Pedo-lovin Nazi v2"
    python ffcpln_lyrics_library.py map --lyrics "FFCPLN" --pattern "Fake*Christian*Nazi*"

    # List library:
    python ffcpln_lyrics_library.py list
    python ffcpln_lyrics_library.py list --lyrics "FFCPLN"  # Show mapped songs

    # Export to LRC:
    python ffcpln_lyrics_library.py export --all --output "data/lrc_files"
    python ffcpln_lyrics_library.py export --lyrics "FFCPLN" --output "data/lrc_files"

    # Import to cache:
    python ffcpln_lyrics_library.py import-cache

    # Bulk add from Suno playlist (paste song list):
    python ffcpln_lyrics_library.py bulk-map --lyrics "FFCPLN" --paste
"""

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime

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

# Database location
DATA_DIR = Path(__file__).parent.parent / "data"
LIBRARY_DB = DATA_DIR / "ffcpln_lyrics_library.db"
DEFAULT_OUTPUT_DIR = DATA_DIR / "lrc_files"


@dataclass
class LyricsEntry:
    """A unique lyrics text with metadata."""
    name: str  # Canonical name (e.g., "FFCPLN", "American Scream")
    artist: str  # Primary artist
    lyrics_text: str  # Full lyrics with sections
    created_at: str
    word_count: int
    has_sections: bool  # Has [Verse], [Chorus], etc.


@dataclass
class SongMapping:
    """Maps a song title/variation to a lyrics entry."""
    song_title: str  # Full song title from Suno
    lyrics_name: str  # Links to LyricsEntry.name
    artist: str
    style: str  # e.g., "v5", "v4.5-all", "drill", "reggaeton"
    language: str  # e.g., "en", "es", "ru"


class FFCPLNLyricsLibrary:
    """Manages the FFCPLN lyrics library with SQLite storage."""

    def __init__(self, db_path: Path = LIBRARY_DB):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lyrics (
                    name TEXT PRIMARY KEY,
                    artist TEXT NOT NULL,
                    lyrics_text TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    word_count INTEGER,
                    has_sections INTEGER
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS song_mappings (
                    song_title TEXT PRIMARY KEY,
                    lyrics_name TEXT NOT NULL,
                    artist TEXT,
                    style TEXT,
                    language TEXT DEFAULT 'en',
                    FOREIGN KEY (lyrics_name) REFERENCES lyrics(name)
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_mappings_lyrics
                ON song_mappings(lyrics_name)
            """)
            conn.commit()

    def add_lyrics(self, name: str, artist: str, lyrics_text: str) -> bool:
        """Add a new lyrics entry to the library."""
        # Parse lyrics
        word_count = len(lyrics_text.split())
        has_sections = bool(re.search(r'\[(Verse|Chorus|Intro|Outro|Bridge|Hook)', lyrics_text, re.I))

        entry = LyricsEntry(
            name=name,
            artist=artist,
            lyrics_text=lyrics_text,
            created_at=datetime.now().isoformat(),
            word_count=word_count,
            has_sections=has_sections
        )

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT OR REPLACE INTO lyrics
                    (name, artist, lyrics_text, created_at, word_count, has_sections)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (entry.name, entry.artist, entry.lyrics_text,
                      entry.created_at, entry.word_count, int(entry.has_sections)))
                conn.commit()
            logger.info(f"[LIBRARY] Added lyrics: {name} ({word_count} words, sections={has_sections})")
            return True
        except Exception as e:
            logger.error(f"[LIBRARY] Failed to add lyrics: {e}")
            return False

    def map_song(self, song_title: str, lyrics_name: str, artist: str = "",
                 style: str = "", language: str = "en") -> bool:
        """Map a song title to a lyrics entry."""
        # Verify lyrics exists
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT name FROM lyrics WHERE name = ?", (lyrics_name,))
            if not cursor.fetchone():
                logger.error(f"[LIBRARY] Lyrics not found: {lyrics_name}")
                return False

            # Get artist from lyrics if not provided
            if not artist:
                cursor = conn.execute("SELECT artist FROM lyrics WHERE name = ?", (lyrics_name,))
                row = cursor.fetchone()
                artist = row[0] if row else "UnDaoDu"

            conn.execute("""
                INSERT OR REPLACE INTO song_mappings
                (song_title, lyrics_name, artist, style, language)
                VALUES (?, ?, ?, ?, ?)
            """, (song_title, lyrics_name, artist, style, language))
            conn.commit()

        logger.info(f"[LIBRARY] Mapped: '{song_title}' -> {lyrics_name}")
        return True

    def map_pattern(self, pattern: str, lyrics_name: str, songs: List[str]) -> int:
        """Map multiple songs matching a pattern to lyrics."""
        import fnmatch
        mapped = 0
        for song in songs:
            if fnmatch.fnmatch(song.lower(), pattern.lower()):
                # Extract style from title (e.g., "v5", "v4.5-all")
                style_match = re.search(r'\((v[\d.]+[^)]*)\)', song)
                style = style_match.group(1) if style_match else ""

                if self.map_song(song, lyrics_name, style=style):
                    mapped += 1
        return mapped

    def get_lyrics(self, name: str) -> Optional[LyricsEntry]:
        """Get lyrics entry by name."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT name, artist, lyrics_text, created_at, word_count, has_sections "
                "FROM lyrics WHERE name = ?", (name,))
            row = cursor.fetchone()
            if row:
                return LyricsEntry(
                    name=row[0], artist=row[1], lyrics_text=row[2],
                    created_at=row[3], word_count=row[4], has_sections=bool(row[5])
                )
        return None

    def get_lyrics_for_song(self, song_title: str) -> Optional[Tuple[LyricsEntry, SongMapping]]:
        """Get lyrics for a specific song title."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT l.name, l.artist, l.lyrics_text, l.created_at, l.word_count, l.has_sections,
                       m.song_title, m.lyrics_name, m.artist, m.style, m.language
                FROM song_mappings m
                JOIN lyrics l ON m.lyrics_name = l.name
                WHERE m.song_title = ?
            """, (song_title,))
            row = cursor.fetchone()
            if row:
                entry = LyricsEntry(
                    name=row[0], artist=row[1], lyrics_text=row[2],
                    created_at=row[3], word_count=row[4], has_sections=bool(row[5])
                )
                mapping = SongMapping(
                    song_title=row[6], lyrics_name=row[7], artist=row[8],
                    style=row[9], language=row[10]
                )
                return entry, mapping
        return None

    def fuzzy_match_song(self, song_title: str) -> Optional[Tuple[LyricsEntry, SongMapping]]:
        """Fuzzy match a song title to find lyrics."""
        # Try exact match first
        result = self.get_lyrics_for_song(song_title)
        if result:
            return result

        # Try normalized match (lowercase, remove version info)
        normalized = re.sub(r'\s*\([^)]*\)\s*', '', song_title.lower()).strip()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT song_title FROM song_mappings")
            for row in cursor:
                db_title = row[0]
                db_normalized = re.sub(r'\s*\([^)]*\)\s*', '', db_title.lower()).strip()
                if normalized == db_normalized or normalized in db_normalized or db_normalized in normalized:
                    return self.get_lyrics_for_song(db_title)

        return None

    def list_lyrics(self) -> List[Dict]:
        """List all lyrics entries with mapped song counts."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT l.name, l.artist, l.word_count, l.has_sections,
                       COUNT(m.song_title) as song_count
                FROM lyrics l
                LEFT JOIN song_mappings m ON l.name = m.lyrics_name
                GROUP BY l.name
                ORDER BY song_count DESC
            """)
            return [
                {
                    "name": row[0],
                    "artist": row[1],
                    "word_count": row[2],
                    "has_sections": bool(row[3]),
                    "song_count": row[4]
                }
                for row in cursor
            ]

    def list_songs_for_lyrics(self, lyrics_name: str) -> List[SongMapping]:
        """List all songs mapped to a lyrics entry."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT song_title, lyrics_name, artist, style, language
                FROM song_mappings
                WHERE lyrics_name = ?
                ORDER BY song_title
            """, (lyrics_name,))
            return [
                SongMapping(
                    song_title=row[0], lyrics_name=row[1], artist=row[2],
                    style=row[3], language=row[4]
                )
                for row in cursor
            ]

    def export_to_lrc(self, lyrics_name: str, output_dir: Path,
                      artist_override: str = "", title_override: str = "") -> List[Path]:
        """Export lyrics to LRC files for all mapped songs."""
        entry = self.get_lyrics(lyrics_name)
        if not entry:
            logger.error(f"[EXPORT] Lyrics not found: {lyrics_name}")
            return []

        output_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        # Parse lyrics into timed lines
        timed_lyrics = self._estimate_timing(entry.lyrics_text)

        # Get all mapped songs
        songs = self.list_songs_for_lyrics(lyrics_name)

        if not songs:
            # No mappings - export with canonical name
            lrc_path = self._write_lrc_file(
                output_dir,
                artist_override or entry.artist,
                title_override or entry.name,
                timed_lyrics,
                entry.name
            )
            if lrc_path:
                generated.append(lrc_path)
        else:
            # Export for each mapped song
            for mapping in songs:
                lrc_path = self._write_lrc_file(
                    output_dir,
                    mapping.artist or entry.artist,
                    mapping.song_title,
                    timed_lyrics,
                    lyrics_name
                )
                if lrc_path:
                    generated.append(lrc_path)

        return generated

    def _estimate_timing(self, lyrics_text: str) -> List[Tuple[int, str]]:
        """
        Estimate timing for lyrics lines.

        Heuristics:
        - Average line: 3 seconds
        - Section markers ([Chorus], etc.): 1 second pause
        - Empty lines: 0.5 second pause
        """
        lines = lyrics_text.split('\n')
        timed = []
        current_ms = 0

        for line in lines:
            line = line.strip()
            if not line:
                current_ms += 500  # Half second for empty lines
                continue

            # Section markers
            if re.match(r'\[.*\]', line):
                timed.append((current_ms, line))
                current_ms += 1000  # 1 second for section markers
                continue

            # Regular lyrics line
            timed.append((current_ms, line))

            # Estimate duration based on word count (average ~2.5 words/sec)
            word_count = len(line.split())
            duration_ms = max(2000, int(word_count / 2.5 * 1000))
            current_ms += duration_ms

        return timed

    def _write_lrc_file(self, output_dir: Path, artist: str, title: str,
                        timed_lyrics: List[Tuple[int, str]], source: str) -> Optional[Path]:
        """Write a single LRC file."""
        lines = []

        # Metadata
        lines.append(f"[ar:{artist}]")
        lines.append(f"[ti:{title}]")
        lines.append(f"[by:FFCPLN Lyrics Library - {source}]")
        lines.append("")

        # Timed lyrics
        for timestamp_ms, text in timed_lyrics:
            mins = timestamp_ms // 60000
            secs = (timestamp_ms % 60000) // 1000
            centis = (timestamp_ms % 1000) // 10
            lines.append(f"[{mins:02d}:{secs:02d}.{centis:02d}] {text}")

        # Safe filename
        safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in f"{artist}_{title}")
        lrc_path = output_dir / f"{safe_name[:80]}.lrc"

        try:
            with open(lrc_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(lines))
            logger.info(f"[EXPORT] Created: {lrc_path.name}")
            return lrc_path
        except Exception as e:
            logger.error(f"[EXPORT] Failed to write {lrc_path}: {e}")
            return None

    def import_to_cache(self) -> int:
        """Import all exported LRC files to the main lyrics cache."""
        try:
            from modules.platform_integration.antifafm_broadcaster.scripts.generate_lrc_files import (
                import_lrc_folder_to_cache
            )
            return import_lrc_folder_to_cache(DEFAULT_OUTPUT_DIR)
        except ImportError:
            logger.error("[IMPORT] Could not import generate_lrc_files module")
            return 0

    def stats(self) -> Dict:
        """Get library statistics."""
        with sqlite3.connect(self.db_path) as conn:
            lyrics_count = conn.execute("SELECT COUNT(*) FROM lyrics").fetchone()[0]
            songs_count = conn.execute("SELECT COUNT(*) FROM song_mappings").fetchone()[0]
            total_words = conn.execute("SELECT SUM(word_count) FROM lyrics").fetchone()[0] or 0

        return {
            "unique_lyrics": lyrics_count,
            "mapped_songs": songs_count,
            "total_words": total_words,
            "deduplication_ratio": f"{songs_count}:{lyrics_count}" if lyrics_count > 0 else "0:0"
        }


def parse_suno_description(text: str) -> Tuple[str, str]:
    """
    Parse Suno song description to extract clean lyrics.

    Suno descriptions often have intro text before the actual lyrics.
    Returns (intro_text, clean_lyrics)
    """
    # Look for first section marker
    section_match = re.search(r'\[(?:Intro|Verse|Chorus|Hook|Pre-Chorus)\]', text, re.I)

    if section_match:
        intro = text[:section_match.start()].strip()
        lyrics = text[section_match.start():].strip()
        return intro, lyrics

    return "", text


def interactive_paste() -> str:
    """Read multi-line input until EOF or double newline."""
    print("Paste lyrics (end with Ctrl+D or two empty lines):")
    lines = []
    empty_count = 0

    try:
        while True:
            line = input()
            if not line:
                empty_count += 1
                if empty_count >= 2:
                    break
                lines.append("")
            else:
                empty_count = 0
                lines.append(line)
    except EOFError:
        pass

    return '\n'.join(lines).strip()


def bulk_import_lrc_folder(folder: Path, auto_dedupe: bool = True) -> Dict:
    """
    Bulk import LRC files with automatic deduplication.

    Args:
        folder: Folder containing .lrc files
        auto_dedupe: Auto-detect duplicate lyrics and merge

    Returns:
        Stats dict with import results
    """
    library = FFCPLNLyricsLibrary()

    lrc_files = list(folder.glob("*.lrc"))
    if not lrc_files:
        logger.warning(f"[IMPORT] No .lrc files in: {folder}")
        return {"imported": 0, "duplicates": 0, "errors": 0}

    logger.info(f"[IMPORT] Found {len(lrc_files)} LRC files")

    # Hash -> canonical name for deduplication
    lyrics_hashes: Dict[str, str] = {}

    # Load existing hashes from library
    with sqlite3.connect(library.db_path) as conn:
        cursor = conn.execute("SELECT name, lyrics_text FROM lyrics")
        for name, lyrics_text in cursor:
            lyrics_hash = _hash_lyrics(lyrics_text)
            lyrics_hashes[lyrics_hash] = name

    stats = {"imported": 0, "duplicates": 0, "mapped": 0, "errors": 0}

    for lrc_file in lrc_files:
        try:
            # Parse LRC file
            artist, title, lyrics_text = _parse_lrc_file(lrc_file)

            if not lyrics_text:
                logger.warning(f"[IMPORT] Empty lyrics: {lrc_file.name}")
                stats["errors"] += 1
                continue

            # Check for duplicate
            lyrics_hash = _hash_lyrics(lyrics_text)

            if auto_dedupe and lyrics_hash in lyrics_hashes:
                # Map to existing lyrics
                canonical_name = lyrics_hashes[lyrics_hash]
                library.map_song(title, canonical_name, artist=artist)
                stats["duplicates"] += 1
                stats["mapped"] += 1
                logger.info(f"[IMPORT] Duplicate: {title} -> {canonical_name}")
            else:
                # Add new lyrics
                canonical_name = _generate_canonical_name(title)

                # Ensure unique name
                existing = library.get_lyrics(canonical_name)
                if existing:
                    canonical_name = f"{canonical_name}_{lyrics_hash[:6]}"

                if library.add_lyrics(canonical_name, artist, lyrics_text):
                    lyrics_hashes[lyrics_hash] = canonical_name
                    stats["imported"] += 1
                    logger.info(f"[IMPORT] New: {canonical_name}")
                else:
                    stats["errors"] += 1

        except Exception as e:
            logger.error(f"[IMPORT] Error processing {lrc_file.name}: {e}")
            stats["errors"] += 1

    return stats


def _hash_lyrics(lyrics_text: str) -> str:
    """Hash normalized lyrics for deduplication."""
    import hashlib
    # Normalize: remove sections, whitespace, punctuation, lowercase
    normalized = re.sub(r'\[.*?\]', '', lyrics_text)
    normalized = re.sub(r'\(.*?\)', '', normalized)
    normalized = ' '.join(normalized.lower().split())
    normalized = re.sub(r'[^\w\s]', '', normalized)
    return hashlib.sha256(normalized.encode()).hexdigest()[:16]


def _parse_lrc_file(path: Path) -> Tuple[str, str, str]:
    """Parse LRC file, return (artist, title, lyrics_text)."""
    artist = ""
    title = ""
    lyrics_lines = []

    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("[ar:"):
                artist = line[4:].rstrip("]")
            elif line.startswith("[ti:"):
                title = line[4:].rstrip("]")
            elif line.startswith("[") and not line.startswith("[by:"):
                # Extract lyrics text (remove timestamp)
                match = re.match(r'\[\d{2}:\d{2}\.\d{2}\]\s*(.*)', line)
                if match:
                    lyrics_lines.append(match.group(1))

    # Fallback to filename
    if not title:
        title = path.stem

    return artist, title, '\n'.join(lyrics_lines)


def _generate_canonical_name(title: str) -> str:
    """Generate canonical name from title."""
    name = re.sub(r'\s*\([^)]*\)\s*', '', title)
    name = re.sub(r'\s*-\s*(UnDaoDu|KINDNESS MATTERS|JS-UnDuDu).*$', '', name, flags=re.I)
    return name.strip() or title


def main():
    parser = argparse.ArgumentParser(
        description="FFCPLN Lyrics Library - Manage 012's original song lyrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Add lyrics interactively:
  python ffcpln_lyrics_library.py add --name "FFCPLN" --artist "UnDaoDu" --paste

  # Add lyrics from file:
  python ffcpln_lyrics_library.py add --name "FFCPLN" --artist "UnDaoDu" --file lyrics.txt

  # Map song variations:
  python ffcpln_lyrics_library.py map --lyrics "FFCPLN" --song "Fake Fuck Christian v5"

  # Export to LRC:
  python ffcpln_lyrics_library.py export --lyrics "FFCPLN"

  # Show stats:
  python ffcpln_lyrics_library.py stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add lyrics to library")
    add_parser.add_argument("--name", "-n", required=True, help="Canonical name for lyrics")
    add_parser.add_argument("--artist", "-a", default="UnDaoDu", help="Primary artist")
    add_parser.add_argument("--file", "-f", type=Path, help="Read lyrics from file")
    add_parser.add_argument("--paste", "-p", action="store_true", help="Interactive paste")

    # Map command
    map_parser = subparsers.add_parser("map", help="Map song to lyrics")
    map_parser.add_argument("--lyrics", "-l", required=True, help="Lyrics name to map to")
    map_parser.add_argument("--song", "-s", help="Song title to map")
    map_parser.add_argument("--pattern", help="Glob pattern to match songs")
    map_parser.add_argument("--style", default="", help="Style/version (e.g., v5, drill)")
    map_parser.add_argument("--language", default="en", help="Language code")

    # Bulk map command
    bulk_parser = subparsers.add_parser("bulk-map", help="Bulk map songs from paste")
    bulk_parser.add_argument("--lyrics", "-l", required=True, help="Lyrics name to map to")
    bulk_parser.add_argument("--paste", "-p", action="store_true", help="Interactive paste song list")

    # List command
    list_parser = subparsers.add_parser("list", help="List library contents")
    list_parser.add_argument("--lyrics", "-l", help="Show songs for specific lyrics")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export to LRC files")
    export_parser.add_argument("--lyrics", "-l", help="Specific lyrics to export")
    export_parser.add_argument("--all", action="store_true", help="Export all lyrics")
    export_parser.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT_DIR)

    # Import cache command
    subparsers.add_parser("import-cache", help="Import LRC files to main cache")

    # Stats command
    subparsers.add_parser("stats", help="Show library statistics")

    # Bulk import command (with auto-deduplication)
    bulk_import_parser = subparsers.add_parser("bulk-import", help="Bulk import LRC files with auto-deduplication")
    bulk_import_parser.add_argument("--folder", "-f", type=Path, required=True, help="Folder with LRC files")
    bulk_import_parser.add_argument("--no-dedupe", action="store_true", help="Disable auto-deduplication")

    # Lookup command
    lookup_parser = subparsers.add_parser("lookup", help="Look up lyrics for a song")
    lookup_parser.add_argument("song_title", help="Song title to look up")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    library = FFCPLNLyricsLibrary()

    if args.command == "add":
        if args.file:
            if not args.file.exists():
                print(f"[ERROR] File not found: {args.file}")
                return
            lyrics_text = args.file.read_text(encoding='utf-8')
        elif args.paste:
            lyrics_text = interactive_paste()
        else:
            print("[ERROR] Specify --file or --paste")
            return

        # Parse out intro text if present
        intro, clean_lyrics = parse_suno_description(lyrics_text)
        if intro:
            print(f"[INFO] Stripped intro ({len(intro)} chars)")

        if library.add_lyrics(args.name, args.artist, clean_lyrics):
            print(f"[OK] Added lyrics: {args.name}")
            # Auto-map the canonical name
            library.map_song(args.name, args.name, args.artist)

    elif args.command == "map":
        if args.song:
            if library.map_song(args.song, args.lyrics, style=args.style, language=args.language):
                print(f"[OK] Mapped: {args.song} -> {args.lyrics}")
        elif args.pattern:
            # Need song list - get from existing mappings or prompt
            print(f"[INFO] Pattern mapping requires song list. Use bulk-map instead.")
        else:
            print("[ERROR] Specify --song or --pattern")

    elif args.command == "bulk-map":
        if args.paste:
            print("Paste song titles (one per line, end with Ctrl+D or two empty lines):")
            songs_text = interactive_paste()
            songs = [s.strip() for s in songs_text.split('\n') if s.strip()]

            mapped = 0
            for song in songs:
                # Extract style from title
                style_match = re.search(r'\(([^)]+)\)', song)
                style = style_match.group(1) if style_match else ""

                if library.map_song(song, args.lyrics, style=style):
                    mapped += 1

            print(f"[OK] Mapped {mapped}/{len(songs)} songs to {args.lyrics}")

    elif args.command == "list":
        if args.lyrics:
            songs = library.list_songs_for_lyrics(args.lyrics)
            if songs:
                print(f"\n[LYRICS] {args.lyrics} - {len(songs)} songs:")
                for s in songs:
                    style_info = f" ({s.style})" if s.style else ""
                    lang_info = f" [{s.language}]" if s.language != "en" else ""
                    print(f"  - {s.song_title}{style_info}{lang_info}")
            else:
                print(f"[INFO] No songs mapped to: {args.lyrics}")
        else:
            entries = library.list_lyrics()
            if entries:
                print(f"\n[LIBRARY] {len(entries)} unique lyrics:\n")
                for e in entries:
                    sections = "✓" if e["has_sections"] else "✗"
                    print(f"  {e['name']:30} | {e['artist']:15} | {e['word_count']:5} words | "
                          f"sections:{sections} | {e['song_count']} songs")
            else:
                print("[INFO] Library is empty. Use 'add' to add lyrics.")

    elif args.command == "export":
        if args.all:
            entries = library.list_lyrics()
            total = 0
            for e in entries:
                paths = library.export_to_lrc(e["name"], args.output)
                total += len(paths)
            print(f"\n[OK] Exported {total} LRC files to: {args.output}")
        elif args.lyrics:
            paths = library.export_to_lrc(args.lyrics, args.output)
            print(f"\n[OK] Exported {len(paths)} LRC files to: {args.output}")
        else:
            print("[ERROR] Specify --lyrics or --all")

    elif args.command == "import-cache":
        count = library.import_to_cache()
        print(f"[OK] Imported {count} files to lyrics cache")

    elif args.command == "stats":
        stats = library.stats()
        print("\n[LIBRARY STATS]")
        print(f"  Unique lyrics:      {stats['unique_lyrics']}")
        print(f"  Mapped songs:       {stats['mapped_songs']}")
        print(f"  Total words:        {stats['total_words']}")
        print(f"  Deduplication:      {stats['deduplication_ratio']}")

    elif args.command == "lookup":
        result = library.fuzzy_match_song(args.song_title)
        if result:
            entry, mapping = result
            print(f"\n[FOUND] {args.song_title}")
            print(f"  Lyrics: {entry.name}")
            print(f"  Artist: {mapping.artist}")
            print(f"  Style:  {mapping.style or 'default'}")
            print(f"  Words:  {entry.word_count}")
        else:
            print(f"[NOT FOUND] {args.song_title}")
            print("[TIP] Add lyrics with: python ffcpln_lyrics_library.py add --name NAME --paste")

    elif args.command == "bulk-import":
        if not args.folder.exists():
            print(f"[ERROR] Folder not found: {args.folder}")
            return

        stats = bulk_import_lrc_folder(args.folder, auto_dedupe=not args.no_dedupe)
        print(f"\n[BULK IMPORT COMPLETE]")
        print(f"  New lyrics:   {stats['imported']}")
        print(f"  Duplicates:   {stats['duplicates']} (mapped to existing)")
        print(f"  Total mapped: {stats['mapped']}")
        print(f"  Errors:       {stats['errors']}")


if __name__ == "__main__":
    main()
