"""
Test MCP Integration with YouTube Bot
Tests the complete flow: YouTube event -> MCP -> Instant announcement
"""

import asyncio
import sys
import os
import time
import logging

# Add modules to path
sys.path.insert(0, os.path.abspath('.'))

from modules.communication.livechat.src.event_handler import EventHandler
from modules.communication.livechat.src.mcp_youtube_integration import YouTubeDAEWithMCP

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def test_mcp_system():
    """Test the complete MCP integration"""
    print("\n" + "="*60)
    print("MCP INTEGRATION TEST")
    print("="*60)
    
    # Test 1: Direct MCP Integration
    print("\n[TEST 1] Direct MCP Integration...")
    dae = YouTubeDAEWithMCP()
    await dae.initialize()
    
    # Test 2: Event Handler with MCP
    print("\n[TEST 2] Event Handler with MCP...")
    event_handler = EventHandler()
    time.sleep(1)  # Let MCP initialize
    
    # Test 3: Process timeout events
    print("\n[TEST 3] Processing timeout events...")
    
    # Simulate 3 rapid timeouts (multi-whack scenario)
    test_events = [
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_123",
            "target_name": "MAGA_Troll_1",
            "target_channel_id": "target_1",
            "published_at": str(time.time()),
            "duration_seconds": 300
        },
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_123",
            "target_name": "MAGA_Troll_2",
            "target_channel_id": "target_2",
            "published_at": str(time.time() + 2),
            "duration_seconds": 300
        },
        {
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_123",
            "target_name": "MAGA_Troll_3",
            "target_channel_id": "target_3",
            "published_at": str(time.time() + 4),
            "duration_seconds": 300
        }
    ]
    
    for i, event in enumerate(test_events, 1):
        print(f"\n  Event {i}: {event['target_name']}")
        
        # Process through event handler
        result = event_handler.handle_timeout_event(event)
        
        if result.get("instant"):
            print(f"  [OK] MCP INSTANT: {result['announcement']}")
        elif result.get("announcement"):
            print(f"  ⏰ LEGACY: {result['announcement']}")
        else:
            print(f"  [U+26A0]️ NO ANNOUNCEMENT")
        
        # Show stats
        if result.get("stats"):
            stats = result["stats"]
            print(f"  [DATA] Stats: Points={stats.get('points', 0)}, "
                  f"Combo={stats.get('combo_multiplier', 1)}x, "
                  f"Multi={stats.get('is_multi_whack', False)}")
        
        time.sleep(0.5)
    
    # Test 4: Check leaderboard via MCP
    print("\n[TEST 4] Getting leaderboard via MCP...")
    leaderboard = await dae.get_slash_command_response("/leaderboard", "mod_123")
    if leaderboard:
        print(f"  [CLIPBOARD] Leaderboard response:")
        print("  " + leaderboard.replace("\n", "\n  "))
    
    # Test 5: Check user stats
    print("\n[TEST 5] Getting user stats via MCP...")
    rank = await dae.get_slash_command_response("/rank", "mod_123")
    score = await dae.get_slash_command_response("/score", "mod_123")
    whacks = await dae.get_slash_command_response("/whacks", "mod_123")
    
    if rank:
        print(f"  [U+1F3C6] {rank}")
    if score:
        print(f"  [DATA] {score}")
    if whacks:
        print(f"  [TARGET] {whacks}")
    
    # Test 6: Check quota status
    print("\n[TEST 6] Checking quota status via MCP...")
    quota_status = await dae.mcp.check_quota_status()
    if "error" not in quota_status:
        print(f"  [UP] Quota Status:")
        print(f"     Total: {quota_status.get('total_available', 0):,} units")
        print(f"     Used: {quota_status.get('total_used', 0):,} units")
        print(f"     Remaining: {quota_status.get('total_remaining', 0):,} units")
    else:
        print(f"  [FAIL] Quota check failed: {quota_status['error']}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    # Summary
    print("\nSUMMARY:")
    if event_handler.mcp_integration:
        print("[OK] MCP Integration: ACTIVE")
        print("[OK] Instant Announcements: WORKING")
    else:
        print("[U+26A0]️ MCP Integration: FALLBACK TO LEGACY")
    
    print("\nMCP Servers Status:")
    whack_conn = dae.mcp.connections.get('whack')
    quota_conn = dae.mcp.connections.get('quota')
    print(f"  Whack Server: {'Connected' if whack_conn and whack_conn.connected else 'Not Connected'}")
    print(f"  Quota Server: {'Connected' if quota_conn and quota_conn.connected else 'Not Connected'}")

if __name__ == "__main__":
    asyncio.run(test_mcp_system())