"""
LinkedIn API Real Credentials Test
Test script to verify your LinkedIn API credentials work
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
import os
from linkedin_scheduler import LinkedInScheduler, LinkedInAPIError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_credentials():
    """Test LinkedIn API credentials from environment variables"""
    logger.info("[SEARCH] Testing LinkedIn API Credentials")
    logger.info("=" * 50)
    
    # Check environment variables
    client_id = os.getenv('LINKEDIN_CLIENT_ID')
    client_secret = os.getenv('LINKEDIN_CLIENT_SECRET')
    
    if not client_id:
        logger.error("[FAIL] LINKEDIN_CLIENT_ID environment variable not set")
        return False
    
    if not client_secret:
        logger.error("[FAIL] LINKEDIN_CLIENT_SECRET environment variable not set")
        return False
    
    logger.info(f"[OK] Client ID found: {client_id[:8]}...")
    logger.info(f"[OK] Client Secret found: {'*' * len(client_secret)}")
    
    # Initialize scheduler
    scheduler = LinkedInScheduler()
    
    # Test basic API connectivity
    logger.info("\n[U+1F310] Testing LinkedIn API connectivity...")
    
    if scheduler.validate_connection():
        logger.info("[OK] LinkedIn API is reachable")
    else:
        logger.error("[FAIL] Cannot reach LinkedIn API")
        return False
    
    return True


def generate_oauth_url():
    """Generate OAuth URL for testing authentication"""
    logger.info("\n[U+1F510] Generating OAuth URL for Authentication")
    logger.info("=" * 50)
    
    scheduler = LinkedInScheduler()
    
    if not scheduler.client_id:
        logger.error("[FAIL] Cannot generate OAuth URL without client ID")
        return None
    
    # Generate OAuth URL
    redirect_uri = "https://localhost:8000/auth/linkedin/callback"  # Example callback
    state = "test_auth_123"
    
    try:
        oauth_url = scheduler.get_oauth_url(redirect_uri, state)
        
        logger.info("[OK] OAuth URL generated successfully!")
        logger.info(f"\n[U+1F4F1] Visit this URL to authorize your app:")
        logger.info(f"{oauth_url}")
        
        logger.info(f"\n[CLIPBOARD] Next steps:")
        logger.info(f"1. Visit the URL above in your browser")
        logger.info(f"2. Login to LinkedIn and authorize your app")
        logger.info(f"3. LinkedIn will redirect to: {redirect_uri}")
        logger.info(f"4. Copy the 'code' parameter from the callback URL")
        logger.info(f"5. Use that code with exchange_code_for_token() method")
        
        return oauth_url
        
    except Exception as e:
        logger.error(f"[FAIL] Failed to generate OAuth URL: {e}")
        return None


def test_token_exchange():
    """Test token exchange (requires manual authorization code)"""
    logger.info("\n[REFRESH] Token Exchange Test")
    logger.info("=" * 50)
    logger.info("This requires a valid authorization code from OAuth flow")
    
    # This is interactive - would need user to provide auth code
    logger.info("[NOTE] To test token exchange:")
    logger.info("1. Complete OAuth flow above")
    logger.info("2. Get authorization code from callback")
    logger.info("3. Use scheduler.exchange_code_for_token(code, redirect_uri)")


def check_environment():
    """Check all environment variables and LinkedIn app setup"""
    logger.info("\n[U+2699]️  Environment Check")
    logger.info("=" * 50)
    
    # Check required environment variables
    required_vars = ['LINKEDIN_CLIENT_ID', 'LINKEDIN_CLIENT_SECRET']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            if var == 'LINKEDIN_CLIENT_SECRET':
                logger.info(f"[OK] {var}: {'*' * len(value)}")
            else:
                logger.info(f"[OK] {var}: {value[:8]}...")
        else:
            logger.error(f"[FAIL] {var}: NOT SET")
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"\n[FAIL] Missing environment variables: {', '.join(missing_vars)}")
        logger.info("\n[NOTE] To set environment variables:")
        logger.info("Windows PowerShell:")
        logger.info("  $env:LINKEDIN_CLIENT_ID = 'your_client_id'")
        logger.info("  $env:LINKEDIN_CLIENT_SECRET = 'your_client_secret'")
        logger.info("\nWindows Command Prompt:")
        logger.info("  set LINKEDIN_CLIENT_ID=your_client_id")
        logger.info("  set LINKEDIN_CLIENT_SECRET=your_client_secret")
        return False
    
    logger.info("\n[OK] All required environment variables are set!")
    return True


def run_full_test():
    """Run complete LinkedIn API test suite"""
    logger.info("[ROCKET] LinkedIn API Real Credentials Test")
    logger.info("=" * 60)
    
    success = True
    
    # Step 1: Check environment
    if not check_environment():
        success = False
    
    # Step 2: Test credentials
    if success and not test_credentials():
        success = False
    
    # Step 3: Generate OAuth URL
    if success:
        oauth_url = generate_oauth_url()
        if not oauth_url:
            success = False
    
    # Step 4: Show token exchange info
    if success:
        test_token_exchange()
    
    # Final result
    logger.info("\n" + "=" * 60)
    if success:
        logger.info("[CELEBRATE] LinkedIn API credentials test PASSED!")
        logger.info("[OK] Ready for OAuth flow and real posting")
        logger.info("[TOOL] Use the OAuth URL above to get access tokens")
    else:
        logger.error("[FAIL] LinkedIn API credentials test FAILED!")
        logger.info("[CLIPBOARD] Fix the issues above and try again")
    
    return success


if __name__ == "__main__":
    run_full_test() 