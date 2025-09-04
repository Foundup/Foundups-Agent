#!/usr/bin/env python3
"""
Clean runner for YouTube DAE focusing on social media posting
"""
import sys
import os
import time

# Fix Windows encoding
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*80)
print("YOUTUBE DAE - SOCIAL MEDIA POSTING TEST")
print("Watching for: Stream End -> Cache Clear -> New Stream -> Social Post")
print("="*80)

# Import the DAE
from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
import asyncio

async def monitor_dae():
    """Monitor DAE with focus on social media posting"""
    print("\n[1] Creating DAE instance...")
    dae = AutoModeratorDAE()
    
    print("[2] Starting monitoring loop...")
    print("    - Waiting for stream end detection")
    print("    - Cache should clear automatically")
    print("    - When NEW stream starts -> Social media posts")
    print("-"*80)
    
    # Run the DAE
    await dae.run()

if __name__ == "__main__":
    try:
        asyncio.run(monitor_dae())
    except KeyboardInterrupt:
        print("\n[STOPPED] Monitoring stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()