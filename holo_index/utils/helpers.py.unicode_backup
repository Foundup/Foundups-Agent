"""HoloIndex Utility Helpers - WSP 49 Compliant Module Structure

Common utility functions used throughout HoloIndex.

WSP Compliance: WSP 87 (Size Limits), WSP 49 (Module Structure), WSP 72 (Block Independence)
"""

from __future__ import annotations
import os
from pathlib import Path
from typing import Dict, Any, Optional


def safe_print(text: str, **kwargs) -> None:
    """Print text safely, handling Unicode characters that may not be supported by the console encoding.

    WSP 64 COMPLIANCE: This function prevents the recurring cp932 encoding errors
    that 0102 agents keep creating by using Unicode emojis on Windows.

    PATTERN DETECTED: 0102 repeatedly adds emojis, then fixes encoding errors later.
    This is VIBECODING - writing without checking platform compatibility.
    """
    # Comprehensive Unicode to ASCII mappings for Windows cp932 compatibility
    # These are ALL the emojis that 0102 keeps using that break on Windows
    UNICODE_TO_ASCII = {
        # Status indicators - MOST COMMON OFFENDERS
        '✅': '[OK]',
        '❌': '[X]',
        '✓': '[v]',
        '✗': '[x]',
        '⚠️': '[WARNING]',
        '🚫': '[NO]',
        '⚡': '[FAST]',
        '🔄': '[REFRESH]',

        # Common UI symbols
        '🔍': '[SEARCH]',
        '📁': '[FOLDER]',
        '📊': '[STATS]',
        '💡': '[IDEA]',
        '🛡️': '[SHIELD]',
        '🎯': '[TARGET]',
        '🚀': '[LAUNCH]',
        '🧠': '[BRAIN]',
        '📋': '[CLIPBOARD]',
        '🛠️': '[TOOLS]',
        '🗑️': '[DELETE]',
        '🔗': '[LINK]',
        '📍': '[PIN]',

        # Arrows and bullets - FREQUENT IN OUTPUT
        '→': '->',
        '←': '<-',
        '↔': '<->',
        '↑': '^',
        '↓': 'v',
        '•': '*',
        '▶': '>',
        '◀': '<',

        # Quotation marks and dashes
        '\u2014': '--',  # em dash
        '\u2013': '-',   # en dash
        '\u2018': "'",   # left single quote
        '\u2019': "'",   # right single quote
        '\u201c': '"',   # left double quote
        '\u201d': '"',   # right double quote
        '\u2026': '...',  # ellipsis
        '\u00a0': ' ',   # non-breaking space

        # Other common emojis 0102 uses
        '🌟': '[STAR]',
        '📈': '[GRAPH]',
        '🏆': '[TROPHY]',
        '⭐': '[*]',
        '🎮': '[GAME]',
        '🔧': '[WRENCH]',
        '📝': '[MEMO]',
        '🌀': '[SPIRAL]',
        '❄️': '[SNOW]',
        '🍣': '[SUSHI]',
        '🧘': '[MEDITATE]',
        '🐕': '[DOG]',
        '🔥': '[FIRE]',
        '💎': '[GEM]',
        '🎨': '[ART]',
        '📚': '[BOOKS]',
        '🔑': '[KEY]',
    }

    # First try to print normally
    try:
        print(text, **kwargs)
    except UnicodeEncodeError:
        # If that fails, replace ALL problematic Unicode characters
        safe_text = text
        for unicode_char, ascii_char in UNICODE_TO_ASCII.items():
            safe_text = safe_text.replace(unicode_char, ascii_char)

        # Try again with replacements
        try:
            print(safe_text, **kwargs)
        except UnicodeEncodeError:
            # If still failing, strip all non-ASCII as last resort
            safe_text = safe_text.encode('ascii', errors='ignore').decode('ascii')
            print(safe_text, **kwargs)

            # Log this pattern for HoloIndex self-improvement
            if os.path.exists('E:/HoloIndex/logs'):
                import json
                from datetime import datetime
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'event': 'unicode_encoding_failure',
                    'original_text_sample': text[:100],
                    'pattern': 'cp932_encoding_issue',
                    'recommendation': 'Use ASCII alternatives in print statements'
                }
                try:
                    with open('E:/HoloIndex/logs/unicode_issues.jsonl', 'a') as f:
                        f.write(json.dumps(log_entry) + '\n')
                except:
                    pass  # Silent fail on logging


def print_onboarding(args, advisor_available: bool, run_number: str) -> None:
    """Print onboarding information for HoloIndex usage."""
    # Removed visual marker - focus on signal, not noise
    safe_print(f"\n[0102] HoloIndex Quickstart (Run {run_number})")
    safe_print("  - Refresh indexes with `python holo_index.py --index-all` at the start of a session.")
    safe_print("  - Running search for: " + (args.search if args.search else "benchmark"))
    safe_print("  - Add --llm-advisor to receive compliance reminders and TODO checklists.")
    safe_print("  - Log outcomes in ModLogs/TESTModLogs (WSP 22) and consult FMAS before coding.")
    safe_print("  - Example queries:")
    safe_print("      python holo_index.py --check-module 'youtube_auth'  # Check before coding")
    safe_print("      python holo_index.py --search 'pqn cube' --llm-advisor --limit 5")
    safe_print("      python holo_index.py --search 'unit test plan' --llm-advisor")
    safe_print("      python holo_index.py --search 'navigation schema' --limit 3")
    safe_print("      python holo_index.py --init-dae 'YouTube Live'  # Initialize DAE context")
    safe_print("  - Documentation: WSP_35_HoloIndex_Qwen_Advisor_Plan.md | docs/QWEN_ADVISOR_IMPLEMENTATION_COMPLETE.md | tests/holo_index/TESTModLog.md")
    safe_print("  - Session points summary appears after each run (WSP reward telemetry).")
    safe_print("[INFO] Pattern Coach initialized - watching for vibecoding patterns")


# -------------------- Heuristic Configuration -------------------- #

VIOLATION_RULES = [
    {
        "pattern": r"\benhanced\b|\benhanced_",
        "wsp": "WSP 84",
        "message": "WSP 84: evolve existing modules; never create enhanced_* duplicates."
    },
    {
        "pattern": r"create\s+new",
        "wsp": "WSP 50",
        "message": "WSP 50: run pre-action verification before starting new code."
    },
    {
        "pattern": r"rename|naming",
        "wsp": "WSP 57",
        "message": "WSP 57: verify naming coherence before renaming components."
    },
    {
        "pattern": r"script|scripts",
        "wsp": "WSP 85",
        "message": "WSP 85: scripts belong in modules/{domain}/{module}/scripts/, not root or tools/scripts/."
    },
]

CONTEXT_WSP_MAP = {
    "document": ["WSP 22", "WSP 83"],
    "modlog": ["WSP 22"],
    "test": ["WSP 5", "WSP 6"],
    "structure": ["WSP 49"],
    "naming": ["WSP 57"],
    "token": ["WSP 75"],
    "create": ["WSP 50", "WSP 84"],
}

WSP_HINTS = {
    "WSP 22": "Keep module documentation and ModLogs synchronized.",
    "WSP 49": "Follow module directory scaffolding (src/tests/memory/docs).",
    "WSP 50": "Log intent in pre-action journal before coding.",
    "WSP 57": "Maintain naming coherence across files and identifiers.",
    "WSP 75": "Track effort in tokens, not wall-clock minutes.",
    "WSP 84": "Evolve existing modules instead of cloning new versions.",
    "WSP 85": "Scripts belong in modules/{domain}/{module}/scripts/, not root directory.",
    "WSP 87": "Consult navigation assets before writing new code.",
}

def get_wsp_paths():
    """
    Get WSP paths dynamically based on execution context.

    When run from holo_index/ directory, paths are relative to project root.
    When run from project root, paths are relative to current directory.
    """
    current_dir = Path.cwd()

    # Check if we're running from holo_index directory
    if current_dir.name == 'holo_index' or (current_dir.parent.name == 'holo_index'):
        # Running from holo_index - adjust paths to project root
        base_paths = [
            Path("../WSP_framework/src"),
            Path("../WSP_framework/docs"),
            Path("../WSP_knowledge/docs"),
            Path("../WSP_framework/docs/testing"),
            Path("../docs"),  # Root docs: architecture, vision, first principles
            Path("docs"),  # HoloIndex docs relative to holo_index
            Path("../modules"),  # All module documentation
        ]
    else:
        # Running from project root
        base_paths = [
            Path("WSP_framework/src"),
            Path("WSP_framework/docs"),
            Path("WSP_knowledge/docs"),
            Path("WSP_framework/docs/testing"),
            Path("docs"),  # Root docs: architecture, vision, first principles
            Path("holo_index/docs"),  # HoloIndex documentation
            Path("modules"),  # All module documentation
        ]

    # Filter to only existing paths
    return [p for p in base_paths if p.exists()]

# Legacy compatibility - compute dynamically
DEFAULT_WSP_PATHS = get_wsp_paths()
