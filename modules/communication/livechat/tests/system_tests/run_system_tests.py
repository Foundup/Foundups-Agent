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
{Fore.CYAN}[U+2554]==============================================================================[U+2557]
[U+2551]                         FOUNDUPS AGENT SYSTEM TEST SUITE                        [U+2551]
[U+2551]                                                                                  [U+2551]
[U+2551]  Comprehensive validation of:                                                   [U+2551]
[U+2551]    • Stream Detection & Monitoring                                              [U+2551]
[U+2551]    • Social Media Posting (X/Twitter & LinkedIn)                                [U+2551]
[U+2551]    • YouTube Live Chat Integration                                              [U+2551]
[U+2551]    • Gamification System (Whack-a-MAGAT)                                       [U+2551]
[U+2551]    • Command Processing & Error Recovery                                        [U+2551]
[U+2551]                                                                                  [U+2551]
[U+2551]  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S'):<72}[U+2551]
[U+255A]==============================================================================[U+255D]{Style.RESET_ALL}
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
        print(f"{Fore.GREEN}[OK] Environment file (.env) found{Style.RESET_ALL}")
        checks.append(True)
    else:
        print(f"{Fore.RED}[FAIL] Environment file (.env) not found{Style.RESET_ALL}")
        checks.append(False)
    
    # Check 2: YouTube API key
    if os.getenv('YOUTUBE_API_KEY'):
        print(f"{Fore.GREEN}[OK] YouTube API key configured{Style.RESET_ALL}")
        checks.append(True)
    else:
        print(f"{Fore.RED}[FAIL] YouTube API key not configured{Style.RESET_ALL}")
        checks.append(False)
    
    # Check 3: Core modules
    try:
        import modules.communication.livechat.src.livechat_core
        print(f"{Fore.GREEN}[OK] LiveChat Core module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}[FAIL] LiveChat Core module not found{Style.RESET_ALL}")
        checks.append(False)
    
    try:
        import modules.gamification.whack_a_magat.src.whack
        print(f"{Fore.GREEN}[OK] Gamification module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}[FAIL] Gamification module not found{Style.RESET_ALL}")
        checks.append(False)
    
    try:
        import modules.platform_integration.stream_resolver.src.stream_resolver
        print(f"{Fore.GREEN}[OK] Stream Resolver module available{Style.RESET_ALL}")
        checks.append(True)
    except ImportError:
        print(f"{Fore.RED}[FAIL] Stream Resolver module not found{Style.RESET_ALL}")
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
   [U+25A1] Detect when stream goes live
   [U+25A1] Identify stream title and URL
   [U+25A1] Get stream metadata (channel, description)
   [U+25A1] Handle stream ending detection
   [U+25A1] Clear cache for fresh detection
   [U+25A1] Quick check mode (5-15s intervals)
   [U+25A1] Find new stream after current ends

2. SOCIAL MEDIA POSTING
   [U+25A1] Authenticate with X/Twitter (geozeAI)
   [U+25A1] Authenticate with LinkedIn (Move2Japan)
   [U+25A1] Generate post content with stream info
   [U+25A1] Include stream title in posts
   [U+25A1] Include stream URL in posts
   [U+25A1] Post to X when stream starts
   [U+25A1] Post to LinkedIn when stream starts
   [U+25A1] Handle rate limiting
   [U+25A1] Queue failed posts for retry

3. YOUTUBE CHAT INTEGRATION
   [U+25A1] Connect to live chat
   [U+25A1] Authenticate with YouTube API
   [U+25A1] Send greeting message
   [U+25A1] Process incoming messages
   [U+25A1] Detect slash commands
   [U+25A1] Handle /score command
   [U+25A1] Handle /rank command
   [U+25A1] Handle /leaderboard command
   [U+25A1] Handle /whacks command (mods only)
   [U+25A1] Handle /help command
   [U+25A1] Detect emoji triggers ([U+270A][U+270B][U+1F590])
   [U+25A1] Respond to consciousness queries
   [U+25A1] Detect MAGA content
   [U+25A1] Send responses to chat
   [U+25A1] Handle rate limiting (60s cooldown)

4. GAMIFICATION SYSTEM
   [U+25A1] Track moderator scores
   [U+25A1] Calculate XP from timeout duration
   [U+25A1] Update SQLite database
   [U+25A1] Generate leaderboards
   [U+25A1] Track player rankings (Bronze/Silver/Gold/Platinum)
   [U+25A1] Calculate player levels
   [U+25A1] Detect multi-whacks (30s window)
   [U+25A1] Generate Duke Nukem announcements
   [U+25A1] Track kill streaks
   [U+25A1] Persist scores across restarts

5. ERROR RECOVERY
   [U+25A1] Handle YouTube API quota exceeded
   [U+25A1] Switch credential sets on quota limit
   [U+25A1] Reconnect on chat disconnection
   [U+25A1] Retry failed social media posts
   [U+25A1] Handle network timeouts
   [U+25A1] Log errors for debugging
   [U+25A1] Graceful degradation on component failure

6. INTEGRATION POINTS
   [U+25A1] YouTube API authentication working
   [U+25A1] X/Twitter API accessible
   [U+25A1] LinkedIn API accessible
   [U+25A1] Database file created/accessible
   [U+25A1] All modules importable
   [U+25A1] WSP compliance (modules <500 lines)
   [U+25A1] Cross-module communication working
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
        
        print(f"  Quick Check:       {'[OK] PASS' if quick_ok else '[FAIL] FAIL'}")
        print(f"  Integration Tests: {'[OK] PASS' if integration_ok else '[FAIL] FAIL'}")
        print(f"  Workflow Tests:    {'[OK] PASS' if workflow_ok else '[FAIL] FAIL'}")
        
        if quick_ok and integration_ok and workflow_ok:
            print(f"\n{Fore.GREEN}SYSTEM STATUS: FULLY OPERATIONAL [OK]{Style.RESET_ALL}")
            print(f"{Fore.GREEN}All tests passed. System is ready for production.{Style.RESET_ALL}")
        elif integration_ok:
            print(f"\n{Fore.YELLOW}SYSTEM STATUS: OPERATIONAL WITH WARNINGS [U+26A0]{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Core systems functional but some workflows need attention.{Style.RESET_ALL}")
        else:
            print(f"\n{Fore.RED}SYSTEM STATUS: NOT READY [FAIL]{Style.RESET_ALL}")
            print(f"{Fore.RED}Critical failures detected. Please fix issues before deployment.{Style.RESET_ALL}")
            
        print(f"\n{Fore.CYAN}Run with --checklist to see comprehensive test checklist{Style.RESET_ALL}")

if __name__ == "__main__":
    main()