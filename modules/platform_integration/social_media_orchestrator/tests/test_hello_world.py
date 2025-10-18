#!/usr/bin/env python3
"""
Hello World Tests for Social Media Orchestrator
WSP Compliance: WSP 49, WSP 22

These are safe tests that run in dry-run mode by default.
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


import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Add module to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from social_media_orchestrator import (
    create_social_media_orchestrator,
    TwitterAdapter,
    LinkedInAdapter,
    AuthenticationError
)


async def test_twitter_hello_world():
    """Test Twitter hello world with dry run"""
    print("\n[BIRD] Testing Twitter Hello World (Dry Run)")
    print("-" * 40)
    
    try:
        # Create Twitter adapter
        twitter = TwitterAdapter()
        
        # Simulate authentication with dummy credentials
        dummy_creds = {
            'bearer_token': 'dummy_bearer_token_for_testing',
            'access_token': 'dummy_access_token',
            'access_token_secret': 'dummy_secret'
        }
        
        auth_success = await twitter.authenticate(dummy_creds)
        if auth_success:
            print("[OK] Twitter authentication simulation successful")
        else:
            print("[FAIL] Twitter authentication simulation failed")
            return False
            
        # Test hello world posting (dry run)
        result = await twitter.post(
            "[BOT] Hello World from FoundUps Social Media Orchestrator! #TestMode #FoundUps",
            {'dry_run': True, 'test_mode': True}
        )
        
        print(f"[OK] Twitter dry run post successful: {result}")
        
        # Test platform limits
        limits = twitter.get_platform_limits()
        print(f"[OK] Twitter limits: {limits['max_content_length']} chars, {limits['max_hashtags']} hashtags")
        
        # Test platform status
        status = await twitter.get_platform_status()
        print(f"[OK] Twitter status: {status['platform']} - {status['service_status']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Twitter hello world test failed: {e}")
        return False


async def test_linkedin_hello_world():
    """Test LinkedIn hello world with dry run"""
    print("\n[U+1F4BC] Testing LinkedIn Hello World (Dry Run)")
    print("-" * 40)
    
    try:
        # Create LinkedIn adapter
        linkedin = LinkedInAdapter()
        
        # Simulate authentication with dummy credentials
        dummy_creds = {
            'client_id': 'dummy_client_id_for_testing',
            'client_secret': 'dummy_client_secret',
            'access_token': 'dummy_access_token'
        }
        
        auth_success = await linkedin.authenticate(dummy_creds)
        if auth_success:
            print("[OK] LinkedIn authentication simulation successful")
        else:
            print("[FAIL] LinkedIn authentication simulation failed")
            return False
            
        # Test hello world posting (dry run)
        content = """[ROCKET] Hello World from FoundUps Social Media Orchestrator!

This is a professional update showcasing our autonomous social media management capabilities.

#FoundUps #SocialMediaAutomation #LinkedIn #Development #Innovation"""
        
        result = await linkedin.post(content, {'dry_run': True, 'test_mode': True})
        print(f"[OK] LinkedIn dry run post successful: {result}")
        
        # Test platform limits
        limits = linkedin.get_platform_limits()
        print(f"[OK] LinkedIn limits: {limits['max_content_length']} chars, {limits['max_hashtags']} hashtags")
        
        # Test platform status
        status = await linkedin.get_platform_status()
        print(f"[OK] LinkedIn status: {status['platform']} - {status['service_status']}")
        
        # Test content formatting
        test_content = "Professional update from our development team!"
        formatted = linkedin.format_content_for_linkedin(test_content, {
            'hashtags': ['#FoundUps', '#Development', '#Innovation'],
            'add_signature': True
        })
        print(f"[OK] LinkedIn formatted content: {len(formatted)} chars")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] LinkedIn hello world test failed: {e}")
        return False


async def test_orchestrator_hello_world():
    """Test full orchestrator hello world functionality"""
    print("\n[U+1F3AD] Testing Orchestrator Hello World (Dry Run)")
    print("-" * 40)
    
    try:
        # Create orchestrator
        config = {
            'logging_level': 'WARNING',  # Reduce noise
            'enable_scheduling': False   # Skip scheduling for hello world
        }
        
        orchestrator = create_social_media_orchestrator(config)
        print("[OK] Orchestrator created successfully")
        
        # Initialize
        init_success = await orchestrator.initialize()
        if not init_success:
            print("[FAIL] Orchestrator initialization failed")
            return False
            
        print("[OK] Orchestrator initialized successfully")
        
        # Test platform hello world tests
        platforms = orchestrator.list_supported_platforms()
        print(f"[OK] Supported platforms: {platforms}")
        
        results = {}
        for platform in platforms:
            print(f"\n[NOTE] Testing {platform.title()} hello world...")
            result = await orchestrator.test_platform_hello_world(platform, dry_run=True)
            results[platform] = result
            
            if result['success']:
                print(f"[OK] {platform.title()} hello world: SUCCESS")
                print(f"   Content: {result['content'][:50]}...")
                print(f"   Post ID: {result['post_id']}")
            else:
                print(f"[FAIL] {platform.title()} hello world: FAILED")
                print(f"   Error: {result.get('error')}")
                
        # Test cross-platform posting (dry run)
        print(f"\n[U+1F310] Testing cross-platform posting...")
        
        # Simulate authentication for both platforms
        twitter_creds = {'bearer_token': 'dummy_token'}
        linkedin_creds = {
            'client_id': 'dummy_id',
            'client_secret': 'dummy_secret', 
            'access_token': 'dummy_token'
        }
        
        await orchestrator.authenticate_platform('twitter', twitter_creds)
        await orchestrator.authenticate_platform('linkedin', linkedin_creds)
        
        # Post to both platforms (dry run via test_mode)
        post_result = await orchestrator.post_content(
            content="[TARGET] Cross-platform hello world from FoundUps!",
            platforms=['twitter', 'linkedin'],
            options={
                'twitter': {'test_mode': True, 'hashtags': ['#FoundUps']},
                'linkedin': {'test_mode': True, 'hashtags': ['#FoundUps', '#Development']}
            }
        )
        
        # Check results
        all_success = True
        for platform, result in post_result.items():
            if result['success']:
                print(f"[OK] {platform.title()} cross-platform post: SUCCESS")
            else:
                print(f"[FAIL] {platform.title()} cross-platform post: FAILED - {result['error']}")
                all_success = False
                
        if all_success:
            print("\n[CELEBRATE] All orchestrator hello world tests passed!")
            
        return all_success
        
    except Exception as e:
        print(f"[FAIL] Orchestrator hello world test failed: {e}")
        return False


def main():
    """Main test runner"""
    print("[ROCKET] Social Media Orchestrator Hello World Tests")
    print("=" * 60)
    print("Running safe dry-run tests (no actual API calls)")
    print("WSP 49 Compliance Verification")
    print("=" * 60)
    
    # Suppress logs during testing
    logging.getLogger().setLevel(logging.CRITICAL)
    
    # Track test results
    test_results = {}
    
    try:
        # Setup event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run individual platform tests
        test_results['twitter'] = loop.run_until_complete(test_twitter_hello_world())
        test_results['linkedin'] = loop.run_until_complete(test_linkedin_hello_world())
        test_results['orchestrator'] = loop.run_until_complete(test_orchestrator_hello_world())
        
        # Summary
        print("\n[DATA] Test Summary")
        print("=" * 30)
        
        all_passed = True
        for test_name, passed in test_results.items():
            status = "[OK] PASSED" if passed else "[FAIL] FAILED"
            print(f"{test_name.title():15}: {status}")
            if not passed:
                all_passed = False
                
        if all_passed:
            print("\n[TARGET] ALL HELLO WORLD TESTS PASSED!")
            print("Social Media Orchestrator is ready for use")
            print("WSP 49 Compliance: [OK] VERIFIED")
            return 0
        else:
            print("\n[ALERT] SOME TESTS FAILED!")
            print("Check the output above for details")
            print("WSP 49 Compliance: [FAIL] NEEDS ATTENTION") 
            return 1
            
    except Exception as e:
        print(f"\n[U+1F4A5] Test execution error: {e}")
        print("WSP 49 Compliance: [FAIL] FAILED")
        return 1
    finally:
        if 'loop' in locals():
            loop.close()


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)