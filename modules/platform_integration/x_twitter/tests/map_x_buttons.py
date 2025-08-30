#!/usr/bin/env python3
"""
Interactive X/Twitter button mapper
Highlights each button one by one for identification
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

def map_x_buttons():
    """Map all buttons on X compose page"""
    print("X/Twitter Button Mapper")
    print("=" * 60)
    print("I will highlight each button in RED")
    print("Tell me what each button is")
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
        # Go to compose page
        print("\n[SETUP] Going to compose page...")
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        # Type some content
        print("[SETUP] Adding test content...")
        text_area = driver.find_element(By.XPATH, "//div[@role='textbox']")
        text_area.click()
        text_area.send_keys("Test post for button mapping")
        time.sleep(2)
        
        # Find ALL buttons
        print("\n[MAPPING] Finding all buttons...")
        all_buttons = driver.find_elements(By.XPATH, "//button | //div[@role='button']")
        
        # Filter for visible buttons only
        visible_buttons = []
        for btn in all_buttons:
            try:
                if btn.is_displayed() and btn.is_enabled():
                    visible_buttons.append(btn)
            except:
                pass
        
        print(f"Found {len(visible_buttons)} visible buttons\n")
        
        button_map = {}
        
        for i, btn in enumerate(visible_buttons):
            try:
                # Get button properties
                text = btn.text.strip()
                aria = btn.get_attribute('aria-label')
                testid = btn.get_attribute('data-testid')
                tag = btn.tag_name
                
                # Clear previous highlight
                driver.execute_script("document.querySelectorAll('*').forEach(el => el.style.border = '');")
                
                # Highlight this button
                driver.execute_script("arguments[0].style.border = '5px solid red';", btn)
                driver.execute_script("arguments[0].scrollIntoView(true);", btn)
                
                print(f"\n========== BUTTON {i+1}/{len(visible_buttons)} ==========")
                print(f"Text: '{text}'")
                print(f"Aria-label: '{aria}'")
                print(f"Data-testid: '{testid}'")
                print(f"Tag: {tag}")
                print("THIS BUTTON IS NOW HIGHLIGHTED IN RED")
                
                # Auto-identify known buttons
                if testid == 'tweetButton':
                    print(">>> IDENTIFIED: This is the POST/TWEET button!")
                elif testid == 'scheduleOption':
                    print(">>> IDENTIFIED: Schedule post button")
                elif testid == 'grokImgGen':
                    print(">>> IDENTIFIED: Grok AI enhancement button")
                elif testid == 'addButton':
                    print(">>> IDENTIFIED: Add another tweet to thread")
                elif 'reply' in str(testid).lower():
                    print(">>> IDENTIFIED: Reply button")
                elif 'retweet' in str(testid).lower():
                    print(">>> IDENTIFIED: Retweet button")
                elif 'like' in str(testid).lower():
                    print(">>> IDENTIFIED: Like button")
                else:
                    print(">>> UNKNOWN: Needs identification")
                
                # Wait 10 seconds before moving to next
                print("Moving to next button in 10 seconds...")
                time.sleep(10)
                
                # Store mapping
                if testid:
                    button_map[testid] = {
                        'text': text,
                        'aria': aria,
                        'purpose': 'USER TO IDENTIFY'
                    }
                
            except Exception as e:
                print(f"Error with button {i}: {e}")
                continue
        
        # Summary
        print("\n" + "=" * 60)
        print("BUTTON MAPPING COMPLETE")
        print("=" * 60)
        print("\nIdentified buttons with data-testid:")
        for testid, info in button_map.items():
            print(f"\n{testid}:")
            print(f"  Text: '{info['text']}'")
            print(f"  Aria: '{info['aria']}'")
        
        print("\n[INFO] Keeping browser open for 30 seconds...")
        time.sleep(30)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    map_x_buttons()