#!/usr/bin/env python3
"""
Send a test message to YouTube Live Chat
WSP-Compliant tool for testing chat functionality
"""

from modules.infrastructure.oauth_management.src.oauth_manager import get_authenticated_service_with_fallback

def send_message(live_chat_id, message):
    """Send a message to live chat"""
    auth_result = get_authenticated_service_with_fallback()
    if not auth_result:
        print("[ERROR] Failed to authenticate")
        return False
    
    service, credentials, credential_set = auth_result
    print(f"[OK] Authenticated with {credential_set}")
    
    try:
        request = service.liveChatMessages().insert(
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
        )
        
        response = request.execute()
        print(f"[OK] Message sent: {message}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")
        return False

if __name__ == "__main__":
    # Your livestream chat ID
    chat_id = "KicKGFVDLUxTU2xPWndwR0lSSVlpaGF6OHpDdxILTFFpZXhobmU2dTQ"
    
    # Send test message with emoji sequence
    message = "✊✋🖐️"  # This should trigger "You stepped off the wheel. Welcome."
    
    print(f"[INFO] Sending emoji sequence: {message}")
    if send_message(chat_id, message):
        print("[INFO] Message sent! Check monitor for banter response.")
    else:
        print("[ERROR] Failed to send message")