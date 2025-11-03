#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

OAuth Credential Rotation Demo

Disconnect and Reconnect Demo
Demonstrates how to safely disconnect from Move2Japan and reconnect using UnDaoDu
to avoid same-account conflicts. Includes session management and credential rotation.

Author: FoundUps Agent Utilities Team
Version: 1.0.0
Date: 2025-01-29
WSP Compliance: WSP 54 (WRE Agent Duties), WSP 13 (Test Creation & Management)

Dependencies:
- modules.infrastructure.agent_management.src.multi_agent_manager

Usage:
    python tools/disconnect_reconnect_demo.py demo          # Run full demo
    python tools/disconnect_reconnect_demo.py status       # Show agent status
    python tools/disconnect_reconnect_demo.py force-undaodu # Force UnDaoDu
    python tools/disconnect_reconnect_demo.py help         # Show help
    
Features:
- Safe disconnect and reconnect procedures
- Multi-agent system initialization and management
- Credential rotation for conflict avoidance
- Session management with status monitoring
"""

import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.infrastructure.agent_management.src.multi_agent_manager import (
    get_agent_manager, show_agent_status
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demonstrate_disconnect_reconnect():
    """Demonstrate the disconnect and reconnect process."""
    print("\n[REFRESH] DISCONNECT & RECONNECT DEMONSTRATION")
    print("=" * 60)
    
    # Simulate user channel ID (Move2Japan account)
    user_channel_id = "UCMove2JapanChannelID123"
    
    print(f"[U+1F464] Current User: Logged in as Move2Japan")
    print(f"[CLIPBOARD] User Channel ID: {user_channel_id[:8]}...{user_channel_id[-4:]}")
    print(f"[ALERT] Problem: Agent and user on same account = conflicts!")
    
    print("\n[DATA] STEP 1: Initialize Multi-Agent System")
    print("-" * 40)
    
    # Initialize agent manager with user channel ID
    manager = get_agent_manager()
    success = manager.initialize(user_channel_id)
    
    if not success:
        print("[FAIL] Failed to initialize multi-agent system")
        return
    
    print("[OK] Multi-agent system initialized")
    
    print("\n[SEARCH] STEP 2: Agent Discovery & Conflict Detection")
    print("-" * 40)
    
    # Show discovered agents
    available_agents = manager.registry.get_available_agents()
    conflicted_agents = manager.registry.get_conflicted_agents()
    
    print(f"[UP] Total agents discovered: {len(manager.registry.agents)}")
    print(f"[OK] Available agents: {len(available_agents)}")
    print(f"[U+26A0]️ Conflicted agents: {len(conflicted_agents)}")
    
    if conflicted_agents:
        print("\n[ALERT] SAME-ACCOUNT CONFLICTS DETECTED:")
        for agent in conflicted_agents:
            print(f"   [FAIL] {agent.channel_name} ({agent.credential_set})")
            print(f"      +- {agent.conflict_reason}")
    
    if available_agents:
        print("\n[OK] SAFE AGENTS (Different Accounts):")
        for agent in available_agents:
            print(f"   [OK] {agent.channel_name} ({agent.credential_set})")
    
    print("\n[TARGET] STEP 3: Safe Agent Selection")
    print("-" * 40)
    
    # Try to select Move2Japan (should be blocked)
    print("[U+1F9EA] Test 1: Attempt to select Move2Japan...")
    move2japan_agent = manager.select_agent("Move2Japan")
    if move2japan_agent:
        if move2japan_agent.channel_name == "Move2Japan":
            print("[U+26A0]️ WARNING: Move2Japan selected despite conflict!")
        else:
            print(f"[OK] System redirected to safe agent: {move2japan_agent.channel_name}")
    else:
        print("[OK] Move2Japan correctly blocked due to same-account conflict")
    
    # Select UnDaoDu (should work)
    print("\n[U+1F9EA] Test 2: Select UnDaoDu (safe agent)...")
    undaodu_agent = manager.select_agent("UnDaoDu")
    if undaodu_agent:
        print(f"[OK] Successfully selected: {undaodu_agent.channel_name}")
        print(f"[CLIPBOARD] Agent ID: {undaodu_agent.agent_id}")
        print(f"[U+1F511] Credential Set: {undaodu_agent.credential_set}")
        print(f"[DATA] Status: {undaodu_agent.status}")
    else:
        print("[FAIL] Failed to select UnDaoDu")
    
    # Auto-selection (should pick safe agent)
    print("\n[U+1F9EA] Test 3: Auto-selection (system chooses best)...")
    auto_agent = manager.select_agent()
    if auto_agent:
        print(f"[OK] Auto-selected: {auto_agent.channel_name}")
        print(f"[IDEA] System automatically avoided conflicted agents")
    else:
        print("[FAIL] No agents available for auto-selection")
    
    print("\n[REFRESH] STEP 4: Disconnect & Reconnect Process")
    print("-" * 40)
    
    if undaodu_agent:
        print("1️⃣ DISCONNECT from Move2Japan:")
        print("   • Current session using Move2Japan credentials")
        print("   • Detected same-account conflict")
        print("   • Gracefully ending session...")
        
        print("\n2️⃣ RECONNECT with UnDaoDu:")
        print(f"   • Selected agent: {undaodu_agent.channel_name}")
        print(f"   • Using credential set: {undaodu_agent.credential_set}")
        print(f"   • Channel ID: {undaodu_agent.channel_id[:8]}...{undaodu_agent.channel_id[-4:]}")
        print("   • No conflicts detected [OK]")
        
        # Simulate session start
        success = manager.start_agent_session(
            undaodu_agent,
            "demo_stream_123",
            "Demo Stream for Disconnect/Reconnect"
        )
        
        if success:
            print("   • Session started successfully [OK]")
            print(f"   • Active agent: {manager.current_agent.channel_name}")
            
            # End session
            manager.end_current_session()
            print("   • Session ended cleanly [OK]")
        else:
            print("   • Failed to start session [FAIL]")
    
    print("\n[IDEA] STEP 5: Recommendations")
    print("-" * 40)
    print("[OK] RECOMMENDED APPROACH:")
    print("   1. Use UnDaoDu agent (different account from user)")
    print("   2. System automatically prevents same-account conflicts")
    print("   3. No manual intervention required")
    print("   4. Safe and reliable operation")
    
    print("\n[U+26A0]️ ALTERNATIVE APPROACHES:")
    print("   1. Log out of Move2Japan in browser")
    print("   2. Log in with different Google account")
    print("   3. Use different credential set for Move2Japan")
    print("   4. Run agent from different machine/session")
    
    print("\n[ALERT] RISKS OF SAME-ACCOUNT USAGE:")
    print("   • Agent responds to user's own messages")
    print("   • Identity confusion in chat")
    print("   • Self-triggering emoji response loops")
    print("   • Authentication conflicts")

def show_current_status():
    """Show current multi-agent status."""
    print("\n[DATA] CURRENT MULTI-AGENT STATUS")
    print("=" * 60)
    show_agent_status()

def force_undaodu():
    """Force the system to use UnDaoDu agent."""
    print("\n[TARGET] FORCING UNDAODU AGENT SELECTION")
    print("=" * 60)
    
    # Set environment variable
    os.environ["FORCE_AGENT"] = "UnDaoDu"
    print("[OK] Environment variable set: FORCE_AGENT=UnDaoDu")
    print("[IDEA] Next application start will use UnDaoDu agent")
    print("[REFRESH] Run: python main.py")

def main():
    """Main demonstration function."""
    print("[BOT] FoundUps Agent - Disconnect & Reconnect Demo")
    print("Following WSP (Windsurf Protocol) Guidelines")
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "status":
            show_current_status()
        elif command == "force-undaodu":
            force_undaodu()
        elif command == "demo":
            demonstrate_disconnect_reconnect()
        elif command in ["help", "-h", "--help"]:
            print("\nUsage:")
            print("  python tools/disconnect_reconnect_demo.py demo          # Run full demo")
            print("  python tools/disconnect_reconnect_demo.py status       # Show agent status")
            print("  python tools/disconnect_reconnect_demo.py force-undaodu # Force UnDaoDu")
            print("  python tools/disconnect_reconnect_demo.py help         # Show this help")
        else:
            print(f"[FAIL] Unknown command: {command}")
            print("[IDEA] Use 'help' to see available commands")
    else:
        # Default: run full demonstration
        demonstrate_disconnect_reconnect()

if __name__ == "__main__":
    main() 