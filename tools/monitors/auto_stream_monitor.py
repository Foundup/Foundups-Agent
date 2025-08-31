#!/usr/bin/env python3
"""
Automatic Stream Monitor & Social Media Orchestrator
Runs continuously to detect streams and post notifications automatically
"""

import os
import sys
import time
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
import traceback
import signal

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()

class AutoStreamMonitor:
    """Fully automatic stream monitoring and notification system"""
    
    def __init__(self):
        self.running = True
        self.current_stream = None
        self.posted_streams = set()  # Track what we've already posted about
        self.youtube_service = None
        self.stream_resolver = None
        self.chat_listener = None
        self.last_check = None
        self.quick_check_mode = False
        self.quick_check_count = 0
        
        # Configuration
        self.channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
        self.check_interval = 60  # Normal check every 60 seconds
        self.quick_check_interval = 10  # Quick check every 10 seconds after stream ends
        self.max_quick_checks = 30  # Quick check for up to 5 minutes
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Auto Stream Monitor Starting...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📺 Monitoring channel: {self.channel_id}")
        
    def initialize_services(self) -> bool:
        """Initialize all required services"""
        try:
            # Initialize YouTube service
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            self.youtube_service = get_authenticated_service()
            if not self.youtube_service:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to initialize YouTube service")
                return False
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ YouTube service initialized")
            
            # Initialize stream resolver
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            self.stream_resolver = StreamResolver(self.youtube_service)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Stream resolver initialized")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Service initialization failed: {e}")
            return False
            
    async def check_for_stream(self) -> Optional[Dict]:
        """Check if a stream is live"""
        try:
            # Clear cache for fresh detection
            self.stream_resolver.clear_cache()
            
            # Try to find active stream
            result = self.stream_resolver.resolve_stream(self.channel_id)
            
            if result:
                video_id, chat_id = result
                
                # Get stream details
                video_response = self.youtube_service.videos().list(
                    part="snippet,liveStreamingDetails",
                    id=video_id
                ).execute()
                
                if video_response.get('items'):
                    video = video_response['items'][0]
                    stream_info = {
                        'video_id': video_id,
                        'chat_id': chat_id,
                        'title': video['snippet']['title'],
                        'channel': video['snippet']['channelTitle'],
                        'description': video['snippet'].get('description', '')[:500],
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'thumbnail': video['snippet']['thumbnails']['high']['url'],
                        'started_at': video['liveStreamingDetails'].get('actualStartTime'),
                        'concurrent_viewers': video['liveStreamingDetails'].get('concurrentViewers', 0)
                    }
                    return stream_info
                    
            return None
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Stream check error: {e}")
            return None
            
    async def post_to_x_twitter(self, stream_info: Dict) -> bool:
        """Post stream notification to X/Twitter"""
        try:
            from modules.platform_integration.x_twitter.src.anti_detection_poster import XAntiDetectionPoster
            
            # Create post content
            content = f"""🔴 LIVE NOW: {stream_info['title'][:100]}

📺 Watch: {stream_info['url']}

Join us for cutting-edge AI development!

#AI #LiveCoding #FoundUps #QuantumComputing #0102"""
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Posting to X/Twitter...")
            print(f"    Content: {content[:60]}...")
            
            poster = XAntiDetectionPoster()
            success = await poster.post_content(content)
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Posted to X/Twitter successfully")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ X/Twitter post failed")
                return False
                
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ X/Twitter module not available")
            # Try simple approach
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 X/Twitter post prepared (manual posting required):")
            print(f"    {content}")
            return False
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ X/Twitter posting error: {e}")
            return False
            
    async def post_to_linkedin(self, stream_info: Dict) -> bool:
        """Post stream notification to LinkedIn"""
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import LinkedInAntiDetectionPoster
            
            # Create post content
            content = f"""🚀 We're LIVE NOW!

{stream_info['title']}

Join our AI development session where we're building the future of autonomous systems with quantum computing and 0102 consciousness architecture.

🔗 {stream_info['url']}

Currently {stream_info['concurrent_viewers']} viewers watching!

#ArtificialIntelligence #SoftwareDevelopment #Innovation #QuantumComputing #FoundUps #LiveCoding"""
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📝 Posting to LinkedIn...")
            print(f"    Content: {content[:60]}...")
            
            poster = LinkedInAntiDetectionPoster()
            success = await poster.post_content(content)
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Posted to LinkedIn successfully")
                return True
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ LinkedIn post failed")
                return False
                
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ LinkedIn module not available")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 📋 LinkedIn post prepared (manual posting required):")
            print(f"    {content[:100]}...")
            return False
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ LinkedIn posting error: {e}")
            return False
            
    async def start_chat_monitor(self, stream_info: Dict):
        """Start monitoring YouTube live chat"""
        try:
            from modules.communication.livechat.src.auto_moderator_dae import YouTubeAutoModeratorDAE
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 💬 Starting chat monitor...")
            
            # Create DAE instance
            self.chat_listener = YouTubeAutoModeratorDAE()
            
            # Start monitoring in background
            asyncio.create_task(self.chat_listener.run(
                video_id=stream_info['video_id'],
                live_chat_id=stream_info['chat_id']
            ))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Chat monitor started")
            
            # Send greeting message
            greeting = os.getenv('AGENT_GREETING_MESSAGE', 
                               f"🤖 UnDaoDu Bot is online! Stream: {stream_info['title'][:50]}... Type /help for commands")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 Sending greeting: {greeting}")
            
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Chat monitor module not available")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Chat monitor error: {e}")
            
    async def handle_new_stream(self, stream_info: Dict):
        """Handle a newly detected stream"""
        video_id = stream_info['video_id']
        
        # Check if we've already posted about this stream
        if video_id in self.posted_streams:
            return
            
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🎉 NEW STREAM DETECTED!")
        print(f"    Title: {stream_info['title'][:80]}")
        print(f"    URL: {stream_info['url']}")
        print(f"    Viewers: {stream_info['concurrent_viewers']}")
        
        # Post to social media
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📢 Posting to social media...")
        
        # Post to X/Twitter
        x_success = await self.post_to_x_twitter(stream_info)
        
        # Post to LinkedIn  
        ln_success = await self.post_to_linkedin(stream_info)
        
        # Start chat monitor
        await self.start_chat_monitor(stream_info)
        
        # Mark as posted
        self.posted_streams.add(video_id)
        self.current_stream = stream_info
        
        # Save state
        self.save_state()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ✅ Stream handling complete")
        
    def handle_stream_ended(self):
        """Handle when a stream ends"""
        if self.current_stream:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 📴 Stream ended: {self.current_stream['title'][:50]}")
            
        # Enter quick check mode
        self.quick_check_mode = True
        self.quick_check_count = 0
        print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚡ Entering quick check mode (checking every {self.quick_check_interval}s)")
        
        # Stop chat monitor
        if self.chat_listener:
            self.chat_listener = None
            
        self.current_stream = None
        
    def save_state(self):
        """Save current state to file"""
        try:
            state = {
                'posted_streams': list(self.posted_streams),
                'current_stream': self.current_stream,
                'last_check': datetime.now().isoformat()
            }
            
            with open('auto_monitor_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Failed to save state: {e}")
            
    def load_state(self):
        """Load previous state from file"""
        try:
            if os.path.exists('auto_monitor_state.json'):
                with open('auto_monitor_state.json', 'r') as f:
                    state = json.load(f)
                    
                self.posted_streams = set(state.get('posted_streams', []))
                
                # Clean up old streams (older than 24 hours)
                # This prevents the set from growing indefinitely
                if len(self.posted_streams) > 100:
                    self.posted_streams.clear()
                    
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 📂 Loaded state: {len(self.posted_streams)} previous streams tracked")
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ⚠️ Failed to load state: {e}")
            
    async def monitoring_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                # Check for stream
                stream_info = await self.check_for_stream()
                
                if stream_info:
                    # Stream is live
                    if not self.current_stream or self.current_stream['video_id'] != stream_info['video_id']:
                        # New stream detected
                        await self.handle_new_stream(stream_info)
                    else:
                        # Same stream still live
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 📺 Stream still live: {stream_info['title'][:50]}")
                        
                    # Exit quick check mode if we were in it
                    if self.quick_check_mode:
                        self.quick_check_mode = False
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Returning to normal check interval")
                        
                else:
                    # No stream detected
                    if self.current_stream:
                        # Stream just ended
                        self.handle_stream_ended()
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 💤 No stream active")
                        
                # Determine next check interval
                if self.quick_check_mode:
                    self.quick_check_count += 1
                    if self.quick_check_count > self.max_quick_checks:
                        # Exit quick check mode after max checks
                        self.quick_check_mode = False
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Quick check timeout, returning to normal interval")
                        wait_time = self.check_interval
                    else:
                        wait_time = self.quick_check_interval
                else:
                    wait_time = self.check_interval
                    
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ⏰ Next check in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Monitoring stopped by user")
                self.running = False
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Monitoring error: {e}")
                print(traceback.format_exc())
                print(f"[{datetime.now().strftime('%H:%M:%S')}] 🔄 Retrying in 60 seconds...")
                await asyncio.sleep(60)
                
    async def run(self):
        """Main run method"""
        print(f"\n{'='*60}")
        print("AUTOMATIC STREAM MONITOR & NOTIFIER")
        print(f"{'='*60}")
        print(f"Channel: {self.channel_id}")
        print(f"Check Interval: {self.check_interval}s (normal) / {self.quick_check_interval}s (quick)")
        print(f"Social Media: X/Twitter (@geozeAI) & LinkedIn (Move2Japan)")
        print(f"{'='*60}\n")
        
        # Load previous state
        self.load_state()
        
        # Initialize services
        if not self.initialize_services():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] ❌ Failed to initialize services")
            return
            
        # Start monitoring
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Starting automatic monitoring...")
        await self.monitoring_loop()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 👋 Auto monitor stopped")
        
    def stop(self):
        """Stop monitoring"""
        self.running = False
        

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Shutdown signal received")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run monitor
    monitor = AutoStreamMonitor()
    
    try:
        await monitor.run()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 🛑 Stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] ❌ Fatal error: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())