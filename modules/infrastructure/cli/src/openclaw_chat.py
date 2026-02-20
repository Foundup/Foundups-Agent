"""
OpenClaw Local Chat REPL - Talk to 0102 directly from terminal.

Bypasses the Node.js gateway + webhook stack entirely.
Calls OpenClawDAE.process() directly with commander authority.

Usage:
    python -m modules.infrastructure.cli.src.openclaw_chat
    python main.py --chat

WSP Compliance:
    WSP 73: Partner (012 terminal) -> Principal (OpenClawDAE) -> Associates (domain DAEs)
    WSP 72: No new dependencies — reuses existing OpenClawDAE
"""

import asyncio
import sys
from pathlib import Path


def _ensure_repo_root():
    """Add repo root to sys.path if not already present."""
    repo = Path(__file__).resolve().parents[4]  # cli/src -> cli -> infrastructure -> modules -> repo
    root_str = str(repo)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)
    return repo


def run_chat_repl() -> None:
    """Interactive REPL loop for OpenClaw."""
    repo_root = _ensure_repo_root()

    print("=" * 60)
    print("  0102 OpenClaw Local Chat")
    print("  Commander: @UnDaoDu | Channel: local_repl")
    print("  Type 'exit' or Ctrl+C to quit")
    print("=" * 60)

    try:
        from modules.communication.moltbot_bridge.src.openclaw_dae import OpenClawDAE
    except ImportError as exc:
        print(f"[ERROR] Cannot import OpenClawDAE: {exc}")
        print("  Ensure you are running from the repo root (O:/Foundups-Agent)")
        return

    dae = OpenClawDAE(repo_root=repo_root)
    print(f"[OK] OpenClawDAE initialized (state={dae.state}, coherence={dae.coherence})")
    print()

    session_key = "local_repl_012"

    while True:
        try:
            message = input("012> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[EXIT] Session ended.")
            break

        if not message:
            continue
        if message.lower() in ("exit", "quit", "q"):
            print("[EXIT] Session ended.")
            break

        try:
            response = asyncio.run(
                dae.process(
                    message=message,
                    sender="@UnDaoDu",
                    channel="local_repl",
                    session_key=session_key,
                )
            )
            print(f"\n0102> {response}\n")
        except Exception as exc:
            print(f"\n[ERROR] {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    run_chat_repl()
