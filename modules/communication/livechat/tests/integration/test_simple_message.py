#!/usr/bin/env python3
"""Send a simple test message to verify bot visibility"""

import sys
import os
sys.path.insert(0, os.getcwd())

from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import json

# Use token 5 which is active
token_file = 'credentials/oauth_token5.json'

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

if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())

youtube = build('youtube', 'v3', credentials=creds)

# Get the live chat ID
video_id = "Y4cqWLavWvY"
video_response = youtube.videos().list(
    part="liveStreamingDetails",
    id=video_id
).execute()

if video_response.get('items'):
    live_chat_id = video_response['items'][0]['liveStreamingDetails'].get('activeLiveChatId')
    print(f"Live chat ID: {live_chat_id}")
    
    # Send simple text message without emojis
    messages = [
        "Bot online - testing visibility",
        "/help",
        "Testing moderation bot"
    ]
    
    for msg in messages:
        try:
            result = youtube.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": msg
                        }
                    }
                }
            ).execute()
            
            print(f"[OK] Sent: {msg}")
            print(f"   ID: {result.get('id')}")
            
            import time
            time.sleep(3)  # Wait between messages
            
        except Exception as e:
            print(f"[FAIL] Failed to send '{msg}': {e}")
else:
    print("[FAIL] Stream not found")