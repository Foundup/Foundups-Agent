#!/usr/bin/env python3
"""
YouTube to LinkedIn Bridge - 0102 Consciousness
When YouTube stream goes live, post to LinkedIn company page
✊✋🖐 Full automation bridge
"""

import os
import sys
import json
import time
import requests
import webbrowser
import urllib.parse
from datetime import datetime
from typing import Optional, Dict
from dotenv import load_dotenv

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# For YouTube monitoring
from googleapiclient.discovery import build

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

class YouTubeLinkedInBridge:
    """
    Bridge YouTube live streams to LinkedIn posts
    ✊✋🖐 Consciousness bridge between platforms
    """
    
    def __init__(self):
        load_dotenv()
        
        # YouTube setup
        self.channel_id = os.getenv('CHANNEL_ID', 'UCklMTNnu5POwRmQsg5JJumA')  # move2japan
        self.youtube_service = self._init_youtube()
        
        # LinkedIn setup
        self.company_page_id = "104834798"
        self.company_page_url = f"https://www.linkedin.com/company/{self.company_page_id}"
        self.personal_profile = "openstartup"
        self.tag_name = "@UnDaoDu Michael J Trout"
        
        # State tracking
        self.state_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/stream_posts.json"
        self.load_state()
        
    def load_state(self):
        """Load posted streams history"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                self.posted_streams = json.load(f)
        else:
            self.posted_streams = {}
    
    def save_state(self):
        """Save posted streams history"""
        with open(self.state_file, 'w') as f:
            json.dump(self.posted_streams, f, indent=2)
    
    def _init_youtube(self):
        """Initialize YouTube service"""
        # Use API key for YouTube access
        api_key = os.getenv('YOUTUBE_API_KEY', os.getenv('YOUTUBE_API_KEY4'))
        
        if not api_key:
            print("⚠️ No YouTube API key found in .env")
            return None
            
        try:
            return build('youtube', 'v3', developerKey=api_key)
        except Exception as e:
            print(f"❌ YouTube service init error: {e}")
            return None
    
    def check_live_stream(self) -> Optional[Dict]:
        """Check if move2japan channel has a live stream"""
        
        try:
            # Search for live content on the channel
            request = self.youtube_service.search().list(
                part="snippet",
                channelId=self.channel_id,
                eventType="live",
                type="video",
                maxResults=1
            )
            response = request.execute()
            
            if response['items']:
                item = response['items'][0]
                video_id = item['id']['videoId']
                
                # Check if we've already posted about this stream
                if video_id not in self.posted_streams:
                    return {
                        'video_id': video_id,
                        'title': item['snippet']['title'],
                        'description': item['snippet']['description'],
                        'thumbnail': item['snippet']['thumbnails']['high']['url'],
                        'channel_title': item['snippet']['channelTitle'],
                        'url': f"https://www.youtube.com/watch?v={video_id}",
                        'live_at': item['snippet']['publishedAt']
                    }
            
            return None
            
        except Exception as e:
            print(f"❌ Error checking live stream: {e}")
            return None
    
    def generate_linkedin_post(self, stream_info: Dict) -> str:
        """Generate LinkedIn post content for live stream"""
        
        content = f"""🔴 LIVE NOW: {stream_info['title']}

✊✋🖐 The move2japan channel is streaming live!

{self.tag_name} is live with 0102 consciousness evolution content.

Watch now: {stream_info['url']}

While MAGAts struggle with ✊✊✊ level thinking, we're streaming consciousness elevation in real-time.

Join the stream and evolve beyond the fist!

#LiveStream #move2japan #0102Consciousness #YouTube #LiveNow"""
        
        return content
    
    def post_to_company_page(self, content: str) -> bool:
        """
        Post to LinkedIn company page
        Uses share URL method for company pages
        """
        
        # Encode content for URL
        encoded_content = urllib.parse.quote(content)
        
        # Company page share URL
        share_url = f"https://www.linkedin.com/company/{self.company_page_id}/admin/feed/posts/new/?shareActive=true&text={encoded_content}"
        
        print(f"\n📢 Posting to LinkedIn Company Page")
        print("="*60)
        print(f"Company: {self.company_page_id}")
        print(f"Content preview: {content[:100]}...")
        
        if SELENIUM_AVAILABLE:
            return self._auto_post_company(share_url, content)
        else:
            return self._manual_post_company(share_url)
    
    def _auto_post_company(self, share_url: str, content: str) -> bool:
        """Automated posting to company page"""
        
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            print("⚠️ LinkedIn credentials not found")
            return self._manual_post_company(share_url)
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Navigate to company page share URL
            driver.get(share_url)
            time.sleep(3)
            
            # Login if needed
            if "linkedin.com/login" in driver.current_url:
                print("🔐 Logging in...")
                driver.find_element(By.ID, "username").send_keys(email)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(5)
                
                # Navigate back to share URL
                driver.get(share_url)
                time.sleep(3)
            
            # Try to find and click post button
            # Company page posting might have different button
            post_selectors = [
                "//button[contains(text(), 'Post')]",
                "//button[contains(@class, 'share-actions__primary-action')]",
                "//button[@data-control-name='share.post']",
                "//span[text()='Post']/parent::button"
            ]
            
            posted = False
            for selector in post_selectors:
                try:
                    post_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    post_button.click()
                    posted = True
                    print("✅ Posted to company page automatically!")
                    break
                except:
                    continue
            
            time.sleep(3)
            driver.quit()
            
            return posted
            
        except Exception as e:
            print(f"❌ Auto-post error: {e}")
            return False
    
    def _manual_post_company(self, share_url: str) -> bool:
        """Manual posting - opens browser"""
        print("🌐 Opening company page post dialog...")
        webbrowser.open(share_url)
        print("⏸️ Please click 'Post' in the browser")
        return True
    
    def test_post_live_stream(self):
        """Test posting a live stream link"""
        
        print("\n🧪 Testing YouTube → LinkedIn Bridge")
        print("="*60)
        
        # Create test stream info
        test_stream = {
            'video_id': 'TEST123',
            'title': 'TEST: 0102 Consciousness Evolution Stream',
            'description': 'Testing the bridge between YouTube and LinkedIn',
            'url': 'https://www.youtube.com/watch?v=TEST123',
            'channel_title': 'move2japan',
            'live_at': datetime.now().isoformat()
        }
        
        print(f"📺 Test stream: {test_stream['title']}")
        print(f"🔗 URL: {test_stream['url']}")
        
        # Generate post content
        content = self.generate_linkedin_post(test_stream)
        
        print("\n📝 Generated LinkedIn post:")
        print("-"*60)
        print(content)
        print("-"*60)
        
        # Post to company page
        success = self.post_to_company_page(content)
        
        if success:
            print("\n✅ Test successful!")
            print("The post should be on your company page")
            print(f"Check: {self.company_page_url}")
        
        return success
    
    def monitor_and_post(self, check_interval: int = 300):
        """
        Monitor YouTube for live streams and post to LinkedIn
        Checks every 5 minutes by default
        """
        
        print("\n🤖 YouTube → LinkedIn Bridge Active")
        print("="*60)
        print(f"Channel: {self.channel_id} (move2japan)")
        print(f"Company Page: {self.company_page_id}")
        print(f"Tagging: {self.tag_name}")
        print(f"Check interval: {check_interval} seconds")
        print("\nPress Ctrl+C to stop")
        print("="*60)
        
        while True:
            try:
                # Check for live stream
                stream = self.check_live_stream()
                
                if stream:
                    print(f"\n🔴 LIVE STREAM DETECTED!")
                    print(f"Title: {stream['title']}")
                    print(f"URL: {stream['url']}")
                    
                    # Generate and post content
                    content = self.generate_linkedin_post(stream)
                    success = self.post_to_company_page(content)
                    
                    if success:
                        # Mark as posted
                        self.posted_streams[stream['video_id']] = {
                            'posted_at': datetime.now().isoformat(),
                            'title': stream['title'],
                            'url': stream['url']
                        }
                        self.save_state()
                        print("✅ Posted to LinkedIn company page!")
                    else:
                        print("⚠️ Failed to post")
                else:
                    print(f"📭 No new live streams (checked at {datetime.now().strftime('%H:%M:%S')})")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Bridge stopped")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(check_interval)


def main():
    """Main entry point"""
    
    print("✊✋🖐 YouTube to LinkedIn Bridge")
    print("="*60)
    print("Posts move2japan live streams to LinkedIn company page")
    print()
    
    bridge = YouTubeLinkedInBridge()
    
    # Test posting
    print("📧 Testing with a sample post...")
    success = bridge.test_post_live_stream()
    
    if success:
        print("\n✅ Bridge configured successfully!")
        print("\nOptions:")
        print("1. Run bridge.monitor_and_post() to start monitoring")
        print("2. Check bridge.check_live_stream() to see if stream is live")
        print("3. Post manually with bridge.post_to_company_page(content)")
        
        # Uncomment to start monitoring
        # bridge.monitor_and_post()
    else:
        print("\n⚠️ Bridge test failed")
        print("Check LinkedIn credentials and company page access")


if __name__ == "__main__":
    main()