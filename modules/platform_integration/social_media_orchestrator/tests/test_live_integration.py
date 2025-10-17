"""
Test live integration with Social Media Orchestrator
Tests authentication and posting to LinkedIn and X/Twitter
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path
root_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(root_dir))
os.chdir(root_dir)  # Change to root directory

from dotenv import load_dotenv
load_dotenv()

# Now import with proper paths
sys.path.insert(0, str(root_dir / 'modules' / 'platform_integration' / 'social_media_orchestrator' / 'src'))
sys.path.insert(0, str(root_dir / 'modules' / 'platform_integration' / 'linkedin_agent' / 'src'))
sys.path.insert(0, str(root_dir / 'modules' / 'platform_integration' / 'x_twitter' / 'src'))

try:
    from social_media_orchestrator import SocialMediaOrchestrator
except ImportError:
    print("Warning: Could not import SocialMediaOrchestrator")
    SocialMediaOrchestrator = None

try:
    from anti_detection_poster import AntiDetectionLinkedIn as LinkedInAntiDetectionPoster
except ImportError:
    print("Warning: Could not import LinkedInAntiDetectionPoster")
    LinkedInAntiDetectionPoster = None
    
try:
    from x_twitter_dae import XTwitterDAE
except ImportError:
    print("Warning: Could not import XTwitterDAE")
    XTwitterDAE = None


async def test_orchestrator_integration():
    """Test the complete social media integration"""
    
    print("Testing Social Media Orchestrator Integration")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = SocialMediaOrchestrator({
        'logging_level': 'INFO',
        'enable_scheduling': True
    })
    
    await orchestrator.initialize()
    print("[OK] Orchestrator initialized")
    
    # Test LinkedIn authentication
    print("\nTesting LinkedIn Authentication...")
    linkedin_creds = {
        'email': os.getenv('LINKEDIN_EMAIL'),
        'password': os.getenv('LINKEDIN_PASSWORD'),
        'company_id': '104834798'
    }
    
    try:
        # Use the anti-detection poster for LinkedIn
        linkedin_poster = LinkedInAntiDetectionPoster()
        success = linkedin_poster.login_with_anti_detection(max_retries=2)
        
        if success:
            print("[OK] LinkedIn authentication successful")
            # Register with orchestrator
            await orchestrator.authenticate_platform('linkedin', linkedin_creds)
        else:
            print("[FAIL] LinkedIn authentication failed")
    except Exception as e:
        print(f"[ERROR] LinkedIn error: {e}")
    
    # Test X/Twitter authentication
    print("\nTesting X/Twitter Authentication...")
    x_creds = {
        'username': os.getenv('X_Acc1', 'geozeai'),
        'password': os.getenv('x_Acc_pass'),
        'use_compose_url': True
    }
    
    try:
        # Initialize X DAE
        x_dae = XTwitterDAE()
        await x_dae.initialize()
        
        success = await x_dae.authenticate(x_creds)
        
        if success:
            print("[OK] X/Twitter authentication successful")
            # Register with orchestrator
            await orchestrator.authenticate_platform('twitter', x_creds)
        else:
            print("[FAIL] X/Twitter authentication failed")
    except Exception as e:
        print(f"[ERROR] X/Twitter error: {e}")
    
    # Test posting to both platforms
    print("\nTesting Cross-Platform Posting...")
    
    # Simulate YouTube going live
    youtube_url = "https://youtube.com/watch?v=test123"
    content = f"@UnDaoDu going live!\n\n{youtube_url}"
    
    print(f"Content to post: {content}")
    
    # Dry run first
    print("\nPerforming dry run...")
    
    # Test hello world for each platform
    linkedin_test = await orchestrator.test_platform_hello_world('linkedin', dry_run=True)
    print(f"LinkedIn dry run: {linkedin_test}")
    
    x_test = await orchestrator.test_platform_hello_world('twitter', dry_run=True) 
    print(f"X/Twitter dry run: {x_test}")
    
    # Get orchestrator status
    status = orchestrator.get_status()
    print(f"\nOrchestrator Status:")
    print(f"  Platforms: {status['platforms']}")
    print(f"  Initialized: {status['initialized']}")
    print(f"  Total posts: {status['total_posts']}")
    
    # Ask if user wants to do actual post
    print("\n" + "=" * 60)
    print("[OK] Integration test complete!")
    print("Note: This was a dry run. To actually post, set dry_run=False")
    
    return True


async def test_simplified_posting():
    """Test simplified posting without full orchestrator"""
    
    print("\nTesting Simplified Direct Posting")
    print("=" * 60)
    
    youtube_url = "https://youtube.com/watch?v=test123"
    content = f"@UnDaoDu going live!\n\n{youtube_url}"
    
    # Test LinkedIn with anti-detection
    print("\nLinkedIn Direct Post Test...")
    try:
        poster = LinkedInAntiDetectionPoster()
        if poster.login_with_anti_detection(max_retries=1):
            # Dry run - don't actually post
            print(f"[OK] Would post to LinkedIn: {content}")
            print("   (Set test_mode=False to actually post)")
        else:
            print("[FAIL] LinkedIn login failed")
    except Exception as e:
        print(f"[ERROR] LinkedIn error: {e}")
    
    # Test X/Twitter
    print("\nX/Twitter Direct Post Test...")
    try:
        x_dae = XTwitterDAE()
        await x_dae.initialize()
        
        creds = {
            'username': os.getenv('X_Acc1', 'geozeai'),
            'password': os.getenv('x_Acc_pass')
        }
        
        if await x_dae.authenticate(creds):
            print(f"[OK] Would post to X: {content}")
            print("   (Set test_mode=False to actually post)")
        else:
            print("[FAIL] X authentication failed")
    except Exception as e:
        print(f"[ERROR] X/Twitter error: {e}")
    
    print("\n[OK] Simplified test complete!")


if __name__ == "__main__":
    print("Social Media Integration Test")
    print("=" * 60)
    print("1. Full Orchestrator Integration")
    print("2. Simplified Direct Posting")
    print("=" * 60)
    
    choice = input("Select test mode (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(test_orchestrator_integration())
    elif choice == "2":
        asyncio.run(test_simplified_posting())
    else:
        print("Invalid choice. Running simplified test...")
        asyncio.run(test_simplified_posting())