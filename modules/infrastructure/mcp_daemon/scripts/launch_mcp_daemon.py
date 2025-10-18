#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCP DAEmons Launch Script
=========================

Launches the MCP DAEmons with proper environment setup.

Usage:
    python launch_mcp_daemon.py

WSP Compliance: WSP 80 (Cube-Level DAE), WSP 77 (Agent Coordination Protocol)
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

import os
import signal
import logging
from pathlib import Path

# Add Foundups paths
repo_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(repo_root))

from modules.infrastructure.mcp_daemon.src.mcp_daemon import MCPDaemon

def main():
    """Launch MCP DAEmons"""
    print("🚀 Starting MCP DAEmons...")
    print("=" * 50)

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(repo_root / "logs" / "mcp_daemon.log"),
            logging.StreamHandler()
        ]
    )

    # Create daemon instance
    daemon = MCPDaemon()

    # Handle graceful shutdown
    def signal_handler(signum, frame):
        print("\n🛑 Received shutdown signal, stopping MCP DAEmons...")
        daemon.stop()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Start the daemon
    try:
        daemon.start()
    except Exception as e:
        logging.error(f"MCP DAEmons failed to start: {e}")
        print(f"❌ MCP DAEmons failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
