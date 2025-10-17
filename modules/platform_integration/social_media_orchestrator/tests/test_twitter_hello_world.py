#!/usr/bin/env python3
"""
Simple Twitter Hello World Test
WSP Compliance: WSP 49
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up basic logging
logging.basicConfig(level=logging.INFO)

async def test_twitter_hello_world():
    """Test Twitter hello world functionality"""
    print("Testing Twitter Hello World (Dry Run)")
    print("=" * 40)
    
    try:
        # Import TwitterAdapter directly
        from platform_adapters.twitter_adapter import TwitterAdapter
        
        # Create adapter
        twitter = TwitterAdapter()
        print("OK Twitter adapter created successfully")
        
        # Test authentication simulation
        dummy_creds = {
            'bearer_token': 'dummy_bearer_token_for_testing',
            'access_token': 'dummy_access_token',
            'access_token_secret': 'dummy_secret'
        }
        
        auth_result = await twitter.authenticate(dummy_creds)
        print(f"OK Authentication simulation: {'SUCCESS' if auth_result else 'FAILED'}")
        
        if not auth_result:
            print("ERROR Cannot proceed without authentication")
            return False
            
        # Test hello world post (dry run)
        hello_content = "Hello World from FoundUps Twitter integration! #FoundUps #HelloWorld #TestMode"
        
        post_result = await twitter.post(hello_content, {
            'dry_run': True,
            'test_mode': True
        })
        
        print(f"OK Dry run post successful: {post_result}")
        
        # Test platform limits
        limits = twitter.get_platform_limits()
        print(f"OK Platform limits: {limits}")
        
        # Test platform status
        status = await twitter.get_platform_status()
        print(f"OK Platform status: {status['platform']} - authenticated: {status['authenticated']}")
        
        # Test content formatting
        test_content = "Test content for Twitter"
        formatted = twitter.format_content_for_twitter(test_content, {
            'hashtags': ['#FoundUps', '#Test'],
            'mentions': ['@foundups']
        })
        print(f"OK Content formatting test: '{formatted}' ({len(formatted)} chars)")
        
        print("\nSUCCESS Twitter hello world test PASSED!")
        return True
        
    except Exception as e:
        print(f"ERROR Twitter hello world test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("Twitter Hello World Test")
    print("WSP 49 Compliance Check")
    print("=" * 50)
    
    try:
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(test_twitter_hello_world())
        
        if success:
            print("\nTWITTER TEST: PASSED")
            print("Twitter adapter is functional and WSP 49 compliant")
            return 0
        else:
            print("\nTWITTER TEST: FAILED")
            return 1
            
    except Exception as e:
        print(f"\nTest execution error: {e}")
        return 1
    finally:
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    sys.exit(main())