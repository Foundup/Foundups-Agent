#!/usr/bin/env python3
"""
Simple X/Twitter Post Test
Assumes user is already logged in manually
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def simple_post():
    """Simple X post test - assumes already logged in"""
    
    print("Simple X/Twitter Post Test")
    print("=" * 60)
    print("[INFO] This test assumes you're already logged into X in Chrome")
    print("[INFO] The browser will open and navigate to compose page")
    print("")
    
    # Setup Chrome to use existing profile
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Use existing Chrome profile to maintain login
    profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile"
    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    chrome_options.add_argument('--profile-directory=Default')
    
    print("[INFO] Starting Chrome with existing profile...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate directly to home first to verify login
        print("[NAV] Going to X home page...")
        driver.get("https://x.com/home")
        time.sleep(3)
        
        current_url = driver.current_url
        print(f"[DEBUG] Current URL: {current_url}")
        
        if "login" in current_url:
            print("[INFO] Not logged in - attempting login...")
            
            # Get credentials from environment
            import os
            from dotenv import load_dotenv
            load_dotenv()
            
            username = os.getenv('X_Acc1', 'geozeai')
            password = os.getenv('x_Acc_pass')
            
            if not password:
                print("[ERROR] X_Acc1 and x_Acc_pass not found in .env")
                print("[INFO] Please login manually in the browser")
                time.sleep(60)
                return False
            
            print(f"[AUTH] Logging in as {username}...")
            
            # Find username field
            try:
                username_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@name='text' or @autocomplete='username']"))
                )
                username_field.click()
                username_field.clear()
                username_field.send_keys(username)
                username_field.send_keys(Keys.RETURN)
                time.sleep(3)
                
                # Find password field
                password_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='password' or @name='password']"))
                )
                password_field.click()
                password_field.clear()
                password_field.send_keys(password)
                password_field.send_keys(Keys.RETURN)
                
                print("[AUTH] Login submitted, waiting...")
                time.sleep(5)
                
                # Check if logged in now
                driver.get("https://x.com/home")
                time.sleep(3)
                
                if "login" not in driver.current_url:
                    print("[OK] Login successful!")
                else:
                    print("[ERROR] Login failed - please login manually")
                    time.sleep(60)
                    return False
                    
            except Exception as e:
                print(f"[ERROR] Login error: {e}")
                print("[INFO] Please login manually")
                time.sleep(60)
                return False
        
        print("[OK] Logged in! Now going to compose...")
        
        # Now go to compose
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        print(f"[DEBUG] Compose URL: {driver.current_url}")
        
        # Try to find the text area
        print("[UI] Looking for text area...")
        
        # Try multiple selectors
        selectors = [
            "//div[@role='textbox']",
            "//div[@contenteditable='true']",
            "//div[contains(@aria-label, 'Post text')]",
            "//div[contains(@aria-label, 'Tweet text')]",
            "//div[@data-testid='tweetTextarea_0']",
            "//br[@data-text='true']/parent::div",
            "//div[contains(@class, 'public-DraftEditor')]//div[@contenteditable='true']"
        ]
        
        text_area = None
        for selector in selectors:
            try:
                print(f"[DEBUG] Trying: {selector}")
                elements = driver.find_elements(By.XPATH, selector)
                if elements:
                    print(f"[DEBUG] Found {len(elements)} elements")
                    # Get the first visible, editable element
                    for elem in elements:
                        if elem.is_displayed() and elem.is_enabled():
                            text_area = elem
                            print(f"[OK] Found text area!")
                            break
                if text_area:
                    break
            except Exception as e:
                print(f"[DEBUG] Error with selector: {e}")
                continue
        
        if not text_area:
            print("[ERROR] Could not find text area")
            print("[INFO] Page source sample:")
            print(driver.page_source[:500])
            return False
        
        # Click and type
        print("[TYPE] Clicking text area...")
        text_area.click()
        time.sleep(1)
        
        content = "@UnDaoDu going live!\n\nhttps://www.youtube.com/watch?v=Edka5TBGLuA"
        print(f"[TYPE] Typing: {content}")
        
        # Type slowly
        for char in content:
            if char == '\n':
                text_area.send_keys(Keys.RETURN)
            else:
                text_area.send_keys(char)
            time.sleep(0.05)
        
        print("[OK] Content typed!")
        
        # Find Post button
        print("[UI] Looking for Post button...")
        post_selectors = [
            "//button[@data-testid='tweetButtonInline']",
            "//button[contains(text(), 'Post')]",
            "//span[text()='Post']/parent::button",
            "//div[@data-testid='tweetButton']",
            "//button[contains(@aria-label, 'Post')]"
        ]
        
        for selector in post_selectors:
            try:
                post_button = driver.find_element(By.XPATH, selector)
                if post_button and post_button.is_enabled():
                    print("[OK] Found Post button!")
                    print("[ACTION] Clicking Post...")
                    post_button.click()
                    time.sleep(3)
                    print("[OK] Posted successfully!")
                    return True
            except:
                continue
        
        print("[ERROR] Could not find Post button")
        return False
        
    except Exception as e:
        print(f"[ERROR] Exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print("[INFO] Keeping browser open for inspection")
        time.sleep(10)  # Keep open for 10 seconds
        # Don't quit to keep session
        print("[INFO] Browser kept open for reuse")


if __name__ == "__main__":
    success = simple_post()
    
    if success:
        print("\n[OK] Test successful!")
    else:
        print("\n[FAIL] Test failed")