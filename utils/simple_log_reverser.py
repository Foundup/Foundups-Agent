# File: simple_log_reverser.py
# Purpose: Reverses the lines of a single text file.
# Version: 1.0.0

import argparse
import sys
import logging
from pathlib import Path

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
# --- End Logging Setup ---

def reverse_log_file(input_path: Path, output_path: Path):
    """Reads lines from input_path, reverses them, and writes to output_path."""
    try:
        log.info(f"Reading input file: {input_path}")
        if not input_path.is_file():
            log.error(f"Input file not found or is not a file: {input_path}")
            return False

        with open(input_path, 'r', encoding='utf-8', errors='ignore') as infile:
            lines = infile.readlines()

        log.info(f"Read {len(lines)} lines. Reversing order...")
        lines.reverse()

        log.info(f"Writing reversed content to: {output_path}")
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(lines)

        log.info(f"Successfully reversed log file. Output saved to {output_path}")
        return True

    except Exception as e:
        log.exception(f"An error occurred during file reversal: {e}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Reverse the lines in a log or text file.",
        epilog="Example: python simple_log_reverser.py input.log output_reversed.log"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the input log/text file."
    )
    parser.add_argument(
        "output_file",
        type=Path,
        help="Path where the reversed output file will be saved."
    )

    args = parser.parse_args()

    log.info(f"Starting log reversal process...")
    success = reverse_log_file(args.input_file, args.output_file)

    if success:
        log.info("Process completed successfully.")
        sys.exit(0)
    else:
        log.error("Process failed.")
        sys.exit(1) 