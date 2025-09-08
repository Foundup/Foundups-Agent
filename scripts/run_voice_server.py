#!/usr/bin/env python3
"""
Voice Server Launcher - Easy access to Social Media DAE Voice Command Processor

WSP 85 compliant wrapper to run the voice command processor from outside modules.
This provides easy access to the complete voice command system.

Usage: python scripts/run_voice_server.py
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import and run the existing voice command processor
from modules.ai_intelligence.social_media_dae.src.voice_command_processor import main
import asyncio

if __name__ == "__main__":
    print("🎤 Starting Social Media DAE Voice Command Processor...")
    print("🎯 Full functionality: iPhone commands + Social Media DAE integration")
    print("📱 iPhone endpoint: http://localhost:5012/voice-command")
    print("🌐 Test interface: http://localhost:5012/test")
    print("📊 Status endpoint: http://localhost:5012/status")
    print()
    
    asyncio.run(main())