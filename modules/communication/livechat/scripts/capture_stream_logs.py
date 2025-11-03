#!/usr/bin/env python3
"""
Terminal Log Capture for Stream Sessions
Captures all terminal output during stream sessions for 0102 analysis

Saves complete terminal logs to conversation memory for:
- Mod interaction patterns
- Bot responses
- Error tracking
- Session statistics
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path
import subprocess
import threading

class StreamLogCapture:
    """Captures terminal output during stream sessions"""

    def __init__(self):
        self.conversation_dir = Path("modules/communication/livechat/memory/conversation")
        self.conversation_dir.mkdir(parents=True, exist_ok=True)
        self.current_log = []
        self.session_start = datetime.now()

    def capture_stream_session(self):
        """Run main.py --youtube and capture all output"""

        # Create session folder
        session_name = f"stream_{self.session_start.strftime('%Y%m%d_%H%M%S')}"
        session_dir = self.conversation_dir / session_name
        session_dir.mkdir(exist_ok=True)

        # Log file paths
        terminal_log = session_dir / "terminal_output.log"
        summary_file = session_dir / "session_summary.txt"

        print(f"[U+1F4F9] Starting stream session capture: {session_name}")
        print(f"[U+1F4C1] Logs will be saved to: {session_dir}")
        print("=" * 60)

        # Run the main YouTube DAE and capture output
        try:
            process = subprocess.Popen(
                ["python", "main.py", "--youtube"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            # Open log file for writing
            with open(terminal_log, 'w', encoding='utf-8') as log_file:
                # Write header
                log_file.write(f"STREAM SESSION LOG\n")
                log_file.write(f"==================\n")
                log_file.write(f"Start Time: {self.session_start}\n")
                log_file.write(f"Session ID: {session_name}\n")
                log_file.write("=" * 60 + "\n\n")

                # Capture and display output in real-time
                for line in iter(process.stdout.readline, ''):
                    if line:
                        # Display to terminal
                        print(line, end='')

                        # Write to log file
                        log_file.write(line)
                        log_file.flush()

                        # Track for summary
                        self.current_log.append(line)

            # Wait for process to complete
            process.wait()

        except KeyboardInterrupt:
            print("\n\n[STOP] Stream session interrupted by user")
            if process:
                process.terminate()

        except Exception as e:
            print(f"\n[FAIL] Error during capture: {e}")

        finally:
            # Save session summary
            self._save_summary(summary_file)
            print("\n" + "=" * 60)
            print(f"[U+1F4C1] Session logs saved to: {session_dir}")
            print(f"[DATA] Total lines captured: {len(self.current_log)}")

    def _save_summary(self, summary_file: Path):
        """Save session summary with statistics"""

        # Calculate statistics
        mod_messages = sum(1 for line in self.current_log if "[MOD]" in line or "[OWNER]" in line)
        bot_responses = sum(1 for line in self.current_log if "Sending message:" in line)
        consciousness = sum(1 for line in self.current_log if "[U+270A][U+270B][U+1F590]" in line)
        errors = sum(1 for line in self.current_log if "ERROR" in line)

        duration = datetime.now() - self.session_start

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("STREAM SESSION SUMMARY\n")
            f.write("=====================\n")
            f.write(f"Start Time: {self.session_start}\n")
            f.write(f"Duration: {duration}\n")
            f.write(f"\nSTATISTICS:\n")
            f.write(f"- Total Log Lines: {len(self.current_log)}\n")
            f.write(f"- Mod/Owner Messages: {mod_messages}\n")
            f.write(f"- Bot Responses: {bot_responses}\n")
            f.write(f"- Consciousness Triggers: {consciousness}\n")
            f.write(f"- Errors: {errors}\n")

            # Extract mod interactions
            f.write(f"\nMOD INTERACTIONS:\n")
            f.write("-" * 40 + "\n")
            for line in self.current_log:
                if "[MOD]" in line or "[OWNER]" in line:
                    # Extract just the message part
                    if "]: " in line:
                        message_part = line.split("]: ", 1)[1].strip()
                        f.write(f"  • {message_part}\n")


if __name__ == "__main__":
    print("[U+1F3AC] STREAM SESSION LOG CAPTURE")
    print("=" * 60)
    print("This will run the YouTube DAE and capture all terminal output")
    print("for 0102 analysis and pattern learning.\n")
    print("Press Ctrl+C to stop the session.\n")

    capturer = StreamLogCapture()
    capturer.capture_stream_session()