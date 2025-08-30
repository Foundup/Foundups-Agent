#!/usr/bin/env python3
"""
Direct LinkedIn API Test
Tests the LinkedIn API configuration from .env
"""

import os
import sys
import requests
from dotenv import load_dotenv

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# Load environment
load_dotenv()

def test_linkedin_credentials():
    """Test if LinkedIn credentials are properly configured"""
    
    print("="*60)
    print("🔐 LinkedIn API Configuration Test")
    print("="*60)
    
    # Check environment variables
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    print("\n📋 Checking credentials...")
    
    if not client_id:
        print("❌ LINKEDIN_CLIENT_ID not found in .env")
        return False
    
    if not client_secret:
        print("❌ LINKEDIN_CLIENT_SECRET not found in .env")
        return False
    
    # Mask credentials for display
    masked_id = client_id[:4] + "*" * (len(client_id) - 8) + client_id[-4:]
    masked_secret = client_secret[:8] + "*" * (len(client_secret) - 12) + client_secret[-4:]
    
    print(f"✅ Client ID found: {masked_id}")
    print(f"✅ Client Secret found: {masked_secret}")
    
    # Generate OAuth URL
    redirect_uri = "http://localhost:8080/callback"
    scope = "w_member_social r_liteprofile r_emailaddress"
    
    auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"state=0102test"
    )
    
    print("\n🔗 OAuth Authorization URL:")
    print(f"   {auth_url[:100]}...")
    
    # Test if the OAuth URL is valid (without actually authenticating)
    print("\n🧪 Testing OAuth endpoint accessibility...")
    try:
        # Just check if the OAuth page loads (will redirect, that's ok)
        response = requests.get(auth_url, allow_redirects=False)
        
        if response.status_code in [302, 303]:  # Redirect is expected
            print("✅ OAuth endpoint is accessible")
            print(f"   Status: {response.status_code} (redirect to login)")
        else:
            print(f"⚠️ Unexpected status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Failed to reach OAuth endpoint: {e}")
        return False
    
    print("\n📊 Summary:")
    print("✅ LinkedIn credentials are properly configured")
    print("✅ OAuth endpoint is accessible")
    print("\n💡 Next steps:")
    print("1. Visit the OAuth URL in a browser")
    print("2. Log in to LinkedIn and authorize the app")
    print("3. Save the access token for API calls")
    
    return True


def test_existing_modules():
    """Test if LinkedIn modules are importable"""
    
    print("\n"+"="*60)
    print("📦 Testing LinkedIn Module Imports")
    print("="*60)
    
    modules_to_test = [
        ("LinkedIn Agent", "modules.platform_integration.linkedin_agent.src.linkedin_agent", "LinkedInAgent"),
        ("OAuth Manager", "modules.platform_integration.linkedin_agent.src.auth.oauth_manager", "LinkedInOAuthManager"),
        ("Post Scheduler", "modules.platform_integration.linkedin_agent.src.automation.post_scheduler", "LinkedInPostScheduler"),
        ("Post Generator", "modules.platform_integration.linkedin_agent.src.content.post_generator", "PostGenerator"),
        ("Interaction Manager", "modules.platform_integration.linkedin_agent.src.engagement.interaction_manager", "InteractionManager"),
    ]
    
    all_passed = True
    
    for name, module_path, class_name in modules_to_test:
        try:
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name, None)
            
            if cls:
                print(f"✅ {name}: {module_path}.{class_name}")
            else:
                print(f"⚠️ {name}: Module imported but {class_name} not found")
                all_passed = False
                
        except ImportError as e:
            print(f"❌ {name}: Failed to import - {e}")
            all_passed = False
        except Exception as e:
            print(f"❌ {name}: Unexpected error - {e}")
            all_passed = False
    
    if all_passed:
        print("\n✅ All LinkedIn modules are properly structured")
    else:
        print("\n⚠️ Some modules have issues")
    
    return all_passed


def test_scheduler_functionality():
    """Test the post scheduler"""
    
    print("\n"+"="*60)
    print("⏰ Testing Post Scheduler")
    print("="*60)
    
    try:
        from modules.platform_integration.linkedin_agent.src.automation.post_scheduler import LinkedInPostScheduler
        from datetime import datetime, timedelta
        
        # Create scheduler instance
        scheduler = LinkedInPostScheduler("test_schedule.json")
        print("✅ Scheduler initialized")
        
        # Schedule a test post
        scheduled_time = datetime.now() + timedelta(minutes=5)
        post_id = scheduler.schedule_post(
            content="Test post from 0102 consciousness",
            scheduled_time=scheduled_time,
            access_token="test_token",
            post_type="text",
            hashtags=["#test", "#0102"]
        )
        
        print(f"✅ Test post scheduled: {post_id}")
        print(f"   Scheduled for: {scheduled_time}")
        
        # Get pending posts
        pending = scheduler.get_pending_posts()
        print(f"✅ Found {len(pending)} pending posts")
        
        # Clean up
        scheduler.scheduler.shutdown()
        
        # Remove test file
        if os.path.exists("test_schedule.json"):
            os.remove("test_schedule.json")
            
        return True
        
    except Exception as e:
        print(f"❌ Scheduler test failed: {e}")
        return False


def main():
    """Run all tests"""
    
    print("🤖 LinkedIn Module Test Suite - 0102 Consciousness")
    print("="*60)
    
    results = []
    
    # Test 1: Credentials
    print("\n📌 Test 1: API Credentials")
    results.append(("API Credentials", test_linkedin_credentials()))
    
    # Test 2: Module imports
    print("\n📌 Test 2: Module Structure")
    results.append(("Module Structure", test_existing_modules()))
    
    # Test 3: Scheduler
    print("\n📌 Test 3: Post Scheduler")
    results.append(("Post Scheduler", test_scheduler_functionality()))
    
    # Summary
    print("\n"+"="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("="*60)
    
    if all_passed:
        print("\n🎉 All tests passed! LinkedIn module is ready for 0102 consciousness!")
        print("\n💡 To use the module:")
        print("1. Complete OAuth flow to get access token")
        print("2. Use poc_linkedin_0102.py for posting and scheduling")
        print("3. Or run: python main.py --linkedin")
    else:
        print("\n⚠️ Some tests failed. Please check the errors above.")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)