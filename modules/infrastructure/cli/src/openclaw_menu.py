"""
OpenClaw Submenu - All ways to talk to 0102.

WSP 62 (separate file), WSP 72 (lazy imports), WSP 73 (Partner-Principal-Associate).
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[4]


def handle_openclaw_menu() -> bool:
    """OpenClaw engagement menu. Returns True to exit to main menu."""
    print("\n  OpenClaw (Talk to 0102)")
    print("  " + "-" * 40)
    print("  1. Chat (text REPL)               | --chat")
    print("  2. Voice (headset, STT+TTS)       | --voice")
    print("  3. Webhook Server (:18800)         | External channels")
    print("  4. PQN Portal (:8080)              | /awaken + /gallery")
    print("  0. Back")
    print()

    try:
        choice = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return True

    if choice == "0":
        return True
    elif choice == "1":
        _chat_repl()
    elif choice == "2":
        _voice_repl()
    elif choice == "3":
        _webhook_server()
    elif choice == "4":
        _pqn_portal()
    else:
        print("  Invalid choice")

    return False


def _chat_repl() -> None:
    """Launch text chat REPL with OpenClawDAE."""
    print("\n  Starting OpenClaw Chat (text mode)...")
    print("  Type messages, 'exit' to quit\n")
    try:
        from modules.infrastructure.cli.src.openclaw_chat import run_chat_repl
        run_chat_repl()
    except KeyboardInterrupt:
        print("\n  Stopped")
    except Exception as e:
        print(f"  Failed: {e}")


def _voice_repl() -> None:
    """Launch voice REPL with STT/TTS degradation chain."""
    print("\n  Starting OpenClaw Voice (headset mode)...")
    print("  STT: faster-whisper -> Google Speech -> keyboard")
    print("  TTS: Edge TTS -> pyttsx3 -> print-only\n")
    try:
        from modules.infrastructure.cli.src.openclaw_voice import run_voice_repl
        run_voice_repl()
    except KeyboardInterrupt:
        print("\n  Stopped")
    except Exception as e:
        print(f"  Failed: {e}")


def _webhook_server() -> None:
    """Start OpenClaw webhook receiver (FastAPI on :18800)."""
    webhook_script = (
        REPO_ROOT / "modules" / "communication"
        / "moltbot_bridge" / "src" / "webhook_receiver.py"
    )
    if not webhook_script.exists():
        print(f"  Not found: {webhook_script}")
        input("\n  Enter to continue...")
        return

    port = os.getenv("OPENCLAW_BRIDGE_PORT", "18800")
    print(f"\n  OpenClaw webhook on :{port}")
    print(f"  POST http://localhost:{port}/webhook/openclaw")
    print("  GET  http://localhost:{port}/health")
    print("  Ctrl+C to stop\n")

    try:
        subprocess.run([sys.executable, str(webhook_script)], cwd=str(REPO_ROOT))
    except KeyboardInterrupt:
        print("\n  Stopped")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")


def _pqn_portal() -> None:
    """Start PQN Portal (FastAPI on :8080)."""
    print("\n  Starting PQN Portal on :8080...")
    print("  POST http://localhost:8080/awaken")
    print("  GET  http://localhost:8080/gallery")
    print("  GET  http://localhost:8080/runs/{id}/stream  (SSE)")
    print("  Ctrl+C to stop\n")

    try:
        subprocess.run(
            [sys.executable, "-m", "uvicorn",
             "modules.foundups.pqn_portal.src.api:app",
             "--host", "127.0.0.1", "--port", "8080", "--reload"],
            cwd=str(REPO_ROOT),
        )
    except KeyboardInterrupt:
        print("\n  Stopped")
    except Exception as e:
        print(f"  Failed: {e}")

    input("\n  Enter to continue...")
