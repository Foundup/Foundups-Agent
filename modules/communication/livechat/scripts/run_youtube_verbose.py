#!/usr/bin/env python3
"""
Verbose runner for YouTube DAE with detailed logging
"""
import sys
import os
import logging

# Setup VERBOSE logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment for verbose output
os.environ['DEBUG'] = '1'
os.environ['VERBOSE'] = '1'

print("="*80)
print("YOUTUBE DAE - VERBOSE MODE")
print("Monitoring for stream end detection and system behavior")
print("="*80)

# Now import and run the DAE
from modules.communication.livechat.src.auto_moderator_dae import main

if __name__ == "__main__":
    try:
        print("\n[STARTUP] Initializing YouTube DAE...")
        main()
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopped by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()