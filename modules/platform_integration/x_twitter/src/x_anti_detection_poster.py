#!/usr/bin/env python3
"""
X/Twitter Anti-Detection Posting System
Posts to X using browser automation with human-like behavior
Uses same approach as LinkedIn for consistency
WSP 48: Includes recursive learning for self-improvement
"""

import os
import json
import time
import random
import pickle
from datetime import datetime
from typing import Optional, Dict, Any
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

class AntiDetectionX:
    """
    X/Twitter poster with anti-detection measures
    Uses compose URL for direct posting
    """
    
    def __init__(self, use_foundups=True):
        load_dotenv()
        # Support multiple X accounts
        # For git posting, use FoundUps account (X_Acc2)
        # For YouTube streams, can use Move2Japan (X_Acc1)
        if use_foundups:
            self.username = os.getenv('X_Acc2', 'Foundups')  # FoundUps account
        else:
            self.username = os.getenv('X_Acc1', 'geozeai')  # Move2Japan account
        self.password = os.getenv('x_Acc_pass')
        self.compose_url = "https://x.com/compose/post"
        self.data_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data"
        self.session_file = os.path.join(self.data_dir, "x_session.pkl")
        self.memory_file = "O:/Foundups-Agent/modules/platform_integration/social_media_orchestrator/memory/posting_patterns.json"
        self.driver = None
        
        # WSP 48: Load pattern memory for recursive learning
        self.memory = self.load_memory()
        
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
    
    def load_memory(self) -> Dict[str, Any]:
        """WSP 48: Load posting patterns memory for recursive improvement"""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"[WSP48] Could not load memory: {e}")
        
        # Return default structure
        return {
            "x_twitter": {
                "successful_patterns": {},
                "failed_patterns": [],
                "optimal_posting_times": [],
                "character_limits": {"post": 280, "thread": 25},
                "mention_handling": {}
            },
            "learning_statistics": {
                "total_posts": 0,
                "successful_posts": 0,
                "failed_posts": 0
            }
        }
    
    def save_memory(self):
        """WSP 48: Save improved patterns back to memory"""
        try:
            os.makedirs(os.path.dirname(self.memory_file), exist_ok=True)
            with open(self.memory_file, 'w') as f:
                json.dump(self.memory, f, indent=2)
        except Exception as e:
            print(f"[WSP48] Could not save memory: {e}")
    
    def learn_from_post(self, content: str, success: bool):
        """WSP 48: Learn from posting attempt for recursive improvement"""
        # Update statistics
        self.memory["learning_statistics"]["total_posts"] += 1
        
        if success:
            self.memory["learning_statistics"]["successful_posts"] += 1
            
            # Learn successful patterns
            patterns = self.memory.get("x_twitter", {}).get("successful_patterns", {})
            
            # Track character-by-character typing success for @mentions
            if "@" in content:
                mention_patterns = self.memory["x_twitter"].get("mention_handling", {})
                mention_patterns["character_by_character"] = {
                    "works": True,
                    "method": "slow typing preserves @mentions",
                    "last_success": datetime.now().isoformat()
                }
                self.memory["x_twitter"]["mention_handling"] = mention_patterns
            
            # Track successful posting times
            current_hour = datetime.now().hour
            optimal_times = self.memory["x_twitter"].get("optimal_posting_times", [])
            if current_hour not in optimal_times:
                optimal_times.append(current_hour)
                self.memory["x_twitter"]["optimal_posting_times"] = optimal_times
            
            # Track content patterns that work
            if "stream_announcements" not in patterns:
                patterns["stream_announcements"] = {
                    "format": "@mention + content + URL",
                    "success_rate": 1.0,
                    "total_posts": 1,
                    "character_typing": "required for @mentions"
                }
            else:
                # Update success rate
                pattern = patterns["stream_announcements"]
                total = pattern.get("total_posts", 0) + 1
                success_count = int(pattern.get("success_rate", 0) * pattern.get("total_posts", 0)) + 1
                pattern["success_rate"] = success_count / total
                pattern["total_posts"] = total
            
            self.memory["x_twitter"]["successful_patterns"] = patterns
            
        else:
            self.memory["learning_statistics"]["failed_posts"] += 1
            
            # Learn from failures
            failed_patterns = self.memory["x_twitter"].get("failed_patterns", [])
            failed_patterns.append({
                "content_preview": content[:100],
                "timestamp": datetime.now().isoformat(),
                "possible_issues": ["login required", "rate limit", "UI change"]
            })
            # Keep only last 10 failures for analysis
            self.memory["x_twitter"]["failed_patterns"] = failed_patterns[-10:]
        
        # Calculate and show learning progress
        stats = self.memory["learning_statistics"]
        success_rate = stats["successful_posts"] / max(stats["total_posts"], 1)
        
        print(f"[WSP48] Learning Statistics:")
        print(f"   Total X posts: {stats['total_posts']}")
        print(f"   Success rate: {success_rate:.1%}")
        print(f"   Patterns learned: {len(self.memory['x_twitter'].get('successful_patterns', {}))}")
        
        # Save improved memory
        self.save_memory()
        
        # WSP 48: Self-improvement message
        if success_rate > 0.8:
            print("[WSP48] ✓ System performing well - patterns stabilized")
        elif success_rate > 0.5:
            print("[WSP48] ↑ System improving - learning from patterns")
        else:
            print("[WSP48] ⚠ System adapting - analyzing failures")
    
    def setup_driver(self, use_existing_session=True):
        """Setup browser with anti-detection measures - Edge for FoundUps, Chrome for GeozeAi"""

        # Determine if we're using FoundUps or GeozeAi account
        use_foundups = self.username == os.getenv('X_Acc2', 'Foundups')

        if use_foundups:
            # Use Edge for FoundUps account
            try:
                from selenium.webdriver.edge.options import Options as EdgeOptions
                from selenium.webdriver.edge.service import Service as EdgeService

                edge_options = EdgeOptions()

                # Anti-detection flags (similar to Chrome)
                edge_options.add_argument('--disable-blink-features=AutomationControlled')
                edge_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                edge_options.add_experimental_option('useAutomationExtension', False)

                # More human-like settings
                edge_options.add_argument('--disable-web-security')
                edge_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                edge_options.add_argument('--window-size=1920,1080')
                edge_options.add_argument('--start-maximized')

                # User agent to appear as regular Edge
                edge_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0')

                # Use profile to maintain session
                if use_existing_session:
                    profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/edge_profile_foundups"
                    os.makedirs(profile_dir, exist_ok=True)
                    edge_options.add_argument(f'--user-data-dir={profile_dir}')
                    edge_options.add_argument('--profile-directory=Default')

                print("[INFO] Starting Edge for @Foundups with anti-detection measures...")
                # Try to find Edge driver
                try:
                    self.driver = webdriver.Edge(options=edge_options)
                except:
                    # If Edge driver not found, try with webdriver-manager
                    from webdriver_manager.microsoft import EdgeChromiumDriverManager
                    edge_service = EdgeService(EdgeChromiumDriverManager().install())
                    self.driver = webdriver.Edge(service=edge_service, options=edge_options)

            except ImportError:
                print("[WARNING] Edge WebDriver not available for FoundUps, falling back to Chrome")
                print("[INFO] Install with: pip install selenium webdriver-manager")
                # Fallback to Chrome if Edge not available
                from selenium.webdriver.chrome.options import Options
                chrome_options = Options()
                chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                chrome_options.add_argument('--disable-web-security')
                chrome_options.add_argument('--disable-features=IsolateOrigins,site-per-process')
                chrome_options.add_argument('--window-size=1920,1080')
                chrome_options.add_argument('--start-maximized')
                chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

                if use_existing_session:
                    profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile_foundups"
                    os.makedirs(profile_dir, exist_ok=True)
                    chrome_options.add_argument(f'--user-data-dir={profile_dir}')
                    chrome_options.add_argument('--profile-directory=Default')

                print("[INFO] Starting Chrome (Edge fallback) for @Foundups...")
                self.driver = webdriver.Chrome(options=chrome_options)
        else:
            # Use Chrome for GeozeAi/Move2Japan account
            from selenium.webdriver.chrome.options import Options
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
                profile_dir = "O:/Foundups-Agent/modules/platform_integration/x_twitter/data/chrome_profile_geozai"
                os.makedirs(profile_dir, exist_ok=True)
                chrome_options.add_argument(f'--user-data-dir={profile_dir}')
                chrome_options.add_argument('--profile-directory=Default')

            print("[INFO] Starting Chrome for @GeozeAi with anti-detection measures...")
            self.driver = webdriver.Chrome(options=chrome_options)

        # Override navigator.webdriver flag
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Random initial delay
        time.sleep(random.uniform(2, 4))

        return self.driver
    
    def is_logged_in(self) -> bool:
        """Check if already logged in to X"""
        if not self.driver:
            return False
        
        try:
            # Navigate to X home
            self.driver.get("https://x.com/home")
            time.sleep(random.uniform(3, 5))
            
            # Check if we're on the home feed (logged in) or login page
            if "home" in self.driver.current_url:
                print("[OK] Already logged in to X!")
                return True
            else:
                return False
        except:
            return False
    
    def login_with_anti_detection(self, max_retries=3):
        """Login to X with human-like behavior and retry logic"""
        
        if self.is_logged_in():
            print("[OK] Using existing session - no login needed!")
            return True
        
        for attempt in range(max_retries):
            print(f"[AUTH] Login attempt {attempt + 1}/{max_retries} with anti-detection measures...")
            
            try:
                # Navigate to login page
                self.driver.get("https://x.com/login")
                
                # Random delay before starting
                time.sleep(random.uniform(3, 5))
                
                # Find username field - X may have different selectors
                print("   Entering username...")
                username_selectors = [
                    "//input[@name='text']",
                    "//input[@autocomplete='username']",
                    "//input[@type='text']"
                ]
                
                username_field = None
                for selector in username_selectors:
                    try:
                        username_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if username_field:
                            break
                    except:
                        continue
                
                if not username_field:
                    print("[ERROR] Could not find username field")
                    continue
                
                # Random mouse movement
                self.random_mouse_movement()
                
                # Click on field first (human behavior)
                username_field.click()
                time.sleep(random.uniform(0.5, 1))
                
                # Type username with human-like delays
                self.human_type(username_field, self.username)
                
                # Press Next/Enter
                username_field.send_keys(Keys.RETURN)
                time.sleep(random.uniform(2, 4))
                
                print("   Entering password...")
                # Find password field
                password_selectors = [
                    "//input[@name='password']",
                    "//input[@type='password']",
                    "//input[@autocomplete='current-password']"
                ]
                
                password_field = None
                for selector in password_selectors:
                    try:
                        password_field = WebDriverWait(self.driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, selector))
                        )
                        if password_field:
                            break
                    except:
                        continue
                
                if not password_field:
                    print("[ERROR] Could not find password field")
                    continue
                
                # Type password with human-like delays
                self.human_type(password_field, self.password)
                
                # Random mouse movement before clicking
                self.random_mouse_movement()
                
                # Press Enter to login
                print("   Logging in...")
                password_field.send_keys(Keys.RETURN)
                
                # Wait for login to complete
                print("[WAIT] Waiting for login to complete...")
                time.sleep(random.uniform(5, 8))
                
                # Verify login succeeded
                if "home" in self.driver.current_url:
                    print("[OK] Login successful!")
                    
                    # Save cookies for session persistence
                    self.save_session()
                    return True
                else:
                    print("[WARNING] Login may have failed or needs verification")
                    
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
            self.driver.get("https://x.com")
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
    
    def post_to_x(self, content: str, video_id: str = None):
        """Post to X using compose URL with anti-detection"""
        
        print("\n[POST] Posting to X/Twitter (Anti-Detection Mode)")
        print("="*60)
        
        # Check for duplicate posts if video_id provided
        if video_id:
            post_tracking_file = os.path.join(self.data_dir, 'posted_videos.json')
            posted_videos = {}
            
            # Load existing posts
            if os.path.exists(post_tracking_file):
                try:
                    with open(post_tracking_file, 'r') as f:
                        posted_videos = json.load(f)
                except:
                    posted_videos = {}
            
            # Check if we posted this video recently
            if video_id in posted_videos:
                last_post_timestamp = posted_videos[video_id].get('timestamp', None)
                if last_post_timestamp:
                    # Handle both ISO string and Unix timestamp formats
                    if isinstance(last_post_timestamp, str):
                        # Parse ISO format timestamp
                        from datetime import datetime
                        last_post_dt = datetime.fromisoformat(last_post_timestamp.replace('Z', '+00:00'))
                        last_post_time = last_post_dt.timestamp()
                    else:
                        last_post_time = float(last_post_timestamp)
                    
                    hours_since_post = (time.time() - last_post_time) / 3600
                    if hours_since_post < 4:
                        print(f"[SKIP] Already posted {hours_since_post:.1f} hours ago for video {video_id}")
                        return False
        
        # Setup driver if not already
        if not self.driver:
            self.setup_driver(use_existing_session=True)
        else:
            print("[OK] Using existing browser session")
        
        try:
            # Go directly to the compose URL
            print(f"[NAV] Going directly to compose page...")
            self.driver.get(self.compose_url)
            
            # Wait for page to load
            time.sleep(random.uniform(3, 5))
            
            # Check if we got redirected to login
            current_url = self.driver.current_url
            print(f"[DEBUG] Current URL after navigation: {current_url}")
            
            if "login" in current_url.lower():
                print("[INFO] Redirected to login - attempting login...")
                if not self.login_with_anti_detection():
                    print("[FAIL] Could not login")
                    return False
                # After login, go back to compose
                print("[NAV] Navigating back to compose after login...")
                self.driver.get(self.compose_url)
                time.sleep(random.uniform(3, 5))
            
            # Now look for text area
            print("[UI] Looking for post text area...")
            print(f"[DEBUG] Current URL: {self.driver.current_url}")
            
            # Wait a bit for page to fully load
            time.sleep(2)
            
            text_selectors = [
                "//div[@role='textbox']",
                "//div[@contenteditable='true']",
                "//div[contains(@aria-label, 'Post text')]",
                "//div[contains(@aria-label, 'Tweet text')]",
                "//div[@data-testid='tweetTextarea_0']",
                "//div[contains(@class, 'DraftEditor')]//div[@contenteditable='true']",
                "//div[contains(@class, 'public-DraftEditor')]//div[@contenteditable='true']"
            ]
            
            text_area = None
            for selector in text_selectors:
                try:
                    print(f"[DEBUG] Trying selector: {selector}")
                    text_area = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, selector))
                    )
                    if text_area:
                        print(f"[OK] Found text area with selector: {selector}")
                        break
                except:
                    continue
            
            if text_area:
                # Click on text area
                print("[ACTION] Clicking text area...")
                text_area.click()
                time.sleep(random.uniform(2, 3))  # Longer delay for page to settle
                
                # Clear any existing text first
                print("[CLEAR] Clearing any existing text...")
                try:
                    # Try multiple methods to clear
                    text_area.send_keys(Keys.CONTROL + "a")  # Select all
                    time.sleep(0.5)
                    text_area.send_keys(Keys.DELETE)  # Delete
                    time.sleep(0.5)
                    
                    # Also clear via JavaScript to be sure
                    self.driver.execute_script("arguments[0].textContent = '';", text_area)
                    self.driver.execute_script("arguments[0].innerHTML = '';", text_area)
                    time.sleep(1)
                except:
                    pass
                
                # Type content with human-like speed - character by character preserves @mentions
                print("[TYPE] Typing post content character by character...")

                # Sanitize content for ChromeDriver BMP limitation
                def sanitize_for_chromedriver(text):
                    """Remove characters outside BMP that ChromeDriver can't handle"""
                    # Keep only characters in the Basic Multilingual Plane (U+0000 to U+FFFF)
                    sanitized = ''
                    for char in text:
                        if ord(char) <= 0xFFFF:
                            sanitized += char
                        else:
                            # Replace problematic emojis with text equivalents
                            if char == '🚀':
                                sanitized += '[rocket]'
                            elif char == '🦄':
                                sanitized += '[unicorn]'
                            elif char == '💎':
                                sanitized += '[gem]'
                            elif char == '🔥':
                                sanitized += '[fire]'
                            elif char == '⚡':
                                sanitized += '[lightning]'
                            else:
                                # Skip other non-BMP characters
                                pass
                    return sanitized

                # Use slower, more reliable typing method
                try:
                    # Click again to ensure focus
                    text_area.click()
                    time.sleep(0.5)

                    # Sanitize content first
                    safe_content = sanitize_for_chromedriver(content)
                    if safe_content != content:
                        print("[SANITIZE] Removed non-BMP characters for ChromeDriver compatibility")

                    # Type character by character - this method preserves @mentions correctly
                    for char in safe_content:
                        text_area.send_keys(char)
                        time.sleep(random.uniform(0.03, 0.08))  # Human-like speed that works

                    print("[OK] Content typed successfully")
                    
                except Exception as e:
                    print(f"[WARNING] Typing error: {e}")
                    # Fallback to JavaScript if typing fails
                    try:
                        js_content = content.replace("'", "\\'").replace("\n", "\\n")
                        self.driver.execute_script(f"arguments[0].textContent = '{js_content}';", text_area)
                        
                        # Trigger input event
                        self.driver.execute_script("""
                            var event = new Event('input', { bubbles: true });
                            arguments[0].dispatchEvent(event);
                        """, text_area)
                    except:
                        pass
                
                # Random pause after typing
                time.sleep(random.uniform(2, 4))
                
                # Find and click Post button
                print("[UI] Looking for Post button...")
                post_selectors = [
                    # Primary selector - the actual Post button
                    "//button[@data-testid='tweetButton']",
                    "//div[@data-testid='tweetButton']",
                    "//button[@data-testid='tweetButtonInline']",
                    # Backup selectors
                    "//button[text()='Post' and not(@aria-label)]",  # Post button has text but no aria-label
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
                            # Verify it's the right button
                            btn_text = post_button.text
                            btn_aria = post_button.get_attribute('aria-label')
                            btn_testid = post_button.get_attribute('data-testid')
                            print(f"[OK] Found button: text='{btn_text}', aria='{btn_aria}', testid='{btn_testid}'")
                            
                            # Make sure it's the Post button, not Grok or Schedule
                            # Post button has text='Post' and NO aria-label
                            if (btn_text == 'Post' and not btn_aria) or btn_testid == 'tweetButton':
                                print(f"[VERIFIED] This is the Post button!")
                                break
                            elif 'grok' in str(btn_aria).lower() or 'schedule' in str(btn_aria).lower():
                                print(f"[SKIP] This is {btn_aria}, not the Post button")
                                post_button = None
                            else:
                                print(f"[SKIP] Not the Post button, continuing...")
                                post_button = None
                    except:
                        continue
                
                if not post_button:
                    # Try to find all buttons to debug
                    print("[DEBUG] Looking for any button elements...")
                    all_buttons = self.driver.find_elements(By.XPATH, "//button")
                    for btn in all_buttons[:10]:  # Check first 10 buttons
                        try:
                            text = btn.text
                            aria_label = btn.get_attribute('aria-label')
                            data_testid = btn.get_attribute('data-testid')
                            if text or aria_label or data_testid:
                                print(f"[DEBUG] Button: text='{text}', aria-label='{aria_label}', data-testid='{data_testid}'")
                        except:
                            pass
                    
                    print("[WARNING] Could not find Post button")
                    return False
                
                # Click the Post button
                try:
                    # Random movement before clicking
                    self.random_mouse_movement()
                    
                    # Make sure button is enabled
                    if not post_button.is_enabled():
                        print("[ERROR] Post button is disabled!")
                        return False
                    
                    # Try multiple click methods to ensure it works
                    print("[ACTION] Attempting to click Post button...")
                    
                    # Method 1: JavaScript click (most reliable)
                    try:
                        self.driver.execute_script("arguments[0].click();", post_button)
                        print("[CLICK] JavaScript click executed")
                    except Exception as e:
                        print(f"[FALLBACK] JS click failed: {e}")
                        # Method 2: Action chains
                        action = ActionChains(self.driver)
                        action.move_to_element(post_button)
                        action.pause(random.uniform(0.5, 1))
                        action.click()
                        action.perform()
                        print("[CLICK] ActionChains click executed")
                    
                    # Double-click to be sure
                    time.sleep(1)
                    try:
                        self.driver.execute_script("arguments[0].click();", post_button)
                        print("[DOUBLE] Clicked again to ensure submission")
                    except:
                        pass
                    
                    # Wait for post to complete
                    print("[WAIT] Waiting for post to complete...")
                    initial_url = self.driver.current_url
                    time.sleep(3)
                    
                    # Check if text area is cleared (indicates post went through)
                    try:
                        text_area = self.driver.find_element(By.XPATH, "//div[@role='textbox']")
                        remaining_text = text_area.text
                        if not remaining_text or remaining_text == "What's happening?!":
                            print("[SUCCESS] Text area cleared - post likely sent!")
                        else:
                            print(f"[WARNING] Text still in compose: {remaining_text[:50]}...")
                            print("[ACTION] Post may not have gone through - trying again...")
                            # Try clicking Post button again
                            try:
                                post_button = self.driver.find_element(By.XPATH, "//button[@data-testid='tweetButton']")
                                post_button.click()
                                print("[RETRY] Clicked Post button again")
                                time.sleep(3)
                            except:
                                pass
                    except:
                        print("[INFO] Could not check text area")
                    
                    # Check if we left the compose page
                    current_url = self.driver.current_url
                    if current_url != initial_url:
                        print(f"[REDIRECT] Moved from compose to: {current_url}")
                    
                    # Verify post appears on profile
                    print("[VERIFY] Checking profile for the posted tweet...")
                    self.driver.get("https://x.com/GeozeAi")  # Go to profile
                    time.sleep(7)  # Give more time for page to load
                    
                    # Look for our post content
                    success = False
                    try:
                        # Check for @UnDaoDu posts
                        posts = self.driver.find_elements(By.XPATH, "//span[contains(text(), '@UnDaoDu')]")
                        if posts:
                            print(f"[FEED] ✓✓✓ Found {len(posts)} @UnDaoDu posts on profile")
                            # Check the first one (most recent)
                            try:
                                recent_post = posts[0].text
                                if 'going live' in recent_post.lower():
                                    print(f"[VERIFIED] ✓✓✓ Live stream post confirmed on X/Twitter!")
                                    print(f"   Post preview: {recent_post[:100]}...")
                                    success = True
                            except:
                                pass
                        
                        # Also check for the YouTube link
                        if not success:
                            links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'youtube.com/watch')]")
                            if links:
                                print(f"[VERIFIED] ✓ YouTube link found in recent posts")
                                success = True
                    except Exception as e:
                        print(f"[WARNING] Could not verify post: {e}")
                    
                    if success:
                        print("[SUCCESS] ✓✓✓ Posted and verified on X/Twitter!")
                    else:
                        print("[WARNING] Post may be processing or saved as draft")
                    
                    # WSP 48: Learn from this posting attempt
                    self.learn_from_post(content, success)
                    
                    # Save successful post to prevent duplicates
                    if success and video_id:
                        post_tracking_file = os.path.join(self.data_dir, 'posted_videos.json')
                        try:
                            if os.path.exists(post_tracking_file):
                                with open(post_tracking_file, 'r') as f:
                                    posted_videos = json.load(f)
                            else:
                                posted_videos = {}
                            
                            posted_videos[video_id] = {
                                'timestamp': time.time(),  # Use Unix timestamp for easier comparison
                                'content': content[:100]  # Store first 100 chars for reference
                            }
                            
                            with open(post_tracking_file, 'w') as f:
                                json.dump(posted_videos, f, indent=2)
                            print(f"[TRACK] Saved post for video {video_id} to prevent duplicates")
                        except Exception as e:
                            print(f"[WARNING] Could not save post tracking: {e}")
                    
                    # Save session after successful post
                    self.save_session()
                    
                    # Don't close browser - keep session alive
                    print("[INFO] Keeping browser session alive for future posts")
                    print("[BROWSER] Browser will remain open - DO NOT CLOSE")
                    print("[BROWSER] You can manually verify the post was sent")
                    
                    # Keep browser open for manual verification
                    print("[WAIT] Keeping browser open for 30 seconds for verification...")
                    time.sleep(30)
                    
                    return success
                    
                except Exception as e:
                    print(f"[ERROR] Failed to click Post button: {e}")
                    return False
            else:
                print("[WARNING] Could not find text area")
            
            return False
            
        except Exception as e:
            print(f"[ERROR] Error posting: {e}")

            # Check if this is a cancellation/duplicate attempt
            error_msg = str(e).lower()
            if any(indicator in error_msg for indicator in ["window already closed", "target window already closed", "no such window", "session not created"]):
                print("[DUPLICATE] User likely cancelled because post was already made!")

                # Import safety monitor and auto-fix
                try:
                    from modules.platform_integration.social_media_orchestrator.src.post_safety_monitor import detect_and_fix_duplicate

                    # Extract video ID from content if it's a YouTube link
                    import re
                    video_id_match = re.search(r'youtube\.com/watch\?v=([a-zA-Z0-9_-]+)', content)
                    if video_id_match:
                        video_id = video_id_match.group(1)
                        print(f"[AUTO-FIX] Marking video {video_id} as already posted to X/Twitter")
                        detect_and_fix_duplicate(video_id, 'x_twitter', str(e))
                except Exception as fix_error:
                    print(f"[WARNING] Could not auto-fix duplicate: {fix_error}")

            return False
    
    def close(self):
        """Close browser (only when done with all posting)"""
        if self.driver:
            self.save_session()
            self.driver.quit()
            print("[CLOSE] Browser closed, session saved")


def test_anti_detection_post():
    """Test posting with anti-detection measures"""
    
    print("Anti-Detection X/Twitter Posting Test")
    print("="*60)
    
    poster = AntiDetectionX()
    
    # Test content - simple
    content = f"""@UnDaoDu going live!

https://www.youtube.com/watch?v=test123"""
    
    print("[CONTENT] Content to post:")
    print("-"*50)
    print(content)
    print("-"*50)
    
    # Post with anti-detection
    success = poster.post_to_x(content)
    
    if success:
        print("\n[OK] SUCCESS! Posted with anti-detection measures")
        print("Session saved for reuse")
        print("No multiple logins needed")
        print("Human-like behavior maintained")
    else:
        print("\n[WARNING] Posting failed - check browser window")
    
    # Keep browser open for reuse
    print("\n[TIP] Browser kept open for next post (no re-login needed)")
    print("[INFO] To post again, call: poster.post_to_x(new_content)")
    
    return poster  # Return poster object to reuse session


if __name__ == "__main__":
    poster = test_anti_detection_post()
    
    # Example: Post again without re-login
    # time.sleep(10)
    # poster.post_to_x("Second post without re-login!")