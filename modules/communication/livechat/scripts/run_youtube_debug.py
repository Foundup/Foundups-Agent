#!/usr/bin/env python3
"""
Debug runner for YouTube DAE with more logging
"""
import sys
import os
import logging

# Setup logging FIRST
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== YouTube DAE Debug Runner ===")
print("1. Import path set")

# Now import and run the DAE
try:
    print("2. Importing auto_moderator_dae...")
    from modules.communication.livechat.src.auto_moderator_dae import AutoModeratorDAE
    print("3. Import successful")
    
    print("4. Importing asyncio...")
    import asyncio
    print("5. Asyncio imported")
    
    print("6. Creating DAE instance...")
    dae = AutoModeratorDAE()
    print("7. DAE instance created")
    
    print("8. Starting async run...")
    asyncio.run(dae.run())
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()