#!/usr/bin/env python3
"""Test which account the bot is using and send a test message"""

import os
import sys
sys.path.insert(0, os.getcwd())

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

def test_send():
    # Try each token
    for i in range(1, 8):
        token_file = f'credentials/oauth_token{i}.json' if i > 1 else 'credentials/oauth_token.json'
        
        if not os.path.exists(token_file):
            print(f"❌ {token_file} not found")
            continue
            
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes')
            )
            
            # Check if token is valid
            if creds and creds.expired and creds.refresh_token:
                print(f"🔄 Refreshing {token_file}")
                creds.refresh(Request())
            
            # Build service
            youtube = build('youtube', 'v3', credentials=creds)
            
            # Get channel info
            response = youtube.channels().list(
                part='snippet',
                mine=True
            ).execute()
            
            if response.get('items'):
                channel = response['items'][0]['snippet']
                print(f"✅ {token_file}: {channel['title']} (ID: {response['items'][0]['id']})")
                
                # This is the account being used
                return youtube, channel['title'], response['items'][0]['id']
            else:
                print(f"❌ {token_file}: No channel info")
                
        except Exception as e:
            print(f"❌ {token_file}: {str(e)[:100]}")
    
    return None, None, None

def main():
    print("🔍 Testing which YouTube account the bot is using...")
    print("=" * 60)
    
    youtube, channel_name, channel_id = test_send()
    
    if youtube and channel_name:
        print("\n" + "=" * 60)
        print(f"🤖 Bot is using account: {channel_name}")
        print(f"📍 Channel ID: {channel_id}")
        print("=" * 60)
        
        # Now test sending to the stream
        video_id = "jW5GDGXWjzY"  # Move2Japan's stream
        
        # Get live chat ID
        try:
            video_response = youtube.videos().list(
                part="liveStreamingDetails",
                id=video_id
            ).execute()
            
            if video_response.get('items'):
                live_chat_id = video_response['items'][0]['liveStreamingDetails'].get('activeLiveChatId')
                if live_chat_id:
                    print(f"📺 Found live chat: {live_chat_id}")
                    
                    # Send test message
                    message = f"🤖 Bot Status Check - Account: {channel_name} - System operational ✅"
                    
                    result = youtube.liveChatMessages().insert(
                        part="snippet",
                        body={
                            "snippet": {
                                "liveChatId": live_chat_id,
                                "type": "textMessageEvent",
                                "textMessageDetails": {
                                    "messageText": message
                                }
                            }
                        }
                    ).execute()
                    
                    print(f"✅ Test message sent! ID: {result.get('id')}")
                    print(f"📝 Message: {message}")
                else:
                    print("❌ No active live chat found")
            else:
                print("❌ Video not found")
                
        except Exception as e:
            print(f"❌ Error sending test message: {e}")
    else:
        print("\n❌ Could not determine which account is being used")

if __name__ == "__main__":
    main()