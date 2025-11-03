#!/usr/bin/env python3
"""
Detailed test of LinkedIn posting with YouTube stream data
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


import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def test_linkedin_post_with_youtube():
    """Test LinkedIn posting with YouTube stream data"""
    print("LinkedIn Detailed Post Test with YouTube Data")
    print("=" * 60)
    
    # The actual content that would come from YouTube
    content = """@UnDaoDu going live!

#twitter #X on [U+1F525] #TrumpDead ?" [U+1F635]🪦 #DC #ICEraids Move2Japan Show LIVE!

https://www.youtube.com/watch?v=jQSgx8K1178"""
    
    print("[CONTENT] Content to post:")
    print("-" * 40)
    print(content)
    print("-" * 40)
    
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
        # Go directly to company share page
        print("\n[NAV] Going to company share page...")
        driver.get("https://www.linkedin.com/company/104834798/admin/page-posts/published/?share=true")
        time.sleep(5)
        
        # Find text area
        print("[UI] Looking for text area...")
        text_area = None
        selectors = [
            "//div[@role='textbox']",
            "//div[@contenteditable='true']",
            "//div[contains(@aria-label, 'Text editor')]"
        ]
        
        for selector in selectors:
            try:
                text_area = driver.find_element(By.XPATH, selector)
                if text_area:
                    print(f"[OK] Found text area")
                    break
            except:
                continue
        
        if text_area:
            # Clear and type content
            print("[TYPE] Clearing text area...")
            text_area.click()
            time.sleep(1)
            text_area.send_keys(Keys.CONTROL + "a")
            time.sleep(0.5)
            text_area.send_keys(Keys.DELETE)
            time.sleep(1)
            
            print("[TYPE] Typing YouTube stream content...")
            # Type line by line
            lines = content.split('\n')
            for i, line in enumerate(lines):
                print(f"  Line {i+1}: {line[:50]}...")
                text_area.send_keys(line)
                if i < len(lines) - 1:
                    text_area.send_keys(Keys.RETURN)
                time.sleep(0.5)
            
            time.sleep(2)
            
            # Find the Post button
            print("\n[BUTTON] Looking for Post button...")
            post_button = None
            
            # Try the specific selector we know works
            try:
                post_button = driver.find_element(By.XPATH, "//button[contains(@class, 'share-actions__primary-action') and contains(@class, 'artdeco-button--primary')]")
                if post_button:
                    print(f"[OK] Found Post button!")
                    print(f"  Text: '{post_button.text}'")
                    print(f"  Enabled: {post_button.is_enabled()}")
                    print(f"  Displayed: {post_button.is_displayed()}")
            except:
                print("[ERROR] Could not find Post button with primary selector")
            
            if post_button and post_button.is_enabled():
                print("\n[ACTION] Clicking Post button...")
                
                # Scroll into view
                driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                time.sleep(1)
                
                # Click the button
                try:
                    action = ActionChains(driver)
                    action.move_to_element(post_button)
                    action.pause(1)
                    action.click()
                    action.perform()
                    print("[CLICK] Post button clicked with ActionChains!")
                except Exception as e:
                    print(f"[FALLBACK] ActionChains failed: {e}")
                    driver.execute_script("arguments[0].click();", post_button)
                    print("[CLICK] Post button clicked with JavaScript!")
                
                # Wait and check result
                print("\n[WAIT] Waiting for post to complete...")
                time.sleep(5)
                
                current_url = driver.current_url
                print(f"[URL] Current URL: {current_url}")
                
                if "share" not in current_url:
                    print("[SUCCESS] [OK] Post completed - redirected from share page!")
                    print("[SUCCESS] [OK] YouTube stream data was posted to LinkedIn!")
                else:
                    print("[WARNING] Still on share page - checking for errors...")
                    
                    # Check for error messages
                    try:
                        errors = driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-toast-item--error')]")
                        if errors:
                            print("[ERROR] LinkedIn error message found!")
                            for err in errors:
                                print(f"  Error: {err.text}")
                    except:
                        pass
                    
                    # Check if post went through anyway
                    print("[CHECK] Waiting 5 more seconds...")
                    time.sleep(5)
                    
                    current_url = driver.current_url
                    if "share" not in current_url:
                        print("[SUCCESS] [OK] Post completed after delay!")
                    else:
                        print("[FAIL] Post may not have completed")
                        print("[INFO] Check LinkedIn manually to verify")
            else:
                print("[ERROR] Post button not found or not enabled!")
                
        else:
            print("[ERROR] Could not find text area")
        
        print("\n[INFO] Keeping browser open for 10 seconds...")
        time.sleep(10)
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[INFO] Closing browser...")
        driver.quit()

if __name__ == "__main__":
    test_linkedin_post_with_youtube()