#!/usr/bin/env python3
"""
LinkedIn Unified Module Test
WSP Compliance: WSP 49
"""

import sys
import asyncio
import logging
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

# Set up basic logging
logging.basicConfig(level=logging.WARNING)

async def test_linkedin_unified():
    """Test LinkedIn unified module functionality"""
    print("Testing LinkedIn Unified Module")
    print("=" * 40)
    
    try:
        # Import unified LinkedIn manager
        from linkedin_manager import LinkedInManager, create_linkedin_manager
        
        # Test factory function
        config = {
            'logging_level': 'WARNING',
            'enable_scheduling': True
        }
        
        auth_creds = {
            'client_id': 'test_client_id',
            'client_secret': 'test_client_secret',
            'access_token': 'test_access_token'
        }
        
        linkedin = create_linkedin_manager(config, auth_creds)
        print("OK LinkedIn manager created successfully")
        
        # Test authentication
        auth_result = await linkedin.authenticate(auth_creds)
        print(f"OK Authentication test: {'SUCCESS' if auth_result else 'FAILED'}")
        
        if not auth_result:
            print("ERROR Cannot proceed without authentication")
            return False
            
        # Test OAuth URL generation
        oauth_url = linkedin.get_oauth_url(
            redirect_uri="http://localhost:8080/callback",
            scope="w_member_social r_liteprofile"
        )
        print(f"OK OAuth URL generation: {len(oauth_url)} chars")
        
        # Test content formatting
        test_content = "Professional update from our development team!"
        formatted = linkedin.format_content_for_linkedin(test_content, {
            'hashtags': ['#FoundUps', '#Development', '#Innovation'],
            'call_to_action': 'Connect with us to learn more!'
        })
        print(f"OK Content formatting: {len(formatted)} chars")
        
        # Test post creation (simulated)
        post_id = await linkedin.create_post(
            "Test professional post for LinkedIn integration",
            options={
                'hashtags': ['#Testing', '#LinkedIn'],
                'visibility': 'PUBLIC'
            }
        )
        print(f"OK Post creation simulation: {post_id}")
        
        # Test profile info
        profile = await linkedin.get_profile_info()
        print(f"OK Profile info: {profile['firstName']['localized']['en_US']} {profile['lastName']['localized']['en_US']}")
        
        # Test connections
        connections = await linkedin.get_connections(limit=5)
        print(f"OK Connections simulation: {len(connections)} connections")
        
        # Test analytics
        analytics = await linkedin.get_post_analytics(post_id)
        print(f"OK Analytics simulation: {analytics['views']} views, {analytics['engagement_rate']:.1%} engagement")
        
        # Test status
        status = linkedin.get_status()
        print(f"OK Status check: authenticated={status['authenticated']}")
        
        print("\nSUCCESS LinkedIn unified module test PASSED!")
        return True
        
    except Exception as e:
        print(f"ERROR LinkedIn unified test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main test function"""
    print("LinkedIn Unified Module Test")
    print("WSP 49 Compliance Check")
    print("=" * 50)
    
    try:
        # Run the async test
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(test_linkedin_unified())
        
        if success:
            print("\nLINKEDIN UNIFIED TEST: PASSED")
            print("LinkedIn unified module is functional and WSP 49 compliant")
            return 0
        else:
            print("\nLINKEDIN UNIFIED TEST: FAILED")
            return 1
            
    except Exception as e:
        print(f"\nTest execution error: {e}")
        return 1
    finally:
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    sys.exit(main())