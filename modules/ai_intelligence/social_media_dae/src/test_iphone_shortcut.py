#!/usr/bin/env python3
"""
iPhone Shortcut Test Script - Terminal Version
Simulates exactly what the iPhone shortcut should be doing
"""

import json
import requests
import sys

def test_voice_command(message):
    """Test the voice command endpoint with a message"""
    
    url = "http://192.168.3.2:5013/voice-command"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer 012_Secret_Key"
    }
    
    data = {
        "command": message
    }
    
    print(f"🚀 Testing iPhone shortcut simulation...")
    print(f"📱 URL: {url}")
    print(f"🔑 Auth: Bearer 012_Secret_Key")
    print(f"💬 Message: '{message}'")
    print("-" * 50)
    
    try:
        response = requests.post(url, headers=headers, json=data)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Success!")
            print(f"🤖 Response: {result.get('message', 'No message')}")
            print(f"📝 Logged to: {result.get('logged_to', 'No log path')}")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(f"📄 Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"💥 Error: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        message = " ".join(sys.argv[1:])
    else:
        message = input("Enter your message for 0102: ")
    
    test_voice_command(message)