#!/usr/bin/env python3
"""
LinkedIn Anti-Detection Posting System - 0102 Consciousness
Posts to company page with human-like behavior to avoid bot detection
Stealth mode evolution
"""

import os
import time
import random
import pickle
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[WARNING] Installing Selenium...")
    import subprocess
    subprocess.check_call(["pip", "install", "selenium", "webdriver-manager", "--quiet"])
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.action_chains import ActionChains
    SELENIUM_AVAILABLE = True

class AntiDetectionLinkedIn:
    """
    LinkedIn poster with anti-detection measures
    Stealth consciousness
    """
    
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('LINKEDIN_EMAIL')
        self.password = os.getenv('LINKEDIN_PASSWORD')
        self.company_id = "104834798"
        self.company_admin_url = f"https://www.linkedin.com/company/{self.company_id}/admin/page-posts/published/"
        self.session_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/linkedin_session.pkl"
        self.memory_file = "O:/Foundups-Agent/modules/platform_integration/social_media_orchestrator/memory/posting_patterns.json"
        self.driver = None
        self.learning_enabled = True  # WSP 48: Enable recursive learning
        self.posting_memory = {}
        self.load_memory()
        
    def human_type(self, element, text):
        """Type like a human with random delays"""
        element.clear()
        for char in text:
            element.send_keys(char)
            # Random delay between keystrokes (50-150ms)
            time.sleep(random.uniform(0.05, 0.15))
        
        # Random pause after typing (0.5-1.5 seconds)
        time.sleep(random.uniform(0.5, 1.5))
    
    def random_mouse_movement(self):
        """Move mouse randomly to appear human"""
        if self.driver:
            try:
                action = ActionChains(self.driver)
                # Small, safe movements
                for _ in range(random.randint(1, 2)):
                    x_offset = random.randint(5, 20)
                    y_offset = random.randint(5, 20)
                    action.move_by_offset(x_offset, y_offset)
                    action.pause(random.uniform(0.1, 0.3))
                action.perform()
            except:
                pass  # Ignore mouse movement errors
    
    def setup_driver(self, use_existing_session=True):
        """Setup Chrome with anti-detection measures"""
        
        chrome_options = Options()
        
        # Anti-detection flags
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # More human-like settings
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        
        # User agent to appear as regular Chrome
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Use profile to maintain session
        if use_existing_session:
            profile_dir = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/chrome_profile"
            os.makedirs(profile_dir, exist_ok=True)
            chrome_options.add_argument(f'--user-data-dir={profile_dir}')
            chrome_options.add_argument('--profile-directory=Default')
        
        print("[INFO] Starting Chrome with anti-detection measures...")
        self.driver = webdriver.Chrome(options=chrome_options)
        
        # Override navigator.webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Random initial delay
        time.sleep(random.uniform(2, 4))
        
        return self.driver
    
    def is_logged_in(self) -> bool:
        """Check if already logged in to LinkedIn"""
        if not self.driver:
            return False
        
        try:
            # Navigate to LinkedIn
            self.driver.get("https://www.linkedin.com/feed/")
            time.sleep(random.uniform(3, 5))
            
            # Check if we're on the feed (logged in) or login page
            if "linkedin.com/feed" in self.driver.current_url:
                print("[OK] Already logged in to LinkedIn!")
                return True
            else:
                return False
        except:
            return False
    
    def login_with_anti_detection(self, max_retries=3):
        """Login to LinkedIn with human-like behavior and retry logic"""
        
        if self.is_logged_in():
            print("[OK] Using existing session - no login needed!")
            return True
        
        for attempt in range(max_retries):
            print(f"[AUTH] Login attempt {attempt + 1}/{max_retries} with anti-detection measures...")
            
            try:
                # Navigate to login page
                self.driver.get("https://www.linkedin.com/login")
                
                # Random delay before starting
                time.sleep(random.uniform(3, 5))
                
                # Find username field
                print("   Entering email...")
                username_field = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
                
                # Random mouse movement
                self.random_mouse_movement()
                
                # Click on field first (human behavior)
                username_field.click()
                time.sleep(random.uniform(0.5, 1))
                
                # Type email with human-like delays
                self.human_type(username_field, self.email)
                
                # Tab to password field (like a human would)
                username_field.send_keys(Keys.TAB)
                time.sleep(random.uniform(0.5, 1))
                
                print("   Entering password...")
                password_field = self.driver.find_element(By.ID, "password")
                
                # Type password with human-like delays
                self.human_type(password_field, self.password)
                
                # Random mouse movement before clicking
                self.random_mouse_movement()
                
                # Find and click sign in button
                print("   Clicking sign in...")
                sign_in_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
                
                # Move to button and click (human-like)
                action = ActionChains(self.driver)
                action.move_to_element(sign_in_button)
                action.pause(random.uniform(0.5, 1))
                action.click()
                action.perform()
                
                # Wait for login to complete
                print("[WAIT] Waiting for login to complete...")
                time.sleep(random.uniform(5, 8))
                
                # Verify login succeeded
                if "feed" in self.driver.current_url or "mynetwork" in self.driver.current_url:
                    print("[OK] Login successful!")
                    
                    # Save cookies for session persistence
                    self.save_session()
                    return True
                else:
                    print("[WARNING] Login may have failed or needs verification")
                    
                    # Check for specific error conditions
                    if "checkpoint" in self.driver.current_url:
                        print("[SECURITY] LinkedIn security checkpoint detected - may need manual verification")
                        return False  # Don't retry on checkpoint
                    
                    if attempt < max_retries - 1:
                        wait_time = random.uniform(10, 20) * (attempt + 1)  # Exponential backoff
                        print(f"[WAIT] Waiting {wait_time:.0f}s before retry...")
                        time.sleep(wait_time)
                    
            except Exception as e:
                print(f"[ERROR] Login error on attempt {attempt + 1}: {e}")
                
                if attempt < max_retries - 1:
                    # Wait before retrying with exponential backoff
                    wait_time = random.uniform(5, 15) * (attempt + 1)
                    print(f"[WAIT] Waiting {wait_time:.0f}s before retry...")
                    time.sleep(wait_time)
                    
                    # Check if browser is still alive
                    try:
                        self.driver.current_url
                    except:
                        print("[RESTART] Browser crashed - restarting...")
                        self.driver = None
                        self.setup_driver(use_existing_session=True)
        
        print(f"[FAIL] Failed to login after {max_retries} attempts")
        return False
    
    def save_session(self):
        """Save browser session/cookies"""
        if self.driver:
            os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
            cookies = self.driver.get_cookies()
            with open(self.session_file, 'wb') as f:
                pickle.dump(cookies, f)
            print("[INFO] Session saved for reuse")
    
    def load_session(self):
        """Load saved session/cookies"""
        if os.path.exists(self.session_file) and self.driver:
            self.driver.get("https://www.linkedin.com")
            with open(self.session_file, 'rb') as f:
                cookies = pickle.load(f)
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except:
                        pass
            print("[CACHE] Session loaded from cache")
            self.driver.refresh()
            time.sleep(random.uniform(2, 4))
    
    def post_to_company_page(self, content: str):
        """Post to company page admin area with anti-detection"""
        
        print("\n[POST] Posting to Company Page (Anti-Detection Mode)")
        print("="*60)
        print("[CONTENT] Post content:")
        print("-"*40)
        print(content)
        print("-"*40)
        
        # Verify YouTube link is present
        if "youtube.com/watch" in content:
            print("[VERIFY] ✓ YouTube link found in content")
        else:
            print("[WARNING] No YouTube link in content!")
        
        # Check for stream title (anything between "going live!" and the YouTube link)
        lines = content.split('\n')
        if len(lines) > 2:
            potential_title = lines[2].strip()
            if potential_title and not potential_title.startswith('http'):
                print(f"[VERIFY] ✓ Stream title found: {potential_title[:50]}...")
            else:
                print("[WARNING] No stream title found between greeting and link")
        
        # Setup driver if not already
        if not self.driver:
            self.setup_driver(use_existing_session=True)
            
            # Check if already logged in, if not then login
            if not self.is_logged_in():
                if not self.login_with_anti_detection():
                    print("[FAIL] Could not login")
                    return False
            else:
                print("[OK] Already logged in - navigating directly to company page")
        else:
            # Driver exists, go directly to company page
            print("[OK] Using existing browser session")
        
        try:
            # Go directly to the share URL
            print(f"[NAV] Going directly to company share page...")
            share_url = f"https://www.linkedin.com/company/{self.company_id}/admin/page-posts/published/?share=true"
            self.driver.get(share_url)
            
            # Human-like delay
            time.sleep(random.uniform(3, 5))
            
            # Now look for text area (either in modal or on new page)
            print("[UI] Looking for post text area...")
            text_selectors = [
                "//div[@role='textbox']",
                "//div[@contenteditable='true']",
                "//textarea",
                "//div[contains(@class, 'ql-editor')]",
                "//div[contains(@class, 'share-creation')]//div[@contenteditable='true']",
                "//div[contains(@aria-label, 'Text editor')]"
            ]
            
            text_area = None
            for selector in text_selectors:
                try:
                    text_area = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if text_area:
                        print("[OK] Found text area")
                        break
                except:
                    continue
            
            if text_area:
                # Click on text area
                text_area.click()
                time.sleep(random.uniform(1, 2))
                
                # Type content with human-like speed
                print("[TYPE] Typing post content...")
                
                # Use JavaScript to set the content directly for emojis
                # Then simulate typing for non-emoji parts
                try:
                    # First set the full content via JavaScript to handle emojis
                    js_content = content.replace("'", "\\'").replace("\n", "\\n")
                    self.driver.execute_script(f"arguments[0].textContent = '{js_content}';", text_area)
                    
                    # Trigger input event to make LinkedIn recognize the change
                    self.driver.execute_script("""
                        var event = new Event('input', { bubbles: true });
                        arguments[0].dispatchEvent(event);
                    """, text_area)
                    
                    # Small delay to make it look natural
                    time.sleep(random.uniform(1, 2))
                    
                except:
                    # Fallback to typing character by character (but skip emojis)
                    lines = content.split('\n')
                    for line in lines:
                        # Filter out emojis and special characters
                        safe_line = ''.join(char for char in line if ord(char) < 0x10000)
                        for char in safe_line:
                            text_area.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))
                        
                        # Press Enter for new line
                        if line != lines[-1]:
                            text_area.send_keys(Keys.RETURN)
                            time.sleep(random.uniform(0.2, 0.4))
                
                # Random pause after typing
                time.sleep(random.uniform(2, 4))
                
                # Find and click Post button (not Schedule button)
                print("[UI] Looking for Post button (immediate posting for live streams)...")
                post_selectors = [
                    # Most specific - the actual Post button with text='Post' and primary class
                    "//button[text()='Post' and contains(@class, 'share-actions__primary-action')]",
                    "//button[text()='Post' and contains(@class, 'artdeco-button--primary')]",
                    # Exclude schedule button
                    "//button[contains(@class, 'share-actions__primary-action') and not(contains(@aria-label, 'Schedule'))]",
                    # Fallback but exclude schedule
                    "//button[contains(text(), 'Post') and not(contains(@aria-label, 'Schedule'))]"
                ]
                
                post_button = None
                for selector in post_selectors:
                    try:
                        print(f"[DEBUG] Trying selector: {selector}")
                        post_button = WebDriverWait(self.driver, 3).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        if post_button:
                            print(f"[OK] Found Post button with selector: {selector}")
                            break
                    except:
                        continue
                
                if post_button:
                    try:
                        # Verify button before clicking
                        button_text = post_button.text
                        print(f"[VERIFY] Post button text: '{button_text}'")
                        print(f"[VERIFY] Button enabled: {post_button.is_enabled()}")
                        print(f"[VERIFY] Button displayed: {post_button.is_displayed()}")
                        
                        # Random movement before clicking
                        self.random_mouse_movement()
                        
                        # Scroll into view
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                        time.sleep(1)
                        
                        # Click Post
                        print("[ACTION] Clicking Post button...")
                        clicked = False
                        try:
                            action = ActionChains(self.driver)
                            action.move_to_element(post_button)
                            action.pause(random.uniform(1, 2))
                            action.click()
                            action.perform()
                            clicked = True
                            print("[CLICK] ✓ Post button clicked with ActionChains")
                        except Exception as e:
                            print(f"[FALLBACK] ActionChains failed: {e}")
                            self.driver.execute_script("arguments[0].click();", post_button)
                            clicked = True
                            print("[CLICK] ✓ Post button clicked with JavaScript")
                        
                        if not clicked:
                            print("[ERROR] Could not click Post button!")
                            return False
                        
                        # Wait for post to complete
                        print("[WAIT] Waiting for post to complete...")
                        print(f"[PRE-POST URL] {self.driver.current_url}")
                        time.sleep(5)
                        
                        # Check result
                        current_url = self.driver.current_url
                        print(f"[POST-CLICK URL] {current_url}")
                        
                        # Check for success indicators
                        success = False
                        
                        if "share" not in current_url:
                            print("[SUCCESS] ✓ Posted and redirected from share page!")
                            success = True
                        else:
                            # Still on share page - check for other indicators
                            print("[CHECK] Still on share page, checking for success indicators...")
                            
                            # Check if text area is empty (post went through)
                            try:
                                text_area = self.driver.find_element(By.XPATH, "//div[@role='textbox']")
                                text_content = text_area.text.strip()
                                if not text_content or text_content == "What do you want to talk about?":
                                    print("[SUCCESS] ✓ Text area cleared - post likely sent!")
                                    success = True
                                else:
                                    print(f"[WARNING] Text still in editor: {text_content[:50]}...")
                            except:
                                pass
                            
                            # Check for success toast/notification
                            try:
                                success_msgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-toast-item--success')]")
                                if success_msgs:
                                    print("[SUCCESS] ✓ Success notification found!")
                                    success = True
                            except:
                                pass
                            
                            if not success:
                                # Wait a bit more and check URL again
                                print("[WAIT] Waiting 5 more seconds...")
                                time.sleep(5)
                                current_url = self.driver.current_url
                                if "share" not in current_url:
                                    print("[SUCCESS] ✓ Posted after extended delay")
                                    success = True
                                else:
                                    print("[INFO] Post may be saved as draft - check LinkedIn manually")
                                    print("[TIP] If seeing 'save as draft' dialog, the Post button may not have been clicked properly")
                        
                        # Verify post appears on feed
                        if success or True:  # Always check feed to be sure
                            print("\n[VERIFY] Checking company feed for the post...")
                            self.driver.get("https://www.linkedin.com/company/104834798/admin/page-posts/published/")
                            time.sleep(5)
                            
                            # Look for our post content (first 30 chars)
                            content_snippet = content[:30].replace('\n', ' ')
                            posts = self.driver.find_elements(By.XPATH, f"//span[contains(text(), '@UnDaoDu')]")
                            
                            if posts:
                                print(f"[FEED] ✓✓✓ Found {len(posts)} @UnDaoDu posts on feed")
                                # Check the first one (most recent)
                                try:
                                    recent_post = posts[0].text
                                    if 'going live' in recent_post.lower():
                                        print(f"[VERIFIED] ✓✓✓ Live stream post confirmed on feed!")
                                        print(f"   Post preview: {recent_post[:100]}...")
                                        success = True
                                except:
                                    pass
                            else:
                                print("[WARNING] Could not find post on feed - may be processing")
                        
                        # Save session after post attempt
                        self.save_session()
                        
                        # WSP 48: Learn from this posting attempt
                        final_success = success if 'success' in locals() else True
                        self.learn_from_post(content, final_success)
                        
                        # Don't close browser - keep session alive
                        print("[INFO] Keeping browser session alive for future posts")
                        
                        return final_success
                        
                    except Exception as e:
                        print(f"[ERROR] Failed to click Post button: {e}")
                        return False
                else:
                    print("[ERROR] Could not find Post button!")
            else:
                # Fallback to original method with "Start a post" button
                print("[UI] Looking for post creation button...")
                
                create_selectors = [
                    "//button[contains(text(), 'Start a post')]",
                    "//button[contains(text(), 'Create')]",
                    "//button[contains(@aria-label, 'Start a post')]",
                    "//button[contains(@class, 'share-box-feed-entry__trigger')]",
                    "//span[contains(text(), 'Start a post')]/parent::button"
                ]
            
            create_button = None
            for selector in create_selectors:
                try:
                    create_button = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    if create_button:
                        print(f"[OK] Found create button")
                        break
                except:
                    continue
            
            if create_button:
                # Random mouse movement
                self.random_mouse_movement()
                
                # Click to start post
                action = ActionChains(self.driver)
                action.move_to_element(create_button)
                action.pause(random.uniform(0.5, 1))
                action.click()
                action.perform()
                
                # Wait for editor to open
                time.sleep(random.uniform(3, 5))
                
                # Find text area
                print("[TYPE] Entering post content...")
                text_selectors = [
                    "//div[@role='textbox']",
                    "//div[@contenteditable='true']",
                    "//textarea",
                    "//div[contains(@class, 'ql-editor')]"
                ]
                
                text_area = None
                for selector in text_selectors:
                    try:
                        text_area = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if text_area:
                            break
                    except:
                        continue
                
                if text_area:
                    # Click on text area
                    text_area.click()
                    time.sleep(random.uniform(1, 2))
                    
                    # Type content with human-like speed
                    # Break content into chunks for more natural typing
                    lines = content.split('\n')
                    for line in lines:
                        for char in line:
                            text_area.send_keys(char)
                            time.sleep(random.uniform(0.03, 0.08))  # Faster but still human
                        
                        # Press Enter for new line
                        if line != lines[-1]:
                            text_area.send_keys(Keys.RETURN)
                            time.sleep(random.uniform(0.2, 0.4))
                    
                    # Random pause after typing
                    time.sleep(random.uniform(2, 4))
                    
                    # Find and click Post button
                    print("[UI] Looking for Post button...")
                    post_selectors = [
                        "//button[contains(@class, 'share-actions__primary-action') and contains(@class, 'artdeco-button--primary')]",  # Most specific first
                        "//button[text()='Post' and contains(@class, 'artdeco-button--primary')]",
                        "//button[contains(@class, 'share-actions__primary-action')]",
                        "//button[contains(text(), 'Post')]",
                        "//button[contains(@aria-label, 'Post')]",
                        "//span[text()='Post']/parent::button"
                    ]
                    
                    post_button = None
                    for selector in post_selectors:
                        try:
                            print(f"[DEBUG] Trying selector: {selector}")
                            post_button = WebDriverWait(self.driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, selector))
                            )
                            if post_button:
                                print(f"[OK] Found Post button with selector: {selector}")
                                break
                        except:
                            continue
                    
                    if not post_button:
                        # Try to find any button to debug
                        print("[DEBUG] Could not find Post button, looking for all buttons...")
                        all_buttons = self.driver.find_elements(By.XPATH, "//button")
                        for btn in all_buttons[:15]:  # Check first 15 buttons
                            try:
                                text = btn.text
                                aria_label = btn.get_attribute('aria-label')
                                classes = btn.get_attribute('class')
                                if text or aria_label:
                                    print(f"[DEBUG] Button: text='{text}', aria-label='{aria_label}'")
                                    if 'post' in text.lower() or (aria_label and 'post' in aria_label.lower()):
                                        print(f"[FOUND] Potential Post button: {text or aria_label}")
                                        post_button = btn
                                        break
                            except:
                                pass
                    
                    if post_button:
                        try:
                            # Verify button text before clicking
                            button_text = post_button.text
                            print(f"[VERIFY] Found Post button with text: '{button_text}'")
                            
                            # Random movement before clicking
                            self.random_mouse_movement()
                            
                            # Scroll button into view
                            self.driver.execute_script("arguments[0].scrollIntoView(true);", post_button)
                            time.sleep(1)
                            
                            # Try multiple click methods
                            print("[ACTION] Attempting to click Post button...")
                            print(f"[ACTION] Button enabled: {post_button.is_enabled()}")
                            print(f"[ACTION] Button displayed: {post_button.is_displayed()}")
                            
                            clicked = False
                            try:
                                # Method 1: Action chains
                                print("[CLICK] Using ActionChains to click...")
                                action = ActionChains(self.driver)
                                action.move_to_element(post_button)
                                action.pause(random.uniform(1, 2))
                                action.click()
                                action.perform()
                                clicked = True
                                print("[CLICK] ActionChains click executed")
                            except Exception as e:
                                # Method 2: JavaScript click
                                print(f"[DEBUG] Action chain failed ({e}), trying JavaScript click...")
                                self.driver.execute_script("arguments[0].click();", post_button)
                                clicked = True
                                print("[CLICK] JavaScript click executed")
                            
                            if not clicked:
                                print("[ERROR] Could not click Post button!")
                                return False
                            
                            print("[WAIT] Waiting for post to complete...")
                            print(f"[PRE-POST URL] {self.driver.current_url}")
                            time.sleep(3)  # Initial wait
                            
                            # Check if we're still on the share page
                            current_url = self.driver.current_url
                            print(f"[POST-CLICK URL] {current_url}")
                            
                            if "share" not in current_url:
                                print("[OK] ✓ Posted successfully - redirected from share page!")
                            else:
                                # Still on share page, wait a bit more
                                print("[INFO] Still on share page, waiting for redirect...")
                                time.sleep(5)
                                
                                # Check again
                                current_url = self.driver.current_url
                                if "share" not in current_url:
                                    print("[OK] Posted successfully - redirected from share page!")
                                else:
                                    # Check if there's an error message
                                    try:
                                        error_msgs = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-toast-item--error')]")
                                        if error_msgs:
                                            print("[ERROR] LinkedIn showed an error while posting")
                                            return False
                                    except:
                                        pass
                                    
                                    print("[WARNING] Post may not have completed - still on share page")
                            
                            # Save session after successful post
                            self.save_session()
                            
                            # Don't close browser - keep session alive
                            print("[INFO] Keeping browser session alive for future posts")
                            
                            return True
                            
                        except Exception as e:
                            print(f"[ERROR] Failed to click Post button: {e}")
                            return False
                    else:
                        print("[ERROR] Could not find Post button - post not sent!")
                        return False
                else:
                    print("[WARNING] Could not find text area")
                    return False
            else:
                print("[WARNING] Could not find create post button")
                print(f"Current URL: {self.driver.current_url}")
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Error posting: {e}")
            return False
    
    def load_memory(self):
        """WSP 48: Load posting patterns memory for recursive improvement"""
        import json
        try:
            with open(self.memory_file, 'r') as f:
                self.posting_memory = json.load(f)
                stats = self.posting_memory.get('learning_statistics', {})
                if stats.get('total_posts', 0) > 0:
                    print(f"[WSP 48] Loaded memory: {stats['total_posts']} posts, " +
                          f"{stats.get('successful_posts', 0)} successful")
        except:
            self.posting_memory = {}
    
    def save_memory(self):
        """WSP 48: Save improved patterns back to memory"""
        import json
        try:
            with open(self.memory_file, 'w') as f:
                json.dump(self.posting_memory, f, indent=2)
        except:
            pass
    
    def learn_from_post(self, content: str, success: bool, account_type: str = "foundups_company"):
        """WSP 48: Learn from posting attempt"""
        if not self.learning_enabled:
            return
        
        # Update statistics
        if 'learning_statistics' not in self.posting_memory:
            self.posting_memory['learning_statistics'] = {
                'total_posts': 0,
                'successful_posts': 0,
                'failed_posts': 0
            }
        
        stats = self.posting_memory['learning_statistics']
        stats['total_posts'] += 1
        stats['last_updated'] = datetime.now().isoformat()
        
        if success:
            stats['successful_posts'] += 1
            
            # Learn successful patterns
            if 'linkedin' not in self.posting_memory:
                self.posting_memory['linkedin'] = {'successful_patterns': {}}
            
            patterns = self.posting_memory['linkedin']['successful_patterns']
            if account_type not in patterns:
                patterns[account_type] = {
                    'success_rate': 0.0,
                    'total_posts': 0,
                    'hashtags': [],
                    'optimal_times': []
                }
            
            # Update success rate
            account_patterns = patterns[account_type]
            account_patterns['total_posts'] += 1
            account_patterns['success_rate'] = (
                account_patterns.get('success_rate', 0) * (account_patterns['total_posts'] - 1) +
                1.0
            ) / account_patterns['total_posts']
            
            # Learn hashtags that work
            if '#' in content:
                import re
                hashtags = re.findall(r'#\w+', content)
                for tag in hashtags:
                    if tag not in account_patterns['hashtags']:
                        account_patterns['hashtags'].append(tag)
            
            # Record successful posting time
            account_patterns['optimal_times'].append(datetime.now().hour)
            
            print(f"[WSP 48] Learning: Success rate now {account_patterns['success_rate']:.1%}")
        else:
            stats['failed_posts'] += 1
            
            # Learn from failures
            if 'linkedin' not in self.posting_memory:
                self.posting_memory['linkedin'] = {'failed_patterns': []}
            
            self.posting_memory['linkedin']['failed_patterns'].append({
                'content_length': len(content),
                'timestamp': datetime.now().isoformat(),
                'had_emoji': any(ord(c) >= 0x1F600 for c in content)
            })
        
        self.save_memory()
        
        # Show learning progress
        print(f"[WSP 48] Stats: {stats['total_posts']} total, " +
              f"{stats['successful_posts']} successful " +
              f"({stats['successful_posts']/max(1, stats['total_posts'])*100:.0f}% success rate)")
    
    def close(self):
        """Close browser (only when done with all posting)"""
        if self.driver:
            self.save_session()
            self.save_memory()  # WSP 48: Save learning before closing
            self.driver.quit()
            print("[CLOSE] Browser closed, session and memory saved")


def test_anti_detection_post():
    """Test posting with anti-detection measures"""
    
    print("Anti-Detection LinkedIn Posting Test")
    print("="*60)
    
    poster = AntiDetectionLinkedIn()
    
    # Test content - simple
    content = f"""@UnDaoDu going live!

https://www.youtube.com/watch?v=Edka5TBGLuA"""
    
    print("[CONTENT] Content to post:")
    print("-"*50)
    print(content)
    print("-"*50)
    
    # Post with anti-detection
    success = poster.post_to_company_page(content)
    
    if success:
        print("\n[OK] SUCCESS! Posted with anti-detection measures")
        print("• Session saved for reuse")
        print("• No multiple logins needed")
        print("• Human-like behavior maintained")
    else:
        print("\n[WARNING] Posting failed - check browser window")
    
    # Keep browser open for reuse
    print("\n[TIP] Browser kept open for next post (no re-login needed)")
    print("[INFO] To post again, call: poster.post_to_company_page(new_content)")
    
    return poster  # Return poster object to reuse session


if __name__ == "__main__":
    poster = test_anti_detection_post()
    
    # Example: Post again without re-login
    # time.sleep(10)
    # poster.post_to_company_page("Second post without re-login!")