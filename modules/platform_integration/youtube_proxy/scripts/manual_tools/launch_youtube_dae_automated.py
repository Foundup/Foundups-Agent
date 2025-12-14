"""
Automated YouTube DAE Launcher
Simulates menu inputs to launch AutoModeratorDAE without manual interaction.
"""
from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

import subprocess
import sys

def launch_youtube_dae():
    """Launch YouTube DAE with automated menu selections."""

    # Prepare input: "1" for YouTube menu, "1" for AutoModeratorDAE
    input_data = "1\n1\n"

    # Launch main.py with input (UTF-8 encoding for emoji support)
    process = subprocess.Popen(
        [sys.executable, "main.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace',  # Replace problematic characters instead of crashing
        bufsize=1  # Line buffered
    )

    try:
        # Send menu selections
        process.stdin.write(input_data)
        process.stdin.flush()

        print("[MONITOR] YouTube DAE starting...")
        print("[MONITOR] Watching for:")
        print("  - Vision detection (PRIORITY 0)")
        print("  - Stream detection")
        print("  - CommunityMonitor initialization")
        print("  - Heartbeat loop")
        print()

        # Monitor output for key events
        for line in iter(process.stdout.readline, ''):
            line = line.strip()
            if not line:
                continue

            print(line)

            # Highlight key events
            if '[VISION]' in line:
                print("  ^^^ VISION DETECTION EVENT ^^^")
            elif '[COMMUNITY]' in line:
                print("  ^^^ COMMUNITY MONITOR EVENT ^^^")
            elif '[HEART]' in line:
                print("  ^^^ HEARTBEAT EVENT ^^^")
            elif 'STREAM DETECTED' in line or 'LIVE' in line:
                print("  ^^^ STREAM DETECTION EVENT ^^^")
            elif 'ERROR' in line or 'FAIL' in line:
                print("  !!! ERROR DETECTED !!!")

    except KeyboardInterrupt:
        print("\n[MONITOR] Interrupted by user")
        process.terminate()
    except Exception as e:
        print(f"\n[ERROR] Monitoring error: {e}")
        process.terminate()
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)

if __name__ == "__main__":
    launch_youtube_dae()
