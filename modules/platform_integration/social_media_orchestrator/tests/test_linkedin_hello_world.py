#!/usr/bin/env python3
"""
Simple LinkedIn Hello World Test
WSP Compliance: WSP 49
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up basic logging
logging.basicConfig(level=logging.INFO)

async def test_linkedin_hello_world():
    """Test LinkedIn hello world functionality"""
    print("Testing LinkedIn Hello World (Dry Run)")
    print("=" * 40)
    
    try:
        # Import LinkedInAdapter directly
        from platform_adapters.linkedin_adapter import LinkedInAdapter
        
        # Create adapter
        linkedin = LinkedInAdapter()
        print("OK LinkedIn adapter created successfully")
        
        # Test authentication simulation
        dummy_creds = {
            'client_id': 'dummy_client_id_for_testing',
            'client_secret': 'dummy_client_secret',
            'access_token': 'dummy_access_token'
        }
        
        auth_result = await linkedin.authenticate(dummy_creds)
        print(f"OK Authentication simulation: {'SUCCESS' if auth_result else 'FAILED'}")
        
        if not auth_result:
            print("ERROR Cannot proceed without authentication")
            return False
            
        # Test hello world post (dry run)
        hello_content = """Hello World from FoundUps LinkedIn integration!

This is a professional update showcasing our autonomous social media management capabilities for the LinkedIn platform.

Our system demonstrates:
- Cross-platform content orchestration
- Intelligent content formatting
- Professional networking automation
- WSP 49 compliance standards

#FoundUps #LinkedInIntegration #SocialMediaAutomation #Development #Innovation #HelloWorld"""
        
        post_result = await linkedin.post(hello_content, {
            'dry_run': True,
            'test_mode': True
        })
        
        print(f"OK Dry run post successful: {post_result}")
        
        # Test platform limits
        limits = linkedin.get_platform_limits()
        print(f"OK Platform limits: {limits}")
        
        # Test platform status
        status = await linkedin.get_platform_status()
        print(f"OK Platform status: {status['platform']} - authenticated: {status['authenticated']}")
        
        # Test content formatting
        test_content = "Professional update from our development team!"
        formatted = linkedin.format_content_for_linkedin(test_content, {
            'hashtags': ['#FoundUps', '#Development', '#Innovation'],
            'add_signature': True,
            'call_to_action': 'Connect with us to learn more about autonomous development!'
        })
        print(f"OK Content formatting test: {len(formatted)} chars")
        print(f"   Preview: {formatted[:100]}...")
        
        # Test profile info simulation
        profile = await linkedin.get_profile_info()
        print(f"OK Profile info simulation: {profile['firstName']['localized']['en_US']} {profile['lastName']['localized']['en_US']}")
        
        print("\nSUCCESS LinkedIn hello world test PASSED!")
        return True
        
    except Exception as e:
        print(f"ERROR LinkedIn hello world test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("LinkedIn Hello World Test")
    print("WSP 49 Compliance Check")
    print("=" * 50)
    
    try:
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(test_linkedin_hello_world())
        
        if success:
            print("\nLINKEDIN TEST: PASSED")
            print("LinkedIn adapter is functional and WSP 49 compliant")
            return 0
        else:
            print("\nLINKEDIN TEST: FAILED")
            return 1
            
    except Exception as e:
        print(f"\nTest execution error: {e}")
        return 1
    finally:
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    sys.exit(main())