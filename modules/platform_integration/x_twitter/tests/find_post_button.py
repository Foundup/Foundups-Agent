#!/usr/bin/env python3
"""
Find the X/Twitter Post button - it's the LAST button!
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
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def find_post_button():
    """Find the Post button by getting the LAST button"""
    print("X/Twitter Post Button Finder")
    print("=" * 60)
    
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        print("[1] Going to X/Twitter compose...")
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        print("[2] Finding text box...")
        textbox = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[role="textbox"]'))
        )
        
        print("[3] Typing test content...")
        textbox.click()
        time.sleep(1)
        
        # Type simple text without emojis
        test_text = "LIVE NOW: Stream is active! Watch at youtube.com/watch?v=PD-NYPQtEZ8"
        textbox.send_keys(test_text)
        time.sleep(2)
        
        print("[4] Finding ALL buttons...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        
        print(f"\nTotal buttons found: {len(all_buttons)}")
        print("\nButton list:")
        print("-" * 40)
        
        visible_buttons = []
        for i, btn in enumerate(all_buttons):
            if btn.is_displayed():
                text = btn.text.strip()
                aria = btn.get_attribute("aria-label")
                testid = btn.get_attribute("data-testid")
                
                visible_buttons.append(btn)
                print(f"{i+1}. Text: '{text}' | Aria: '{aria}' | TestID: '{testid}'")
        
        print("-" * 40)
        print(f"\nTotal visible buttons: {len(visible_buttons)}")
        
        if visible_buttons:
            # The LAST button should be POST
            last_button = visible_buttons[-1]
            print(f"\n[5] THE LAST BUTTON IS:")
            print(f"   Text: '{last_button.text.strip()}'")
            print(f"   Aria: '{last_button.get_attribute('aria-label')}'")
            print(f"   TestID: '{last_button.get_attribute('data-testid')}'")
            
            # Highlight it in red
            driver.execute_script("arguments[0].style.border = '5px solid red';", last_button)
            print("\n[6] HIGHLIGHTED THE LAST BUTTON IN RED!")
            print("   This should be the POST button")
            
            # Also check the last few buttons
            if len(visible_buttons) >= 3:
                print("\n[7] Last 3 buttons for reference:")
                for i in range(-3, 0):
                    btn = visible_buttons[i]
                    print(f"   {i}: '{btn.text.strip()}' / '{btn.get_attribute('aria-label')}'")
        
        print("\n[8] Keeping browser open for inspection...")
        print("   Check if the red-bordered button is the POST button")
        print("   Press Ctrl+C to close")
        
        time.sleep(60)
        
    except KeyboardInterrupt:
        print("\n[STOP] Closing...")
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    find_post_button()