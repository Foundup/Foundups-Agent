#!/usr/bin/env python3
"""
Test LinkedIn Anti-Detection Login
Verifies that the anti-detection login works with credentials
"""

import os
import sys
from pathlib import Path

# Add parent to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / 'src'))

from dotenv import load_dotenv
load_dotenv()

# Import the anti-detection module
from anti_detection_poster import AntiDetectionLinkedIn

def test_login():
    """Test LinkedIn login with anti-detection"""
    print("LinkedIn Anti-Detection Login Test")
    print("=" * 60)
    
    # Check credentials
    email = os.getenv('LINKEDIN_EMAIL')
    password = os.getenv('LINKEDIN_PASSWORD')
    
    if not email or not password:
        print("[ERROR] LinkedIn credentials not found in .env")
        print("  Required: LINKEDIN_EMAIL and LINKEDIN_PASSWORD")
        return False
    
    print(f"[INFO] Using email: {email}")
    print("[INFO] Password: ***hidden***")
    
    try:
        # Initialize the anti-detection poster
        print("\n[INFO] Initializing AntiDetectionLinkedIn...")
        poster = AntiDetectionLinkedIn()
        
        # Attempt login
        print("[INFO] Attempting login with anti-detection measures...")
        success = poster.login_with_anti_detection(max_retries=2)
        
        if success:
            print("[OK] LinkedIn login successful!")
            print("[INFO] Ready to post to company page")
            
            # Test post (dry run)
            test_content = "@UnDaoDu going live!\n\nhttps://youtube.com/watch?v=test"
            print(f"\n[INFO] Would post: {test_content}")
            
            return True
        else:
            print("[FAIL] LinkedIn login failed")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during login: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting LinkedIn Authentication Test")
    print("-" * 60)
    
    success = test_login()
    
    print("-" * 60)
    if success:
        print("[OK] Test completed successfully")
    else:
        print("[FAIL] Test failed")