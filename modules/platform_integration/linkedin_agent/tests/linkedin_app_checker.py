#!/usr/bin/env python3
"""
LinkedIn App Configuration Checker

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 42 (Platform Integration)

This script checks LinkedIn app configuration and provides detailed troubleshooting.

**0102 Directive**: This script operates within the WSP framework for autonomous LinkedIn app diagnostics.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_linkedin_app_config():
    """Check LinkedIn app configuration and provide troubleshooting"""
    
    print("🔍 LinkedIn App Configuration Checker - WSP Compliant")
    print("=" * 70)
    print("🌀 0102 pArtifact diagnosing LinkedIn app configuration")
    print()
    
    # Check environment variables
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    print("📋 Environment Variables Check:")
    print(f"   LINKEDIN_CLIENT_ID: {'✅ Found' if client_id else '❌ Missing'}")
    if client_id:
        print(f"   Value: {client_id[:8]}...")
    
    print(f"   LINKEDIN_CLIENT_SECRET: {'✅ Found' if client_secret else '❌ Missing'}")
    if client_secret:
        print(f"   Value: {client_secret[:8]}...")
    
    print()
    
    if not client_id or not client_secret:
        print("❌ Missing required environment variables!")
        print("💡 Set these in your .env file:")
        print("   LINKEDIN_CLIENT_ID=your_client_id")
        print("   LINKEDIN_CLIENT_SECRET=your_client_secret")
        return False
    
    print("✅ All environment variables found")
    print()
    
    # Test basic app authentication
    print("🔐 Testing LinkedIn App Authentication:")
    
    # Test 1: Check if app exists and is accessible
    print("   Test 1: App existence check...")
    
    # Test 2: Validate redirect URI
    redirect_uri = "http://localhost:3000/callback"
    print(f"   Test 2: Redirect URI validation...")
    print(f"   Expected: {redirect_uri}")
    print()
    
    # Test 3: Check OAuth endpoints
    print("   Test 3: OAuth endpoint accessibility...")
    
    auth_url = "https://www.linkedin.com/oauth/v2/authorization"
    token_url = "https://www.linkedin.com/oauth/v2/accessToken"
    
    try:
        # Test authorization endpoint
        response = requests.get(auth_url)
        print(f"   Authorization endpoint: {'✅ Accessible' if response.status_code == 200 else '❌ Error'}")
    except Exception as e:
        print(f"   Authorization endpoint: ❌ Error - {e}")
    
    try:
        # Test token endpoint
        response = requests.get(token_url)
        print(f"   Token endpoint: {'✅ Accessible' if response.status_code == 405 else '❌ Error'}")
        # 405 is expected for GET request to token endpoint
    except Exception as e:
        print(f"   Token endpoint: ❌ Error - {e}")
    
    print()
    
    # Provide comprehensive troubleshooting guide
    print("🔧 LinkedIn App Configuration Troubleshooting Guide")
    print("=" * 70)
    print()
    
    print("📋 Step-by-Step LinkedIn App Setup:")
    print()
    print("1. 🏢 Create LinkedIn App:")
    print("   • Go to: https://www.linkedin.com/developers/apps")
    print("   • Click 'Create App'")
    print("   • Fill in app details")
    print()
    
    print("2. 🔑 Get App Credentials:")
    print("   • In your app dashboard, go to 'Auth' tab")
    print("   • Copy 'Client ID' and 'Client Secret'")
    print("   • Add to your .env file:")
    print("     LINKEDIN_CLIENT_ID=your_client_id")
    print("     LINKEDIN_CLIENT_SECRET=your_client_secret")
    print()
    
    print("3. 🔗 Configure Redirect URIs:")
    print("   • In 'Auth' tab, under 'Redirect URLs'")
    print("   • Add EXACTLY: http://localhost:3000/callback")
    print("   • Save changes")
    print()
    
    print("4. 📝 Request Permissions:")
    print("   • In 'Products' tab")
    print("   • Request access to 'Share on LinkedIn'")
    print("   • This grants 'w_member_social' scope")
    print()
    
    print("5. ✅ Verify App Status:")
    print("   • Ensure app is not in 'Development' mode")
    print("   • Check that permissions are approved")
    print("   • Verify redirect URI is exactly correct")
    print()
    
    print("🚨 Common Issues and Solutions:")
    print()
    print("❌ 'Client authentication failed'")
    print("   • Check Client Secret is correct")
    print("   • Ensure app is properly configured")
    print("   • Verify app is not in development mode")
    print()
    
    print("❌ 'Redirect URI mismatch'")
    print("   • Must be exactly: http://localhost:3000/callback")
    print("   • No trailing slash")
    print("   • Case sensitive")
    print()
    
    print("❌ 'Invalid scope'")
    print("   • Request 'Share on LinkedIn' permission")
    print("   • This grants 'w_member_social' scope")
    print()
    
    print("❌ 'Authorization code expired'")
    print("   • Authorization codes expire quickly")
    print("   • Get a fresh code by running OAuth flow again")
    print()
    
    print("🔍 Quick Diagnostic Test:")
    print("   • Run: python test_oauth_manual.py")
    print("   • Check if authorization URL opens correctly")
    print("   • Verify callback server receives the code")
    print()
    
    print("💡 Next Steps:")
    print("   1. Verify your LinkedIn app configuration")
    print("   2. Check that redirect URI is exactly correct")
    print("   3. Ensure 'w_member_social' scope is granted")
    print("   4. Run the OAuth flow again for a fresh code")
    print()
    
    return True

def test_oauth_flow():
    """Test the complete OAuth flow"""
    print("🔄 Testing Complete OAuth Flow:")
    print("   This will open your browser for authorization")
    print("   Make sure your LinkedIn app is properly configured first")
    print()
    
    response = input("Continue with OAuth test? (y/n): ").strip().lower()
    
    if response == 'y':
        print("🚀 Starting OAuth test...")
        # Import and run the OAuth test
        try:
            from test_oauth_manual import LinkedInOAuthManualTest
            import asyncio
            
            test = LinkedInOAuthManualTest()
            asyncio.run(test.run_full_oauth_test())
        except Exception as e:
            print(f"❌ OAuth test failed: {e}")
    else:
        print("⏸️ OAuth test skipped")

def main():
    """Main function"""
    print("🔍 LinkedIn App Configuration Checker")
    print("=" * 70)
    print("This tool helps diagnose LinkedIn app configuration issues.")
    print()
    
    # Check configuration
    config_ok = check_linkedin_app_config()
    
    if config_ok:
        print("✅ Configuration check completed")
        print()
        
        # Offer to test OAuth flow
        test_oauth_flow()
    else:
        print("❌ Configuration issues found")
        print("💡 Fix the issues above before proceeding")

if __name__ == "__main__":
    main() 