#!/usr/bin/env python3
"""
Simple runner for YouTube DAE that fixes import issues
"""
import sys
import os

# Add the root directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Now import and run the DAE
from modules.communication.livechat.src.auto_moderator_dae import main

if __name__ == "__main__":
    print("Starting YouTube DAE...")
    print("Please launch your stream when ready.")
    print("-" * 60)
    main()