#!/usr/bin/env python3
"""
Banter Chat Agent - Responds to YouTube Live Chat using Banter Engine
"""

import sys
import os
import time
import json
from datetime import datetime
from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback
from modules.ai_intelligence.banter_engine.src.banter_engine import BanterEngine

class BanterChatAgent:
    def __init__(self):
        self.service = None
        self.banter_engine = None
        self.live_chat_id = None
        self.next_page_token = None
        self.processed_messages = set()
        self.my_channel_id = None
        
    def authenticate(self):
        """Authenticate with YouTube API"""
        print("[INFO] Authenticating with YouTube...")
        auth_result = get_authenticated_service_with_fallback()
        if not auth_result:
            print("[ERROR] Failed to authenticate")
            return False
            
        self.service, credentials, credential_set = auth_result
        print(f"[OK] Authenticated with {credential_set}")
        
        # Get our channel ID to avoid responding to ourselves
        try:
            response = self.service.channels().list(part='snippet', mine=True).execute()
            if response.get('items'):
                channel = response['items'][0]
                self.my_channel_id = channel['id']
                channel_title = channel['snippet']['title']
                print(f"[OK] Connected as: {channel_title}")
            else:
                print("[ERROR] No channel found")
                return False
        except Exception as e:
            print(f"[ERROR] Failed to get channel info: {e}")
            return False
            
        return True
    
    def initialize_banter_engine(self):
        """Initialize the banter engine"""
        print("[INFO] Initializing Banter Engine...")
        try:
            self.banter_engine = BanterEngine()
            print("[OK] Banter Engine initialized")
            
            # Test the banter engine
            test_response = self.banter_engine.generate_response("Hello", "greeting")
            print(f"[TEST] Banter test: {test_response}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to initialize Banter Engine: {e}")
            print("[INFO] Using fallback responses")
            return False
    
    def find_active_livestream(self):
        """Find active livestream"""
        try:
            # Try to get user's live broadcasts
            request = self.service.liveBroadcasts().list(
                part="id,snippet,status",
                mine=True
            )
            response = request.execute()
            
            if response.get('items'):
                for item in response['items']:
                    if item['status']['lifeCycleStatus'] in ['live']:
                        video_id = item['id']
                        title = item['snippet']['title']
                        self.live_chat_id = item['snippet'].get('liveChatId')
                        
                        if self.live_chat_id:
                            print(f"[OK] Found livestream: {title}")
                            print(f"[OK] Video ID: {video_id}")
                            print(f"[OK] Chat ID: {self.live_chat_id}")
                            return True
                            
            # Try search method
            request = self.service.search().list(
                part="id,snippet",
                channelId=self.my_channel_id,
                eventType="live",
                type="video",
                maxResults=1
            )
            
            response = request.execute()
            
            if response.get('items'):
                video_id = response['items'][0]['id']['videoId']
                title = response['items'][0]['snippet']['title']
                
                # Get live chat ID
                video_response = self.service.videos().list(
                    part="liveStreamingDetails",
                    id=video_id
                ).execute()
                
                if video_response.get('items'):
                    self.live_chat_id = video_response['items'][0].get('liveStreamingDetails', {}).get('activeLiveChatId')
                    if self.live_chat_id:
                        print(f"[OK] Found livestream: {title}")
                        print(f"[OK] Video ID: {video_id}")
                        print(f"[OK] Chat ID: {self.live_chat_id}")
                        return True
                        
            print("[INFO] No active livestream found")
            return False
            
        except Exception as e:
            print(f"[ERROR] Error finding livestream: {e}")
            return False
    
    def get_chat_messages(self):
        """Get new chat messages"""
        try:
            request = self.service.liveChatMessages().list(
                liveChatId=self.live_chat_id,
                part="id,snippet,authorDetails",
                pageToken=self.next_page_token
            )
            
            response = request.execute()
            self.next_page_token = response.get('nextPageToken')
            
            messages = []
            for item in response.get('items', []):
                msg_id = item['id']
                
                # Skip if we've already processed this message
                if msg_id in self.processed_messages:
                    continue
                    
                self.processed_messages.add(msg_id)
                
                # Skip our own messages
                author_channel_id = item['authorDetails']['channelId']
                if author_channel_id == self.my_channel_id:
                    continue
                
                author = item['authorDetails']['displayName']
                text = item['snippet']['textMessageDetails']['messageText']
                
                messages.append({
                    'id': msg_id,
                    'author': author,
                    'author_channel_id': author_channel_id,
                    'text': text,
                    'timestamp': item['snippet']['publishedAt']
                })
            
            return messages
            
        except Exception as e:
            print(f"[ERROR] Failed to get chat messages: {e}")
            return []
    
    def detect_message_type(self, message):
        """Detect the type of message for banter categorization"""
        text = message.lower()
        
        if any(word in text for word in ['hi', 'hello', 'hey', 'greetings', 'sup']):
            return 'greeting'
        elif any(word in text for word in ['thanks', 'thank you', 'thx', 'ty']):
            return 'gratitude'
        elif '?' in text:
            return 'question'
        elif any(word in text for word in ['lol', 'haha', 'funny', '😂', '🤣']):
            return 'humor'
        elif any(word in text for word in ['love', 'like', 'awesome', 'great', '❤️', '👍']):
            return 'positive'
        elif any(word in text for word in ['trump', 'maga', 'politics']):
            return 'political'
        elif any(word in text for word in ['japan', 'tokyo', 'japanese']):
            return 'japan'
        else:
            return 'general'
    
    def generate_banter_response(self, message):
        """Generate a banter response to a message"""
        msg_type = self.detect_message_type(message['text'])
        
        if self.banter_engine:
            try:
                # Process input through banter engine
                state, response = self.banter_engine.process_input(message['text'])
                
                # If no response from emoji processing, get themed response
                if not response:
                    response = self.banter_engine.get_random_banter(theme=msg_type)
                
                # Personalize with author name if not already included
                if message['author'] not in response:
                    response = f"@{message['author']} {response}"
                
                return response
            except Exception as e:
                print(f"[WARN] Banter engine error: {e}")
                pass
        
        # Fallback responses if banter engine isn't available
        fallback_responses = {
            'greeting': [
                f"Hey {message['author']}! Welcome to the stream! [CELEBRATE]",
                f"What's up {message['author']}! Good to see you here!",
                f"Yo {message['author']}! Thanks for joining! 🙌"
            ],
            'gratitude': [
                f"You're welcome {message['author']}! 😊",
                f"No problem at all, {message['author']}!",
                f"Happy to help, {message['author']}! 💪"
            ],
            'question': [
                f"Great question, {message['author']}! Let me think about that...",
                f"Hmm {message['author']}, that's interesting... 🤔",
                f"{message['author']}, I'll need to ponder that one! [AI]"
            ],
            'humor': [
                f"😂 {message['author']}, you're hilarious!",
                f"LMAO {message['author']}! That's a good one!",
                f"Haha, {message['author']} bringing the comedy gold! 🏆"
            ],
            'positive': [
                f"Thanks {message['author']}! Spreading the good vibes! ✨",
                f"Appreciate you {message['author']}! Keep that energy! 🔥",
                f"{message['author']}, you're awesome! Much love! ❤️"
            ],
            'political': [
                f"{message['author']}, let's keep it chill and enjoy the stream! 😎",
                f"Politics aside {message['author']}, we're all friends here! [HANDSHAKE]",
                f"{message['author']}, save the politics for Twitter! 😄"
            ],
            'japan': [
                f"{message['author']}, Japan is amazing! 🗾 Have you been?",
                f"Ah {message['author']}, talking about the best country! 🇯🇵",
                f"{message['author']}, Japan talk? Now we're speaking my language! 🍜"
            ],
            'general': [
                f"Thanks for chatting, {message['author']}! 👋",
                f"{message['author']}, appreciate your input! 💬",
                f"Good point, {message['author']}! 👍"
            ]
        }
        
        import random
        responses = fallback_responses.get(msg_type, fallback_responses['general'])
        return random.choice(responses)
    
    def send_chat_message(self, message_text):
        """Send a message to the live chat"""
        try:
            request = self.service.liveChatMessages().insert(
                part="snippet",
                body={
                    "snippet": {
                        "liveChatId": self.live_chat_id,
                        "type": "textMessageEvent",
                        "textMessageDetails": {
                            "messageText": message_text
                        }
                    }
                }
            )
            
            response = request.execute()
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to send message: {e}")
            return False
    
    def run(self):
        """Main loop to monitor chat and respond with banter"""
        print("\n[INFO] Starting Banter Chat Agent...")
        
        # Authenticate
        if not self.authenticate():
            return
        
        # Initialize banter engine
        self.initialize_banter_engine()
        
        # Find livestream
        if not self.find_active_livestream():
            print("[WARN] No active livestream found!")
            print("[INFO] Start a livestream and run this script again")
            return
        
        print("\n[OK] Banter Chat Agent is running!")
        print("[INFO] Monitoring chat for messages...")
        print("[INFO] Press Ctrl+C to stop\n")
        
        # Send initial greeting
        self.send_chat_message("[BOT] Banter Bot activated! Ready to chat! Say hello! 👋")
        
        # Main monitoring loop
        try:
            while True:
                messages = self.get_chat_messages()
                
                for message in messages:
                    print(f"\n[CHAT] {message['author']}: {message['text']}")
                    
                    # Generate banter response
                    response = self.generate_banter_response(message)
                    
                    if response:
                        print(f"[BANTER] Responding: {response}")
                        if self.send_chat_message(response):
                            print("[OK] Response sent!")
                        
                        # Add a small delay to avoid spamming
                        time.sleep(2)
                
                # Wait before checking for new messages
                time.sleep(5)
                
        except KeyboardInterrupt:
            print("\n[INFO] Stopping Banter Chat Agent...")
            self.send_chat_message("[BOT] Banter Bot signing off! Thanks for chatting! 👋")
            print("[OK] Agent stopped")

if __name__ == "__main__":
    agent = BanterChatAgent()
    agent.run()