#!/usr/bin/env python3
"""
Simple test server to receive commands from your iPhone
This will confirm your Shortcut is working!
"""

from flask import Flask, request, jsonify
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get secret key from environment (WSP compliant security)
SECRET_KEY = os.getenv('VOICE_CONTROL_SECRET', '012_secret_key_change_me')

@app.route('/voice-command', methods=['POST'])
def voice_command():
    """Receive command from iPhone"""
    print("\n" + "="*50)
    print(">>> RECEIVED REQUEST FROM IPHONE!")
    print("="*50)
    
    # Check auth
    auth = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    if not auth and request.json:
        auth = request.json.get('auth', '').strip()
    
    # Log everything
    print(f"Auth Token Received: {auth}")
    print(f"Headers: {dict(request.headers)}")
    print(f"Body: {request.json}")
    
    # Accept the simple test key for now
    valid_keys = [
        SECRET_KEY,
        '012_secret_key',
        '012_Secret_Key'
    ]
    
    if auth not in valid_keys:
        print(f"UNAUTHORIZED - Token '{auth}' not in valid keys")
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get the command
    data = request.json or {}
    command = data.get('command', 'No command received')
    
    print(f"\n>>> SUCCESS! Command received: '{command}'")
    print(f"Timestamp: {datetime.now()}")
    
    # Save to file so we can see it
    with open('command_log.txt', 'a') as f:
        f.write(f"\n{datetime.now()}: {command}")
    
    # Would normally trigger DAE here
    # For now, just confirm receipt
    
    return jsonify({
        'success': True,
        'message': f'Received: {command}',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/test', methods=['GET', 'POST'])
def test():
    """Simple test endpoint"""
    return """
    <h1>Server is Running!</h1>
    <p>Your iPhone should POST to: http://192.168.3.2:5012/voice-command</p>
    <form method="POST" action="/voice-command">
        <input type="text" name="command" placeholder="Test command">
        <input type="hidden" name="auth" value="012_secret_key">
        <button type="submit">Test Send</button>
    </form>
    """

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({'status': 'running', 'time': datetime.now().isoformat()})

if __name__ == '__main__':
    print("\n" + "="*60)
    print("VOICE COMMAND TEST SERVER")
    print("="*60)
    print("Listening for iPhone commands...")
    print(f"Server URL: http://192.168.3.2:5012/voice-command")
    print(f"Test in browser: http://192.168.3.2:5012/test")
    print("="*60)
    print("\nWaiting for your iPhone to send a command...\n")
    
    # Run server
    app.run(host='0.0.0.0', port=5012, debug=True)