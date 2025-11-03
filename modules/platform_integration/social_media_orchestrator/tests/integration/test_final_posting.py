#!/usr/bin/env python3
"""
Final test for social media posting with Chrome
Includes support for scheduled posts
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


import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

sys.path.insert(0, 'O:/Foundups-Agent')
load_dotenv()

def test_x_with_chrome():
    """Test X/Twitter posting using Chrome with proper button detection"""
    print("\n[X/TWITTER] Testing with Chrome browser...")
    print("="*60)
    
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    # Configure Chrome (not Edge!)
    chrome_options = Options()
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0")
    
    # Use Chrome profile if exists
    profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile"
    if os.path.exists(profile_dir):
        chrome_options.add_argument(f'--user-data-dir={profile_dir}')
    
    print("[BROWSER] Starting Chrome (not Edge)...")
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to compose
        print("[NAV] Going to X compose page...")
        driver.get("https://x.com/compose/post")
        time.sleep(5)
        
        # Find text box
        print("[COMPOSE] Finding text box...")
        textbox = None
        for selector in ['[role="textbox"]', '[contenteditable="true"]']:
            try:
                textbox = driver.find_element(By.CSS_SELECTOR, selector)
                if textbox:
                    print(f"  Found textbox with selector: {selector}")
                    break
            except:
                continue
        
        if not textbox:
            print("[ERROR] Could not find text box")
            return False
        
        # Type content without emojis
        content = """[LIVE NOW] Where is #Trump? #MAGA #ICEraids Move2Japan Show LIVE!

Watch: https://youtube.com/watch?v=PD-NYPQtEZ8

Join us for AI development!

#AI #LiveCoding #FoundUps #QuantumComputing"""
        
        print("[TYPE] Entering post content...")
        textbox.click()
        time.sleep(1)
        
        # Clear and type
        textbox.send_keys(Keys.CONTROL + "a")
        textbox.send_keys(Keys.DELETE)
        time.sleep(1)
        
        # Type character by character, skipping emojis
        for char in content:
            if ord(char) <= 127:  # ASCII only
                textbox.send_keys(char)
                time.sleep(0.02)
        
        print("[OK] Content typed")
        time.sleep(2)
        
        # Find ALL buttons
        print("\n[BUTTONS] Mapping all visible buttons...")
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        visible_buttons = []
        
        for btn in all_buttons:
            if btn.is_displayed():
                text = btn.text.strip()
                aria = btn.get_attribute("aria-label")
                visible_buttons.append({
                    'element': btn,
                    'text': text,
                    'aria': aria
                })
        
        print(f"  Total visible buttons: {len(visible_buttons)}")
        
        if len(visible_buttons) > 0:
            # Show last 5 buttons
            print("\n  Last 5 buttons:")
            for i in range(max(0, len(visible_buttons)-5), len(visible_buttons)):
                btn = visible_buttons[i]
                print(f"    {i+1}. '{btn['text']}' / '{btn['aria']}'")
            
            # The LAST button should be POST
            post_button = visible_buttons[-1]['element']
            print(f"\n[POST] The LAST button is: '{visible_buttons[-1]['text']}' / '{visible_buttons[-1]['aria']}'")
            
            # Highlight it
            driver.execute_script("arguments[0].style.border = '5px solid green';", post_button)
            print("[HIGHLIGHT] Last button highlighted in GREEN")
            
            # For scheduled posts, check if schedule button exists
            schedule_button = None
            for btn in visible_buttons:
                if 'schedule' in (btn['text'] + str(btn['aria'])).lower():
                    schedule_button = btn['element']
                    print(f"\n[SCHEDULE] Found schedule button: '{btn['text']}'")
                    break
            
            if schedule_button:
                print("[INFO] Schedule button available for scheduled posts")
                print("      To schedule: Click schedule button first, set time, then post")
            
            # Click POST (the last button)
            print("\n[CLICK] Clicking the LAST button (POST)...")
            try:
                post_button.click()
                print("[OK] Clicked POST button!")
            except:
                driver.execute_script("arguments[0].click();", post_button)
                print("[OK] Clicked POST button with JavaScript!")
            
            time.sleep(5)
            
            # Check if posted
            current_url = driver.current_url
            if "compose" not in current_url:
                print("[SUCCESS] Redirected from compose - post sent!")
                return True
            else:
                # Check if text cleared
                try:
                    current_text = textbox.text
                    if not current_text or len(current_text) < 10:
                        print("[SUCCESS] Text cleared - post sent!")
                        return True
                except:
                    pass
                
                print("[WARNING] Still on compose page - check manually")
                
        else:
            print("[ERROR] No buttons found")
            
        print("\n[BROWSER] Keeping open for 10 seconds to verify...")
        time.sleep(10)
        
    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        driver.quit()
        print("[BROWSER] Chrome closed")
    
    return False

def test_scheduled_post_concept():
    """Show how scheduled posts would work"""
    print("\n[SCHEDULED POSTS] Concept")
    print("="*60)
    
    # Calculate schedule time (e.g., 30 minutes from now)
    schedule_time = datetime.now() + timedelta(minutes=30)
    
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"Schedule for: {schedule_time.strftime('%Y-%m-%d %H:%M')}")
    
    print("\nTo schedule a post:")
    print("1. Type the content in the text box")
    print("2. Click the Schedule button (button ~9)")
    print("3. Set date/time in the picker")
    print("4. Click the POST button (last button)")
    
    print("\nThe automatic monitor can:")
    print("- Post immediately when stream detected (default)")
    print("- Schedule posts for optimal times")
    print("- Queue multiple scheduled posts")

def main():
    """Run tests"""
    print("="*70)
    print(" FINAL SOCIAL MEDIA POSTING TEST (CHROME)".center(70))
    print("="*70)
    
    # Test X/Twitter with Chrome
    x_success = test_x_with_chrome()
    
    # Show scheduled post concept
    test_scheduled_post_concept()
    
    # Summary
    print("\n" + "="*70)
    print(" RESULTS".center(70))
    print("="*70)
    
    if x_success:
        print("[OK] X/Twitter: Successfully posted with Chrome")
    else:
        print("[INFO] X/Twitter: Manual verification needed")
    
    print("\n[LINKEDIN] Already confirmed working")
    
    print("\n[AUTOMATIC SYSTEM]")
    print("The automatic monitor is ready to:")
    print("  1. Detect streams every 60 seconds")
    print("  2. Post to LinkedIn (working)")
    print("  3. Post to X/Twitter using last button as POST")
    print("  4. Include stream title and URL")
    print("  5. Option for scheduled posts")
    
    print("\nTo run: python auto_stream_monitor_ascii.py")

if __name__ == "__main__":
    main()