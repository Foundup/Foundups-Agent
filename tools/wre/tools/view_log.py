"""
WRE Chronicle Viewer

Provides utilities for viewing WRE session chronicle logs with structured formatting
and intelligent parsing of JSON log entries.

Author: FoundUps Agent Utilities Team
Version: 1.0.0
Date: 2025-01-29
WSP Compliance: WSP 46 (WRE Protocol), WSP 22 (Traceable Narrative)

Dependencies:
- tools.wre.logging_utils

Usage:
    python tools/wre/tools/view_log.py                    # View latest log
    python tools/wre/tools/view_log.py path/to/log.jsonl # View specific log
    python tools/wre/tools/view_log.py -n 50             # View last 50 entries
    
Features:
- Automatic latest log discovery
- JSON log parsing with error handling
- Configurable number of entries to display
- Robust handling of malformed log entries
"""

import json
from pathlib import Path
import sys
import re

# Add project root to path to allow importing from other directories
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.wre.logging_utils import LOGS_DIR, sanitize_for_console

def find_latest_chronicle():
    """Finds the most recent session chronicle file based on filename."""
    if not LOGS_DIR.exists():
        return None
    
    chronicles = list(LOGS_DIR.glob("session_*.chronicle.jsonl"))
    if not chronicles:
        return None
        
    # Sort by filename descending to get the latest
    chronicles.sort(reverse=True)
    return chronicles[0]

def view_log(filepath=None, num_lines=30):
    """
    Displays the last N lines of a specified session chronicle,
    or the most recent one if no file is specified.
    """
    chronicle_path = None
    if filepath:
        chronicle_path = Path(filepath)
    else:
        chronicle_path = find_latest_chronicle()
    
    if not chronicle_path or not chronicle_path.exists():
        print(sanitize_for_console("No WRE Chronicle logs found or specified file does not exist."))
        return

    print(sanitize_for_console(f"--- Displaying last {num_lines} entries from {chronicle_path.name} ---"))
    
    try:
        with open(chronicle_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex to find JSON objects, robust against escaped newlines within the log
        # This will look for '{' followed by anything (non-greedy) until '}'
        json_objects = re.findall(r'\{.*?\}', content)
        
        # Get the last N lines
        last_n_objects = json_objects[-num_lines:]
        
        # Print them in reverse order
        for log_str in reversed(last_n_objects):
            try:
                log_entry = json.loads(log_str)
                timestamp = log_entry.get('timestamp', '').split('T')[1].split('.')[0]
                level = log_entry.get('level', 'INFO')
                message = log_entry.get('message', '')
                
                # The 'data' field might contain complex, uninteresting info. 
                # We'll focus on the core message for clarity.
                formatted_line = f"{timestamp} [{level}] {message}"
                    
                print(sanitize_for_console(formatted_line))
            except json.JSONDecodeError:
                # If parsing fails, it's likely a malformed entry.
                # We can still try to extract and clean up the message for readability.
                message_match = re.search(r'"message":\s*"(.*?)"', log_str, re.DOTALL)
                if message_match:
                    # Clean up the extracted message
                    cleaned_message = message_match.group(1).replace('\\n', '\n').replace('\\"', '"')
                    print(sanitize_for_console(f"[UNPARSABLE ENTRY] {cleaned_message}"))
                else:
                    # Generic fallback if message can't be extracted
                    print(sanitize_for_console(f"Unparsable raw data: {log_str}"))

    except FileNotFoundError:
        print(sanitize_for_console(f"Error: Log file not found at {chronicle_path}"))
    except Exception as e:
        print(sanitize_for_console(f"An unexpected error occurred: {e}"))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="View a WRE session chronicle. Shows the latest by default.")
    parser.add_argument(
        'filepath',
        type=str,
        nargs='?',
        default=None,
        help='Optional: Path to a specific chronicle file to view.'
    )
    parser.add_argument(
        '-n', '--lines',
        type=int,
        default=30,
        help='Number of recent lines to display.'
    )
    args = parser.parse_args()
    
    view_log(filepath=args.filepath, num_lines=args.lines) 