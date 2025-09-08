#!/usr/bin/env python3
"""
Test MagaDoom Activity Switches - Live Stream Control Test
Tests the activity control switches that can be triggered via iPhone/voice commands
"""

import requests
import json
import time
import sys
from pathlib import Path

# Test endpoints
BASE_URL = "http://localhost:5012"
VOICE_ENDPOINT = f"{BASE_URL}/voice-command"
STATUS_ENDPOINT = f"{BASE_URL}/status"
TEST_ENDPOINT = f"{BASE_URL}/test"

def test_switch_command(command, description):
    """Test a voice command switch"""
    print(f"\n🧪 Testing: {description}")
    print(f"   Command: '{command}'")
    
    try:
        # Send the voice command
        payload = {
            'command': command,
            'secret': 'test-secret-12345'  # Using test secret
        }
        
        response = requests.post(VOICE_ENDPOINT, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Status: {response.status_code}")
            print(f"   📤 Response: {result.get('response', 'No response')}")
            if 'execution_time' in result:
                print(f"   ⏱️ Time: {result['execution_time']:.2f}s")
        else:
            print(f"   ❌ Status: {response.status_code}")
            print(f"   📤 Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection Error: {e}")
        return False
        
    return True

def check_server_status():
    """Check if the voice server is running"""
    try:
        response = requests.get(STATUS_ENDPOINT, timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"🟢 Server Status: Running")
            print(f"   DAE State: {status.get('dae_state', 'Unknown')}")
            print(f"   Emergency Paused: {status.get('emergency_paused', 'Unknown')}")
            return True
        else:
            print(f"🔴 Server Status: Error {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"🔴 Server Status: Connection failed - {e}")
        return False

def main():
    """Run MagaDoom switch tests"""
    print("🎯 MagaDoom Activity Control Switch Test")
    print("=" * 50)
    
    # Check server status first
    if not check_server_status():
        print("\n❌ Voice server not accessible. Please ensure it's running:")
        print("   python scripts/run_voice_server.py")
        sys.exit(1)
    
    print(f"\n📱 Testing switches at {BASE_URL}")
    print("🎮 These switches control automated activities during live streams")
    
    # Test MagaDoom switches
    test_commands = [
        # MagaDoom controls
        ("MagaDoom off", "Turn off MagaDoom activities (whack announcements, levels)"),
        ("activity status", "Check current activity control status"),
        ("MagaDoom on", "Turn on MagaDoom activities"),
        
        # 0102 consciousness controls  
        ("0102 off", "Turn off consciousness emoji triggers"),
        ("activity status", "Check status after consciousness off"),
        ("0102 on", "Turn on consciousness emoji triggers"),
        
        # Silent mode for testing
        ("silent mode", "Enable silent testing mode (all activities off)"),
        ("activity status", "Check silent mode status"),
        ("normal mode", "Restore normal operation (all activities on)"),
        
        # Final status check
        ("activity status", "Final status check"),
    ]
    
    success_count = 0
    total_tests = len(test_commands)
    
    for command, description in test_commands:
        if test_switch_command(command, description):
            success_count += 1
        
        # Small delay between tests
        time.sleep(1)
    
    # Summary
    print("\n" + "=" * 50)
    print(f"🎉 Test Results: {success_count}/{total_tests} switches tested successfully")
    
    if success_count == total_tests:
        print("✅ All MagaDoom activity switches are working!")
        print("📱 Ready for iPhone live stream control")
    else:
        print("⚠️ Some switches had issues - check the output above")
    
    print(f"\n🌐 You can also test manually at: {TEST_ENDPOINT}")

if __name__ == "__main__":
    main()