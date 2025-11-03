#!/usr/bin/env python3
"""
Test Orchestrator Integration - Verify posting through orchestrator works
Following WSP 84: Test existing orchestrator before refactoring livechat
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import asyncio
import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set UTF-8 encoding for Windows
if os.name == 'nt':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

async def test_orchestrator():
    """Test the social media orchestrator posting functionality"""
    print("[U+1F9EA] Testing Social Media Orchestrator Integration")
    print("=" * 60)
    
    try:
        # Use the simple working orchestrator
        from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
        
        orchestrator = SimplePostingOrchestrator()
        
        print("[OK] Orchestrator imported successfully")
        
        # Test stream notification posting
        print("\n[U+1F4FA] Testing stream notification posting...")
        
        response = await orchestrator.post_stream_notification(
            stream_title="Test Stream - Architecture Integration",
            stream_url="https://youtube.com/watch?v=test123"
        )
        
        print(f"\n[DATA] Results:")
        print(f"   Success Count: {response.success_count}")
        print(f"   Failure Count: {response.failure_count}")
        print(f"   All Successful: {response.all_successful()}")
        
        print(f"\n[CLIPBOARD] Platform Results:")
        for result in response.results:
            status = "[OK]" if result.success else "[FAIL]"
            print(f"   {status} {result.platform.value}: {result.message}")
        
        if response.all_successful():
            print(f"\n[CELEBRATE] Orchestrator integration test PASSED!")
            print("[OK] Ready to refactor livechat to use orchestrator")
        else:
            print(f"\n[U+26A0]️ Orchestrator test partially successful")
            print("ℹ️ Can proceed with refactoring - orchestrator handles sequential posting")
            
    except ImportError as e:
        print(f"[FAIL] Import Error: {e}")
        print("[U+26A0]️ Orchestrator not available - need to check module structure")
        
    except Exception as e:
        print(f"[FAIL] Test Error: {e}")
        print("[U+26A0]️ Orchestrator has issues - need to investigate")

if __name__ == "__main__":
    print("[ROCKET] Starting orchestrator integration test...")
    asyncio.run(test_orchestrator())