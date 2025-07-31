#!/usr/bin/env python3
"""
LinkedIn OAuth Test Script
Simple test runner for LinkedIn OAuth functionality

Usage:
    python test_linkedin_oauth.py
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from linkedin_oauth_test import test_linkedin_oauth

async def main():
    """Main test function"""
    print("🔐 LinkedIn OAuth Test")
    print("=" * 50)
    print("This test will:")
    print("1. Generate LinkedIn authorization URL")
    print("2. Open browser for user authorization")
    print("3. Handle OAuth callback")
    print("4. Exchange code for access token")
    print("5. Post test content to LinkedIn feed")
    print("=" * 50)
    
    # Check environment variables
    if not os.getenv('LINKEDIN_CLIENT_ID') or not os.getenv('LINKEDIN_CLIENT_SECRET'):
        print("❌ ERROR: LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET must be set in .env file")
        print("Please add these to your .env file:")
        print("LINKEDIN_CLIENT_ID=your_client_id_here")
        print("LINKEDIN_CLIENT_SECRET=your_client_secret_here")
        return False
    
    print("✅ Environment variables found")
    print()
    
    # Run the test
    success = await test_linkedin_oauth()
    
    if success:
        print("\n🎉 Test completed successfully!")
        print("✅ LinkedIn OAuth flow is working correctly")
        print("✅ Post publishing to LinkedIn feed is operational")
    else:
        print("\n❌ Test failed!")
        print("❌ Check the logs above for detailed error information")
    
    return success

if __name__ == "__main__":
    asyncio.run(main()) 