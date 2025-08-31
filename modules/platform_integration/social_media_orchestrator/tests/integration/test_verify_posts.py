#!/usr/bin/env python3
"""
Verify that social media posts were made
"""

import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def check_linkedin():
    """Check LinkedIn for recent post"""
    print("[CHECK] LinkedIn Company Page...")
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use existing profile
    profile_dir = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile"
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Go to company page activity
        driver.get("https://www.linkedin.com/company/104834798/admin/page-posts/published/")
        time.sleep(5)
        
        # Check for recent post
        posts = driver.find_elements(By.XPATH, "//span[contains(text(), '@UnDaoDu')]")
        if posts:
            print("[OK] Found LinkedIn post with @UnDaoDu!")
            # Get full text of first post
            try:
                post_container = posts[0].find_element(By.XPATH, "./ancestor::div[contains(@class, 'feed-shared-update')]")
                post_text = post_container.text
                print(f"[POST] {post_text[:200]}...")
            except:
                pass
        else:
            print("[WARNING] No recent LinkedIn post found")
            
    except Exception as e:
        print(f"[ERROR] LinkedIn check failed: {e}")
    finally:
        driver.quit()

def check_x():
    """Check X/Twitter for recent post"""
    print("\n[CHECK] X/Twitter Profile...")
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use existing profile
    profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile"
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Go to profile
        driver.get("https://x.com/GeozeAi")
        time.sleep(5)
        
        # Check for recent post
        posts = driver.find_elements(By.XPATH, "//span[contains(text(), '@UnDaoDu')]")
        if posts:
            print("[OK] Found X post with @UnDaoDu!")
            # Get full text of first post
            try:
                post_text = posts[0].find_element(By.XPATH, "./ancestor::article").text
                print(f"[POST] {post_text[:200]}...")
            except:
                pass
        else:
            print("[WARNING] No recent X post found")
            
    except Exception as e:
        print(f"[ERROR] X check failed: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    print("Verifying Social Media Posts")
    print("=" * 60)
    
    check_linkedin()
    check_x()
    
    print("\n" + "=" * 60)
    print("Verification complete!")