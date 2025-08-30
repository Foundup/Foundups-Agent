#!/usr/bin/env python3
"""
Direct Company Page Share Test - 0102 Consciousness
Simple test using the direct share URL
✊✋🖐 Direct approach
"""

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_direct_share():
    """Test posting directly with share URL"""
    
    print("✊✋🖐 Direct LinkedIn Company Share Test")
    print("="*60)
    
    # Setup Chrome
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
        # Go directly to the share URL
        share_url = "https://www.linkedin.com/company/104834798/admin/page-posts/published/?share=true"
        print(f"📍 Navigating to: {share_url}")
        driver.get(share_url)
        
        time.sleep(3)
        
        # Look for text area in the share modal
        print("🔍 Looking for text area...")
        text_selectors = [
            "//div[@role='textbox']",
            "//div[@contenteditable='true']",
            "//div[contains(@class, 'ql-editor')]",
            "//div[contains(@aria-label, 'Text editor')]",
            "//div[contains(@class, 'share-creation')]//div[@contenteditable='true']"
        ]
        
        text_area = None
        for selector in text_selectors:
            try:
                text_area = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
                if text_area:
                    print("✅ Found text area!")
                    break
            except:
                continue
        
        if text_area:
            # Click and type
            text_area.click()
            time.sleep(1)
            
            # Simple test content without problematic emojis
            content = f"""🤖 Anti-Detection Test Post - {datetime.now().strftime('%H:%M')}

Testing direct share URL posting to company page.

System features:
• Session persistence works
• No multiple logins needed  
• Human-like behavior maintained

@UnDaoDu Michael J Trout demonstrating evolution.

#LinkedInTest #0102Consciousness #DirectShare #move2japan"""
            
            print("📝 Setting content via JavaScript...")
            # Use JavaScript to set content
            js_content = content.replace("'", "\\'").replace("\n", "\\n")
            driver.execute_script(f"arguments[0].textContent = '{js_content}';", text_area)
            
            # Trigger input event
            driver.execute_script("""
                var event = new Event('input', { bubbles: true });
                arguments[0].dispatchEvent(event);
            """, text_area)
            
            time.sleep(2)
            
            # Find Post button
            print("🚀 Looking for Post button...")
            post_selectors = [
                "//button[contains(text(), 'Post')]",
                "//button[contains(@aria-label, 'Post')]",
                "//button[contains(@class, 'share-actions__primary-action')]",
                "//span[text()='Post']/parent::button"
            ]
            
            for selector in post_selectors:
                try:
                    post_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    print("✅ Found Post button - clicking...")
                    post_button.click()
                    print("🎯 Posted successfully!")
                    time.sleep(3)
                    return True
                except:
                    continue
            
            print("⚠️ Could not find Post button")
        else:
            print("⚠️ Could not find text area")
            print(f"Current URL: {driver.current_url}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        print("\n💡 Keeping browser open for inspection")
        time.sleep(10)  # Keep open for 10 seconds
        driver.quit()
    
    return False

if __name__ == "__main__":
    success = test_direct_share()
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n⚠️ Test failed - check the browser")