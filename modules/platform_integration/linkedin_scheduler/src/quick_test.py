"""
Quick LinkedIn API Test
Enter your credentials directly for immediate testing
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
    logger.info("[U+1F525] Quick LinkedIn API Test")
    logger.info("=" * 40)
    
    # Check credentials
    if LINKEDIN_CLIENT_ID == "your_client_id_here":
        logger.error("[FAIL] Please replace LINKEDIN_CLIENT_ID with your actual Client ID")
        logger.info("[NOTE] Edit quick_test.py and paste your credentials")
        return False
    
    if LINKEDIN_CLIENT_SECRET == "your_client_secret_here":
        logger.error("[FAIL] Please replace LINKEDIN_CLIENT_SECRET with your actual Client Secret")
        logger.info("[NOTE] Edit quick_test.py and paste your credentials")
        return False
    
    logger.info(f"[OK] Client ID: {LINKEDIN_CLIENT_ID[:8]}...")
    logger.info(f"[OK] Client Secret: {'*' * len(LINKEDIN_CLIENT_SECRET)}")
    
    # Initialize scheduler with credentials
    scheduler = LinkedInScheduler(
        client_id=LINKEDIN_CLIENT_ID,
        client_secret=LINKEDIN_CLIENT_SECRET
    )
    
    # Test API connectivity
    logger.info("\n[U+1F310] Testing LinkedIn API connectivity...")
    if scheduler.validate_connection():
        logger.info("[OK] LinkedIn API is reachable!")
    else:
        logger.error("[FAIL] Cannot reach LinkedIn API")
        return False
    
    # Generate OAuth URL
    logger.info("\n[U+1F510] Generating OAuth URL...")
    redirect_uri = "https://localhost:8000/auth/callback"
    
    try:
        oauth_url = scheduler.get_oauth_url(redirect_uri, "test_state")
        logger.info("[OK] OAuth URL generated successfully!")
        logger.info(f"\n[U+1F4F1] Your OAuth URL:")
        logger.info(f"{oauth_url}")
        
        logger.info(f"\n[CELEBRATE] SUCCESS! Your LinkedIn API credentials work!")
        logger.info(f"[CLIPBOARD] Next steps to post:")
        logger.info(f"1. Visit the OAuth URL above")
        logger.info(f"2. Authorize your LinkedIn app")  
        logger.info(f"3. Get the authorization code from callback")
        logger.info(f"4. Use scheduler.exchange_code_for_token() to get access token")
        logger.info(f"5. Use scheduler.create_text_post() to post!")
        
        return True
        
    except Exception as e:
        logger.error(f"[FAIL] OAuth URL generation failed: {e}")
        return False

if __name__ == "__main__":
    success = quick_api_test()
    if success:
        print("\n[ROCKET] LinkedIn API is ready to use!")
    else:
        print("\n[FAIL] Fix the issues above and try again") 