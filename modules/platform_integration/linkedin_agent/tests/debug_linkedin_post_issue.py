#!/usr/bin/env python3
"""
Debug LinkedIn Post button issue - verify it actually posts
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def debug_post_button():
    """Debug why Post button isn't posting"""
    print("LinkedIn Post Button Debug - Finding the REAL Post button")
    print("=" * 60)
    
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
        # Go to company share page
        print("[1] Going to company share page...")
        driver.get("https://www.linkedin.com/company/104834798/admin/page-posts/published/?share=true")
        time.sleep(5)
        
        # Type content
        print("[2] Finding and filling text area...")
        text_area = driver.find_element(By.XPATH, "//div[@role='textbox']")
        text_area.click()
        time.sleep(1)
        
        # Clear and type test content
        text_area.send_keys(Keys.CONTROL + "a")
        text_area.send_keys(Keys.DELETE)
        test_content = "@UnDaoDu TEST POST - " + str(int(time.time()))
        text_area.send_keys(test_content)
        print(f"   Typed: {test_content}")
        time.sleep(2)
        
        # Find ALL Post buttons and their properties
        print("\n[3] Finding ALL buttons with 'Post' text or aria-label...")
        all_buttons = driver.find_elements(By.XPATH, "//button")
        post_buttons = []
        
        for btn in all_buttons:
            try:
                text = btn.text.strip()
                aria = btn.get_attribute('aria-label')
                classes = btn.get_attribute('class')
                
                if (text and 'post' in text.lower()) or (aria and 'post' in aria.lower()):
                    is_visible = btn.is_displayed()
                    is_enabled = btn.is_enabled()
                    location = btn.location
                    size = btn.size
                    
                    post_buttons.append({
                        'element': btn,
                        'text': text,
                        'aria': aria,
                        'classes': classes,
                        'visible': is_visible,
                        'enabled': is_enabled,
                        'location': location,
                        'size': size
                    })
                    
                    print(f"\n   FOUND Post button #{len(post_buttons)}:")
                    print(f"     Text: '{text}'")
                    print(f"     Aria: '{aria}'")
                    print(f"     Classes: {classes[:100]}...")
                    print(f"     Visible: {is_visible}, Enabled: {is_enabled}")
                    print(f"     Location: x={location['x']}, y={location['y']}")
                    print(f"     Size: {size['width']}x{size['height']}")
            except:
                pass
        
        print(f"\n[4] Found {len(post_buttons)} potential Post buttons")
        
        # Try to identify the REAL Post button
        real_post_button = None
        for btn_info in post_buttons:
            # The real Post button should be:
            # - Visible and enabled
            # - Have 'Post' as text or in aria-label
            # - Be in the share-actions area (bottom of modal)
            if btn_info['visible'] and btn_info['enabled']:
                if btn_info['text'] == 'Post' or (btn_info['aria'] and 'post' in btn_info['aria'].lower()):
                    if 'share-actions' in btn_info['classes'] or 'primary' in btn_info['classes']:
                        real_post_button = btn_info['element']
                        print(f"\n[5] Identified REAL Post button: {btn_info['text'] or btn_info['aria']}")
                        print(f"     Classes: {btn_info['classes']}")
                        break
        
        if not real_post_button:
            # Fallback - use the first visible, enabled Post button
            for btn_info in post_buttons:
                if btn_info['visible'] and btn_info['enabled']:
                    real_post_button = btn_info['element']
                    print(f"\n[5] Using first visible Post button: {btn_info['text'] or btn_info['aria']}")
                    break
        
        if real_post_button:
            print("\n[6] Attempting to click the Post button...")
            
            # Scroll into view
            driver.execute_script("arguments[0].scrollIntoView(true);", real_post_button)
            time.sleep(1)
            
            # Highlight the button we're about to click
            driver.execute_script("arguments[0].style.border = '3px solid red';", real_post_button)
            print("   Button highlighted in RED - check visually")
            time.sleep(2)
            
            # Try clicking
            print("   Clicking Post button NOW...")
            try:
                # Method 1: Regular click
                real_post_button.click()
                print("   ✓ Regular click executed")
            except Exception as e:
                print(f"   Regular click failed: {e}")
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", real_post_button)
                print("   ✓ JavaScript click executed")
            
            # Wait and check what happens
            print("\n[7] Waiting for post to complete...")
            time.sleep(3)
            
            # Check if we're still on share page
            current_url = driver.current_url
            print(f"   Current URL: {current_url}")
            
            if "share" not in current_url:
                print("   ✓ SUCCESS! Redirected away from share page")
            else:
                print("   ⚠ Still on share page")
                
                # Check if text area is empty
                try:
                    text_area = driver.find_element(By.XPATH, "//div[@role='textbox']")
                    current_text = text_area.text
                    if not current_text or current_text == "What do you want to talk about?":
                        print("   ✓ Text area cleared - post sent!")
                    else:
                        print(f"   ⚠ Text still in area: {current_text[:50]}...")
                except:
                    print("   Could not check text area")
            
            # Navigate to company feed to verify
            print("\n[8] Checking company feed for the post...")
            driver.get("https://www.linkedin.com/company/104834798/admin/page-posts/published/")
            time.sleep(5)
            
            # Look for our test post
            posts = driver.find_elements(By.XPATH, f"//span[contains(text(), '{test_content[:20]}')]")
            if posts:
                print(f"   ✓✓✓ POST FOUND ON FEED! Success!")
            else:
                print(f"   ✗ Post NOT found on feed")
                print("   Checking for any @UnDaoDu posts...")
                undaodu_posts = driver.find_elements(By.XPATH, "//span[contains(text(), '@UnDaoDu')]")
                if undaodu_posts:
                    print(f"   Found {len(undaodu_posts)} @UnDaoDu posts")
                    for post in undaodu_posts[:3]:
                        print(f"     - {post.text[:100]}...")
        else:
            print("\n[ERROR] Could not find any Post button!")
        
        print("\n[9] Keeping browser open for manual inspection...")
        time.sleep(20)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_post_button()