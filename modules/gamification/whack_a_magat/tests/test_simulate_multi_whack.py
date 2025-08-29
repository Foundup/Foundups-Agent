"""
Simulate multi-whack for testing since YouTube API doesn't send all events
"""

import asyncio
import time
from datetime import datetime

async def simulate_multi_whack():
    """Simulate 4 rapid timeouts to test multi-whack detection"""
    
    from modules.communication.livechat.src.event_handler import EventHandler
    from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutManager
    
    # Create event handler
    event_handler = EventHandler()
    
    # Give MCP time to initialize
    await asyncio.sleep(2)
    
    print("=" * 60)
    print("SIMULATING 4 RAPID TIMEOUTS")
    print("=" * 60)
    
    # Create 4 timeout events with timestamps 2 seconds apart
    base_time = datetime.now()
    targets = ["MAGAT1", "MAGAT2", "MAGAT3", "MAGAT4"]
    
    for i, target in enumerate(targets):
        # Create event with proper timestamp
        event_time = base_time.timestamp() + (i * 2)  # 2 seconds apart
        event_timestamp = datetime.fromtimestamp(event_time).isoformat() + "Z"
        
        event = {
            "type": "timeout_event",
            "target_name": target,
            "target_channel_id": f"channel_{i}",
            "moderator_name": "UnDaoDu",
            "moderator_id": "mod_123",
            "duration_seconds": 300,
            "published_at": event_timestamp,
            "deleted_text": f"spam message {i}"
        }
        
        print(f"\n--- Timeout #{i+1} ---")
        print(f"Target: {target}")
        print(f"Timestamp: {event_timestamp}")
        
        # Process through event handler
        result = event_handler.handle_timeout_event(event)
        
        if result.get("announcement"):
            print(f"✅ ANNOUNCEMENT: {result['announcement']}")
        else:
            print(f"⏳ Queued (no announcement yet)")
        
        # Small delay to simulate processing
        await asyncio.sleep(0.1)
    
    # Check for any pending batched announcements
    print("\n--- Checking for batched announcements ---")
    final = event_handler.force_flush()
    if final:
        print(f"📢 BATCHED: {final}")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    
    # Cleanup
    event_handler.cleanup()

if __name__ == "__main__":
    asyncio.run(simulate_multi_whack())