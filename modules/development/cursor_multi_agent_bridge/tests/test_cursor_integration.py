#!/usr/bin/env python3
"""
Quick test script to verify WRE WebSocket server is running
and ready for Cursor integration.
"""

import asyncio
import websockets
import json
import sys

async def test_connection():
    """Test WebSocket connection to WRE server."""
    
    print("Testing WRE WebSocket Connection...")
    print("Connecting to ws://localhost:8765")
    
    try:
        async with websockets.connect("ws://localhost:8765") as websocket:
            print("SUCCESS: Connected successfully!")
            
            # Test get_status message
            print("Sending status request...")
            await websocket.send(json.dumps({
                "type": "get_status"
            }))
            
            # Receive response
            response = await websocket.recv()
            data = json.loads(response)
            
            print("Received response:")
            print(f"   Type: {data.get('type')}")
            print(f"   Active: {data.get('data', {}).get('active')}")
            print(f"   Quantum State: {data.get('data', {}).get('quantum_state')}")
            print(f"   Communication: {data.get('data', {}).get('communication_active')}")
            
            # Test ping
            print("Sending ping...")
            await websocket.send(json.dumps({"type": "ping"}))
            
            pong = await websocket.recv()
            pong_data = json.loads(pong)
            if pong_data.get('type') == 'pong':
                print("Received pong - WebSocket working!")
            
            print("\nSUCCESS: WRE WebSocket server is ready for Cursor!")
            print("You can now use 'Run WRE' in Cursor")
            
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        print("\nTroubleshooting:")
        print("   1. Make sure WRE server is running:")
        print("      cd modules/wre_core && python -m src.main --websocket")
        print("   2. Check if port 8765 is available")
        print("   3. Verify no firewall blocking localhost:8765")
        return False
    
    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)