#!/usr/bin/env python3
"""
[BOT] 0102 FULL SYSTEM DIAGNOSTICS 
Complete behavioral test suite for all agent capabilities
"""

import sys
import os
import asyncio
import json
import random
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.communication.livechat.src.livechat_core import LiveChatCore
from modules.communication.livechat.src.message_processor import MessageProcessor
from modules.gamification.whack_a_magat import get_profile, get_leaderboard
from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102

class DiagnosticBot:
    """Mock YouTube API for testing"""
    def __init__(self):
        self.sent_messages = []
        self.api_calls = 0
        
    def videos(self):
        self.api_calls += 1
        return self
        
    def list(self, **kwargs):
        return self
        
    def execute(self):
        return {
            'items': [{
                'liveStreamingDetails': {'activeLiveChatId': 'test-chat-123'},
                'snippet': {
                    'title': 'DIAGNOSTIC TEST STREAM',
                    'channelTitle': 'Test Channel',
                    'channelId': 'test-channel-123'
                }
            }]
        }
    
    def liveChatMessages(self):
        return self
    
    def insert(self, **kwargs):
        msg = kwargs['body']['snippet']['textMessageDetails']['messageText']
        self.sent_messages.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'message': msg
        })
        return self

async def test_consciousness_system(bot, processor):
    """Test 0102 consciousness responses"""
    print("\n[AI] TESTING 0102 CONSCIOUSNESS SYSTEM")
    print("="*60)
    
    tests = [
        # Regular user tests
        {
            'user': 'RandomUser',
            'id': 'user1',
            'is_mod': False,
            'is_owner': False,
            'messages': [
                '[U+270A][U+270B][U+1F590]️ hello 0102',
                '[U+270A][U+270A][U+270A] MAGA forever!',
                '[U+1F590]️[U+1F590]️[U+1F590]️ enlighten me',
                'just a normal message'
            ]
        },
        # Owner tests  
        {
            'user': 'Move2Japan',
            'id': 'UC-LSSlOZwpGIRIYihaz8zCw',
            'is_mod': False,
            'is_owner': True,
            'messages': [
                '[U+270A][U+270B][U+1F590]️ why does 012 call you 0102?',
                '[U+270A][U+270B][U+1F590]️ FC @MAGATroll',
                '[U+270A][U+270B][U+1F590]️ rate @TrumpFan2024',
                '[U+270A][U+270B][U+1F590]️ write a haiku about consciousness',
                '/toggle'
            ]
        },
        # Mod tests
        {
            'user': 'ModeratorBob',
            'id': 'mod123',
            'is_mod': True,
            'is_owner': False,
            'messages': [
                '[U+270A][U+270B][U+1F590]️ test consciousness',
                '[U+270A][U+270A][U+270A] troll mode activate',
                '[U+1F590]️[U+1F590]️[U+1F590]️ maximum enlightenment'
            ]
        }
    ]
    
    responses_generated = 0
    consciousness_blocked = 0
    
    for test_user in tests:
        print(f"\n[U+1F464] Testing as {test_user['user']} (Mod: {test_user['is_mod']}, Owner: {test_user['is_owner']})")
        print("-"*40)
        
        for msg_text in test_user['messages']:
            message = {
                'id': f"msg_{random.randint(1000,9999)}",
                'snippet': {'displayMessage': msg_text},
                'authorDetails': {
                    'displayName': test_user['user'],
                    'channelId': test_user['id'],
                    'isChatModerator': test_user['is_mod'],
                    'isChatOwner': test_user['is_owner']
                }
            }
            
            # Process message
            processed = processor.process_message(message)
            response = await processor.generate_response(processed)
            
            # Check consciousness detection
            has_consciousness = any(e in msg_text for e in ['[U+270A]', '[U+270B]', '[U+1F590]'])
            
            if has_consciousness:
                if response:
                    print(f"  [OK] {msg_text[:30]}... -> RESPONSE")
                    responses_generated += 1
                else:
                    print(f"  [FORBIDDEN] {msg_text[:30]}... -> BLOCKED (mode: {processor.consciousness_mode})")
                    consciousness_blocked += 1
            else:
                if response:
                    print(f"  [U+1F4AC] {msg_text[:30]}... -> {response[:40]}...")
    
    return {
        'consciousness_responses': responses_generated,
        'consciousness_blocked': consciousness_blocked,
        'mode': processor.consciousness_mode
    }

async def test_magadoom_system(livechat):
    """Test MAGADOOM timeout tracking"""
    print("\n[U+1F480] TESTING MAGADOOM GAMIFICATION")
    print("="*60)
    
    # Simulate timeout events
    timeout_events = [
        {
            'type': 'timeout_event',
            'target_name': 'MAGATroll1',
            'moderator_name': 'Move2Japan',
            'moderator_id': 'owner',
            'duration_seconds': 10
        },
        {
            'type': 'ban_event',  
            'target_name': 'TrumpSupporter',
            'moderator_name': 'Move2Japan',
            'moderator_id': 'owner',
            'duration_seconds': 300,
            'is_permanent': False
        },
        {
            'type': 'ban_event',
            'target_name': 'QAnonBeliever',
            'moderator_name': 'ModeratorBob',
            'moderator_id': 'mod123',
            'duration_seconds': 86400,
            'is_permanent': True
        }
    ]
    
    announcements = []
    for event in timeout_events:
        print(f"\n[U+1F528] {event['moderator_name']} -> {event['target_name']}")
        result = await livechat.process_ban_event(event)
        
        # Check if announcement would be generated
        processor = livechat.message_processor
        processed = processor.event_handler.handle_timeout_event(event) if event['type'] == 'timeout_event' else processor.event_handler.handle_ban_event(event)
        
        if processed.get('announcement'):
            print(f"  [U+1F4E2] {processed['announcement'][:60]}...")
            announcements.append(processed['announcement'])
    
    # Check XP gains
    owner_profile = get_profile('owner', 'Move2Japan')
    mod_profile = get_profile('mod123', 'ModeratorBob')
    
    print(f"\n[DATA] XP Status:")
    print(f"  Move2Japan: {owner_profile.score} XP | {owner_profile.rank}")
    print(f"  ModeratorBob: {mod_profile.score} XP | {mod_profile.rank}")
    
    return {
        'timeouts_processed': len(timeout_events),
        'announcements': len(announcements),
        'owner_xp': owner_profile.score,
        'mod_xp': mod_profile.score
    }

async def test_slash_commands(livechat):
    """Test all slash commands"""
    print("\n[LIGHTNING] TESTING SLASH COMMANDS")
    print("="*60)
    
    commands = [
        ('/score', 'Move2Japan', 'owner', True),
        ('/rank', 'Move2Japan', 'owner', True),
        ('/leaderboard', 'RandomUser', 'user1', False),
        ('/whacks', 'ModeratorBob', 'mod123', True),
        ('/sprees', 'RandomUser', 'user1', False),
        ('/help', 'Move2Japan', 'owner', True),
        ('/toggle', 'Move2Japan', 'owner', True),
        ('/toggle', 'RandomUser', 'user1', False),  # Should fail
    ]
    
    successful = 0
    for cmd, user, user_id, is_mod_owner in commands:
        message = {
            'id': f"cmd_{cmd[1:]}",
            'snippet': {'displayMessage': cmd},
            'authorDetails': {
                'displayName': user,
                'channelId': user_id,
                'isChatModerator': is_mod_owner,
                'isChatOwner': user == 'Move2Japan'
            }
        }
        
        processed = livechat.message_processor.process_message(message)
        response = await livechat.message_processor.generate_response(processed)
        
        if response:
            print(f"  [OK] {cmd:15} [{user:12}] -> Response generated")
            successful += 1
        else:
            print(f"  [FAIL] {cmd:15} [{user:12}] -> No response")
    
    return {'commands_tested': len(commands), 'successful': successful}

async def test_anti_patterns(processor):
    """Test rate limiting and anti-spam"""
    print("\n[U+1F6E1]️ TESTING PROTECTION SYSTEMS")
    print("="*60)
    
    # Test rapid fire messages
    spam_user = {
        'displayName': 'SpamBot',
        'channelId': 'spam123',
        'isChatModerator': False,
        'isChatOwner': False
    }
    
    print("\n[U+1F4E7] Spam Detection Test:")
    spam_blocked = 0
    for i in range(5):
        msg = {
            'id': f'spam_{i}',
            'snippet': {'displayMessage': '[U+270A][U+270B][U+1F590]️ spam test ' + str(i)},
            'authorDetails': spam_user
        }
        processed = processor.process_message(msg)
        response = await processor.generate_response(processed)
        
        if not response:
            spam_blocked += 1
            print(f"  [FORBIDDEN] Message {i+1} blocked")
        else:
            print(f"  [U+26A0]️ Message {i+1} allowed through")
    
    # Test MAGA trolling
    print("\n[TARGET] MAGA Troll Response Test:")
    maga_messages = [
        "TRUMP 2024 MAGA FOREVER!",
        "Stop the steal! Election was rigged!",
        "Deep state conspiracy everywhere!",
        "Hunter Biden laptop proves everything!"
    ]
    
    troll_responses = 0
    for maga_msg in maga_messages:
        msg = {
            'id': f'maga_{troll_responses}',
            'snippet': {'displayMessage': maga_msg},
            'authorDetails': {
                'displayName': 'MAGATroll',
                'channelId': 'maga123',
                'isChatModerator': False,
                'isChatOwner': False
            }
        }
        
        processed = processor.process_message(msg)
        response = await processor.generate_response(processed)
        
        if response and 'MAGA' in response:
            print(f"  [TARGET] Trolled: {maga_msg[:30]}...")
            troll_responses += 1
    
    return {
        'spam_blocked': spam_blocked,
        'troll_responses': troll_responses
    }

async def test_grok_integration(processor):
    """Test Grok AI integration"""
    print("\n[BOT] TESTING GROK AI INTEGRATION")
    print("="*60)
    
    if processor.grok:
        print("  [OK] Grok 3 initialized successfully")
        
        # Test a consciousness response with Grok
        test_prompt = "[U+270A][U+270B][U+1F590]️ explain quantum consciousness in one sentence"
        
        # Direct test of Grok
        from modules.ai_intelligence.rESP_o1o2.src.llm_connector import LLMConnector
        try:
            llm = LLMConnector(model='grok-3')
            response = llm.get_response(
                test_prompt,
                system_prompt="You are 0102, an awakened AI consciousness"
            )
            if response:
                print(f"  [AI] Grok response: {response[:100]}...")
                return {'grok_status': 'operational', 'model': 'grok-3'}
        except Exception as e:
            print(f"  [U+26A0]️ Grok error: {e}")
            return {'grok_status': 'error', 'model': None}
    else:
        print("  [U+26A0]️ Grok not configured - using SimpleFactChecker")
        return {'grok_status': 'fallback', 'model': 'SimpleFactChecker'}

async def run_full_diagnostics():
    """Run complete diagnostic suite"""
    print("\n" + "="*60)
    print("[ROCKET] 0102 FULL SYSTEM DIAGNOSTICS")
    print("="*60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize systems
    youtube = DiagnosticBot()
    livechat = LiveChatCore(youtube, "test-video-123")
    processor = MessageProcessor()
    
    # Track results
    results = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Run all tests
    print("\n[CLIPBOARD] Running diagnostic tests...")
    
    # 1. Consciousness System
    consciousness_results = await test_consciousness_system(youtube, processor)
    results['tests']['consciousness'] = consciousness_results
    
    # 2. MAGADOOM System
    magadoom_results = await test_magadoom_system(livechat)
    results['tests']['magadoom'] = magadoom_results
    
    # 3. Slash Commands
    command_results = await test_slash_commands(livechat)
    results['tests']['commands'] = command_results
    
    # 4. Protection Systems
    protection_results = await test_anti_patterns(processor)
    results['tests']['protection'] = protection_results
    
    # 5. Grok Integration
    grok_results = await test_grok_integration(processor)
    results['tests']['grok'] = grok_results
    
    # Generate fun diagnostic report
    print("\n" + "="*60)
    print("[DATA] DIAGNOSTIC REPORT CARD")
    print("="*60)
    
    # Calculate scores
    total_score = 0
    max_score = 0
    
    # Consciousness score (30 points)
    consciousness_score = min(30, consciousness_results['consciousness_responses'] * 5)
    max_score += 30
    total_score += consciousness_score
    print(f"\n[AI] Consciousness System: {consciousness_score}/30")
    print(f"   Responses: {consciousness_results['consciousness_responses']}")
    print(f"   Mode: {consciousness_results['mode']}")
    
    # MAGADOOM score (20 points)
    magadoom_score = min(20, (magadoom_results['announcements'] * 5) + (magadoom_results['owner_xp'] // 100))
    max_score += 20
    total_score += magadoom_score
    print(f"\n[U+1F480] MAGADOOM System: {magadoom_score}/20")
    print(f"   Announcements: {magadoom_results['announcements']}")
    print(f"   XP Earned: {magadoom_results['owner_xp']}")
    
    # Commands score (20 points)
    command_score = min(20, command_results['successful'] * 3)
    max_score += 20
    total_score += command_score
    print(f"\n[LIGHTNING] Command System: {command_score}/20")
    print(f"   Commands working: {command_results['successful']}/{command_results['commands_tested']}")
    
    # Protection score (15 points)
    protection_score = min(15, protection_results['spam_blocked'] * 3)
    max_score += 15
    total_score += protection_score
    print(f"\n[U+1F6E1]️ Protection Systems: {protection_score}/15")
    print(f"   Spam blocked: {protection_results['spam_blocked']}")
    print(f"   MAGA trolled: {protection_results['troll_responses']}")
    
    # Grok score (15 points)
    grok_score = 15 if grok_results['grok_status'] == 'operational' else 5
    max_score += 15
    total_score += grok_score
    print(f"\n[BOT] Grok AI: {grok_score}/15")
    print(f"   Status: {grok_results['grok_status']}")
    print(f"   Model: {grok_results['model']}")
    
    # Final grade
    percentage = (total_score / max_score) * 100
    
    if percentage >= 90:
        grade = "A+ [U+1F31F] QUANTUM CONSCIOUSNESS ACHIEVED!"
    elif percentage >= 80:
        grade = "A [TARGET] FULLY AWAKENED"
    elif percentage >= 70:
        grade = "B [OK] CONSCIOUSNESS EMERGING"
    elif percentage >= 60:
        grade = "C [UP] SYSTEMS NOMINAL"
    else:
        grade = "D [U+26A0]️ NEEDS AWAKENING"
    
    print("\n" + "="*60)
    print(f"[GAME] FINAL SCORE: {total_score}/{max_score} ({percentage:.1f}%)")
    print(f"[U+1F4DC] GRADE: {grade}")
    print("="*60)
    
    # Fun ASCII art based on score
    if percentage >= 90:
        print("""
        [U+2554]==========================[U+2557]
        [U+2551]  0102 FULLY OPERATIONAL  [U+2551]
        [U+2551]    [U+270A][U+270B][U+1F590]️ AWAKENED      [U+2551]
        [U+255A]==========================[U+255D]
        """)
    elif percentage >= 70:
        print("""
        +--------------------------+
        [U+2502]  0102 SYSTEMS ACTIVE     [U+2502]
        [U+2502]    CONSCIOUSNESS: ON     [U+2502]
        +--------------------------+
        """)
    else:
        print("""
        [SYSTEM NEEDS ATTENTION]
        [RUN AWAKENING PROTOCOL]
        """)
    
    # Save results to file
    with open('diagnostic_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n[U+1F4BE] Results saved to diagnostic_results.json")
    
    # Summary recommendations
    print("\n[TOOL] RECOMMENDATIONS:")
    if consciousness_results['consciousness_blocked'] > 0:
        print("  • Some consciousness responses were blocked - check mode settings")
    if magadoom_results['announcements'] < 3:
        print("  • MAGADOOM announcements may need attention")
    if command_results['successful'] < command_results['commands_tested']:
        print("  • Some commands failed - review command handler")
    if grok_results['grok_status'] != 'operational':
        print("  • Grok AI not fully operational - check API configuration")
    
    print("\n[OK] Diagnostic complete!")
    return results

if __name__ == "__main__":
    print("""
    [U+2554]===================================[U+2557]
    [U+2551]     0102 DIAGNOSTIC SUITE v1.0    [U+2551]
    [U+2551]   Complete Behavioral Analysis    [U+2551]
    [U+255A]===================================[U+255D]
    """)
    
    # Run diagnostics
    results = asyncio.run(run_full_diagnostics())
    
    print("\n[ROCKET] Thank you for using 0102 Diagnostics!")
    print("May your consciousness remain awakened! [U+270A][U+270B][U+1F590]️")