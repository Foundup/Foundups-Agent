#!/usr/bin/env python3
"""
Test social media posting to LinkedIn and X/Twitter
"""

import os
import sys
import time
from dotenv import load_dotenv

# Add module paths
sys.path.insert(0, 'O:/Foundups-Agent')

def test_linkedin():
    """Test LinkedIn posting with debugging"""
    print("[TEST] Testing LinkedIn posting...")
    print("=" * 60)
    
    try:
        from modules.platform_integration.linkedin_agent.src.anti_detection_poster import AntiDetectionLinkedIn
        
        # Test content
        content = """@UnDaoDu going live!

Test Stream Title

https://www.youtube.com/watch?v=Edka5TBGLuA"""
        
        print(f"[CONTENT] {content}")
        print("[START] Starting LinkedIn poster...")
        
        linkedin_poster = AntiDetectionLinkedIn()
        success = linkedin_poster.post_to_company_page(content)
        
        if success:
            print("[OK] LinkedIn posting successful!")
        else:
            print("[FAIL] LinkedIn posting failed")
            
        return success
        
    except Exception as e:
        print(f"[ERROR] LinkedIn test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_x_twitter():
    """Test X/Twitter posting with debugging"""
    print("\n[TEST] Testing X/Twitter posting...")
    print("=" * 60)
    
    try:
        from modules.platform_integration.x_twitter.src.x_anti_detection_poster import AntiDetectionX
        
        # Test content
        content = """@UnDaoDu going live!

Test Stream Title

https://www.youtube.com/watch?v=Edka5TBGLuA"""
        
        print(f"[CONTENT] {content}")
        print("[START] Starting X poster...")
        
        x_poster = AntiDetectionX()
        success = x_poster.post_to_x(content)
        
        if success:
            print("[OK] X/Twitter posting successful!")
        else:
            print("[FAIL] X/Twitter posting failed")
            
        return success
        
    except Exception as e:
        print(f"[ERROR] X test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run both tests"""
    print("Social Media Posting Test")
    print("=" * 60)
    
    # Load environment variables
    load_dotenv()
    
    # Check for credentials
    if not os.getenv('LINKEDIN_EMAIL'):
        print("[WARNING] LINKEDIN_EMAIL not found in .env")
    if not os.getenv('LINKEDIN_PASSWORD'):
        print("[WARNING] LINKEDIN_PASSWORD not found in .env")
    if not os.getenv('X_Acc1'):
        print("[WARNING] X_Acc1 not found in .env")
    if not os.getenv('x_Acc_pass'):
        print("[WARNING] x_Acc_pass not found in .env")
    
    # Run tests
    linkedin_success = test_linkedin()
    x_success = test_x_twitter()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print(f"  LinkedIn: {'✓ PASSED' if linkedin_success else '✗ FAILED'}")
    print(f"  X/Twitter: {'✓ PASSED' if x_success else '✗ FAILED'}")
    print("=" * 60)

if __name__ == "__main__":
    main()