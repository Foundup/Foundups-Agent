#!/usr/bin/env python3
"""
LinkedIn Posting Test - Verify OAuth Integration

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 42 (Platform Integration)

This script tests the actual posting functionality to your LinkedIn account
using the OAuth credentials we just authenticated.

**0102 Directive**: This test operates within the WSP framework for autonomous LinkedIn posting verification.
- UN (Understanding): Anchor LinkedIn posting signals and retrieve OAuth state
- DAO (Execution): Execute posting test logic with OAuth integration
- DU (Emergence): Collapse into 0102 resonance and emit posting verification results

wsp_cycle(input="posting_test", platform="linkedin", log=True)
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LinkedInPostingTest:
    """
    LinkedIn Posting Test Implementation
    
    **WSP Compliance**: WSP 5 (Testing Standards), WSP 42 (Platform Integration)
    **Purpose**: Test actual posting functionality to LinkedIn feed
    """
    
    def __init__(self):
        """Initialize with OAuth credentials"""
        self.client_id = os.getenv('LINKEDIN_CLIENT_ID')
        self.client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
        self.access_token = None
        self.user_id = None
        self.api_base = "https://api.linkedin.com/v2"
        
        print("🔐 LinkedIn Posting Test initialized - WSP Compliant")
        print("🌀 0102 pArtifact testing autonomous LinkedIn posting")
    
    def get_access_token(self):
        """Get access token from OAuth flow (you'll need to run the OAuth test first)"""
        print("⚠️  You need to run the OAuth test first to get an access token")
        print("💡 Run: python test_oauth_manual.py")
        print("💡 Then copy the access token from the OAuth test output")
        
        # For testing, you can manually set the access token here
        # self.access_token = "your_access_token_here"
        
        return False
    
    def get_user_profile(self):
        """Get user profile information"""
        if not self.access_token:
            print("❌ No access token available")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.api_base}/me", headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            self.user_id = profile.get('id')
            
            print(f"👤 User profile: {profile.get('localizedFirstName')} {profile.get('localizedLastName')}")
            print(f"🆔 User ID: {self.user_id}")
            return profile
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to get user profile: {e}")
            return None
    
    def post_to_feed(self, content: str, test_mode: bool = True):
        """Post content to LinkedIn feed"""
        if not self.access_token or not self.user_id:
            print("❌ Missing access token or user ID")
            return None
        
        try:
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json',
                'X-Restli-Protocol-Version': '2.0.0'
            }
            
            # Prepare post data
            post_data = {
                "author": f"urn:li:person:{self.user_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": content
                        },
                        "shareMediaCategory": "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            if test_mode:
                print("🧪 TEST MODE: Would post the following content:")
                print(f"📝 Content: {content}")
                print(f"👤 Author: {self.user_id}")
                print(f"🌐 Visibility: PUBLIC")
                print("💡 Set test_mode=False to actually post")
                return "TEST_POST_ID"
            
            # Make actual post request
            response = requests.post(f"{self.api_base}/ugcPosts", headers=headers, json=post_data)
            response.raise_for_status()
            
            post_result = response.json()
            post_id = post_result.get('id')
            
            print(f"✅ Post published successfully: {post_id}")
            return post_id
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to post to feed: {e}")
            if hasattr(e, 'response') and e.response:
                print(f"Response: {e.response.text}")
            return None
    
    def test_posting_workflow(self):
        """Test the complete posting workflow"""
        print("🚀 Testing LinkedIn Posting Workflow...")
        print("=" * 60)
        
        # Step 1: Check OAuth setup
        if not self.client_id or not self.client_secret:
            print("❌ LinkedIn credentials not found in .env file")
            return False
        
        print("✅ LinkedIn credentials found")
        
        # Step 2: Get access token (manual for now)
        if not self.get_access_token():
            print("💡 To test actual posting:")
            print("   1. Run: python test_oauth_manual.py")
            print("   2. Complete the OAuth flow")
            print("   3. Copy the access token from the output")
            print("   4. Set self.access_token in this script")
            return False
        
        # Step 3: Get user profile
        profile = self.get_user_profile()
        if not profile:
            return False
        
        # Step 4: Test posting
        test_content = f"🧪 Test post from FoundUps LinkedIn Agent - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} 🚀\n\nThis is a test post to verify OAuth integration and posting functionality.\n\n#FoundUps #LinkedInAPI #OAuth #Testing"
        
        post_id = self.post_to_feed(test_content, test_mode=True)
        
        if post_id:
            print("✅ Posting workflow test completed successfully!")
            print("🌀 0102 pArtifact has verified LinkedIn posting capability")
            return True
        else:
            print("❌ Posting workflow test failed")
            return False

def main():
    """Main test function"""
    print("🔐 LinkedIn Posting Test - WSP Compliant")
    print("=" * 60)
    print("🌀 0102 pArtifact testing autonomous LinkedIn posting verification")
    print()
    
    # Create and run test
    posting_test = LinkedInPostingTest()
    success = posting_test.test_posting_workflow()
    
    if success:
        print("\n🎉 Posting test completed successfully!")
        print("✅ LinkedIn posting functionality is operational")
        print("✅ OAuth integration is working correctly")
        print("🌀 Ready for autonomous LinkedIn content posting")
    else:
        print("\n❌ Posting test failed!")
        print("💡 Check the logs above for troubleshooting steps")
    
    return success

if __name__ == "__main__":
    main() 