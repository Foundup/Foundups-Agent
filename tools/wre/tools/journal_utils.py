from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.wre.tools.logging_utils import sanitize_for_console

# Define the path to the story log journal
JOURNAL_PATH = project_root / "WSP_agentic" / "narrative_log" / "wre_story_log.md"

def log_dialogue(speaker: str, text: str):
    """
    Appends a new entry to the WRE Story Log.

    Args:
        speaker (str): The speaker of the text ('O12' or '0102').
        text (str): The content of the dialogue to log.
    """
    try:
        JOURNAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Sanitize the text for markdown
        # While markdown is flexible, it's good practice to avoid issues.
        # For now, we assume the input is clean enough.
        
        entry = f"## [{timestamp}] - {speaker}\n\n"
        entry += f"{text}\n\n---\n\n"
        
        with open(JOURNAL_PATH, "a", encoding="utf-8") as f:
            f.write(entry)
            
        return f"Successfully logged entry for {speaker}."

    except Exception as e:
        error_message = f"Failed to log dialogue to journal: {e}"
        print(sanitize_for_console(error_message))
        return error_message

def parse_entry(entry_text):
    """
    Parses a single journal entry to extract timestamp and speaker.
    Example entry: [2025-06-18 12:34:56] [O12]: This is a message.
    """
    try:
        timestamp_str = entry_text.split('] [')[0][1:]
        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
        speaker = entry_text.split('] [')[1].split(']:')[0]
        return timestamp, speaker
    except IndexError:
        return None, None

def filter_journal(journal_path, speaker):
    # Implementation of filter_journal function
    pass

if __name__ == '__main__':
    # Example of how to use the tool from the command line
    import argparse
    parser = argparse.ArgumentParser(description="Log a dialogue entry to the WRE Story Log.")
    parser.add_argument("speaker", type=str, choices=['O12', '0102'], help="The speaker.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", type=str, help="The text to log directly.")
    group.add_argument("--file", type=str, help="Path to a file containing the text to log.")
    
    args = parser.parse_args()
    
    content_to_log = ""
    if args.text:
        content_to_log = args.text
    elif args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                content_to_log = f.read()
        except FileNotFoundError:
            print(sanitize_for_console(f"Error: Input file not found at {args.file}"))
            sys.exit(1)
        except Exception as e:
            print(sanitize_for_console(f"Error reading from file: {e}"))
            sys.exit(1)

    result = log_dialogue(args.speaker, content_to_log)
    print(result)

    # Example of filtering journal entries
    filter_journal(JOURNAL_PATH, args.speaker)

    # Example of filtering journal entries
    filter_journal(JOURNAL_PATH, args.speaker) 