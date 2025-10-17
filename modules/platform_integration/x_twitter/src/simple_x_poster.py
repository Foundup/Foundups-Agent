#!/usr/bin/env python3
"""
Simple X/Twitter poster that finds the POST button as the LAST button
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if sys.platform.startswith('win'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
# === END UTF-8 ENFORCEMENT ===


import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

class SimpleXPoster:
    """Simple X poster that uses the last button as POST"""
    
    def __init__(self):
        self.username = os.getenv('X_Acc2', os.getenv('X_Acc1', 'foundups'))
        self.password = os.getenv('x_Acc_pass')
        
    def post_to_x(self, content: str) -> bool:
        """Post to X/Twitter - POST button is the LAST button"""
        
        print(f"\n[X/TWITTER] Posting content...")
        
        # Setup Chrome
        chrome_options = Options()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use profile if exists
        profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile"
        if os.path.exists(profile_dir):
            chrome_options.add_argument(f'--user-data-dir={profile_dir}')
        
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            # Go to compose
            print("[NAV] Going to X compose page...")
            driver.get("https://x.com/compose/post")
            time.sleep(5)
            
            # Check if need to login
            if "login" in driver.current_url.lower():
                print("[LOGIN] Need to authenticate...")
                # Login process here if needed
                pass
            
            # Find text box
            print("[COMPOSE] Finding text box...")
            textbox = None
            for selector in ['[role="textbox"]', '[contenteditable="true"]', '.DraftEditor-root']:
                try:
                    textbox = driver.find_element(By.CSS_SELECTOR, selector)
                    if textbox:
                        break
                except:
                    continue
            
            if not textbox:
                print("[ERROR] Could not find text box")
                return False
            
            # Type content
            print("[TYPE] Entering content...")
            textbox.click()
            time.sleep(1)
            
            # Clear first
            textbox.send_keys(Keys.CONTROL + "a")
            textbox.send_keys(Keys.DELETE)
            time.sleep(1)
            
            # Type character by character to avoid emoji issues
            for char in content:
                if ord(char) > 127:  # Skip non-ASCII characters
                    continue
                textbox.send_keys(char)
                time.sleep(0.02)
            
            time.sleep(2)
            
            # Find ALL visible buttons
            print("[BUTTON] Finding POST button (last button)...")
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            visible_buttons = [btn for btn in all_buttons if btn.is_displayed()]
            
            if visible_buttons:
                # The POST button is the LAST visible button!
                post_button = visible_buttons[-1]
                
                print(f"[FOUND] Last button text: '{post_button.text.strip()}'")
                print("[CLICK] Clicking the LAST button (POST)...")
                
                # Highlight it first
                driver.execute_script("arguments[0].style.border = '3px solid green';", post_button)
                time.sleep(1)
                
                # Click it
                try:
                    post_button.click()
                except:
                    driver.execute_script("arguments[0].click();", post_button)
                
                print("[OK] Clicked POST button!")
                time.sleep(5)
                
                # Check if posted
                if "compose" not in driver.current_url:
                    print("[SUCCESS] Post sent successfully!")
                    return True
                else:
                    # Check if text cleared
                    try:
                        current_text = textbox.text
                        if not current_text:
                            print("[SUCCESS] Text cleared - post sent!")
                            return True
                    except:
                        pass
                    
                    print("[WARNING] May not have posted")
                    return False
            else:
                print("[ERROR] No buttons found")
                return False
                
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
        finally:
            driver.quit()

# Test function
def test_post():
    """Test posting with live stream info"""
    poster = SimpleXPoster()
    
    content = """[LIVE] NOW: Where is #Trump? #MAGA #ICEraids Move2Japan Show LIVE!

Watch: https://youtube.com/watch?v=PD-NYPQtEZ8

Join us for AI development!

#AI #LiveCoding #FoundUps"""
    
    success = poster.post_to_x(content)
    
    if success:
        print("\n[TEST] Successfully posted to X/Twitter!")
    else:
        print("\n[TEST] Failed to post to X/Twitter")
    
    return success

if __name__ == "__main__":
    test_post()