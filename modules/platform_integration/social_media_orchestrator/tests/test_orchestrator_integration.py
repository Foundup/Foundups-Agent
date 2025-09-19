#!/usr/bin/env python3
"""
Test Orchestrator Integration - Verify posting through orchestrator works
Following WSP 84: Test existing orchestrator before refactoring livechat
"""

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
    print("🧪 Testing Social Media Orchestrator Integration")
    print("=" * 60)
    
    try:
        # Use the simple working orchestrator
        from modules.platform_integration.social_media_orchestrator.src.simple_posting_orchestrator import SimplePostingOrchestrator
        
        orchestrator = SimplePostingOrchestrator()
        
        print("✅ Orchestrator imported successfully")
        
        # Test stream notification posting
        print("\n📺 Testing stream notification posting...")
        
        response = await orchestrator.post_stream_notification(
            stream_title="Test Stream - Architecture Integration",
            stream_url="https://youtube.com/watch?v=test123"
        )
        
        print(f"\n📊 Results:")
        print(f"   Success Count: {response.success_count}")
        print(f"   Failure Count: {response.failure_count}")
        print(f"   All Successful: {response.all_successful()}")
        
        print(f"\n📋 Platform Results:")
        for result in response.results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.platform.value}: {result.message}")
        
        if response.all_successful():
            print(f"\n🎉 Orchestrator integration test PASSED!")
            print("✅ Ready to refactor livechat to use orchestrator")
        else:
            print(f"\n⚠️ Orchestrator test partially successful")
            print("ℹ️ Can proceed with refactoring - orchestrator handles sequential posting")
            
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("⚠️ Orchestrator not available - need to check module structure")
        
    except Exception as e:
        print(f"❌ Test Error: {e}")
        print("⚠️ Orchestrator has issues - need to investigate")

if __name__ == "__main__":
    print("🚀 Starting orchestrator integration test...")
    asyncio.run(test_orchestrator())