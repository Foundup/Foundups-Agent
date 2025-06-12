"""
Quick LinkedIn API Test
Enter your credentials directly for immediate testing
"""

import logging
from linkedin_scheduler import LinkedInScheduler, LinkedInAPIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# PASTE YOUR LINKEDIN API CREDENTIALS HERE
LINKEDIN_CLIENT_ID = "your_client_id_here"  # Replace with your actual Client ID
LINKEDIN_CLIENT_SECRET = "your_client_secret_here"  # Replace with your actual Client Secret

def quick_api_test():
    """Quick test of LinkedIn API with direct credentials"""
    logger.info("🔥 Quick LinkedIn API Test")
    logger.info("=" * 40)
    
    # Check credentials
    if LINKEDIN_CLIENT_ID == "your_client_id_here":
        logger.error("❌ Please replace LINKEDIN_CLIENT_ID with your actual Client ID")
        logger.info("📝 Edit quick_test.py and paste your credentials")
        return False
    
    if LINKEDIN_CLIENT_SECRET == "your_client_secret_here":
        logger.error("❌ Please replace LINKEDIN_CLIENT_SECRET with your actual Client Secret")
        logger.info("📝 Edit quick_test.py and paste your credentials")
        return False
    
    logger.info(f"✅ Client ID: {LINKEDIN_CLIENT_ID[:8]}...")
    logger.info(f"✅ Client Secret: {'*' * len(LINKEDIN_CLIENT_SECRET)}")
    
    # Initialize scheduler with credentials
    scheduler = LinkedInScheduler(
        client_id=LINKEDIN_CLIENT_ID,
        client_secret=LINKEDIN_CLIENT_SECRET
    )
    
    # Test API connectivity
    logger.info("\n🌐 Testing LinkedIn API connectivity...")
    if scheduler.validate_connection():
        logger.info("✅ LinkedIn API is reachable!")
    else:
        logger.error("❌ Cannot reach LinkedIn API")
        return False
    
    # Generate OAuth URL
    logger.info("\n🔐 Generating OAuth URL...")
    redirect_uri = "https://localhost:8000/auth/callback"
    
    try:
        oauth_url = scheduler.get_oauth_url(redirect_uri, "test_state")
        logger.info("✅ OAuth URL generated successfully!")
        logger.info(f"\n📱 Your OAuth URL:")
        logger.info(f"{oauth_url}")
        
        logger.info(f"\n🎉 SUCCESS! Your LinkedIn API credentials work!")
        logger.info(f"📋 Next steps to post:")
        logger.info(f"1. Visit the OAuth URL above")
        logger.info(f"2. Authorize your LinkedIn app")  
        logger.info(f"3. Get the authorization code from callback")
        logger.info(f"4. Use scheduler.exchange_code_for_token() to get access token")
        logger.info(f"5. Use scheduler.create_text_post() to post!")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ OAuth URL generation failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_api_test()
    if success:
        print("\n🚀 LinkedIn API is ready to use!")
    else:
        print("\n❌ Fix the issues above and try again") 