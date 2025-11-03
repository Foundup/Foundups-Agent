#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import io

"""
# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

Verbose Automatic Stream Monitor with Detailed Terminal Logging
Shows all checks, errors, and OAuth status in terminal

This version provides comprehensive terminal output for debugging
"""

import os
import sys
import time
import asyncio
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Set
import traceback

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()


class VerboseStreamMonitor:
    """
    Stream monitor with detailed terminal logging
    """
    
    def __init__(self):
        self.running = True
        self.current_stream = None
        self.posted_streams = set()
        self.youtube_service = None
        self.stream_resolver = None
        
        # Configuration
        self.channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
        self.check_interval = 60
        self.quick_check_interval = 10
        self.max_quick_checks = 30
        self.quick_check_mode = False
        self.quick_check_count = 0
        self.check_number = 0
        
        # Colors for terminal (ASCII)
        self.HEADER = "="*70
        self.DIVIDER = "-"*50
        
    def log(self, level: str, message: str, detail: str = None):
        """Enhanced logging with timestamps and details"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Level indicators
        indicators = {
            'START': '[>>>]',
            'OK': '[OK ]',
            'INFO': '[INF]',
            'CHECK': '[CHK]',
            'LIVE': '[LIV]',
            'NEW': '[NEW]',
            'POST': '[PST]',
            'WARN': '[WRN]',
            'ERROR': '[ERR]',
            'FAIL': '[FAL]',
            'OAUTH': '[OAU]',
            'QUOTA': '[QTA]',
            'IDLE': '[IDL]',
            'WAIT': '[...]',
            'END': '[END]'
        }
        
        indicator = indicators.get(level, '[???]')
        print(f"{timestamp} {indicator} {message}")
        
        if detail:
            # Indent detail lines
            for line in detail.split('\n'):
                if line.strip():
                    print(f"          {line}")
                    
    def initialize_services(self) -> bool:
        """Initialize YouTube services with detailed logging"""
        self.log('START', 'Initializing YouTube services...')
        
        try:
            # Import and initialize YouTube auth
            self.log('INFO', 'Loading YouTube authentication module...')
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            
            self.log('OAUTH', 'Attempting to authenticate with Google OAuth...')
            self.log('INFO', 'Trying credential sets in rotation order...')
            
            # Capture OAuth details
            try:
                self.youtube_service = get_authenticated_service()
                
                if self.youtube_service:
                    # Check which credential set was used
                    cred_set = getattr(self.youtube_service, '_credential_set', 'unknown')
                    self.log('OK', f'YouTube service authenticated successfully!', 
                            f'Using credential set: {cred_set}')
                    
                    # Test the service
                    test_response = self.youtube_service.channels().list(
                        part='snippet', 
                        mine=True
                    ).execute()
                    
                    if test_response.get('items'):
                        channel_name = test_response['items'][0]['snippet']['title']
                        self.log('OK', f'Connected to YouTube channel: {channel_name}')
                else:
                    self.log('FAIL', 'YouTube service is None')
                    return False
                    
            except Exception as oauth_error:
                self.log('OAUTH', 'OAuth authentication failed!', str(oauth_error))
                
                # Check if it's token expiration
                if 'invalid_grant' in str(oauth_error) or 'Token has been expired' in str(oauth_error):
                    self.log('ERROR', 'OAuth tokens have expired!', 
                            'Run: python modules/platform_integration/youtube_auth/scripts/authorize_sets_8_9_10.py')
                elif 'quotaExceeded' in str(oauth_error):
                    self.log('QUOTA', 'YouTube API quota exceeded!', 
                            'All credential sets may be exhausted for today')
                else:
                    self.log('ERROR', 'Unknown OAuth error', str(oauth_error))
                return False
            
            # Initialize stream resolver
            self.log('INFO', 'Initializing stream resolver...')
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            
            self.stream_resolver = StreamResolver(self.youtube_service)
            self.log('OK', 'Stream resolver initialized')
            
            # Check quota status
            self.check_quota_status()
            
            return True
            
        except ImportError as e:
            self.log('ERROR', 'Module import failed', str(e))
            return False
        except Exception as e:
            self.log('ERROR', 'Service initialization failed', str(e))
            self.log('INFO', 'Full traceback:', traceback.format_exc())
            return False
            
    def check_quota_status(self):
        """Check and log quota status"""
        try:
            quota_file = 'modules/platform_integration/youtube_auth/memory/quota_usage.json'
            if os.path.exists(quota_file):
                with open(quota_file, 'r') as f:
                    quota_data = json.load(f)
                    
                today = datetime.now().strftime('%Y-%m-%d')
                total_usage = 0
                
                self.log('QUOTA', 'Checking quota usage for today...')
                
                for cred_set, data in quota_data.items():
                    if 'daily_usage' in data and today in data['daily_usage']:
                        usage = data['daily_usage'][today]
                        total_usage += usage
                        
                        # Calculate percentage
                        percent = (usage / 10000) * 100
                        status = 'OK' if percent < 80 else 'WARN' if percent < 95 else 'CRITICAL'
                        
                        self.log('QUOTA', f'Set {cred_set}: {usage}/10000 units ({percent:.1f}%)', 
                                f'Status: {status}')
                
                self.log('INFO', f'Total quota used today: {total_usage} units across all sets')
                
        except Exception as e:
            self.log('WARN', 'Could not check quota status', str(e))
            
    async def check_for_stream(self) -> Optional[Dict]:
        """Check if a stream is live with detailed logging"""
        self.check_number += 1
        
        self.log('CHECK', f'Stream check #{self.check_number}')
        self.log('INFO', f'Channel ID: {self.channel_id}')
        
        try:
            # Clear cache for fresh detection
            self.log('INFO', 'Clearing stream cache...')
            self.stream_resolver.clear_cache()
            
            # Find active stream
            self.log('INFO', 'Searching for live streams...')
            result = self.stream_resolver.resolve_stream(self.channel_id)
            
            if result:
                video_id, chat_id = result
                self.log('LIVE', f'STREAM DETECTED!', f'Video ID: {video_id}')
                
                # Get stream details
                self.log('INFO', 'Fetching stream details...')
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
                        'url': f"https://youtube.com/watch?v={video_id}",
                        'concurrent_viewers': video['liveStreamingDetails'].get('concurrentViewers', 0)
                    }
                    
                    self.log('LIVE', 'Stream details retrieved:')
                    self.log('INFO', f'  Title: {stream_info["title"][:80]}')
                    self.log('INFO', f'  URL: {stream_info["url"]}')
                    self.log('INFO', f'  Viewers: {stream_info["concurrent_viewers"]}')
                    self.log('INFO', f'  Chat ID: {chat_id[:30]}...')
                    
                    return stream_info
            else:
                self.log('IDLE', 'No active stream found')
                
            return None
            
        except Exception as e:
            self.log('ERROR', f'Stream check failed', str(e))
            
            # Check for specific errors
            if 'quotaExceeded' in str(e):
                self.log('QUOTA', 'API quota exceeded during stream check')
            elif 'HttpError' in str(e.__class__.__name__):
                self.log('ERROR', 'HTTP error from YouTube API', str(e))
            
            return None
            
    async def handle_new_stream(self, stream_info: Dict):
        """Handle newly detected stream with detailed logging"""
        video_id = stream_info['video_id']
        
        # Check if already posted
        if video_id in self.posted_streams:
            self.log('INFO', 'Stream already posted, skipping')
            return
            
        print(f"\n{self.HEADER}")
        self.log('NEW', '*** NEW STREAM DETECTED! ***')
        print(self.HEADER)
        
        self.log('INFO', f'Title: {stream_info["title"]}')
        self.log('INFO', f'URL: {stream_info["url"]}')
        self.log('INFO', f'Viewers: {stream_info["concurrent_viewers"]}')
        
        print(f"\n{self.DIVIDER}")
        self.log('POST', 'Attempting to post to social media...')
        
        # Post to LinkedIn
        self.log('POST', 'Posting to LinkedIn...')
        ln_success = await self.post_to_linkedin(stream_info)
        
        # Post to X/Twitter
        self.log('POST', 'Posting to X/Twitter...')
        x_success = await self.post_to_x_twitter(stream_info)
        
        # Summary
        print(f"\n{self.DIVIDER}")
        if ln_success and x_success:
            self.log('OK', 'Successfully posted to all platforms!')
        elif ln_success or x_success:
            self.log('WARN', 'Posted to some platforms')
        else:
            self.log('FAIL', 'Failed to post to any platform')
            
        # Mark as posted
        self.posted_streams.add(video_id)
        self.current_stream = stream_info
        
        # Save state
        self.save_state()
        self.log('OK', 'State saved')
        
        print(f"{self.HEADER}\n")
        
    async def post_to_linkedin(self, stream_info: Dict) -> bool:
        """Post to LinkedIn with detailed logging"""
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import LinkedInAntiDetectionPoster
            
            content = f"""[LIVE] We're LIVE NOW!

{stream_info['title']}

Join our AI development session.

Link: {stream_info['url']}

#ArtificialIntelligence #SoftwareDevelopment #Innovation"""
            
            self.log('INFO', 'LinkedIn post content prepared')
            self.log('INFO', f'Content length: {len(content)} chars')
            
            poster = LinkedInAntiDetectionPoster()
            success = await poster.post_content(content)
            
            if success:
                self.log('OK', 'LinkedIn post successful!')
            else:
                self.log('FAIL', 'LinkedIn post failed')
                
            return success
            
        except Exception as e:
            self.log('ERROR', 'LinkedIn posting error', str(e))
            return False
            
    async def post_to_x_twitter(self, stream_info: Dict) -> bool:
        """Post to X/Twitter with detailed logging"""
        try:
            from modules.platform_integration.x_twitter.src.simple_x_poster import SimpleXPoster
            
            content = f"""[LIVE] NOW: {stream_info['title'][:100]}

Watch: {stream_info['url']}

#AI #LiveCoding #FoundUps"""
            
            self.log('INFO', 'X/Twitter post content prepared')
            self.log('INFO', f'Content length: {len(content)} chars')
            
            poster = SimpleXPoster()
            success = poster.post_to_x(content)
            
            if success:
                self.log('OK', 'X/Twitter post successful!')
            else:
                self.log('FAIL', 'X/Twitter post failed')
                
            return success
            
        except Exception as e:
            self.log('ERROR', 'X/Twitter posting error', str(e))
            return False
            
    def save_state(self):
        """Save monitor state"""
        try:
            state = {
                'posted_streams': list(self.posted_streams),
                'current_stream': self.current_stream,
                'last_check': datetime.now().isoformat(),
                'total_checks': self.check_number
            }
            
            with open('verbose_monitor_state.json', 'w') as f:
                json.dump(state, f, indent=2)
                
            self.log('INFO', f'State saved (posted: {len(self.posted_streams)} streams)')
            
        except Exception as e:
            self.log('WARN', 'State save failed', str(e))
            
    def load_state(self):
        """Load previous state"""
        try:
            if os.path.exists('verbose_monitor_state.json'):
                with open('verbose_monitor_state.json', 'r') as f:
                    state = json.load(f)
                    
                self.posted_streams = set(state.get('posted_streams', []))
                last_check = state.get('last_check', 'never')
                total_checks = state.get('total_checks', 0)
                
                self.log('INFO', f'State loaded:')
                self.log('INFO', f'  Posted streams: {len(self.posted_streams)}')
                self.log('INFO', f'  Last check: {last_check}')
                self.log('INFO', f'  Total checks: {total_checks}')
                
        except Exception as e:
            self.log('WARN', 'State load failed', str(e))
            
    async def monitoring_loop(self):
        """Main monitoring loop with detailed logging"""
        while self.running:
            try:
                print(f"\n{self.DIVIDER}")
                
                # Check for stream
                stream_info = await self.check_for_stream()
                
                if stream_info:
                    # Stream is live
                    if not self.current_stream or self.current_stream['video_id'] != stream_info['video_id']:
                        # New stream detected
                        await self.handle_new_stream(stream_info)
                    else:
                        # Same stream still live
                        self.log('LIVE', f'Stream still active', 
                                f'Viewers: {stream_info["concurrent_viewers"]}')
                        
                    # Exit quick check mode
                    if self.quick_check_mode:
                        self.quick_check_mode = False
                        self.log('INFO', 'Returning to normal check interval')
                        
                else:
                    # No stream detected
                    if self.current_stream:
                        # Stream just ended
                        self.log('END', f'Stream ended: {self.current_stream["title"][:50]}')
                        self.current_stream = None
                        self.quick_check_mode = True
                        self.quick_check_count = 0
                        self.log('INFO', f'Entering quick check mode ({self.quick_check_interval}s intervals)')
                    else:
                        self.log('IDLE', 'No stream active')
                        
                # Determine next check interval
                if self.quick_check_mode:
                    self.quick_check_count += 1
                    if self.quick_check_count > self.max_quick_checks:
                        self.quick_check_mode = False
                        self.log('INFO', 'Quick check timeout, returning to normal interval')
                        wait_time = self.check_interval
                    else:
                        wait_time = self.quick_check_interval
                        self.log('INFO', f'Quick check {self.quick_check_count}/{self.max_quick_checks}')
                else:
                    wait_time = self.check_interval
                    
                self.log('WAIT', f'Next check in {wait_time} seconds...')
                
                # Show countdown for last 5 seconds
                if wait_time > 5:
                    await asyncio.sleep(wait_time - 5)
                    for i in range(5, 0, -1):
                        print(f"\r          Checking in {i}...", end='', flush=True)
                        await asyncio.sleep(1)
                    print("\r" + " "*30 + "\r", end='', flush=True)  # Clear countdown
                else:
                    await asyncio.sleep(wait_time)
                    
            except KeyboardInterrupt:
                self.log('INFO', 'User interrupted, shutting down...')
                self.running = False
                break
            except Exception as e:
                self.log('ERROR', 'Monitoring loop error', str(e))
                self.log('INFO', 'Full traceback:', traceback.format_exc())
                self.log('WAIT', 'Retrying in 60 seconds...')
                await asyncio.sleep(60)
                
    async def run(self):
        """Main run method"""
        print(f"\n{self.HEADER}")
        print("    VERBOSE AUTOMATIC STREAM MONITOR")
        print(f"{self.HEADER}")
        print(f"Channel: {self.channel_id}")
        print(f"Check Interval: {self.check_interval}s (normal) / {self.quick_check_interval}s (quick)")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{self.HEADER}\n")
        
        # Load previous state
        self.load_state()
        
        # Initialize services
        if not self.initialize_services():
            self.log('FAIL', 'Service initialization failed!')
            self.log('INFO', 'Common fixes:')
            self.log('INFO', '  1. Check .env file for YOUTUBE_API_KEY')
            self.log('INFO', '  2. Re-authorize OAuth tokens if expired')
            self.log('INFO', '  3. Check quota limits (10,000 units/day per set)')
            return
            
        # Start monitoring
        self.log('START', 'Beginning automatic monitoring...')
        await self.monitoring_loop()
        
        self.log('END', 'Monitor stopped')
        self.save_state()


async def main():
    """Main entry point"""
    monitor = VerboseStreamMonitor()
    
    try:
        await monitor.run()
    except KeyboardInterrupt:
        print(f"\n{'='*70}")
        print("Monitor stopped by user")
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"Fatal error: {e}")
        print(traceback.format_exc())


if __name__ == "__main__":
    # Run the verbose monitor
    asyncio.run(main())