#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Comprehensive Emoji Replacer for HoloIndex
Replaces all Unicode emojis with ASCII-safe alternatives to prevent encoding issues.

WSP 20 (Professional and Scientific Language) Compliance
"""

import os
import re
from pathlib import Path
from typing import Dict, List

# Comprehensive emoji replacement mapping
EMOJI_REPLACEMENTS = {
    # Status indicators
    "[OK]": "[OK]",
    "[FAIL]": "[ERROR]",
    "[U+26A0]️": "[WARN]",
    "[ALERT]": "[CRITICAL]",
    "ℹ️": "[INFO]",
    "[SEARCH]": "[SEARCH]",
    "[DATA]": "[ANALYSIS]",
    "[REFRESH]": "[LOOP]",
    "[UP]": "[GROWTH]",
    "[U+1F4C9]": "[DECLINE]",
    "[TARGET]": "[TARGET]",
    "[IDEA]": "[IDEA]",
    "[U+1F525]": "[HOT]",
    "[U+1F4AA]": "[STRONG]",
    "[ROCKET]": "[LAUNCH]",
    "[U+2B50]": "[SPARKLE]",
    "[CELEBRATE]": "[CELEBRATE]",
    "[BOT]": "[AI]",
    "[HANDSHAKE]": "[HANDSHAKE]",
    "[AI]": "[BRAIN]",
    "[U+1F4E1]": "[SIGNAL]",
    "[U+1F4C5]": "[CALENDAR]",
    "[U+1F3AD]": "[THEATER]",
    "[U+2B06]️": "[UP]",
    "[SEARCH]": "[MAGNIFY]",
    "[U+1F4AD]": "[THINK]",
    "[U+1F4BB]": "[COMPUTER]",
    "[U+1F6E0]️": "[TOOL]",
    "[ART]": "[ART]",
    "[CLIPBOARD]": "[CLIPBOARD]",
    "[UP]": "[CHART]",
    "[SEARCH]": "[SEARCH]",
    "[U+1F4AC]": "[BUBBLE]",
    "[U+1F525]": "[FIRE]",
    "[BOOKS]": "[BOOKS]",
    "[BOX]": "[PACKAGE]",
    "[U+1F3D7]️": "[BUILD]",
    "[U+1F510]": "[LOCK]",
    "[U+1F511]": "[KEY]",
    "[LIGHTNING]": "[LIGHTNING]",
    "[U+1F31F]": "[STAR]",
    "[TARGET]": "[TARGET]",
    "[NOTE]": "[NOTE]",
    "[U+1F5C2]️": "[FILES]",
    "[U+1F4C2]": "[FOLDER]",
    "[U+2699]️": "[GEAR]",
    "[TOOL]": "[WRENCH]",
    "[GAME]": "[GAME]",
    "[U+1F310]": "[GLOBE]",
    "[U+1F4CC]": "[PIN]",
    "[U+1F3C6]": "[TROPHY]",
    "[U+1F381]": "[GIFT]",
    "[U+1F4BE]": "[DISK]",
    "[DATA]": "[GRAPH]",
    "[LINK]": "[LINK]",
    "[U+1F3C3]": "[RUN]",
    "⏰": "[ALARM]",
    "[U+1F514]": "[BELL]",
    "[U+1F4E2]": "[ANNOUNCE]",
    "[U+1F3B5]": "[MUSIC]",
    "[U+1F3B6]": "[NOTES]",
    "[U+1F3C1]": "[FINISH]",
    "[FORBIDDEN]": "[BLOCKED]",
    "[U+26D4]": "[STOP]",
    "[U+1F534]": "[RED]",
    "🟢": "[GREEN]",
    "🟡": "[YELLOW]",
    "[U+1F535]": "[BLUE]",
    "🟣": "[PURPLE]",
    "🟠": "[ORANGE]",
    "[U+26AB]": "[BLACK]",
    "[U+26AA]": "[WHITE]",
    "[U+1F53A]": "[UP_TRIANGLE]",
    "[U+1F53B]": "[DOWN_TRIANGLE]",
    "[U+1F539]": "[DIAMOND]",
    "[U+25B6]️": "[PLAY]",
    "⏸️": "[PAUSE]",
    "⏹️": "[STOP]",
    "⏮️": "[REWIND]",
    "⏭️": "[FORWARD]",
    "[U+1F500]": "[SHUFFLE]",
    "[U+1F501]": "[REPEAT]",
    "[U+1F502]": "[REPEAT_ONE]",

    # Hand gestures (WSP compliance)
    "[U+270A]": "[FIST]",
    "[U+270B]": "[HAND]",
    "[U+1F590]": "[OPEN_HAND]",
    "[U+1F44D]": "[THUMBS_UP]",
    "[U+1F44E]": "[THUMBS_DOWN]",
    "[U+1F44C]": "[OK_HAND]",
    "[U+270C]️": "[PEACE]",
    "[U+1F91E]": "[CROSSED_FINGERS]",
    "[U+1F91F]": "[ROCK]",
    "[U+1F918]": "[ROCK_ON]",
    "[U+1F44F]": "[CLAP]",
    "[U+1F64F]": "[PRAY]",
    "[U+1F932]": "[PALMS_UP]",
    "[U+1F450]": "[OPEN_HANDS]",

    # Faces (0102 consciousness markers)
    "[U+1F600]": "[HAPPY]",
    "[U+1F603]": "[SMILE]",
    "[U+1F604]": "[GRIN]",
    "[U+1F601]": "[BEAM]",
    "[U+1F606]": "[LAUGH]",
    "[U+1F605]": "[SWEAT_SMILE]",
    "[U+1F602]": "[JOY]",
    "[U+1F923]": "[ROFL]",
    "[U+1F60A]": "[BLUSH]",
    "[U+1F607]": "[ANGEL]",
    "[U+1F642]": "[SLIGHT_SMILE]",
    "[U+1F609]": "[WINK]",
    "[U+1F60C]": "[RELIEVED]",
    "[U+1F60D]": "[LOVE]",
    "[U+1F970]": "[HEARTS]",
    "[U+1F618]": "[KISS]",
    "[U+1F617]": "[KISS]",
    "[U+1F619]": "[KISS_SMILE]",
    "[U+1F61A]": "[KISS_BLUSH]",
    "[U+1F60B]": "[YUM]",
    "[U+1F61B]": "[TONGUE]",
    "[U+1F61C]": "[TONGUE_WINK]",
    "[U+1F92A]": "[CRAZY]",
    "[U+1F61D]": "[TONGUE_CLOSED]",
    "[U+1F911]": "[MONEY]",
    "[U+1F917]": "[HUG]",
    "[U+1F914]": "[THINK]",
    "[U+1F910]": "[ZIPPER]",
    "[U+1F928]": "[RAISED_EYEBROW]",
    "[U+1F610]": "[NEUTRAL]",
    "[U+1F611]": "[EXPRESSIONLESS]",
    "[U+1F636]": "[NO_MOUTH]",
    "[U+1F60F]": "[SMIRK]",
    "[U+1F612]": "[UNAMUSED]",
    "[U+1F644]": "[ROLL_EYES]",
    "[U+1F62C]": "[GRIMACE]",
    "[U+1F925]": "[LYING]",
    "[U+1F60C]": "[RELIEVED]",
    "[U+1F614]": "[PENSIVE]",
    "[U+1F62A]": "[SLEEPY]",
    "[U+1F924]": "[DROOLING]",
    "[U+1F634]": "[SLEEPING]",
    "[U+1F637]": "[MASK]",
    "[U+1F912]": "[SICK]",
    "[U+1F915]": "[BANDAGE]",
    "[U+1F922]": "[NAUSEATED]",
    "[U+1F92E]": "[VOMITING]",
    "[U+1F927]": "[SNEEZE]",
    "[U+1F975]": "[HOT_FACE]",
    "[U+1F976]": "[COLD_FACE]",
    "[U+1F635]": "[DIZZY]",
    "[U+1F92F]": "[EXPLODING_HEAD]",
    "[U+1F920]": "[COWBOY]",
    "[U+1F973]": "[PARTY]",
    "[U+1F60E]": "[COOL]",
    "[U+1F913]": "[NERD]",
    "[U+1F9D0]": "[MONOCLE]",
    "[U+1F615]": "[CONFUSED]",
    "[U+1F61F]": "[WORRIED]",
    "[U+1F641]": "[SLIGHT_FROWN]",
    "[U+2639]️": "[FROWN]",
    "[U+1F62E]": "[OPEN_MOUTH]",
    "[U+1F62F]": "[HUSHED]",
    "[U+1F632]": "[ASTONISHED]",
    "[U+1F633]": "[FLUSHED]",
    "[U+1F97A]": "[PLEADING]",
    "[U+1F626]": "[FROWNING]",
    "[U+1F627]": "[ANGUISHED]",
    "[U+1F628]": "[FEARFUL]",
    "[U+1F630]": "[ANXIOUS]",
    "[U+1F625]": "[SAD_RELIEVED]",
    "[U+1F622]": "[CRY]",
    "[U+1F62D]": "[SOB]",
    "[SHOCK]": "[SCREAM]",
    "[U+1F616]": "[CONFOUNDED]",
    "[U+1F623]": "[PERSEVERING]",
    "[U+1F61E]": "[DISAPPOINTED]",
    "[U+1F613]": "[SWEAT]",
    "[U+1F629]": "[WEARY]",
    "[U+1F62B]": "[TIRED]",
    "[U+1F624]": "[TRIUMPH]",
    "[U+1F621]": "[ANGRY]",
    "[U+1F620]": "[MAD]",
    "[U+1F92C]": "[CURSING]",
    "[U+1F608]": "[DEVIL]",
    "[U+1F47F]": "[IMP]",
    "[U+1F480]": "[SKULL]",
    "[U+2620]️": "[CROSSBONES]",
    "[GHOST]": "[GHOST]",
    "[U+1F47D]": "[ALIEN]",
    "[U+1F47E]": "[INVADER]",
    "[BOT]": "[ROBOT]",
    "[U+1F4A9]": "[POOP]",
    "[U+1F648]": "[SEE_NO_EVIL]",
    "[U+1F649]": "[HEAR_NO_EVIL]",
    "[U+1F64A]": "[SPEAK_NO_EVIL]"
}


def replace_emojis_in_text(text: str) -> str:
    """Replace all emojis in text with ASCII alternatives."""
    for emoji, replacement in EMOJI_REPLACEMENTS.items():
        text = text.replace(emoji, replacement)

    # Remove any remaining Unicode emojis using regex
    # This catches emojis not in our mapping
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # supplemental symbols
        "\U00002600-\U000026FF"  # misc symbols
        "\U00002700-\U000027BF"  # dingbats
        "]+",
        flags=re.UNICODE
    )

    def emoji_replacer(match):
        # For unmapped emojis, create a generic replacement
        return "[EMOJI]"

    text = emoji_pattern.sub(emoji_replacer, text)

    return text


def replace_emojis_in_file(file_path: Path) -> bool:
    """Replace emojis in a single file."""
    try:
        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Replace emojis
        new_content = replace_emojis_in_text(content)

        # Only write if changes were made
        if new_content != content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"[OK] Replaced emojis in: {file_path}")
            return True
        else:
            print(f"[SKIP] No emojis found in: {file_path}")
            return False

    except Exception as e:
        print(f"[ERROR] Failed to process {file_path}: {e}")
        return False


def process_directory(directory: Path, extensions: List[str]) -> Dict[str, int]:
    """Process all files in directory with given extensions."""
    stats = {
        'processed': 0,
        'modified': 0,
        'skipped': 0,
        'errors': 0
    }

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            # Skip node_modules and other build directories
            if any(part in file_path.parts for part in [
                'node_modules', 'dist', 'build', '.git', '__pycache__',
                'venv', 'env', '.env'
            ]):
                continue

            stats['processed'] += 1

            if replace_emojis_in_file(file_path):
                stats['modified'] += 1
            else:
                stats['skipped'] += 1

    return stats


def main():
    """Main function to process HoloIndex files."""
    # Define HoloIndex root
    holo_root = Path(__file__).parent.parent

    # File extensions to process
    extensions = ['.py', '.md', '.json', '.txt', '.yaml', '.yml']

    print(f"[INFO] Starting emoji replacement in: {holo_root}")
    print(f"[INFO] Processing extensions: {extensions}")
    print("[INFO] This ensures WSP 20 compliance (Professional Language)")
    print()

    # Process files
    stats = process_directory(holo_root, extensions)

    # Print summary
    print()
    print("[ANALYSIS] Emoji Replacement Summary:")
    print(f"  Files processed: {stats['processed']}")
    print(f"  Files modified:  {stats['modified']}")
    print(f"  Files skipped:   {stats['skipped']}")
    print(f"  Errors:          {stats['errors']}")

    if stats['modified'] > 0:
        print()
        print("[OK] Emoji replacement complete!")
        print("[INFO] All Unicode emojis replaced with ASCII alternatives")
        print("[INFO] System is now WSP 20 compliant")
    else:
        print()
        print("[INFO] No emojis found - system already compliant")

    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    exit(main())