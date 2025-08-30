#!/usr/bin/env python3
"""
Debug X/Twitter posting to see if it's actually posting
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def debug_x_post():
    """Debug X posting and verification"""
    print("X/Twitter Post Debug")
    print("=" * 60)
    
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
        # First check profile to see existing posts
        print("[1] Checking profile first...")
        driver.get("https://x.com/GeozeAi")
        time.sleep(5)
        
        # Count existing @UnDaoDu posts
        existing_posts = driver.find_elements(By.XPATH, "//span[contains(text(), '@UnDaoDu')]")
        print(f"   Found {len(existing_posts)} existing @UnDaoDu posts")
        
        # Now go to compose
        print("\n[2] Going to compose page...")
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        # Find text area
        print("[3] Finding text area...")
        text_area = None
        selectors = [
            "//div[@role='textbox']",
            "//div[@contenteditable='true']",
            "//div[contains(@class, 'DraftEditor')]"
        ]
        
        for selector in selectors:
            try:
                text_area = driver.find_element(By.XPATH, selector)
                if text_area:
                    print(f"   Found text area with: {selector}")
                    break
            except:
                continue
        
        if text_area:
            # Type test content
            print("[4] Typing content...")
            text_area.click()
            time.sleep(1)
            
            # Clear first
            text_area.send_keys(Keys.CONTROL + "a")
            text_area.send_keys(Keys.DELETE)
            time.sleep(1)
            
            test_content = f"@UnDaoDu TEST {int(time.time())}"
            text_area.send_keys(test_content)
            print(f"   Typed: {test_content}")
            time.sleep(2)
            
            # Find ALL Post buttons
            print("\n[5] Finding Post button...")
            all_buttons = driver.find_elements(By.XPATH, "//button | //div[@role='button']")
            post_buttons = []
            
            for btn in all_buttons:
                try:
                    text = btn.text.strip()
                    aria = btn.get_attribute('aria-label')
                    testid = btn.get_attribute('data-testid')
                    role = btn.get_attribute('role')
                    
                    if (text and 'post' in text.lower()) or \
                       (aria and 'post' in aria.lower()) or \
                       (testid and 'tweet' in testid.lower()):
                        
                        is_visible = btn.is_displayed()
                        is_enabled = btn.is_enabled()
                        
                        if is_visible and is_enabled:
                            post_buttons.append({
                                'element': btn,
                                'text': text,
                                'aria': aria,
                                'testid': testid,
                                'role': role
                            })
                            
                            print(f"\n   Found Post button:")
                            print(f"     Text: '{text}'")
                            print(f"     Aria: '{aria}'")
                            print(f"     TestId: '{testid}'")
                            print(f"     Role: '{role}'")
                except:
                    pass
            
            if post_buttons:
                # Use the first one
                post_btn = post_buttons[0]['element']
                print(f"\n[6] Clicking Post button: {post_buttons[0]['text'] or post_buttons[0]['aria']}")
                
                # Highlight it
                driver.execute_script("arguments[0].style.border = '3px solid red';", post_btn)
                time.sleep(2)
                
                # Click it
                try:
                    post_btn.click()
                    print("   ✓ Clicked with regular click")
                except:
                    driver.execute_script("arguments[0].click();", post_btn)
                    print("   ✓ Clicked with JavaScript")
                
                # Wait for post
                print("\n[7] Waiting for post to complete...")
                time.sleep(5)
                
                # Check if still on compose
                current_url = driver.current_url
                print(f"   Current URL: {current_url}")
                
                if "compose" not in current_url:
                    print("   ✓ Redirected away from compose!")
                else:
                    print("   ⚠ Still on compose page")
                    
                    # Check if text area is empty
                    try:
                        text_area = driver.find_element(By.XPATH, "//div[@role='textbox']")
                        current_text = text_area.text
                        if not current_text:
                            print("   ✓ Text area cleared - post sent!")
                        else:
                            print(f"   ⚠ Text still there: {current_text}")
                    except:
                        pass
                
                # Go to profile to verify
                print("\n[8] Checking profile for new post...")
                driver.get("https://x.com/GeozeAi")
                time.sleep(5)
                
                # Check for new posts
                new_posts = driver.find_elements(By.XPATH, f"//span[contains(text(), '{test_content[:10]}')]")
                if new_posts:
                    print(f"   ✓✓✓ TEST POST FOUND! Success!")
                else:
                    print(f"   ✗ Test post not found")
                    
                    # Check any recent posts
                    all_posts = driver.find_elements(By.XPATH, "//article")
                    print(f"   Found {len(all_posts)} total posts on page")
                    
                    if all_posts:
                        # Check first post
                        first_post = all_posts[0].text
                        print(f"   Most recent post preview: {first_post[:100]}...")
            else:
                print("[ERROR] No Post button found!")
        else:
            print("[ERROR] No text area found!")
        
        print("\n[9] Keeping browser open for inspection...")
        time.sleep(20)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_x_post()