#!/usr/bin/env python3
"""
Master System Test Runner
Comprehensive system validation and health check
"""

import os
import sys
# Fix import path for new location
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))
import subprocess
import argparse
from datetime import datetime
from colorama import init, Fore, Style

init(autoreset=True)

def print_banner():
    """Print test suite banner"""
    banner = f"""
{Fore.CYAN}╔══════════════════════════════════════════════════════════════════════════════╗
║                         FOUNDUPS AGENT SYSTEM TEST SUITE                        ║
║                                                                                  ║
║  Comprehensive validation of:                                                   ║
║    • Stream Detection & Monitoring                                              ║
║    • Social Media Posting (X/Twitter & LinkedIn)                                ║
║    • YouTube Live Chat Integration                                              ║
║    • Gamification System (Whack-a-MAGAT)                                       ║
║    • Command Processing & Error Recovery                                        ║
║                                                                                  ║
║  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<72}║
╚══════════════════════════════════════════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def run_integration_tests():
    """Run system integration tests"""
    print(f"\n{Fore.YELLOW}Running System Integration Tests...{Style.RESET_ALL}")
    print(f"{Fore.WHITE}This will validate all system components and configuration{Style.RESET_ALL}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/system_integration_test.py"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{Fore.RED}Failed to run integration tests: {e}{Style.RESET_ALL}")
        return False

def run_workflow_tests():
    """Run detailed workflow tests"""
    print(f"\n{Fore.YELLOW}Running Detailed Workflow Tests...{Style.RESET_ALL}")
    print(f"{Fore.WHITE}This will test actual business logic and user journeys{Style.RESET_ALL}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, "tests/detailed_workflow_test.py"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"{Fore.RED}Failed to run workflow tests: {e}{Style.RESET_ALL}")
        return False

def run_quick_check():
    """Run a quick system check"""
    print(f"\n{Fore.YELLOW}Running Quick System Check...{Style.RESET_ALL}\n")
    
    checks = []
    
    # Check 1: Environment file
    if os.path.exists('.env'):
        print(f"{Fore.GREEN}✓ Environment file (.env) found{Style.RESET_ALL}")
        checks.append(True)
    else:
        print(f"{Fore.RED}✗ Environment file (.env) not found{Style.RESET_ALL}")
        checks.append(False)
    
    # Check 2: YouTube API key
    if os.getenv('YOUTUBE_API_KEY'):
        print(f"{Fore.GREEN}✓ YouTube API key configured{Style.RESET_ALL}")
        checks.append(True)
    else:
        print(f"{Fore.RED}✗ YouTube API key not configured{Style.RESET_ALL}")
        checks.append(False)
    
    # Check 3: Core modules
    try:
        import modules.communication.livechat.src.livechat_core
        print(f"{Fore.GREEN}✓ LiveChat Core module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}✗ LiveChat Core module not found{Style.RESET_ALL}")
        checks.append(False)
    
    try:
        import modules.gamification.whack_a_magat.src.whack
        print(f"{Fore.GREEN}✓ Gamification module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}✗ Gamification module not found{Style.RESET_ALL}")
        checks.append(False)
    
    try:
        import modules.platform_integration.stream_resolver.src.stream_resolver
        print(f"{Fore.GREEN}✓ Stream Resolver module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}✗ Stream Resolver module not found{Style.RESET_ALL}")
        checks.append(False)
    
    # Summary
    passed = sum(checks)
    total = len(checks)
    
    if passed == total:
        print(f"\n{Fore.GREEN}Quick Check: PASSED ({passed}/{total}){Style.RESET_ALL}")
        return True
    else:
        print(f"\n{Fore.YELLOW}Quick Check: PARTIAL ({passed}/{total}){Style.RESET_ALL}")
        return False

def print_test_checklist():
    """Print the comprehensive test checklist"""
    print(f"\n{Fore.CYAN}COMPREHENSIVE TEST CHECKLIST:{Style.RESET_ALL}")
    
    checklist = """
1. STREAM DETECTION
   □ Detect when stream goes live
   □ Identify stream title and URL
   □ Get stream metadata (channel, description)
   □ Handle stream ending detection
   □ Clear cache for fresh detection
   □ Quick check mode (5-15s intervals)
   □ Find new stream after current ends

2. SOCIAL MEDIA POSTING
   □ Authenticate with X/Twitter (geozeAI)
   □ Authenticate with LinkedIn (Move2Japan)
   □ Generate post content with stream info
   □ Include stream title in posts
   □ Include stream URL in posts
   □ Post to X when stream starts
   □ Post to LinkedIn when stream starts
   □ Handle rate limiting
   □ Queue failed posts for retry

3. YOUTUBE CHAT INTEGRATION
   □ Connect to live chat
   □ Authenticate with YouTube API
   □ Send greeting message
   □ Process incoming messages
   □ Detect slash commands
   □ Handle /score command
   □ Handle /rank command
   □ Handle /leaderboard command
   □ Handle /whacks command (mods only)
   □ Handle /help command
   □ Detect emoji triggers (✊✋🖐)
   □ Respond to consciousness queries
   □ Detect MAGA content
   □ Send responses to chat
   □ Handle rate limiting (60s cooldown)

4. GAMIFICATION SYSTEM
   □ Track moderator scores
   □ Calculate XP from timeout duration
   □ Update SQLite database
   □ Generate leaderboards
   □ Track player rankings (Bronze/Silver/Gold/Platinum)
   □ Calculate player levels
   □ Detect multi-whacks (30s window)
   □ Generate Duke Nukem announcements
   □ Track kill streaks
   □ Persist scores across restarts

5. ERROR RECOVERY
   □ Handle YouTube API quota exceeded
   □ Switch credential sets on quota limit
   □ Reconnect on chat disconnection
   □ Retry failed social media posts
   □ Handle network timeouts
   □ Log errors for debugging
   □ Graceful degradation on component failure

6. INTEGRATION POINTS
   □ YouTube API authentication working
   □ X/Twitter API accessible
   □ LinkedIn API accessible
   □ Database file created/accessible
   □ All modules importable
   □ WSP compliance (modules <500 lines)
   □ Cross-module communication working
    """
    print(checklist)

def main():
    """Main test runner"""
    parser = argparse.ArgumentParser(description='FoundUps Agent System Test Runner')
    parser.add_argument('--quick', action='store_true', help='Run quick check only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--workflow', action='store_true', help='Run workflow tests only')
    parser.add_argument('--checklist', action='store_true', help='Show test checklist only')
    
    args = parser.parse_args()
    
    # Load environment variables
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
    
    print_banner()
    
    if args.checklist:
        print_test_checklist()
        return
    
    if args.quick:
        success = run_quick_check()
    elif args.integration:
        success = run_integration_tests()
    elif args.workflow:
        success = run_workflow_tests()
    else:
        # Run all tests
        quick_ok = run_quick_check()
        
        if not quick_ok:
            print(f"\n{Fore.YELLOW}Quick check failed. Continue with full tests? (y/n): {Style.RESET_ALL}", end='')
            response = input().lower()
            if response != 'y':
                print(f"{Fore.YELLOW}Tests cancelled by user{Style.RESET_ALL}")
                return
        
        integration_ok = run_integration_tests()
        workflow_ok = run_workflow_tests()
        
        # Final summary
        print(f"\n{Fore.CYAN}{'='*80}")
        print(f"FINAL TEST SUMMARY")
        print(f"{'='*80}{Style.RESET_ALL}")
        
        print(f"  Quick Check:       {'✓ PASS' if quick_ok else '✗ FAIL'}")
        print(f"  Integration Tests: {'✓ PASS' if integration_ok else '✗ FAIL'}")
        print(f"  Workflow Tests:    {'✓ PASS' if workflow_ok else '✗ FAIL'}")
        
        if quick_ok and integration_ok and workflow_ok:
            print(f"\n{Fore.GREEN}SYSTEM STATUS: FULLY OPERATIONAL ✓{Style.RESET_ALL}")
            print(f"{Fore.GREEN}All tests passed. System is ready for production.{Style.RESET_ALL}")
        elif integration_ok:
            print(f"\n{Fore.YELLOW}SYSTEM STATUS: OPERATIONAL WITH WARNINGS ⚠{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Core systems functional but some workflows need attention.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}SYSTEM STATUS: NOT READY ✗{Style.RESET_ALL}")
            print(f"{Fore.RED}Critical failures detected. Please fix issues before deployment.{Style.RESET_ALL}")
            
        print(f"\n{Fore.CYAN}Run with --checklist to see comprehensive test checklist{Style.RESET_ALL}")

if __name__ == "__main__":
    main()