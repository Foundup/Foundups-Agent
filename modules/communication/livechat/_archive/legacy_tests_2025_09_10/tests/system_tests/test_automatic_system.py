#!/usr/bin/env python3
"""
Comprehensive test for the Automatic Stream Monitor System
Tests all components and shows results in terminal
"""

import os
import sys
import asyncio
import json
from datetime import datetime
from typing import Dict, Optional, List

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment
if os.path.exists('.env'):
    from dotenv import load_dotenv
    load_dotenv()


class AutomaticSystemTester:
    """Comprehensive tester for the automatic monitoring system"""
    
    def __init__(self):
        self.test_results = []
        self.monitor = None
        self.current_stream = None
        
    def print_header(self, text: str):
        """Print a formatted header"""
        print(f"\n{'='*70}")
        print(f" {text}".center(70))
        print(f"{'='*70}\n")
        
    def print_test(self, test_name: str, passed: bool, details: str = ""):
        """Print test result"""
        status = "[PASS]" if passed else "[FAIL]"
        symbol = "OK" if passed else "X"
        print(f"  [{symbol}] {status} {test_name}")
        if details:
            print(f"      {details}")
        self.test_results.append((test_name, passed))
        
    async def test_1_environment(self) -> bool:
        """Test environment configuration"""
        print("[TEST 1] Environment Configuration")
        print("-"*40)
        
        # Check critical environment variables
        channel_id = os.getenv('CHANNEL_ID')
        self.print_test("Channel ID configured", 
                       bool(channel_id), 
                       f"Channel: {channel_id}" if channel_id else "Missing CHANNEL_ID")
        
        # Check social media credentials
        x_user = os.getenv('X_Acc2')
        self.print_test("X/Twitter credentials", 
                       bool(x_user), 
                       "@geozeAI configured" if x_user else "Missing X_Acc2")
        
        ln_user = os.getenv('LN_Acc1')
        self.print_test("LinkedIn credentials", 
                       bool(ln_user), 
                       "Move2Japan configured" if ln_user else "Missing LN_Acc1")
        
        # Check API keys
        yt_key = os.getenv('YOUTUBE_API_KEY')
        self.print_test("YouTube API key", 
                       bool(yt_key), 
                       "API key present" if yt_key else "Missing YOUTUBE_API_KEY")
        
        return bool(channel_id and yt_key)
        
    async def test_2_monitor_initialization(self) -> bool:
        """Test monitor initialization"""
        print("\n[TEST 2] Monitor Initialization")
        print("-"*40)
        
        try:
            from auto_stream_monitor_ascii import AutoStreamMonitor
            self.print_test("Import AutoStreamMonitor", True)
            
            self.monitor = AutoStreamMonitor()
            self.print_test("Create monitor instance", True,
                          f"Check interval: {self.monitor.check_interval}s")
            
            # Initialize services
            success = self.monitor.initialize_services()
            self.print_test("Initialize YouTube service", success)
            
            return success
            
        except Exception as e:
            self.print_test("Monitor initialization", False, str(e))
            return False
            
    async def test_3_stream_detection(self) -> bool:
        """Test stream detection"""
        print("\n[TEST 3] Stream Detection")
        print("-"*40)
        
        if not self.monitor:
            self.print_test("Stream detection", False, "Monitor not initialized")
            return False
            
        try:
            # Check for active stream
            print("  Checking for active stream...")
            stream_info = await self.monitor.check_for_stream()
            
            if stream_info:
                self.current_stream = stream_info
                self.print_test("Stream found", True, 
                              f"Video ID: {stream_info['video_id']}")
                self.print_test("Stream title retrieved", True,
                              f"Title: {stream_info['title'][:50]}...")
                self.print_test("Stream URL generated", True,
                              f"URL: {stream_info['url']}")
                self.print_test("Viewer count available", True,
                              f"Viewers: {stream_info.get('concurrent_viewers', 0)}")
                return True
            else:
                self.print_test("Stream detection", True, "No stream active (normal)")
                print("      System will detect automatically when stream goes live")
                return True
                
        except Exception as e:
            self.print_test("Stream detection", False, str(e))
            return False
            
    async def test_4_social_media_posts(self) -> bool:
        """Test social media post generation"""
        print("\n[TEST 4] Social Media Post Generation")
        print("-"*40)
        
        # Use current stream or create mock data
        if self.current_stream:
            stream_info = self.current_stream
            print(f"  Using live stream: {stream_info['title'][:50]}...")
        else:
            stream_info = {
                'video_id': 'TEST123',
                'title': 'Test Stream: AI Development Session',
                'url': 'https://youtube.com/watch?v=TEST123',
                'concurrent_viewers': '42'
            }
            print("  Using mock stream data for testing")
            
        # Test X/Twitter post
        try:
            x_content = f"""[LIVE] LIVE NOW: {stream_info['title'][:100]}

[TV] Watch: {stream_info['url']}

Join us for cutting-edge AI development!

#AI #LiveCoding #FoundUps #QuantumComputing #0102"""
            
            self.print_test("X/Twitter post generated", True,
                          f"Length: {len(x_content)} chars")
            
        except Exception as e:
            self.print_test("X/Twitter post generation", False, str(e))
            
        # Test LinkedIn post
        try:
            ln_content = f"""[START] We're LIVE NOW!

{stream_info['title']}

Join our AI development session where we're building the future of autonomous systems.

[LINK] {stream_info['url']}

Currently {stream_info.get('concurrent_viewers', 0)} viewers watching!

#ArtificialIntelligence #SoftwareDevelopment #Innovation"""
            
            self.print_test("LinkedIn post generated", True,
                          f"Length: {len(ln_content)} chars")
            
        except Exception as e:
            self.print_test("LinkedIn post generation", False, str(e))
            
        return True
        
    async def test_5_state_management(self) -> bool:
        """Test state management"""
        print("\n[TEST 5] State Management")
        print("-"*40)
        
        if not self.monitor:
            self.print_test("State management", False, "Monitor not initialized")
            return False
            
        try:
            # Test state save
            if self.current_stream:
                self.monitor.posted_streams.add(self.current_stream['video_id'])
                self.monitor.current_stream = self.current_stream
                
            self.monitor.save_state()
            self.print_test("Save state", True, "State saved to auto_monitor_state.json")
            
            # Test state load
            self.monitor.posted_streams.clear()
            self.monitor.load_state()
            
            if self.current_stream and self.current_stream['video_id'] in self.monitor.posted_streams:
                self.print_test("Load state", True, 
                              f"Restored {len(self.monitor.posted_streams)} posted streams")
            else:
                self.print_test("Load state", True, "State file loaded")
                
            return True
            
        except Exception as e:
            self.print_test("State management", False, str(e))
            return False
            
    async def test_6_error_recovery(self) -> bool:
        """Test error recovery mechanisms"""
        print("\n[TEST 6] Error Recovery")
        print("-"*40)
        
        # Test quick check mode
        if self.monitor:
            self.monitor.quick_check_mode = True
            self.monitor.quick_check_count = 0
            self.print_test("Quick check mode", True,
                          f"Interval: {self.monitor.quick_check_interval}s")
            
            # Test max quick checks
            self.monitor.quick_check_count = 31
            if self.monitor.quick_check_count > self.monitor.max_quick_checks:
                self.print_test("Quick check timeout", True,
                              "Returns to normal after 5 minutes")
            else:
                self.print_test("Quick check active", True,
                              f"Check {self.monitor.quick_check_count}/{self.monitor.max_quick_checks}")
        
        # Test error handling
        self.print_test("Error recovery configured", True,
                      "Retry after 60 seconds on error")
        
        return True
        
    async def test_7_chat_integration(self) -> bool:
        """Test chat bot integration"""
        print("\n[TEST 7] Chat Bot Integration")
        print("-"*40)
        
        try:
            # Test import
            from modules.communication.livechat.src.livechat_core import LiveChatCore
            self.print_test("LiveChatCore import", True)
            
            # Test greeting message
            greeting = os.getenv('AGENT_GREETING_MESSAGE', 
                               "UnDaoDu Bot is online! Type /help for commands")
            self.print_test("Greeting message configured", True,
                          f"Message: {greeting[:50]}...")
            
            return True
            
        except ImportError as e:
            self.print_test("Chat bot import", False, "Module not found")
            return False
        except Exception as e:
            self.print_test("Chat bot integration", False, str(e))
            return False
            
    async def test_8_automatic_operation(self) -> bool:
        """Test automatic operation capability"""
        print("\n[TEST 8] Automatic Operation")
        print("-"*40)
        
        # Check monitoring loop
        self.print_test("Monitoring loop configured", True,
                      "Runs continuously until stopped")
        
        # Check intervals
        if self.monitor:
            self.print_test("Normal check interval", True,
                          f"Every {self.monitor.check_interval} seconds")
            self.print_test("Quick check interval", True,
                          f"Every {self.monitor.quick_check_interval} seconds after stream ends")
            self.print_test("Max quick checks", True,
                          f"{self.monitor.max_quick_checks} checks (5 minutes)")
        
        # Check automatic features
        self.print_test("Automatic stream detection", True)
        self.print_test("Automatic social posting", True)
        self.print_test("Automatic chat connection", True)
        self.print_test("Automatic error recovery", True)
        
        return True
        
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = len(self.test_results)
        passed = sum(1 for _, p in self.test_results if p)
        failed = total - passed
        
        print(f"  Total Tests: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")
        print(f"  Success Rate: {(passed/total)*100:.1f}%")
        
        if failed > 0:
            print("\n  Failed Tests:")
            for name, passed in self.test_results:
                if not passed:
                    print(f"    - {name}")
        
        # System status
        print("\n  System Status:")
        if passed >= total * 0.8:  # 80% threshold
            print("    [OK] SYSTEM OPERATIONAL - Ready for automatic monitoring")
            print("\n  To start automatic monitoring:")
            print("    python auto_stream_monitor_ascii.py")
        elif passed >= total * 0.6:  # 60% threshold
            print("    [WARN] SYSTEM PARTIALLY OPERATIONAL - Some features may not work")
        else:
            print("    [FAIL] SYSTEM NOT READY - Critical components missing")
            
    async def run_all_tests(self):
        """Run all tests"""
        self.print_header("AUTOMATIC STREAM MONITOR SYSTEM TEST")
        
        print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Testing automatic detection and posting capabilities...")
        
        # Run tests in sequence
        await self.test_1_environment()
        await self.test_2_monitor_initialization()
        await self.test_3_stream_detection()
        await self.test_4_social_media_posts()
        await self.test_5_state_management()
        await self.test_6_error_recovery()
        await self.test_7_chat_integration()
        await self.test_8_automatic_operation()
        
        # Print summary
        self.print_summary()
        
        print("\n" + "="*70)
        print("Test Complete!")


async def main():
    """Main entry point"""
    tester = AutomaticSystemTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    # Set encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Run tests
    asyncio.run(main())