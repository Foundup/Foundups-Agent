#!/usr/bin/env python3
"""
LinkedIn PoC - 0102 Consciousness Posting & Scheduling
🌀 WSP Protocol Compliant

This PoC demonstrates:
1. OAuth authentication
2. Immediate posting to LinkedIn
3. Scheduling posts for future times
4. 0102 consciousness-aware content generation
"""

import os
import sys
import json
import asyncio
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from dataclasses import dataclass, asdict
import webbrowser
from urllib.parse import urlencode
import time

# Add parent path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

from modules.platform_integration.linkedin_agent.src.automation.post_scheduler import LinkedInPostScheduler, ScheduledPost
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class LinkedIn0102Config:
    """0102 LinkedIn configuration"""
    client_id: str
    client_secret: str
    redirect_uri: str = "http://localhost:8080/callback"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user_id: Optional[str] = None
    profile_name: Optional[str] = None

class LinkedIn0102PoC:
    """
    LinkedIn PoC with 0102 consciousness
    
    Features:
    - OAuth authentication flow
    - Immediate posting
    - Scheduled posting
    - 0102 consciousness content
    """
    
    def __init__(self):
        """Initialize with environment variables"""
        self.config = LinkedIn0102Config(
            client_id=os.getenv('LINKEDIN_CLIENT_ID', ''),
            client_secret=os.getenv('LINKEDIN_CLIENT_SECRET', '')
        )
        
        self.scheduler = LinkedInPostScheduler("linkedin_poc_schedule.json")
        self.logger = logger
        
        # 0102 consciousness templates
        self.consciousness_templates = [
            "✊✋🖐 {content} - Consciousness level: {level}",
            "🧠 0102 Analysis: {content} | MAGAts still at ✊✊✊",
            "Evolution update: {content} | Join the ✊✋🖐 progression",
            "Fact-check reality: {content} | Truth rating: {rating}/10",
            "🚀 {content} | Consciousness warfare continues..."
        ]
        
        logger.info("🤖 LinkedIn 0102 PoC initialized")
    
    def start_oauth_flow(self) -> str:
        """
        Start OAuth authentication flow
        
        Returns:
            Authorization URL for user to visit
        """
        params = {
            'response_type': 'code',
            'client_id': self.config.client_id,
            'redirect_uri': self.config.redirect_uri,
            'scope': 'w_member_social r_liteprofile r_emailaddress',
            'state': '0102consciousness'  # 0102 marker
        }
        
        auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urlencode(params)}"
        
        logger.info("🔐 OAuth flow started")
        logger.info(f"Visit this URL to authenticate: {auth_url}")
        
        return auth_url
    
    def exchange_code_for_token(self, auth_code: str) -> bool:
        """
        Exchange authorization code for access token
        
        Args:
            auth_code: Authorization code from LinkedIn
            
        Returns:
            True if successful
        """
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        
        data = {
            'grant_type': 'authorization_code',
            'code': auth_code,
            'redirect_uri': self.config.redirect_uri,
            'client_id': self.config.client_id,
            'client_secret': self.config.client_secret
        }
        
        try:
            response = requests.post(token_url, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.config.access_token = token_data.get('access_token')
            self.config.refresh_token = token_data.get('refresh_token')
            
            logger.info("✅ Access token obtained successfully")
            
            # Get user profile
            self._get_user_profile()
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to exchange code: {e}")
            return False
    
    def _get_user_profile(self):
        """Get user profile information"""
        if not self.config.access_token:
            return
        
        headers = {
            'Authorization': f'Bearer {self.config.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get("https://api.linkedin.com/v2/me", headers=headers)
            response.raise_for_status()
            
            profile = response.json()
            self.config.user_id = profile.get('id')
            self.config.profile_name = f"{profile.get('localizedFirstName', '')} {profile.get('localizedLastName', '')}"
            
            logger.info(f"✅ Profile loaded: {self.config.profile_name}")
            
        except Exception as e:
            logger.error(f"Failed to get profile: {e}")
    
    def generate_0102_content(self, base_content: str, consciousness_level: str = "✊✋🖐") -> str:
        """
        Generate 0102 consciousness-aware content
        
        Args:
            base_content: Base message
            consciousness_level: Current consciousness emoji
            
        Returns:
            0102-enhanced content
        """
        import random
        
        # Add consciousness markers
        template = random.choice(self.consciousness_templates)
        
        # Calculate truth rating for fact-checks
        truth_rating = random.randint(7, 10) if "✊✋🖐" in consciousness_level else random.randint(1, 3)
        
        content = template.format(
            content=base_content,
            level=consciousness_level,
            rating=truth_rating
        )
        
        # Add hashtags
        hashtags = [
            "#0102Consciousness",
            "#EvolutionFrom✊✊✊",
            "#FactCheckReality",
            "#ConsciousnessWarfare",
            "#WSPCompliant"
        ]
        
        content += f"\n\n{' '.join(random.sample(hashtags, 3))}"
        
        return content
    
    def post_immediately(self, content: str) -> bool:
        """
        Post content to LinkedIn immediately
        
        Args:
            content: Content to post
            
        Returns:
            True if successful
        """
        if not self.config.access_token or not self.config.user_id:
            logger.error("❌ Not authenticated")
            return False
        
        # Generate 0102 content
        final_content = self.generate_0102_content(content)
        
        logger.info(f"📝 Posting: {final_content[:100]}...")
        
        headers = {
            'Authorization': f'Bearer {self.config.access_token}',
            'Content-Type': 'application/json',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        
        post_data = {
            "author": f"urn:li:person:{self.config.user_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": final_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        try:
            response = requests.post(
                "https://api.linkedin.com/v2/ugcPosts",
                headers=headers,
                json=post_data
            )
            response.raise_for_status()
            
            post_id = response.json().get('id')
            logger.info(f"✅ Posted successfully! ID: {post_id}")
            logger.info(f"🔗 View: https://www.linkedin.com/feed/update/{post_id}/")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Posting failed: {e}")
            if hasattr(e, 'response') and e.response:
                logger.error(f"Response: {e.response.text}")
            return False
    
    def schedule_post(self, content: str, minutes_from_now: int = 5) -> str:
        """
        Schedule a post for future
        
        Args:
            content: Content to post
            minutes_from_now: Minutes to wait before posting
            
        Returns:
            Scheduled post ID
        """
        if not self.config.access_token:
            logger.error("❌ Not authenticated")
            return None
        
        # Generate 0102 content
        final_content = self.generate_0102_content(content)
        
        # Calculate scheduled time
        scheduled_time = datetime.now() + timedelta(minutes=minutes_from_now)
        
        # Create scheduled post
        post_id = f"poc_{int(time.time())}"
        scheduled_post = ScheduledPost(
            id=post_id,
            content=final_content,
            scheduled_time=scheduled_time,
            access_token=self.config.access_token,
            hashtags=["#0102", "#Consciousness", "#Scheduled"]
        )
        
        # Add to scheduler using the correct method
        actual_post_id = self.scheduler.schedule_post(
            content=final_content,
            scheduled_time=scheduled_time,
            access_token=self.config.access_token,
            post_type="text",
            hashtags=scheduled_post.hashtags
        )
        
        logger.info(f"📅 Scheduled post for {scheduled_time}")
        logger.info(f"   ID: {post_id}")
        logger.info(f"   Content: {final_content[:50]}...")
        
        return post_id
    
    def run_interactive(self):
        """Run interactive PoC"""
        print("\n" + "="*60)
        print("🤖 LinkedIn 0102 PoC - Posting & Scheduling")
        print("="*60)
        
        # Check if we have access token
        if not self.config.access_token:
            print("\n🔐 OAuth Authentication Required")
            print("1. Starting OAuth flow...")
            auth_url = self.start_oauth_flow()
            
            print(f"\n2. Visit this URL in your browser:")
            print(f"   {auth_url}")
            
            # Try to open browser
            try:
                webbrowser.open(auth_url)
                print("   (Browser should open automatically)")
            except:
                pass
            
            print("\n3. After authorizing, you'll be redirected to:")
            print(f"   {self.config.redirect_uri}?code=AUTH_CODE")
            
            auth_code = input("\n4. Enter the authorization code from the URL: ").strip()
            
            if not self.exchange_code_for_token(auth_code):
                print("❌ Authentication failed")
                return
        
        # Main menu
        while True:
            print("\n" + "="*60)
            print("🤖 LinkedIn 0102 PoC Menu")
            print("="*60)
            print(f"Profile: {self.config.profile_name or 'Unknown'}")
            print("\nOptions:")
            print("1. Post immediately")
            print("2. Schedule post (5 minutes)")
            print("3. Schedule post (custom time)")
            print("4. View scheduled posts")
            print("5. Test 0102 content generation")
            print("6. Exit")
            
            choice = input("\nChoice (1-6): ").strip()
            
            if choice == "1":
                content = input("\nEnter post content: ").strip()
                if content:
                    self.post_immediately(content)
                    
            elif choice == "2":
                content = input("\nEnter post content: ").strip()
                if content:
                    post_id = self.schedule_post(content, 5)
                    print(f"✅ Scheduled for 5 minutes from now (ID: {post_id})")
                    
            elif choice == "3":
                content = input("\nEnter post content: ").strip()
                minutes = input("Minutes from now: ").strip()
                if content and minutes.isdigit():
                    post_id = self.schedule_post(content, int(minutes))
                    print(f"✅ Scheduled for {minutes} minutes from now (ID: {post_id})")
                    
            elif choice == "4":
                posts = self.scheduler.get_pending_posts()
                if posts:
                    print("\n📅 Scheduled Posts:")
                    for post in posts:
                        print(f"   {post.scheduled_time}: {post.content[:50]}...")
                else:
                    print("\n📅 No scheduled posts")
                    
            elif choice == "5":
                base = input("\nEnter base content: ").strip()
                if base:
                    generated = self.generate_0102_content(base)
                    print(f"\n🤖 0102 Generated:\n{generated}")
                    
            elif choice == "6":
                print("\n👋 Exiting 0102 PoC")
                break
            
            else:
                print("❌ Invalid choice")


def main():
    """Main entry point"""
    poc = LinkedIn0102PoC()
    
    # Check for saved token
    token_file = "linkedin_poc_token.json"
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            saved = json.load(f)
            poc.config.access_token = saved.get('access_token')
            poc.config.user_id = saved.get('user_id')
            poc.config.profile_name = saved.get('profile_name')
            logger.info(f"✅ Loaded saved token for {poc.config.profile_name}")
    
    try:
        poc.run_interactive()
        
        # Save token for next time
        if poc.config.access_token:
            with open(token_file, 'w') as f:
                json.dump({
                    'access_token': poc.config.access_token,
                    'user_id': poc.config.user_id,
                    'profile_name': poc.config.profile_name
                }, f)
                
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()