from pathlib import Path
import sys
import os

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
os.chdir(REPO_ROOT)

"""Quick browser state checker"""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

print("="*60)
print(" BROWSER STATE CHECK")
print("="*60)

options = Options()
options.add_experimental_option('debuggerAddress', '127.0.0.1:9222')

try:
    driver = webdriver.Chrome(options=options)
    print(f"\n[OK] Connected to Chrome")
    print(f"URL: {driver.current_url[:100]}")
    print(f"Title: {driver.title[:50] if driver.title else 'N/A'}")
    
    # Check if logged in
    if 'accounts.google.com' in driver.current_url or 'signin' in driver.current_url:
        print("\n[!] ACTION REQUIRED: Please sign into Google/YouTube first!")
        print("    After signing in, run this script again.")
    elif 'studio.youtube.com' in driver.current_url:
        print("\n[OK] On YouTube Studio")
        
        # Count comments
        time.sleep(2)
        comment_count = driver.execute_script(
            "return document.querySelectorAll('ytcp-comment-thread').length"
        )
        print(f"Comments found: {comment_count}")
        
        if comment_count > 0:
            print("\n[READY] System ready for autonomous engagement!")
            print("Run: python test_uitars_comment_engagement.py --max-comments 3")
        else:
            print("\n[!] No comments visible. Navigate to comments inbox.")
    else:
        print(f"\n[!] Not on YouTube Studio. Current page: {driver.current_url[:60]}")
        print("    Please navigate to: https://studio.youtube.com")
        
except Exception as e:
    print(f"\n[ERROR] {e}")

print("\n" + "="*60)



