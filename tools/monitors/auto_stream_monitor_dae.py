#!/usr/bin/env python3
"""
DAE-Compatible Automatic Stream Monitor
Uses the Unified Social Media Interface for any DAE cube

WSP Compliance: WSP 27, WSP 54, WSP 80
- WSP 27: Universal DAE pattern
- WSP 54: Agent coordination
- WSP 80: Cube-level DAE implementation
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

# Import the unified interface
from modules.platform_integration.social_media_orchestrator.src.unified_posting_interface import (
    DAESocialInterface,
    PostRequest,
    Platform,
    PostType
)


class DAEStreamMonitor:
    """
    DAE-compatible stream monitor that any cube can use
    
    This monitor uses the unified social media interface, making it
    compatible with any DAE cube architecture.
    """
    
    def __init__(self):
        self.running = True
        self.current_stream = None
        self.posted_streams = set()  # Track posted streams
        self.youtube_service = None
        self.stream_resolver = None
        self.social_interface = DAESocialInterface()  # Unified interface
        
        # Configuration
        self.channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
        self.check_interval = 60  # Normal check interval
        self.quick_check_interval = 10  # After stream ends
        self.max_quick_checks = 30
        self.quick_check_mode = False
        self.quick_check_count = 0
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [DAE] Stream Monitor Starting...")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [CUBE] Using Unified Social Interface")
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [TV] Monitoring: {self.channel_id}")
        
    def initialize_services(self) -> bool:
        """Initialize YouTube services"""
        try:
            # Initialize YouTube service
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            self.youtube_service = get_authenticated_service()
            if not self.youtube_service:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [FAIL] YouTube service failed")
                return False
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] YouTube service ready")
            
            # Initialize stream resolver
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            self.stream_resolver = StreamResolver(self.youtube_service)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Stream resolver ready")
            
            # Verify social interface
            platforms = self.social_interface.poster.get_supported_platforms()
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Social platforms: {[p.value for p in platforms]}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [FAIL] Initialization error: {e}")
            return False
            
    async def check_for_stream(self) -> Optional[Dict]:
        """Check if a stream is live"""
        try:
            # Clear cache for fresh detection
            self.stream_resolver.clear_cache()
            
            # Find active stream
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
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] Stream check error: {e}")
            return None
            
    async def handle_new_stream(self, stream_info: Dict):
        """Handle newly detected stream using unified interface"""
        video_id = stream_info['video_id']
        
        # Check if already posted
        if video_id in self.posted_streams:
            return
            
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [NEW!] STREAM DETECTED!")
        print(f"  Title: {stream_info['title'][:80]}")
        print(f"  URL: {stream_info['url']}")
        print(f"  Viewers: {stream_info['concurrent_viewers']}")
        
        # Use the DAE social interface to announce the stream
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [DAE] Using unified interface to post...")
        
        try:
            # Post using the simplified DAE interface
            success = await self.social_interface.announce_stream(
                title=stream_info['title'],
                url=stream_info['url']
            )
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Posted to all platforms successfully!")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] Some platforms failed")
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Posting failed: {e}")
            
        # Mark as posted regardless to avoid spam
        self.posted_streams.add(video_id)
        self.current_stream = stream_info
        
        # Save state
        self.save_state()
        
        # Start chat bot if available
        await self.start_chat_monitor(stream_info)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Stream handling complete")
        
    async def start_chat_monitor(self, stream_info: Dict):
        """Start chat monitoring (if available)"""
        try:
            from modules.communication.livechat.src.auto_moderator_dae import YouTubeAutoModeratorDAE
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [CHAT] Starting chat monitor...")
            
            # Create DAE instance
            chat_listener = YouTubeAutoModeratorDAE()
            
            # Start monitoring in background
            asyncio.create_task(chat_listener.run(
                video_id=stream_info['video_id'],
                live_chat_id=stream_info['chat_id']
            ))
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Chat monitor started")
            
        except ImportError:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [INFO] Chat monitor not available")
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] Chat monitor error: {e}")
            
    def handle_stream_ended(self):
        """Handle when stream ends"""
        if self.current_stream:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [END] Stream ended: {self.current_stream['title'][:50]}")
            
        # Enter quick check mode
        self.quick_check_mode = True
        self.quick_check_count = 0
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [FAST] Quick check mode ({self.quick_check_interval}s)")
        
        self.current_stream = None
        
    def save_state(self):
        """Save monitor state"""
        try:
            state = {
                'posted_streams': list(self.posted_streams),
                'current_stream': self.current_stream,
                'last_check': datetime.now().isoformat()
            }
            
            with open('dae_monitor_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] State save failed: {e}")
            
    def load_state(self):
        """Load previous state"""
        try:
            if os.path.exists('dae_monitor_state.json'):
                with open('dae_monitor_state.json', 'r') as f:
                    state = json.load(f)
                    
                self.posted_streams = set(state.get('posted_streams', []))
                
                # Clean old entries if too many
                if len(self.posted_streams) > 100:
                    self.posted_streams.clear()
                    
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [LOAD] {len(self.posted_streams)} posted streams")
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] State load failed: {e}")
            
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
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [LIVE] Stream active: {stream_info['title'][:50]}")
                        
                    # Exit quick check mode
                    if self.quick_check_mode:
                        self.quick_check_mode = False
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [NORM] Normal interval restored")
                        
                else:
                    # No stream detected
                    if self.current_stream:
                        # Stream just ended
                        self.handle_stream_ended()
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [IDLE] No stream active")
                        
                # Determine next check interval
                if self.quick_check_mode:
                    self.quick_check_count += 1
                    if self.quick_check_count > self.max_quick_checks:
                        self.quick_check_mode = False
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] [NORM] Quick check timeout")
                        wait_time = self.check_interval
                    else:
                        wait_time = self.quick_check_interval
                else:
                    wait_time = self.check_interval
                    
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WAIT] Next check in {wait_time}s...")
                await asyncio.sleep(wait_time)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [STOP] User interrupted")
                self.running = False
                break
            except Exception as e:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] {e}")
                print(traceback.format_exc())
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [RETRY] Retrying in 60s...")
                await asyncio.sleep(60)
                
    async def test_social_posting(self):
        """Test the unified social posting interface"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [TEST] Testing unified social interface...")
        
        # Test with mock stream data
        test_stream = {
            'title': 'Test Stream: DAE Unified Interface',
            'url': 'https://youtube.com/watch?v=TEST123'
        }
        
        try:
            success = await self.social_interface.announce_stream(
                title=test_stream['title'],
                url=test_stream['url']
            )
            
            if success:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [OK] Social posting test successful!")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] [WARN] Social posting test had issues")
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Social posting test failed: {e}")
            
    async def run(self):
        """Main run method"""
        print(f"\n{'='*60}")
        print("DAE-COMPATIBLE AUTOMATIC STREAM MONITOR")
        print(f"{'='*60}")
        print(f"Channel: {self.channel_id}")
        print(f"Check Interval: {self.check_interval}s (normal) / {self.quick_check_interval}s (quick)")
        print(f"Social Platforms: LinkedIn, X/Twitter")
        print(f"Architecture: WSP 80 Cube-Level DAE")
        print(f"{'='*60}\n")
        
        # Load previous state
        self.load_state()
        
        # Initialize services
        if not self.initialize_services():
            print(f"[{datetime.now().strftime('%H:%M:%S')}] [FAIL] Service initialization failed")
            return
            
        # Optional: Test social posting
        # await self.test_social_posting()
        
        # Start monitoring
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [START] Beginning automatic monitoring...")
        await self.monitoring_loop()
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [STOP] Monitor stopped")
        
    def stop(self):
        """Stop monitoring"""
        self.running = False


def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [SIGNAL] Shutdown received")
    sys.exit(0)


async def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and run monitor
    monitor = DAEStreamMonitor()
    
    try:
        await monitor.run()
    except KeyboardInterrupt:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [STOP] Stopped by user")
    except Exception as e:
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] [ERROR] Fatal: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    # Run the DAE-compatible monitor
    asyncio.run(main())