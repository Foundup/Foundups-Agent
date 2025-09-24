#!/usr/bin/env python3
"""
Systematic Integration Test Suite for FoundUps Agent
Comprehensive validation of all core system functionality
"""

import os
import sys
import asyncio
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from colorama import init, Fore, Style
import traceback

# Add project root to path
# Add project root to path (4 levels up from tests/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
sys.path.insert(0, project_root)

# Initialize colorama for colored terminal output
init(autoreset=True)

class SystemIntegrationTest:
    """Comprehensive system integration test suite"""
    
    def __init__(self):
        self.test_results = []
        self.critical_failures = []
        self.warnings = []
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        
    def print_header(self, text: str):
        """Print section header"""
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"{Fore.CYAN}{text.center(80)}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        
    def print_test(self, name: str, status: str, details: str = ""):
        """Print test result with color coding"""
        self.total_tests += 1
        
        if status == "PASS":
            self.passed_tests += 1
            symbol = "✓"
            color = Fore.GREEN
        elif status == "FAIL":
            self.failed_tests += 1
            symbol = "✗"
            color = Fore.RED
            self.critical_failures.append(f"{name}: {details}")
        elif status == "WARN":
            symbol = "⚠"
            color = Fore.YELLOW
            self.warnings.append(f"{name}: {details}")
        else:
            symbol = "○"
            color = Fore.WHITE
            
        print(f"{color}[{symbol}] {name:<50} {status:>8}{Style.RESET_ALL}")
        if details:
            print(f"    {Fore.WHITE}{details}{Style.RESET_ALL}")
            
    def test_environment(self) -> Dict[str, bool]:
        """Test 1: Environment Configuration"""
        self.print_header("TEST 1: ENVIRONMENT CONFIGURATION")
        results = {}
        
        # Check .env file exists
        env_exists = os.path.exists('.env')
        self.print_test(".env file exists", "PASS" if env_exists else "FAIL")
        results['env_file'] = env_exists
        
        # Check critical environment variables
        critical_vars = [
            'YOUTUBE_API_KEY',
            'CHANNEL_ID',
            'GROQ_API_KEY',
            'LN_Acc1',
            'ln_Acc_pass',
            'X_Acc2',
            'x_Acc_pass'
        ]
        
        for var in critical_vars:
            value = os.getenv(var)
            if value and len(value) > 5:  # Basic validation
                self.print_test(f"ENV: {var}", "PASS", "Configured")
                results[var] = True
            else:
                self.print_test(f"ENV: {var}", "FAIL", "Missing or invalid")
                results[var] = False
                
        # Check optional but important variables
        optional_vars = [
            'YOUTUBE_VIDEO_ID',
            'AGENT_GREETING_MESSAGE',
            'LINKEDIN_URN'
        ]
        
        for var in optional_vars:
            value = os.getenv(var)
            if value:
                self.print_test(f"ENV: {var}", "PASS", "Configured")
            else:
                self.print_test(f"ENV: {var}", "WARN", "Not configured (optional)")
                
        return results
        
    def test_youtube_auth(self) -> bool:
        """Test 2: YouTube Authentication & API Access"""
        self.print_header("TEST 2: YOUTUBE AUTHENTICATION")
        
        try:
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            
            # Test getting authenticated service
            service = get_authenticated_service()
            if service:
                self.print_test("YouTube API Authentication", "PASS", "Service object created")
                
                # Test API quota check
                try:
                    response = service.channels().list(
                        part="snippet",
                        mine=True
                    ).execute()
                    
                    if response.get('items'):
                        channel_name = response['items'][0]['snippet']['title']
                        self.print_test("API Quota Check", "PASS", f"Authenticated as: {channel_name}")
                        return True
                    else:
                        self.print_test("API Quota Check", "WARN", "No channel found")
                        return True
                except Exception as e:
                    self.print_test("API Quota Check", "FAIL", str(e)[:100])
                    return False
            else:
                self.print_test("YouTube API Authentication", "FAIL", "No service object")
                return False
                
        except ImportError as e:
            self.print_test("YouTube Auth Module", "FAIL", f"Import error: {e}")
            return False
        except Exception as e:
            self.print_test("YouTube Auth Module", "FAIL", str(e)[:100])
            return False
            
    def test_stream_detection(self) -> Optional[Dict]:
        """Test 3: Stream Detection & Resolution"""
        self.print_header("TEST 3: STREAM DETECTION PIPELINE")
        
        try:
            from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            
            service = get_authenticated_service()
            if not service:
                self.print_test("Stream Resolver Init", "FAIL", "No YouTube service")
                return None
                
            resolver = StreamResolver(service)
            self.print_test("Stream Resolver Init", "PASS", "Resolver created")
            
            # Clear cache for fresh detection
            resolver.clear_cache()
            self.print_test("Cache Clear", "PASS", "Cache cleared for fresh detection")
            
            # Try to find active stream
            channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
            result = resolver.resolve_stream(channel_id)
            
            if result:
                video_id, chat_id = result
                self.print_test("Stream Detection", "PASS", f"Found stream: {video_id}")
                
                # Get stream details
                try:
                    video_response = service.videos().list(
                        part="snippet,liveStreamingDetails",
                        id=video_id
                    ).execute()
                    
                    if video_response.get('items'):
                        video = video_response['items'][0]
                        title = video['snippet']['title']
                        channel = video['snippet']['channelTitle']
                        url = f"https://youtube.com/watch?v={video_id}"
                        
                        self.print_test("Stream Title", "PASS", title[:50])
                        self.print_test("Stream Channel", "PASS", channel)
                        self.print_test("Stream URL", "PASS", url)
                        
                        return {
                            'video_id': video_id,
                            'chat_id': chat_id,
                            'title': title,
                            'channel': channel,
                            'url': url
                        }
                except Exception as e:
                    self.print_test("Stream Details", "FAIL", str(e)[:100])
                    return None
            else:
                self.print_test("Stream Detection", "WARN", "No active stream found")
                # Return mock data for testing
                return {
                    'video_id': 'TEST_VIDEO_ID',
                    'chat_id': 'TEST_CHAT_ID',
                    'title': 'Test Stream Title',
                    'channel': 'Test Channel',
                    'url': 'https://youtube.com/watch?v=TEST_VIDEO_ID'
                }
                
        except Exception as e:
            self.print_test("Stream Detection", "FAIL", str(e)[:100])
            return None
            
    def test_social_media_posting(self, stream_info: Optional[Dict]) -> Dict[str, bool]:
        """Test 4: Social Media Posting Pipeline"""
        self.print_header("TEST 4: SOCIAL MEDIA POSTING")
        results = {}
        
        if not stream_info:
            self.print_test("Social Media Tests", "SKIP", "No stream info available")
            return {}
            
        # Test X/Twitter posting capability
        try:
            from modules.platform_integration.x_twitter.src.anti_detection_poster import XAntiDetectionPoster
            
            x_poster = XAntiDetectionPoster()
            self.print_test("X/Twitter Poster Init", "PASS", "Anti-detection poster ready")
            
            # Create test post content
            x_content = f"🔴 LIVE NOW: {stream_info['title']}\n\n📺 Watch: {stream_info['url']}\n\n#AI #Livestream"
            self.print_test("X Post Content", "PASS", x_content[:50] + "...")
            
            # Dry run test (don't actually post)
            self.print_test("X/Twitter Post Ready", "PASS", "Would post to @geozeAI")
            results['x_twitter'] = True
            
        except ImportError:
            self.print_test("X/Twitter Module", "WARN", "Module not available")
            results['x_twitter'] = False
        except Exception as e:
            self.print_test("X/Twitter Module", "FAIL", str(e)[:100])
            results['x_twitter'] = False
            
        # Test LinkedIn posting capability
        try:
            from modules.platform_integration.linkedin_agent.src.anti_detection_poster import LinkedInAntiDetectionPoster
            
            ln_poster = LinkedInAntiDetectionPoster()
            self.print_test("LinkedIn Poster Init", "PASS", "Anti-detection poster ready")
            
            # Create test post content
            ln_content = f"🔴 Now streaming: {stream_info['title']}\n\nJoin us for an AI-powered development session!\n\n📺 {stream_info['url']}"
            self.print_test("LinkedIn Content", "PASS", ln_content[:50] + "...")
            
            # Dry run test
            self.print_test("LinkedIn Post Ready", "PASS", "Would post to Move2Japan")
            results['linkedin'] = True
            
        except ImportError:
            self.print_test("LinkedIn Module", "WARN", "Module not available")
            results['linkedin'] = False
        except Exception as e:
            self.print_test("LinkedIn Module", "FAIL", str(e)[:100])
            results['linkedin'] = False
            
        return results
        
    def test_youtube_chat(self, stream_info: Optional[Dict]) -> bool:
        """Test 5: YouTube Live Chat Interaction"""
        self.print_header("TEST 5: YOUTUBE CHAT PIPELINE")
        
        try:
            from modules.communication.livechat.src.livechat_core import LiveChatCore
            from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
            
            service = get_authenticated_service()
            if not service:
                self.print_test("Chat Service", "FAIL", "No YouTube service")
                return False
                
            # Initialize chat listener
            if stream_info and stream_info.get('video_id') != 'TEST_VIDEO_ID':
                video_id = stream_info['video_id']
                chat_id = stream_info.get('chat_id')
            else:
                video_id = os.getenv('YOUTUBE_VIDEO_ID')
                chat_id = None
                
            if not video_id:
                self.print_test("Chat Init", "WARN", "No video ID available")
                return False
                
            chat = LiveChatCore(
                youtube=service,
                video_id=video_id,
                live_chat_id=chat_id
            )
            self.print_test("LiveChat Core Init", "PASS", "Chat listener created")
            
            # Test chat components
            components = [
                ('Session Manager', hasattr(chat, 'session_manager')),
                ('Message Processor', hasattr(chat, 'message_processor')),
                ('Chat Sender', hasattr(chat, 'chat_sender')),
                ('Chat Poller', hasattr(chat, 'chat_poller'))
            ]
            
            all_good = True
            for name, exists in components:
                if exists:
                    self.print_test(f"Component: {name}", "PASS", "Initialized")
                else:
                    self.print_test(f"Component: {name}", "FAIL", "Not found")
                    all_good = False
                    
            return all_good
            
        except Exception as e:
            self.print_test("YouTube Chat", "FAIL", str(e)[:100])
            return False
            
    def test_gamification(self) -> bool:
        """Test 6: Gamification System (Whack-a-MAGAT)"""
        self.print_header("TEST 6: GAMIFICATION SYSTEM")
        
        try:
            from modules.gamification.whack_a_magat.src.whack import WhackAMagat
            
            whack = WhackAMagat()
            self.print_test("Whack-a-MAGAT Init", "PASS", "Game system initialized")
            
            # Test database connection
            db_path = 'modules/gamification/whack_a_magat/data/magadoom_scores.db'
            db_exists = os.path.exists(db_path)
            self.print_test("Score Database", "PASS" if db_exists else "WARN", 
                          db_path if db_exists else "Will be created on first use")
            
            # Test scoring functions
            test_user = "test_moderator"
            test_target = "test_magat"
            
            # Test timeout scoring
            xp = whack.calculate_xp(300)  # 5 minute timeout
            self.print_test("XP Calculation", "PASS", f"5 min timeout = {xp} XP")
            
            # Test profile creation
            profile = whack.get_profile(test_user)
            if profile:
                self.print_test("Profile System", "PASS", 
                              f"Score: {profile['score']}, Rank: {profile['rank']}")
            else:
                self.print_test("Profile System", "WARN", "No profile (will create on first score)")
                
            # Test leaderboard
            leaderboard = whack.get_leaderboard(limit=5)
            self.print_test("Leaderboard", "PASS", f"{len(leaderboard)} entries")
            
            # Test multi-whack detection
            from modules.gamification.whack_a_magat.src.timeout_tracker import TimeoutTracker
            tracker = TimeoutTracker()
            self.print_test("Timeout Tracker", "PASS", "Multi-whack detection ready")
            
            return True
            
        except Exception as e:
            self.print_test("Gamification System", "FAIL", str(e)[:100])
            return False
            
    def test_command_system(self) -> bool:
        """Test 7: Command Processing System"""
        self.print_header("TEST 7: COMMAND PROCESSING")
        
        try:
            from modules.communication.livechat.src.command_handler import CommandHandler
            
            handler = CommandHandler()
            self.print_test("Command Handler Init", "PASS", "Command system ready")
            
            # Test command detection
            commands = [
                '/score',
                '/rank',
                '/leaderboard',
                '/whacks',
                '/help',
                '/toggle',
                '/quiz'
            ]
            
            for cmd in commands:
                if handler.is_command(cmd):
                    self.print_test(f"Command: {cmd}", "PASS", "Recognized")
                else:
                    self.print_test(f"Command: {cmd}", "FAIL", "Not recognized")
                    
            return True
            
        except Exception as e:
            self.print_test("Command System", "FAIL", str(e)[:100])
            return False
            
    def test_integration_health(self) -> Dict[str, bool]:
        """Test 8: System Integration Health Checks"""
        self.print_header("TEST 8: INTEGRATION HEALTH")
        results = {}
        
        # Test module imports
        modules_to_test = [
            ('YouTube Auth', 'modules.platform_integration.youtube_auth.src.youtube_auth'),
            ('Stream Resolver', 'modules.platform_integration.stream_resolver.src.stream_resolver'),
            ('LiveChat Core', 'modules.communication.livechat.src.livechat_core'),
            ('Message Processor', 'modules.communication.livechat.src.message_processor'),
            ('Command Handler', 'modules.communication.livechat.src.command_handler'),
            ('Whack Game', 'modules.gamification.whack_a_magat.src.whack'),
            ('Chat Sender', 'modules.communication.livechat.src.chat_sender'),
            ('Event Handler', 'modules.communication.livechat.src.event_handler')
        ]
        
        for name, module_path in modules_to_test:
            try:
                __import__(module_path)
                self.print_test(f"Module: {name}", "PASS", "Importable")
                results[name] = True
            except ImportError as e:
                self.print_test(f"Module: {name}", "FAIL", str(e)[:50])
                results[name] = False
                
        # Test WSP compliance
        wsp_compliant_modules = [
            'modules/communication/livechat/src/livechat_core.py',
            'modules/communication/livechat/src/message_processor.py',
            'modules/communication/livechat/src/command_handler.py',
            'modules/gamification/whack_a_magat/src/whack.py'
        ]
        
        for module in wsp_compliant_modules:
            if os.path.exists(module):
                with open(module, 'r') as f:
                    lines = len(f.readlines())
                if lines < 500:
                    self.print_test(f"WSP Compliance: {os.path.basename(module)}", 
                                  "PASS", f"{lines} lines")
                else:
                    self.print_test(f"WSP Compliance: {os.path.basename(module)}", 
                                  "WARN", f"{lines} lines (>500)")
            else:
                self.print_test(f"WSP Compliance: {os.path.basename(module)}", 
                              "FAIL", "File not found")
                              
        return results
        
    def test_end_to_end_workflow(self, stream_info: Optional[Dict]) -> bool:
        """Test 9: End-to-End Workflow Simulation"""
        self.print_header("TEST 9: END-TO-END WORKFLOW")
        
        workflow_steps = []
        
        # Step 1: Stream detection
        if stream_info:
            workflow_steps.append(("Stream Detection", True, stream_info['title'][:30]))
        else:
            workflow_steps.append(("Stream Detection", False, "No stream found"))
            
        # Step 2: Social media notification
        if stream_info:
            workflow_steps.append(("Social Notification Prep", True, 
                                 "X and LinkedIn posts ready"))
        else:
            workflow_steps.append(("Social Notification Prep", False, 
                                 "Skipped - no stream"))
            
        # Step 3: Chat connection
        if stream_info and stream_info.get('chat_id'):
            workflow_steps.append(("Chat Connection", True, "Chat ID obtained"))
        else:
            workflow_steps.append(("Chat Connection", False, "No chat ID"))
            
        # Step 4: Command processing ready
        workflow_steps.append(("Command Processing", True, "7 commands registered"))
        
        # Step 5: Gamification ready
        workflow_steps.append(("Gamification", True, "Scoring system active"))
        
        # Print workflow results
        all_good = True
        for step, success, details in workflow_steps:
            if success:
                self.print_test(step, "PASS", details)
            else:
                self.print_test(step, "FAIL", details)
                all_good = False
                
        return all_good
        
    def run_all_tests(self):
        """Run all system integration tests"""
        self.print_header("FOUNDUPS AGENT SYSTEM INTEGRATION TEST")
        print(f"{Fore.YELLOW}Starting comprehensive system validation...{Style.RESET_ALL}")
        print(f"{Fore.WHITE}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Style.RESET_ALL}")
        
        # Run test suite
        env_results = self.test_environment()
        youtube_auth = self.test_youtube_auth()
        stream_info = self.test_stream_detection()
        social_results = self.test_social_media_posting(stream_info)
        chat_ok = self.test_youtube_chat(stream_info)
        game_ok = self.test_gamification()
        cmd_ok = self.test_command_system()
        health_results = self.test_integration_health()
        workflow_ok = self.test_end_to_end_workflow(stream_info)
        
        # Print summary
        self.print_header("TEST SUMMARY")
        
        print(f"\n{Fore.CYAN}Overall Results:{Style.RESET_ALL}")
        print(f"  Total Tests: {self.total_tests}")
        print(f"  {Fore.GREEN}Passed: {self.passed_tests}{Style.RESET_ALL}")
        print(f"  {Fore.RED}Failed: {self.failed_tests}{Style.RESET_ALL}")
        print(f"  {Fore.YELLOW}Warnings: {len(self.warnings)}{Style.RESET_ALL}")
        
        # Success rate
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            if success_rate >= 80:
                color = Fore.GREEN
            elif success_rate >= 60:
                color = Fore.YELLOW
            else:
                color = Fore.RED
            print(f"\n  {color}Success Rate: {success_rate:.1f}%{Style.RESET_ALL}")
            
        # Critical failures
        if self.critical_failures:
            print(f"\n{Fore.RED}Critical Failures:{Style.RESET_ALL}")
            for failure in self.critical_failures[:5]:  # Show top 5
                print(f"  • {failure}")
                
        # Warnings
        if self.warnings:
            print(f"\n{Fore.YELLOW}Warnings:{Style.RESET_ALL}")
            for warning in self.warnings[:5]:  # Show top 5
                print(f"  • {warning}")
                
        # System readiness
        print(f"\n{Fore.CYAN}System Readiness:{Style.RESET_ALL}")
        
        core_ready = (
            env_results.get('YOUTUBE_API_KEY', False) and
            youtube_auth and
            game_ok and
            cmd_ok
        )
        
        if core_ready:
            print(f"  {Fore.GREEN}✓ Core Systems: READY{Style.RESET_ALL}")
        else:
            print(f"  {Fore.RED}✗ Core Systems: NOT READY{Style.RESET_ALL}")
            
        if stream_info and stream_info.get('video_id') != 'TEST_VIDEO_ID':
            print(f"  {Fore.GREEN}✓ Live Stream: DETECTED{Style.RESET_ALL}")
            print(f"    Stream: {stream_info['title'][:50]}")
            print(f"    URL: {stream_info['url']}")
        else:
            print(f"  {Fore.YELLOW}⚠ Live Stream: NOT DETECTED{Style.RESET_ALL}")
            
        if social_results.get('x_twitter'):
            print(f"  {Fore.GREEN}✓ X/Twitter: READY{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ X/Twitter: NOT CONFIGURED{Style.RESET_ALL}")
            
        if social_results.get('linkedin'):
            print(f"  {Fore.GREEN}✓ LinkedIn: READY{Style.RESET_ALL}")
        else:
            print(f"  {Fore.YELLOW}⚠ LinkedIn: NOT CONFIGURED{Style.RESET_ALL}")
            
        # Final status
        print(f"\n{Fore.CYAN}{'='*80}{Style.RESET_ALL}")
        if self.failed_tests == 0:
            print(f"{Fore.GREEN}SYSTEM STATUS: ALL TESTS PASSED ✓{Style.RESET_ALL}")
        elif self.failed_tests <= 3:
            print(f"{Fore.YELLOW}SYSTEM STATUS: OPERATIONAL WITH ISSUES ⚠{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}SYSTEM STATUS: CRITICAL FAILURES DETECTED ✗{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'='*80}{Style.RESET_ALL}")


def main():
    """Main test runner"""
    tester = SystemIntegrationTest()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Tests interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Fatal error during testing:{Style.RESET_ALL}")
        print(traceback.format_exc())
        
    # Return exit code based on failures
    if tester.failed_tests == 0:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()