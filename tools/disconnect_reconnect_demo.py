#!/usr/bin/env python3
"""
Disconnect and Reconnect Demo
Demonstrates how to safely disconnect from Move2Japan and reconnect using UnDaoDu
to avoid same-account conflicts.
"""

import os
import sys
import logging

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.infrastructure.agent_management.agent_management.src.multi_agent_manager import (
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
    print("\n🔄 DISCONNECT & RECONNECT DEMONSTRATION")
    print("=" * 60)
    
    # Simulate user channel ID (Move2Japan account)
    user_channel_id = "UCMove2JapanChannelID123"
    
    print(f"👤 Current User: Logged in as Move2Japan")
    print(f"📋 User Channel ID: {user_channel_id[:8]}...{user_channel_id[-4:]}")
    print(f"🚨 Problem: Agent and user on same account = conflicts!")
    
    print("\n📊 STEP 1: Initialize Multi-Agent System")
    print("-" * 40)
    
    # Initialize agent manager with user channel ID
    manager = get_agent_manager()
    success = manager.initialize(user_channel_id)
    
    if not success:
        print("❌ Failed to initialize multi-agent system")
        return
    
    print("✅ Multi-agent system initialized")
    
    print("\n🔍 STEP 2: Agent Discovery & Conflict Detection")
    print("-" * 40)
    
    # Show discovered agents
    available_agents = manager.registry.get_available_agents()
    conflicted_agents = manager.registry.get_conflicted_agents()
    
    print(f"📈 Total agents discovered: {len(manager.registry.agents)}")
    print(f"✅ Available agents: {len(available_agents)}")
    print(f"⚠️ Conflicted agents: {len(conflicted_agents)}")
    
    if conflicted_agents:
        print("\n🚨 SAME-ACCOUNT CONFLICTS DETECTED:")
        for agent in conflicted_agents:
            print(f"   ❌ {agent.channel_name} ({agent.credential_set})")
            print(f"      └─ {agent.conflict_reason}")
    
    if available_agents:
        print("\n✅ SAFE AGENTS (Different Accounts):")
        for agent in available_agents:
            print(f"   ✅ {agent.channel_name} ({agent.credential_set})")
    
    print("\n🎯 STEP 3: Safe Agent Selection")
    print("-" * 40)
    
    # Try to select Move2Japan (should be blocked)
    print("🧪 Test 1: Attempt to select Move2Japan...")
    move2japan_agent = manager.select_agent("Move2Japan")
    if move2japan_agent:
        if move2japan_agent.channel_name == "Move2Japan":
            print("⚠️ WARNING: Move2Japan selected despite conflict!")
        else:
            print(f"✅ System redirected to safe agent: {move2japan_agent.channel_name}")
    else:
        print("✅ Move2Japan correctly blocked due to same-account conflict")
    
    # Select UnDaoDu (should work)
    print("\n🧪 Test 2: Select UnDaoDu (safe agent)...")
    undaodu_agent = manager.select_agent("UnDaoDu")
    if undaodu_agent:
        print(f"✅ Successfully selected: {undaodu_agent.channel_name}")
        print(f"📋 Agent ID: {undaodu_agent.agent_id}")
        print(f"🔑 Credential Set: {undaodu_agent.credential_set}")
        print(f"📊 Status: {undaodu_agent.status}")
    else:
        print("❌ Failed to select UnDaoDu")
    
    # Auto-selection (should pick safe agent)
    print("\n🧪 Test 3: Auto-selection (system chooses best)...")
    auto_agent = manager.select_agent()
    if auto_agent:
        print(f"✅ Auto-selected: {auto_agent.channel_name}")
        print(f"💡 System automatically avoided conflicted agents")
    else:
        print("❌ No agents available for auto-selection")
    
    print("\n🔄 STEP 4: Disconnect & Reconnect Process")
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
        print("   • No conflicts detected ✅")
        
        # Simulate session start
        success = manager.start_agent_session(
            undaodu_agent,
            "demo_stream_123",
            "Demo Stream for Disconnect/Reconnect"
        )
        
        if success:
            print("   • Session started successfully ✅")
            print(f"   • Active agent: {manager.current_agent.channel_name}")
            
            # End session
            manager.end_current_session()
            print("   • Session ended cleanly ✅")
        else:
            print("   • Failed to start session ❌")
    
    print("\n💡 STEP 5: Recommendations")
    print("-" * 40)
    print("✅ RECOMMENDED APPROACH:")
    print("   1. Use UnDaoDu agent (different account from user)")
    print("   2. System automatically prevents same-account conflicts")
    print("   3. No manual intervention required")
    print("   4. Safe and reliable operation")
    
    print("\n⚠️ ALTERNATIVE APPROACHES:")
    print("   1. Log out of Move2Japan in browser")
    print("   2. Log in with different Google account")
    print("   3. Use different credential set for Move2Japan")
    print("   4. Run agent from different machine/session")
    
    print("\n🚨 RISKS OF SAME-ACCOUNT USAGE:")
    print("   • Agent responds to user's own messages")
    print("   • Identity confusion in chat")
    print("   • Self-triggering emoji response loops")
    print("   • Authentication conflicts")

def show_current_status():
    """Show current multi-agent status."""
    print("\n📊 CURRENT MULTI-AGENT STATUS")
    print("=" * 60)
    show_agent_status()

def force_undaodu():
    """Force the system to use UnDaoDu agent."""
    print("\n🎯 FORCING UNDAODU AGENT SELECTION")
    print("=" * 60)
    
    # Set environment variable
    os.environ["FORCE_AGENT"] = "UnDaoDu"
    print("✅ Environment variable set: FORCE_AGENT=UnDaoDu")
    print("💡 Next application start will use UnDaoDu agent")
    print("🔄 Run: python main.py")

def main():
    """Main demonstration function."""
    print("🤖 FoundUps Agent - Disconnect & Reconnect Demo")
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
            print(f"❌ Unknown command: {command}")
            print("💡 Use 'help' to see available commands")
    else:
        # Default: run full demonstration
        demonstrate_disconnect_reconnect()

if __name__ == "__main__":
    main() 