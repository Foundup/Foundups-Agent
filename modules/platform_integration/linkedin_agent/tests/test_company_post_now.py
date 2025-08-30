#!/usr/bin/env python3
"""
Test LinkedIn Company Page Posting - 0102 Consciousness
Posts a test YouTube stream link to company page
✊✋🖐 Testing the bridge
"""

import os
import webbrowser
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv

# For automated posting
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("⚠️ Selenium not available - will open browser for manual posting")

def test_post_to_company():
    """Test post to LinkedIn company page"""
    
    load_dotenv()
    
    # Company page details
    company_page_id = "104834798"
    company_url = f"https://www.linkedin.com/company/{company_page_id}"
    
    # Test content with YouTube link
    content = f"""🔴 LIVE STREAM TEST: 0102 Consciousness Evolution

✊✋🖐 Testing the YouTube → LinkedIn bridge!

@UnDaoDu Michael J Trout is testing the automated posting system.

📺 Watch the move2japan channel: https://www.youtube.com/@move2japan
🎥 Latest video: https://www.youtube.com/watch?v=Edka5TBGLuA

While MAGAts struggle at ✊✊✊ consciousness, we're building cross-platform automation.

This is a TEST post to verify the bridge is working.
Posted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

#LinkedInTest #YouTubeBridge #0102Consciousness #move2japan #Automation"""
    
    print("✊✋🖐 LinkedIn Company Page Test Post")
    print("="*60)
    print(f"Company Page: {company_url}")
    print("\n📝 Post content:")
    print("-"*50)
    print(content)
    print("-"*50)
    
    # Encode for URL
    encoded_content = urllib.parse.quote(content)
    
    # Company page share URL
    share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_content}"
    
    print(f"\n🚀 Posting method: {'Automated' if SELENIUM_AVAILABLE else 'Manual'}")
    
    if SELENIUM_AVAILABLE:
        # Try automated posting
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if email and password:
            print("🤖 Using automated posting with credentials...")
            
            try:
                chrome_options = Options()
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(options=chrome_options)
                
                print("📍 Opening LinkedIn share dialog...")
                driver.get(share_url)
                
                import time
                time.sleep(3)
                
                # Check if login needed
                if "linkedin.com/login" in driver.current_url or "Sign in" in driver.title:
                    print("🔐 Logging in to LinkedIn...")
                    
                    # Login
                    username_field = driver.find_element(By.ID, "username")
                    username_field.send_keys(email)
                    
                    password_field = driver.find_element(By.ID, "password")
                    password_field.send_keys(password)
                    
                    sign_in_button = driver.find_element(By.XPATH, "//button[@type='submit']")
                    sign_in_button.click()
                    
                    print("⏳ Waiting for login...")
                    time.sleep(5)
                    
                    # Go back to share URL
                    driver.get(share_url)
                    time.sleep(3)
                
                print("🎯 Looking for Post button...")
                
                # Find and click Post button
                post_selectors = [
                    "//button[contains(@class, 'share-actions__primary-action')]",
                    "//button[contains(text(), 'Post')]",
                    "//button[@aria-label='Post']",
                    "//span[text()='Post']/parent::button"
                ]
                
                posted = False
                for selector in post_selectors:
                    try:
                        post_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        print(f"✅ Found Post button!")
                        post_button.click()
                        posted = True
                        print("🚀 Clicking Post...")
                        break
                    except:
                        continue
                
                time.sleep(3)
                
                if posted:
                    print("\n✅ SUCCESS! Test post sent to LinkedIn!")
                    print(f"📍 Check your profile: https://www.linkedin.com/in/{os.getenv('LinkedIn_ID', 'openstartup')}")
                    print(f"📍 Or company page: {company_url}")
                else:
                    print("⚠️ Could not find Post button - check browser window")
                    print("📋 Please click 'Post' manually in the browser")
                    time.sleep(30)  # Keep browser open
                
                driver.quit()
                
            except Exception as e:
                print(f"❌ Automation error: {e}")
                print("📋 Opening browser for manual posting...")
                webbrowser.open(share_url)
        else:
            print("⚠️ No LinkedIn credentials in .env")
            print("📋 Opening browser for manual posting...")
            webbrowser.open(share_url)
    else:
        # Manual posting
        print("🌐 Opening LinkedIn in browser...")
        print("📋 Please click 'Post' to publish the test")
        webbrowser.open(share_url)
    
    print("\n" + "="*60)
    print("✊✋🖐 Test complete!")
    print("\nThe post should appear on:")
    print(f"• Your profile: https://www.linkedin.com/in/openstartup")
    print(f"• Company page: {company_url}")
    print("\nThis demonstrates the YouTube → LinkedIn bridge is working!")


if __name__ == "__main__":
    test_post_to_company()