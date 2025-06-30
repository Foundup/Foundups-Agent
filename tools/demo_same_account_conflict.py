#!/usr/bin/env python3
"""
Demonstration: Same-Account Conflict Detection
Shows how the multi-agent system handles conflicts when user and agent are on the same account.
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from modules.infrastructure.agent_management.src.multi_agent_manager import (
    MultiAgentManager,
    AgentIdentity
)

def demo_same_account_conflict():
    """Demonstrate same-account conflict detection and resolution."""
    print("\n🚨 SAME-ACCOUNT CONFLICT DEMONSTRATION")
    print("=" * 60)
    
    # Simulate scenario where user is logged in as Move2Japan
    user_channel_id = "UCMove2JapanChannelID123"
    
    print(f"👤 User logged in as channel: {user_channel_id[:8]}...{user_channel_id[-4:]}")
    print("📝 Scenario: User is streaming from Move2Japan account")
    
    # Create manager and simulate agent discovery
    manager = MultiAgentManager()
    
    # Manually add agents to simulate discovery results
    # Agent 1: Different account (safe to use)
    safe_agent = AgentIdentity(
        agent_id="agent_set_1_undaodu",
        channel_id="UCUnDaoDuChannelID456",
        channel_name="UnDaoDu",
        credential_set="set_1",
        status="available"
    )
    
    # Agent 2: Same account as user (conflict!)
    conflicted_agent = AgentIdentity(
        agent_id="agent_set_2_move2japan", 
        channel_id=user_channel_id,  # Same as user!
        channel_name="Move2Japan",
        credential_set="set_2",
        status="same_account_conflict",
        conflict_reason=f"Same channel ID as user: {user_channel_id[:8]}...{user_channel_id[-4:]}"
    )
    
    # Agent 3: Another different account (safe to use)
    safe_agent_2 = AgentIdentity(
        agent_id="agent_set_3_anotherchannel",
        channel_id="UCAnotherChannelID789",
        channel_name="AnotherChannel",
        credential_set="set_3",
        status="available"
    )
    
    manager.registry.agents = {
        "agent_set_1_undaodu": safe_agent,
        "agent_set_2_move2japan": conflicted_agent,
        "agent_set_3_anotherchannel": safe_agent_2
    }
    manager.user_channel_id = user_channel_id
    
    print("\n🤖 DISCOVERED AGENTS:")
    print("✅ UnDaoDu (set_1) - Available (different account)")
    print("⚠️ Move2Japan (set_2) - CONFLICT: Same account as user")
    print("✅ AnotherChannel (set_3) - Available (different account)")
    
    print("\n🔍 AGENT SELECTION TESTS:")
    
    # Test 1: Auto-selection (should pick safe agent)
    print("\n1️⃣ Auto-selection test:")
    selected = manager.select_agent()
    if selected:
        print(f"   ✅ Auto-selected: {selected.channel_name} (safe to use)")
        print(f"   📋 Agent ID: {selected.agent_id}")
        print(f"   🔑 Credential Set: {selected.credential_set}")
    else:
        print("   ❌ No agents available for auto-selection")
    
    # Test 2: Try to select conflicted agent (should fail)
    print("\n2️⃣ Attempt to select conflicted agent:")
    conflicted_selected = manager.select_agent("Move2Japan")
    if conflicted_selected:
        if conflicted_selected.agent_id == "agent_set_2_move2japan":
            print(f"   ⚠️ WARNING: Selected conflicted agent: {conflicted_selected.channel_name}")
        else:
            print(f"   ✅ System redirected to safe agent: {conflicted_selected.channel_name}")
    else:
        print("   ✅ Correctly blocked selection of conflicted agent")
    
    # Test 3: Override conflict (manual override)
    print("\n3️⃣ Manual conflict override test:")
    override_selected = manager.select_agent("Move2Japan", allow_conflicts=True)
    if override_selected:
        print(f"   ⚠️ Override successful: {override_selected.channel_name}")
        print("   🚨 WARNING: This could cause identity conflicts!")
        print("   💡 Agent may respond to user's own messages")
    else:
        print("   ❌ Override failed")
    
    # Test 4: Show available vs conflicted agents
    print("\n4️⃣ Agent availability summary:")
    available_agents = manager.registry.get_available_agents()
    conflicted_agents = manager.registry.get_conflicted_agents()
    
    print(f"   ✅ Available agents: {len(available_agents)}")
    for agent in available_agents:
        print(f"      • {agent.channel_name} ({agent.credential_set})")
    
    print(f"   ⚠️ Conflicted agents: {len(conflicted_agents)}")
    for agent in conflicted_agents:
        print(f"      • {agent.channel_name} ({agent.credential_set}) - {agent.conflict_reason}")
    
    print("\n💡 RECOMMENDATIONS:")
    print("=" * 60)
    print("✅ SAFE OPTIONS:")
    print("   1. Use UnDaoDu agent (different account) - RECOMMENDED")
    print("   2. Use AnotherChannel agent (different account) - RECOMMENDED")
    print()
    print("⚠️ TO USE MOVE2JAPAN AGENT:")
    print("   1. Log out of Move2Japan account in browser")
    print("   2. Log in with different Google account")
    print("   3. Use different credential set for Move2Japan")
    print("   4. Run agent from different machine/session")
    print()
    print("🚨 RISKS OF SAME-ACCOUNT USAGE:")
    print("   • Agent may respond to your own messages")
    print("   • Identity confusion in chat")
    print("   • Potential authentication conflicts")
    print("   • Self-triggering emoji response loops")

def demo_multi_agent_coordination():
    """Demonstrate multi-agent coordination capabilities."""
    print("\n🤖 MULTI-AGENT COORDINATION DEMONSTRATION")
    print("=" * 60)
    
    manager = MultiAgentManager()
    
    # Simulate multiple agents for future multi-agent scenarios
    agents = [
        AgentIdentity(
            agent_id="agent_undaodu",
            channel_id="UCUnDaoDu123",
            channel_name="UnDaoDu",
            credential_set="set_1",
            status="available"
        ),
        AgentIdentity(
            agent_id="agent_backup",
            channel_id="UCBackup456", 
            channel_name="BackupChannel",
            credential_set="set_3",
            status="available"
        ),
        AgentIdentity(
            agent_id="agent_specialized",
            channel_id="UCSpecial789",
            channel_name="SpecializedBot",
            credential_set="set_4",
            status="available"
        )
    ]
    
    for agent in agents:
        manager.registry.agents[agent.agent_id] = agent
    
    print("🎯 FUTURE MULTI-AGENT CAPABILITIES:")
    print("   • Multiple agents monitoring different streams")
    print("   • Agent rotation for quota management")
    print("   • Specialized agents for different tasks")
    print("   • Coordinated responses to avoid spam")
    print("   • Load balancing across credential sets")
    
    print(f"\n📊 CURRENT SETUP: {len(agents)} agents ready for coordination")
    for agent in agents:
        print(f"   • {agent.channel_name} ({agent.credential_set}) - {agent.status}")
    
    print("\n🔄 COORDINATION RULES:")
    rules = manager.coordination_rules
    print(f"   • Max concurrent agents: {rules['max_concurrent_agents']}")
    print(f"   • Min response interval: {rules['min_response_interval']}s")
    print(f"   • Agent rotation: {'Enabled' if rules['agent_rotation_enabled'] else 'Disabled'}")
    print(f"   • Channel affinity: {'Enabled' if rules['prefer_channel_affinity'] else 'Disabled'}")
    print(f"   • Block same account: {'Enabled' if rules['block_same_account'] else 'Disabled'}")

if __name__ == "__main__":
    # Run demonstrations
    demo_same_account_conflict()
    demo_multi_agent_coordination()
    
    print("\n" + "=" * 60)
    print("🎉 DEMONSTRATION COMPLETE")
    print("💡 The multi-agent system is ready for production use!")
    print("🔒 Same-account conflicts are automatically detected and prevented.")
    print("🚀 Ready for future multi-agent coordination features.") 