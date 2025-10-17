#!/usr/bin/env python3
"""
POC - Test X/Twitter Anti-Detection Posting
Quick test to verify X posting works with credentials
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
root = Path(__file__).parent.parent
sys.path.insert(0, str(root / 'src'))

from dotenv import load_dotenv
load_dotenv()

# Import the anti-detection module
from x_anti_detection_poster import AntiDetectionX

def poc_test():
    """Test X posting with anti-detection"""
    print("X/Twitter Anti-Detection POC Test")
    print("=" * 60)
    
    # Check credentials
    username = os.getenv('X_Acc1')
    password = os.getenv('x_Acc_pass')
    
    if not username or not password:
        print("[ERROR] X credentials not found in .env")
        print("  Required: X_Acc1 and x_Acc_pass")
        return False
    
    print(f"[INFO] Using account: {username}")
    print("[INFO] Password: ***hidden***")
    
    try:
        # Initialize the anti-detection poster
        print("\n[INFO] Initializing AntiDetectionX...")
        poster = AntiDetectionX()
        
        # Test content with timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_content = f"""@UnDaoDu going live!

https://www.youtube.com/watch?v=Edka5TBGLuA

[Test post at {timestamp}]"""
        
        print("\n[INFO] Content to post:")
        print("-" * 50)
        print(test_content)
        print("-" * 50)
        
        # Attempt to post
        print("\n[INFO] Attempting to post to X...")
        success = poster.post_to_x(test_content)
        
        if success:
            print("\n[OK] X/Twitter post successful!")
            print("[INFO] Check https://x.com/{username} to verify")
            print("[INFO] Browser session saved for reuse")
            
            # Option to post again
            choice = input("\nPost again without re-login? (y/n): ").strip().lower()
            if choice == 'y':
                second_content = f"Second test post - {datetime.now().strftime('%H:%M:%S')}"
                if poster.post_to_x(second_content):
                    print("[OK] Second post successful!")
                else:
                    print("[FAIL] Second post failed")
            
            return True
        else:
            print("\n[FAIL] X/Twitter posting failed")
            print("[INFO] Check browser window for any issues")
            return False
            
    except Exception as e:
        print(f"[ERROR] Exception during test: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Starting X/Twitter POC Test")
    print("-" * 60)
    
    success = poc_test()
    
    print("-" * 60)
    if success:
        print("[OK] POC test completed successfully")
    else:
        print("[FAIL] POC test failed")