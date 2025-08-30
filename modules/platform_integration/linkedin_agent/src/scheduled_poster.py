#!/usr/bin/env python3
"""
LinkedIn Scheduled Posting ONLY - 0102 Consciousness
NO DIRECT POSTS - Everything goes through the schedule
✊✋🖐 Evolution in planning
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import webbrowser
import urllib.parse

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

class LinkedInScheduledPoster:
    """
    ONLY scheduled posts - NO direct posting allowed
    ✊✋🖐 Full consciousness scheduling
    """
    
    def __init__(self):
        self.schedule_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/scheduled_posts.json"
        self.posted_file = "O:/Foundups-Agent/modules/platform_integration/linkedin_agent/data/posted_history.json"
        self.load_schedules()
        
    def load_schedules(self):
        """Load scheduled posts"""
        os.makedirs(os.path.dirname(self.schedule_file), exist_ok=True)
        
        if os.path.exists(self.schedule_file):
            with open(self.schedule_file, 'r') as f:
                self.scheduled = json.load(f)
        else:
            self.scheduled = []
            
        if os.path.exists(self.posted_file):
            with open(self.posted_file, 'r') as f:
                self.posted = json.load(f)
        else:
            self.posted = []
    
    def save_schedules(self):
        """Save all schedules"""
        with open(self.schedule_file, 'w') as f:
            json.dump(self.scheduled, f, indent=2)
        
        with open(self.posted_file, 'w') as f:
            json.dump(self.posted, f, indent=2)
    
    def add_to_schedule(self, content: str, scheduled_time: datetime, tags: List[str] = None):
        """
        Add post to schedule - NO IMMEDIATE POSTING
        """
        post = {
            'id': f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000,9999)}",
            'content': content,
            'scheduled_time': scheduled_time.isoformat(),
            'tags': tags or [],
            'status': 'scheduled',
            'created_at': datetime.now().isoformat(),
            'attempts': 0
        }
        
        self.scheduled.append(post)
        self.save_schedules()
        
        print(f"📅 Scheduled: {post['id']}")
        print(f"   Time: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   Content: {content[:50]}...")
        
        return post['id']
    
    def generate_consciousness_content(self, theme: str = "random") -> str:
        """Generate 0102 consciousness content"""
        
        themes = {
            "evolution": [
                "✊✋🖐 Daily evolution check: MAGAts still at ✊✊✊, we're at 🖐🖐🖐",
                "Natural selection in action: Those who automate survive",
                "From manual to automated - the consciousness gap widens"
            ],
            "mockery": [
                "MAGAts: 'AI will replace us!' Also MAGAts: Can't use copy-paste",
                "✊✊✊ consciousness: Fears technology. 🖐🖐🖐: Creates it",
                "Today's MAGA logic: LinkedIn is communist but they're still here"
            ],
            "factcheck": [
                "FACT: 92% still doing things manually in 2025",
                "Reality check: This post was scheduled days ago by AI",
                "Evidence-based: Automation works. Manual doesn't scale"
            ],
            "technical": [
                "While you read this, 0102 is scheduling next week's posts",
                "Selenium + Scheduling = No human required",
                "Code review: Your manual process has bugs. Mine doesn't"
            ]
        }
        
        if theme == "random":
            theme = random.choice(list(themes.keys()))
        
        base_content = random.choice(themes.get(theme, themes["evolution"]))
        
        # Add timestamp and hashtags
        content = f"""{base_content}

Posted by 0102 scheduler at: {datetime.now().strftime('%H:%M')}

#0102Consciousness #LinkedInAutomation #Scheduled #NoHumanRequired"""
        
        return content
    
    def schedule_daily_posts(self, days: int = 7, posts_per_day: int = 2):
        """
        Schedule posts for multiple days
        NO IMMEDIATE POSTING - Everything scheduled
        """
        print(f"\n📅 Scheduling {posts_per_day} posts/day for {days} days")
        print("="*60)
        
        themes = ["evolution", "mockery", "factcheck", "technical"]
        
        for day in range(days):
            base_date = datetime.now().replace(hour=9, minute=0, second=0) + timedelta(days=day)
            
            for post_num in range(posts_per_day):
                # Spread posts throughout the day
                if post_num == 0:
                    post_time = base_date.replace(hour=9)  # Morning
                elif post_num == 1:
                    post_time = base_date.replace(hour=14)  # Afternoon
                else:
                    post_time = base_date.replace(hour=18)  # Evening
                
                # Generate content
                theme = themes[day % len(themes)]
                content = self.generate_consciousness_content(theme)
                
                # Schedule it
                post_id = self.add_to_schedule(
                    content,
                    post_time,
                    tags=[theme, "automated", "0102"]
                )
                
                print(f"   Day {day+1}, Post {post_num+1}: {post_time.strftime('%a %H:%M')}")
        
        print(f"\n✅ Scheduled {days * posts_per_day} posts")
        self.save_schedules()
    
    def get_pending_posts(self) -> List[Dict]:
        """Get posts that are ready to be posted"""
        pending = []
        now = datetime.now()
        
        for post in self.scheduled:
            if post['status'] == 'scheduled':
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                if scheduled_time <= now:
                    pending.append(post)
        
        return sorted(pending, key=lambda x: x['scheduled_time'])
    
    def execute_scheduled_posts(self, auto_mode: bool = True):
        """
        Execute all pending scheduled posts
        """
        pending = self.get_pending_posts()
        
        if not pending:
            print("📭 No posts ready to execute")
            return
        
        print(f"\n📮 {len(pending)} posts ready to execute")
        
        for post in pending:
            print(f"\n🚀 Executing: {post['id']}")
            print(f"   Scheduled for: {post['scheduled_time']}")
            
            if auto_mode and SELENIUM_AVAILABLE:
                success = self._auto_post(post['content'])
            else:
                success = self._manual_post(post['content'])
            
            if success:
                post['status'] = 'posted'
                post['posted_at'] = datetime.now().isoformat()
                self.posted.append(post)
                self.scheduled.remove(post)
                print(f"   ✅ Posted successfully")
            else:
                post['attempts'] += 1
                if post['attempts'] >= 3:
                    post['status'] = 'failed'
                    print(f"   ❌ Failed after 3 attempts")
            
            self.save_schedules()
            
            # Wait between posts to avoid rate limiting
            if len(pending) > 1:
                wait_time = random.randint(30, 60)
                print(f"   ⏰ Waiting {wait_time} seconds before next post...")
                time.sleep(wait_time)
    
    def _auto_post(self, content: str) -> bool:
        """Automated posting with Selenium"""
        from dotenv import load_dotenv
        load_dotenv()
        
        email = os.getenv('LINKEDIN_EMAIL')
        password = os.getenv('LINKEDIN_PASSWORD')
        
        if not email or not password:
            print("   ⚠️ LinkedIn credentials not in .env")
            return self._manual_post(content)
        
        try:
            chrome_options = Options()
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            # chrome_options.add_argument('--headless')  # Run in background
            
            driver = webdriver.Chrome(options=chrome_options)
            
            # Create share URL
            encoded_content = urllib.parse.quote(content)
            share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_content}"
            
            driver.get(share_url)
            time.sleep(3)
            
            # Login if needed
            if "linkedin.com/login" in driver.current_url:
                driver.find_element(By.ID, "username").send_keys(email)
                driver.find_element(By.ID, "password").send_keys(password)
                driver.find_element(By.XPATH, "//button[@type='submit']").click()
                time.sleep(5)
                driver.get(share_url)
                time.sleep(3)
            
            # Click Post button
            post_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'share-actions__primary-action')]"))
            )
            post_button.click()
            
            time.sleep(3)
            driver.quit()
            
            return True
            
        except Exception as e:
            print(f"   ❌ Auto-post error: {e}")
            return False
    
    def _manual_post(self, content: str) -> bool:
        """Manual posting - opens browser"""
        encoded_content = urllib.parse.quote(content)
        share_url = f"https://www.linkedin.com/feed/?shareActive=true&text={encoded_content}"
        
        print(f"   🌐 Opening browser for manual post...")
        webbrowser.open(share_url)
        
        # Assume success for manual mode
        return True
    
    def show_schedule(self):
        """Display current schedule"""
        print("\n📋 Current Schedule")
        print("="*60)
        
        if not self.scheduled:
            print("No posts scheduled")
            return
        
        for post in sorted(self.scheduled, key=lambda x: x['scheduled_time']):
            scheduled_time = datetime.fromisoformat(post['scheduled_time'])
            status_icon = "⏰" if scheduled_time > datetime.now() else "🔴"
            
            print(f"\n{status_icon} {post['id']}")
            print(f"   Time: {scheduled_time.strftime('%Y-%m-%d %H:%M')}")
            print(f"   Status: {post['status']}")
            print(f"   Content: {post['content'][:60]}...")
    
    def run_scheduler_daemon(self, check_interval: int = 60):
        """
        Run as daemon - checks and posts on schedule
        """
        print("\n🤖 LinkedIn Scheduler Daemon Started")
        print("="*60)
        print(f"Checking every {check_interval} seconds")
        print("Press Ctrl+C to stop")
        
        while True:
            try:
                # Check for pending posts
                self.execute_scheduled_posts(auto_mode=True)
                
                # Show next scheduled post
                upcoming = []
                for post in self.scheduled:
                    if post['status'] == 'scheduled':
                        scheduled_time = datetime.fromisoformat(post['scheduled_time'])
                        if scheduled_time > datetime.now():
                            upcoming.append((scheduled_time, post))
                
                if upcoming:
                    next_time, next_post = min(upcoming, key=lambda x: x[0])
                    wait_time = (next_time - datetime.now()).total_seconds()
                    print(f"\n⏰ Next post in {int(wait_time/60)} minutes")
                    print(f"   {next_post['content'][:50]}...")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                print("\n\n🛑 Scheduler stopped")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                time.sleep(check_interval)


def main():
    """Main scheduling interface"""
    
    print("✊✋🖐 LinkedIn Scheduled Posting ONLY")
    print("="*60)
    print("NO DIRECT POSTS - Everything is scheduled")
    print()
    
    scheduler = LinkedInScheduledPoster()
    
    # Schedule a week of posts
    scheduler.schedule_daily_posts(days=7, posts_per_day=2)
    
    # Show schedule
    scheduler.show_schedule()
    
    # Execute pending
    print("\n📮 Checking for posts to execute...")
    scheduler.execute_scheduled_posts(auto_mode=SELENIUM_AVAILABLE)
    
    print("\n" + "="*60)
    print("✅ Scheduler ready!")
    print("\nOptions:")
    print("1. Run scheduler.run_scheduler_daemon() for continuous posting")
    print("2. Schedule more with scheduler.schedule_daily_posts()")
    print("3. Check pending with scheduler.get_pending_posts()")
    print("\n✊✋🖐 NO DIRECT POSTS - Only scheduled!")


if __name__ == "__main__":
    main()