#!/usr/bin/env python3
"""
Simple System Test Runner - ASCII only version
"""

import os
import sys
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def print_header(text):
    print("\n" + "="*80)
    print(text.center(80))
    print("="*80)

def run_simple_tests():
    """Run simple system tests"""
    print_header("FOUNDUPS AGENT SYSTEM TEST")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    passed = 0
    failed = 0
    
    # Test 1: Environment
    print_header("TEST 1: ENVIRONMENT")
    
    if os.path.exists('.env'):
        print("[PASS] .env file found")
        passed += 1
    else:
        print("[FAIL] .env file not found")
        failed += 1
        
    critical_vars = [
        'YOUTUBE_API_KEY',
        'CHANNEL_ID', 
        'GROQ_API_KEY',
        'LN_Acc1',
        'X_Acc2'
    ]
    
    for var in critical_vars:
        value = os.getenv(var)
        if value and len(value) > 5:
            print(f"[PASS] {var} configured")
            passed += 1
        else:
            print(f"[FAIL] {var} not configured")
            failed += 1
            
    # Test 2: Core Modules
    print_header("TEST 2: CORE MODULES")
    
    modules_to_test = [
        ('YouTube Auth', 'modules.platform_integration.youtube_auth.src.youtube_auth'),
        ('Stream Resolver', 'modules.platform_integration.stream_resolver.src.stream_resolver'),
        ('LiveChat Core', 'modules.communication.livechat.src.livechat_core'),
        ('Message Processor', 'modules.communication.livechat.src.message_processor'),
        ('Command Handler', 'modules.communication.livechat.src.command_handler'),
        ('Whack Game', 'modules.gamification.whack_a_magat.src.whack')
    ]
    
    for name, module_path in modules_to_test:
        try:
            __import__(module_path)
            print(f"[PASS] {name} module loaded")
            passed += 1
        except ImportError as e:
            print(f"[FAIL] {name} module failed: {str(e)[:50]}")
            failed += 1
            
    # Test 3: YouTube API
    print_header("TEST 3: YOUTUBE API")
    
    try:
        from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
        
        service = get_authenticated_service()
        if service:
            print("[PASS] YouTube API authentication successful")
            passed += 1
            
            # Try to get channel info
            try:
                response = service.channels().list(
                    part="snippet",
                    mine=True
                ).execute()
                
                if response.get('items'):
                    channel = response['items'][0]['snippet']['title']
                    print(f"[PASS] Connected as: {channel}")
                    passed += 1
                else:
                    print("[WARN] No channel found")
            except Exception as e:
                print(f"[FAIL] API call failed: {str(e)[:50]}")
                failed += 1
        else:
            print("[FAIL] YouTube API authentication failed")
            failed += 1
    except Exception as e:
        print(f"[FAIL] YouTube Auth module error: {str(e)[:50]}")
        failed += 1
        
    # Test 4: Stream Detection
    print_header("TEST 4: STREAM DETECTION")
    
    try:
        from modules.platform_integration.stream_resolver.src.stream_resolver import StreamResolver
        from modules.platform_integration.youtube_auth.src.youtube_auth import get_authenticated_service
        
        service = get_authenticated_service()
        if service:
            resolver = StreamResolver(service)
            print("[PASS] Stream resolver initialized")
            passed += 1
            
            # Clear cache
            resolver.clear_cache()
            print("[PASS] Cache cleared")
            passed += 1
            
            # Try to find stream
            channel_id = os.getenv('CHANNEL_ID', 'UC-LSSlOZwpGIRIYihaz8zCw')
            result = resolver.resolve_stream(channel_id)
            
            if result:
                video_id, chat_id = result
                print(f"[PASS] Live stream found: {video_id}")
                passed += 1
                
                # Get stream info
                try:
                    video_response = service.videos().list(
                        part="snippet",
                        id=video_id
                    ).execute()
                    
                    if video_response.get('items'):
                        video = video_response['items'][0]
                        title = video['snippet']['title'][:50]
                        print(f"[PASS] Stream title: {title}")
                        passed += 1
                except:
                    pass
            else:
                print("[INFO] No live stream currently active")
    except Exception as e:
        print(f"[FAIL] Stream detection error: {str(e)[:50]}")
        failed += 1
        
    # Test 5: Gamification
    print_header("TEST 5: GAMIFICATION SYSTEM")
    
    try:
        from modules.gamification.whack_a_magat.src.whack import WhackAMagat
        
        whack = WhackAMagat()
        print("[PASS] Whack-a-MAGAT initialized")
        passed += 1
        
        # Test XP calculation
        xp = whack.calculate_xp(300)  # 5 minute timeout
        if xp == 5:
            print("[PASS] XP calculation correct (5 min = 5 XP)")
            passed += 1
        else:
            print(f"[FAIL] XP calculation wrong: {xp}")
            failed += 1
            
        # Test database
        db_path = 'modules/gamification/whack_a_magat/data/magadoom_scores.db'
        if os.path.exists(db_path):
            print("[PASS] Score database exists")
            passed += 1
        else:
            print("[INFO] Score database will be created on first use")
            
        # Test leaderboard
        leaderboard = whack.get_leaderboard(limit=5)
        print(f"[PASS] Leaderboard has {len(leaderboard)} entries")
        passed += 1
        
    except Exception as e:
        print(f"[FAIL] Gamification error: {str(e)[:50]}")
        failed += 1
        
    # Test 6: Commands
    print_header("TEST 6: COMMAND SYSTEM")
    
    try:
        from modules.communication.livechat.src.command_handler import CommandHandler
        
        handler = CommandHandler()
        print("[PASS] Command handler initialized")
        passed += 1
        
        commands = ['/score', '/rank', '/leaderboard', '/help']
        for cmd in commands:
            if handler.is_command(cmd):
                print(f"[PASS] Command recognized: {cmd}")
                passed += 1
            else:
                print(f"[FAIL] Command not recognized: {cmd}")
                failed += 1
                
    except Exception as e:
        print(f"[FAIL] Command system error: {str(e)[:50]}")
        failed += 1
        
    # Summary
    print_header("TEST SUMMARY")
    
    total = passed + failed
    if total > 0:
        success_rate = (passed / total) * 100
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if failed == 0:
            print("\nSYSTEM STATUS: FULLY OPERATIONAL")
            print("All tests passed!")
        elif failed <= 5:
            print("\nSYSTEM STATUS: OPERATIONAL WITH ISSUES")
            print("Core systems functional but some components need attention")
        else:
            print("\nSYSTEM STATUS: CRITICAL FAILURES")
            print("Please fix critical issues before deployment")
            
    print("\n" + "="*80)
    
    # Return exit code
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    # Load environment
    if os.path.exists('.env'):
        from dotenv import load_dotenv
        load_dotenv()
        
    sys.exit(run_simple_tests())