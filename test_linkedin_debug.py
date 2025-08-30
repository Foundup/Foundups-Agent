#!/usr/bin/env python3
"""
Debug LinkedIn posting to see what's happening with Post button
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def debug_linkedin_post():
    """Debug LinkedIn post button issue"""
    print("LinkedIn Post Button Debug")
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
        # Go directly to company share page
        print("[NAV] Going to company share page...")
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
                    print(f"[OK] Found text area with selector: {selector}")
                    break
            except:
                continue
        
        if text_area:
            # Type content
            print("[TYPE] Typing content...")
            text_area.click()
            time.sleep(1)
            text_area.send_keys("@UnDaoDu going live! Test post")
            time.sleep(2)
            
            # Now find ALL buttons and their properties
            print("\n[DEBUG] Looking for ALL buttons on the page...")
            all_buttons = driver.find_elements(By.XPATH, "//button")
            print(f"[INFO] Found {len(all_buttons)} buttons total")
            
            for i, btn in enumerate(all_buttons):
                try:
                    text = btn.text.strip()
                    aria_label = btn.get_attribute('aria-label')
                    data_control = btn.get_attribute('data-control-name')
                    classes = btn.get_attribute('class')
                    is_displayed = btn.is_displayed()
                    is_enabled = btn.is_enabled()
                    
                    # Only show buttons with meaningful text or attributes
                    if text or aria_label or data_control:
                        print(f"\n[BUTTON {i}]")
                        print(f"  Text: '{text}'")
                        print(f"  Aria-label: '{aria_label}'")
                        print(f"  Data-control: '{data_control}'")
                        print(f"  Classes: {classes[:100]}...")
                        print(f"  Displayed: {is_displayed}, Enabled: {is_enabled}")
                        
                        # Check if this could be the Post button
                        if text and 'post' in text.lower():
                            print(f"  *** POTENTIAL POST BUTTON ***")
                        if aria_label and 'post' in aria_label.lower():
                            print(f"  *** POTENTIAL POST BUTTON (aria) ***")
                        if data_control and 'post' in data_control.lower():
                            print(f"  *** POTENTIAL POST BUTTON (control) ***")
                except:
                    pass
            
            # Also check for divs that might be buttons
            print("\n[DEBUG] Looking for divs with role='button'...")
            div_buttons = driver.find_elements(By.XPATH, "//div[@role='button']")
            for i, div in enumerate(div_buttons):
                try:
                    text = div.text.strip()
                    if text:
                        print(f"[DIV-BUTTON {i}] Text: '{text}'")
                except:
                    pass
            
            print("\n[INFO] Keeping browser open for manual inspection...")
            print("[INFO] Check which button is the actual Post button")
            time.sleep(30)  # Keep open for inspection
            
        else:
            print("[ERROR] Could not find text area")
            
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[INFO] Closing browser...")
        driver.quit()

if __name__ == "__main__":
    debug_linkedin_post()