#!/usr/bin/env python3
"""
Debug why X post content doesn't match what we type
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

def debug_x_content():
    """Debug content typing issue"""
    print("X/Twitter Content Debug")
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
        # Go to compose
        print("[1] Going to compose page...")
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        # Find text area
        print("[2] Finding text area...")
        text_area = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        
        # Test different typing methods
        print("\n[3] Testing different typing methods...")
        
        # Method 1: Direct send_keys
        print("\n--- Method 1: Direct send_keys ---")
        text_area.click()
        time.sleep(1)
        text_area.clear()
        
        test_content = "@UnDaoDu TEST 1 - Direct typing"
        print(f"Typing: {test_content}")
        text_area.send_keys(test_content)
        time.sleep(3)
        
        # Read back what's actually in the text area
        actual_content = text_area.text
        print(f"Actually shows: {actual_content}")
        
        if actual_content != test_content:
            print("[WARNING] MISMATCH DETECTED!")
            print(f"Expected: '{test_content}'")
            print(f"Actual: '{actual_content}'")
        
        time.sleep(3)
        
        # Clear for next test
        text_area.send_keys(Keys.CONTROL + "a")
        text_area.send_keys(Keys.DELETE)
        time.sleep(2)
        
        # Method 2: Character by character
        print("\n--- Method 2: Character by character ---")
        test_content = "@UnDaoDu TEST 2 - Char by char"
        print(f"Typing: {test_content}")
        
        for char in test_content:
            text_area.send_keys(char)
            time.sleep(0.05)
        
        time.sleep(3)
        actual_content = text_area.text
        print(f"Actually shows: {actual_content}")
        
        if actual_content != test_content:
            print("[WARNING] MISMATCH DETECTED!")
            print(f"Expected: '{test_content}'")
            print(f"Actual: '{actual_content}'")
        
        time.sleep(3)
        
        # Clear for next test
        text_area.send_keys(Keys.CONTROL + "a")
        text_area.send_keys(Keys.DELETE)
        time.sleep(2)
        
        # Method 3: JavaScript
        print("\n--- Method 3: JavaScript injection ---")
        test_content = "@UnDaoDu TEST 3 - JavaScript"
        print(f"Typing: {test_content}")
        
        # Set via JavaScript
        driver.execute_script(f"arguments[0].textContent = '{test_content}';", text_area)
        
        # Trigger input event
        driver.execute_script("""
            var event = new Event('input', { bubbles: true });
            arguments[0].dispatchEvent(event);
        """, text_area)
        
        time.sleep(3)
        actual_content = text_area.text
        print(f"Actually shows: {actual_content}")
        
        if actual_content != test_content:
            print("[WARNING] MISMATCH DETECTED!")
            print(f"Expected: '{test_content}'")
            print(f"Actual: '{actual_content}'")
        
        # Method 4: Test with newlines
        print("\n--- Method 4: Content with newlines ---")
        text_area.send_keys(Keys.CONTROL + "a")
        text_area.send_keys(Keys.DELETE)
        time.sleep(2)
        
        test_content = "@UnDaoDu going live!\n\nTest Stream\n\nhttps://youtube.com/watch"
        print(f"Typing (with newlines):")
        print(test_content)
        
        lines = test_content.split('\n')
        for i, line in enumerate(lines):
            text_area.send_keys(line)
            if i < len(lines) - 1:
                text_area.send_keys(Keys.RETURN)
        
        time.sleep(3)
        actual_content = text_area.text
        print(f"\nActually shows:")
        print(actual_content)
        
        # Check for differences
        if actual_content != test_content:
            print("\n[WARNING] DIFFERENCES FOUND:")
            print(f"Expected length: {len(test_content)}")
            print(f"Actual length: {len(actual_content)}")
            print(f"Expected: '{test_content}'")
            print(f"Actual: '{actual_content}'")
            
            # Character comparison
            for i, (expected, actual) in enumerate(zip(test_content, actual_content)):
                if expected != actual:
                    print(f"  Position {i}: expected '{expected}' (ord={ord(expected)}), got '{actual}' (ord={ord(actual)})")
        
        print("\n[4] Keeping browser open for manual inspection...")
        print("Check what actually appears in the compose box")
        time.sleep(30)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()

if __name__ == "__main__":
    debug_x_content()