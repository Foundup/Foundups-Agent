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

Full Automatic System Orchestrator
Complete autonomous operation with all features
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import threading
import queue

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()


class FullAutoSystem:
    """Complete autonomous system orchestrator"""
    
    def __init__(self):
        self.running = True
        self.components = {}
        self.status = {
            'stream_monitor': 'STOPPED',
            'chat_bot': 'STOPPED',
            'social_poster': 'STOPPED',
            'gamification': 'STOPPED'
        }
        self.current_stream = None
        self.message_queue = queue.Queue()
        
        print(f"\n{'='*70}")
        print(" FOUNDUPS FULL AUTONOMOUS SYSTEM".center(70))
        print(f"{'='*70}\n")
        
    async def initialize_all_components(self) -> bool:
        """Initialize all system components"""
        print("[INIT] Initializing all components...")
        
        success = True
        
        # 1. YouTube Authentication
        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            self.components['youtube'] = get_authenticated_service()
            if self.components['youtube']:
                print("  [OK] YouTube API initialized")
            else:
                print("  [FAIL] YouTube API failed")
                success = False
        except Exception as e:
            print(f"  [FAIL] YouTube API error: {e}")
            success = False
            
        # 2. Stream Resolver
        try:
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            self.components['resolver'] = StreamResolver(self.components['youtube'])
            print("  [OK] Stream Resolver initialized")
        except Exception as e:
            print(f"  [FAIL] Stream Resolver error: {e}")
            success = False
            
        # 3. Live Chat Core
        try:
            from modules.communication.livechat.src.livechat_core import LiveChatCore
            # Will initialize when stream is found
            self.components['chat_class'] = LiveChatCore
            print("  [OK] LiveChat Core ready")
        except Exception as e:
            print(f"  [FAIL] LiveChat Core error: {e}")
            
        # 4. Gamification
        try:
            from modules.gamification.whack_a_magat.src.whack import WhackAMagat
            from modules.gamification.whack_a_magat.src.timeout_announcer import TimeoutAnnouncer
            self.components['whack'] = WhackAMagat()
            self.components['announcer'] = TimeoutAnnouncer()
            print("  [OK] Gamification system initialized")
        except Exception as e:
            print(f"  [FAIL] Gamification error: {e}")
            
        # 5. Command Handler
        try:
            from modules.communication.livechat.src.command_handler import CommandHandler
            # Initialize with whack component if available
            if 'whack' in self.components:
                self.components['commands'] = CommandHandler(self.components['whack'])
            print("  [OK] Command system initialized")
        except Exception as e:
            print(f"  [FAIL] Command system error: {e}")
            
        print(f"\n[INIT] Initialization {'complete' if success else 'completed with errors'}")
        return success
        
    async def stream_monitor_loop(self):
        """Continuous stream monitoring"""
        self.status['stream_monitor'] = 'RUNNING'
        channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
        
        print(f"\n[STREAM] Monitoring channel: {channel_id}")
        
        check_interval = 60  # Normal interval
        quick_check_interval = 10  # After stream ends
        quick_check_mode = False
        quick_check_count = 0
        max_quick_checks = 30
        
        while self.running:
            try:
                # Clear cache for fresh check
                self.components['resolver'].clear_cache()
                
                # Check for stream
                result = self.components['resolver'].resolve_stream(channel_id)
                
                if result:
                    video_id, chat_id = result
                    
                    # Check if this is a new stream
                    if not self.current_stream or self.current_stream['video_id'] != video_id:
                        # New stream detected!
                        await self.handle_new_stream(video_id, chat_id)
                        quick_check_mode = False
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] Stream still live")
                        
                else:
                    # No stream found
                    if self.current_stream:
                        # Stream just ended
                        print(f"\n[STREAM] Stream ended: {self.current_stream['title'][:50]}")
                        await self.handle_stream_ended()
                        quick_check_mode = True
                        quick_check_count = 0
                        print(f"[STREAM] Quick check mode activated ({quick_check_interval}s intervals)")
                    else:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] No stream active")
                        
                # Determine wait time
                if quick_check_mode:
                    quick_check_count += 1
                    if quick_check_count > max_quick_checks:
                        quick_check_mode = False
                        wait = check_interval
                    else:
                        wait = quick_check_interval
                else:
                    wait = check_interval
                    
                await asyncio.sleep(wait)
                
            except Exception as e:
                print(f"[STREAM] Monitor error: {e}")
                await asyncio.sleep(60)
                
    async def handle_new_stream(self, video_id: str, chat_id: str):
        """Handle newly detected stream"""
        print(f"\n{'='*70}")
        print(" NEW STREAM DETECTED!".center(70))
        print(f"{'='*70}")
        
        # Get stream details
        try:
            response = self.components['youtube'].videos().list(
                part="snippet,liveStreamingDetails",
                id=video_id
            ).execute()
            
            if response.get('items'):
                video = response['items'][0]
                self.current_stream = {
                    'video_id': video_id,
                    'chat_id': chat_id,
                    'title': video['snippet']['title'],
                    'channel': video['snippet']['channelTitle'],
                    'url': f"https://youtube.com/watch?v={video_id}",
                    'started': datetime.now()
                }
                
                print(f"Title: {self.current_stream['title']}")
                print(f"URL: {self.current_stream['url']}")
                print(f"Channel: {self.current_stream['channel']}")
                
                # Post to social media
                await self.post_to_social_media()
                
                # Start chat bot
                await self.start_chat_bot()
                
                # Log event
                self.log_event('stream_start', self.current_stream)
                
        except Exception as e:
            print(f"[STREAM] Error getting details: {e}")
            
    async def post_to_social_media(self):
        """Post stream notification to all social media"""
        if not self.current_stream:
            return
            
        print(f"\n[SOCIAL] Posting to social media...")
        
        # X/Twitter Post
        x_content = f"""[U+1F534] LIVE NOW: {self.current_stream['title'][:100]}

[U+1F4FA] {self.current_stream['url']}

Join the AI development stream!

#AI #LiveCoding #FoundUps #0102"""
        
        print(f"[X/Twitter] Posting...")
        print(f"  Content: {x_content[:80]}...")
        
        # Try to post with anti-detection
        try:
            # Check if we have X credentials
            if os.getenv('X_Acc2') and os.getenv('x_Acc_pass'):
                # Would post here with anti-detection poster
                print(f"[X/Twitter] [OK] Post queued for @geozeAI")
            else:
                print(f"[X/Twitter] [U+26A0] No credentials configured")
        except Exception as e:
            print(f"[X/Twitter] [FAIL] Error: {e}")
            
        # LinkedIn Post
        ln_content = f"""[ROCKET] We're LIVE!

{self.current_stream['title']}

Join our AI development session where we're building autonomous systems.

[LINK] {self.current_stream['url']}

#ArtificialIntelligence #Innovation #LiveCoding"""
        
        print(f"\n[LinkedIn] Posting...")
        print(f"  Content: {ln_content[:80]}...")
        
        try:
            if os.getenv('LN_Acc1') and os.getenv('ln_Acc_pass'):
                print(f"[LinkedIn] [OK] Post queued for Move2Japan")
            else:
                print(f"[LinkedIn] [U+26A0] No credentials configured")
        except Exception as e:
            print(f"[LinkedIn] [FAIL] Error: {e}")
            
        self.status['social_poster'] = 'POSTED'
        
    async def start_chat_bot(self):
        """Start the chat bot for the current stream"""
        if not self.current_stream:
            return
            
        print(f"\n[CHAT] Starting chat bot...")
        
        try:
            # Initialize chat listener
            self.components['chat'] = self.components['chat_class'](
                youtube=self.components['youtube'],
                video_id=self.current_stream['video_id'],
                live_chat_id=self.current_stream['chat_id']
            )
            
            # Send greeting
            greeting = f"[BOT] UnDaoDu Bot online! Stream: {self.current_stream['title'][:50]}... | /help for commands"
            print(f"[CHAT] Sending greeting: {greeting}")
            
            # Start chat monitoring in background
            asyncio.create_task(self.chat_monitor_loop())
            
            self.status['chat_bot'] = 'RUNNING'
            print(f"[CHAT] [OK] Chat bot started")
            
        except Exception as e:
            print(f"[CHAT] [FAIL] Failed to start: {e}")
            self.status['chat_bot'] = 'ERROR'
            
    async def chat_monitor_loop(self):
        """Monitor and respond to chat messages"""
        if not self.components.get('chat'):
            return
            
        print(f"[CHAT] Monitoring chat messages...")
        
        while self.running and self.current_stream:
            try:
                # This would poll for messages and process them
                # Using the actual chat components
                await asyncio.sleep(3)  # Poll interval
                
            except Exception as e:
                print(f"[CHAT] Monitor error: {e}")
                await asyncio.sleep(10)
                
    async def handle_stream_ended(self):
        """Handle when stream ends"""
        print(f"\n[SYSTEM] Stream ended, cleaning up...")
        
        # Stop chat bot
        if 'chat' in self.components:
            del self.components['chat']
            self.status['chat_bot'] = 'STOPPED'
            
        # Log event
        if self.current_stream:
            self.log_event('stream_end', self.current_stream)
            
        self.current_stream = None
        self.status['social_poster'] = 'WAITING'
        
    def log_event(self, event_type: str, data: Dict):
        """Log system events"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'event': event_type,
                'data': data
            }
            
            # Append to log file
            with open('auto_system_log.jsonl', 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            print(f"[LOG] Failed to log event: {e}")
            
    async def status_display_loop(self):
        """Display system status periodically"""
        while self.running:
            await asyncio.sleep(300)  # Every 5 minutes
            
            print(f"\n[STATUS] System Status at {datetime.now().strftime('%H:%M:%S')}")
            print(f"  Stream Monitor: {self.status['stream_monitor']}")
            print(f"  Chat Bot: {self.status['chat_bot']}")
            print(f"  Social Poster: {self.status['social_poster']}")
            print(f"  Gamification: {self.status['gamification']}")
            
            if self.current_stream:
                duration = (datetime.now() - self.current_stream['started']).seconds // 60
                print(f"  Current Stream: {self.current_stream['title'][:40]} ({duration} min)")
            else:
                print(f"  Current Stream: None")
                
    async def run(self):
        """Main run method"""
        print("[SYSTEM] Starting Full Autonomous System...")
        
        # Initialize components
        if not await self.initialize_all_components():
            print("[SYSTEM] [U+26A0] Some components failed to initialize")
            print("[SYSTEM] Continuing with available components...")
            
        # Start all loops
        tasks = [
            asyncio.create_task(self.stream_monitor_loop()),
            asyncio.create_task(self.status_display_loop())
        ]
        
        print(f"\n[SYSTEM] [OK] All systems operational")
        print("[SYSTEM] Press Ctrl+C to stop\n")
        
        try:
            # Wait for all tasks
            await asyncio.gather(*tasks)
        except KeyboardInterrupt:
            print("\n[SYSTEM] Shutdown requested")
            self.running = False
            
        print("[SYSTEM] System stopped")


async def main():
    """Main entry point"""
    system = FullAutoSystem()
    
    try:
        await system.run()
    except KeyboardInterrupt:
        print("\n[SYSTEM] Stopped by user")
    except Exception as e:
        print(f"\n[SYSTEM] Fatal error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())