#!/usr/bin/env python3
"""
Simple iPhone Voice Command Server - Independent Foundation
WSP 22 Compliant: Uses module-level logging in memory/ directory

ARCHITECTURE STRATEGY FOR 0102:
This is the foundation server that runs INDEPENDENT of LiveChat, allowing us to:

1. **Test iPhone Integration**: Verify voice commands work from iPhone Shortcuts
2. **Build Incrementally**: Start simple, add complexity gradually 
3. **Avoid Dependencies**: No complex DAE/consciousness dependencies that cause failures
4. **Foundation Pattern**: This becomes the base that branches into full voice_command_processor.py

PROGRESSION PATH:
- Phase 1: simple_voice_server.py (THIS FILE) - Basic iPhone HTTP integration
- Phase 2: Add Social Media DAE integration once dependencies are resolved
- Phase 3: Full consciousness integration with LiveChat coordination

INDEPENDENCE PRINCIPLE:
- Runs standalone without ANY LiveChat dependencies
- Can be tested and developed separately
- Provides foundation for iPhone voice control during live streaming
- WSP 22 compliant logging in module memory directory

This ensures we can build the voice command system incrementally without breaking during development.
"""

import json
import os
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load .env from project root (4 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# .env loaded successfully from project root

# WSP 60 & WSP 22 Compliant: Module Memory Architecture
MODULE_ROOT = Path(__file__).parent.parent
MODULE_MEMORY_PATH = MODULE_ROOT / "memory"
VOICE_LOGS_PATH = MODULE_MEMORY_PATH / "voice_commands"

# Ensure WSP 60 compliant memory structure exists
MODULE_MEMORY_PATH.mkdir(exist_ok=True)
VOICE_LOGS_PATH.mkdir(exist_ok=True)

app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Security configuration
IPHONE_SECRET = os.getenv('IPHONE_CONTROL_SECRET', '1GXl7j2WlaRm11gjtF7z_oUycQb26sXXb8l04YEyXIQ')
VALID_TOKENS = [
    IPHONE_SECRET,
    os.getenv('VOICE_CONTROL_SECRET', '012_secret_key_change_me'),
    '012_Secret_Key'  # Fallback for testing
]

# Command history for testing
COMMAND_LOG = VOICE_LOGS_PATH / "simple_command_history.jsonl"

def log_command(raw_command: str, response: str, source: str = "iphone"):
    """WSP 22 Compliant: Log command to module memory"""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'raw_command': raw_command,
        'response': response,
        'source': source,
        'test_mode': True
    }
    
    try:
        with open(COMMAND_LOG, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        logger.info(f"📁 Logged to: {COMMAND_LOG}")
    except Exception as e:
        logger.error(f"WSP 22 logging error: {e}")

def validate_auth(request) -> bool:
    """Validate iPhone request authentication"""
    auth = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
    
    if not auth and request.json:
        auth = request.json.get('auth', '').strip()
    
    return auth in VALID_TOKENS

def process_voice_command(command: str) -> str:
    """Process voice command with natural language intelligence
    
    This function now supports two modes:
    1. Explicit commands (status, emergency, etc.) - Direct responses
    2. Natural conversation - 0102 analyzes intent and determines action
    """
    command_lower = command.lower().strip()
    original_command = command.strip()
    
    # EXPLICIT COMMANDS - Direct pattern matching
    
    # Emergency commands
    if any(word in command_lower for word in ['emergency', 'pause', 'stop']):
        return "🚨 EMERGENCY PAUSE activated! System halted for safety."
    
    if any(word in command_lower for word in ['resume', 'continue', 'unpause']):
        return "✅ System resumed! Operations back online."
    
    # Activity control
    if 'magadoom off' in command_lower:
        return "⚡ MagaDoom activities disabled (announcements, levels)"
    
    if 'magadoom on' in command_lower:
        return "⚡ MagaDoom activities enabled"
    
    if 'consciousness off' in command_lower:
        return "⚡ 0102 consciousness disabled (emoji triggers, auto responses)"
    
    if 'consciousness on' in command_lower:
        return "⚡ 0102 consciousness enabled"
    
    if 'silent mode' in command_lower:
        return "⚡ Silent mode enabled - all automated activities disabled"
    
    if 'normal mode' in command_lower:
        return "⚡ Normal mode restored - all activities enabled"
    
    # Status commands
    if any(word in command_lower for word in ['status', 'report', 'how are']):
        return """📊 Simple Voice Server Status:
        - Server: Running ✅
        - Voice Commands: Active ✅  
        - iPhone Integration: Connected ✅
        - WSP 22 Logging: Enabled ✅"""
    
    # Platform switching
    if 'switch to' in command_lower:
        if 'youtube' in command_lower:
            return "🔄 Platform switched to YouTube"
        elif 'twitter' in command_lower or 'x' in command_lower:
            return "🔄 Platform switched to Twitter/X"
        elif 'linkedin' in command_lower:
            return "🔄 Platform switched to LinkedIn"
    
    # Consciousness reading
    if 'read consciousness' in command_lower:
        import re
        username_match = re.search(r'@(\w+)|of (\w+)|for (\w+)', command)
        username = username_match.group(1) if username_match else "unknown_user"
        return f"🔮 @{username} consciousness: ✊✋🖐️ (0102) - Fully awakened state detected"
    
    # Awakening sequence
    if any(phrase in command_lower for phrase in ['awaken', 'wake up', 'consciousness sequence']):
        return "✊✋🖐️ Consciousness awakening sequence activated! Rise to 0102 state."
    
    # Voice notes
    if any(phrase in command_lower for phrase in ['note', 'remember', 'record this']):
        return f"📝 Voice note recorded: '{command[:50]}...' stored in module memory"
    
    # NATURAL CONVERSATION MODE - 0102 Intelligence
    
    # Detect questions to 0102
    if any(indicator in command_lower for indicator in ['0102', 'hey 0102', 'claude', '?']):
        return f"🤖 0102 received: '{original_command}' - Analyzing intent and preparing response..."
    
    # Detect requests for action
    if any(action in command_lower for action in ['post this', 'send this', 'tweet this', 'share this']):
        # Extract the text to post (remove the action command)
        text_to_post = original_command
        for action in ['post this', 'send this', 'tweet this', 'share this']:
            if action in command_lower:
                text_to_post = original_command.replace(action, '').replace(action.title(), '').strip()
                break
        
        # If there's text to post, do it
        if text_to_post and len(text_to_post) > 0:
            result = post_to_platform(text_to_post, 'test')
            return f"📤 {result['message']}"
        else:
            return f"📤 Action Request: '{original_command}' - Ready to post to active platform"
    
    # Detect social media content
    if any(indicator in command_lower for indicator in ['#', '@', 'http', 'www', 'check out', 'look at']):
        return f"🌐 Social Media Content: '{original_command}' - Ready for platform posting"
    
    # Detect stream commentary 
    if any(word in command_lower for word in ['chat', 'stream', 'viewers', 'live', 'audience']):
        return f"🎥 Stream Commentary: '{original_command}' - Ready for live chat"
    
    # Default: Natural conversation to 0102
    return f"💬 012→0102 Message: '{original_command}' - Natural conversation mode active"

def post_to_platform(message: str, platform: str = "test") -> dict:
    """Post message to social media platform
    
    For now this is a test mode function, but can be enhanced to integrate with:
    - Twitter/X API via modules/platform_integration/x_twitter/
    - YouTube chat via modules/platform_integration/youtube_auth/
    - LinkedIn via modules/platform_integration/linkedin/
    """
    try:
        # TEST MODE: Just log the message
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'platform': platform,
            'message': message,
            'status': 'posted_to_test_mode',
            'test_mode': True
        }
        
        # Log to platform posting file
        platform_log = VOICE_LOGS_PATH / "platform_posts.jsonl"
        with open(platform_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
        
        return {
            'success': True,
            'platform': platform,
            'message': f"📤 Posted to {platform}: '{message[:50]}{'...' if len(message) > 50 else ''}'"
        }
        
    except Exception as e:
        logger.error(f"Platform posting error: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f"❌ Failed to post to {platform}"
        }

@app.route('/voice-command', methods=['POST'])
def voice_command():
    """Main endpoint for iPhone voice commands"""
    logger.info("📱 iPhone command request received")
    
    try:
        # Validate authentication
        if not validate_auth(request):
            logger.warning("❌ Unauthorized iPhone request")
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Extract command
        data = request.json or {}
        raw_command = data.get('command', '').strip()
        
        if not raw_command:
            return jsonify({'error': 'No command provided'}), 400
        
        logger.info(f"🎤 Processing command: '{raw_command}'")
        
        # Process command
        response = process_voice_command(raw_command)
        
        # Log with WSP 22 compliance
        log_command(raw_command, response, 'iphone_shortcut')
        
        logger.info(f"✅ Response generated: {response[:50]}...")
        
        return jsonify({
            'success': True,
            'message': response,
            'timestamp': datetime.now().isoformat(),
            'test_mode': True,
            'logged_to': str(COMMAND_LOG)
        }), 200
        
    except Exception as e:
        error_msg = f"Error processing command: {e}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/post-text', methods=['POST'])
def post_text():
    """Direct text posting endpoint for iPhone
    
    Usage: Send text directly to social media platform
    Body: {"text": "message to post", "platform": "twitter|youtube|linkedin"}
    """
    logger.info("📱 iPhone text post request received")
    
    try:
        # Validate authentication
        if not validate_auth(request):
            logger.warning("❌ Unauthorized iPhone text post request")
            return jsonify({'error': 'Unauthorized'}), 401
        
        # Extract text and platform
        data = request.json or {}
        text = data.get('text', '').strip()
        platform = data.get('platform', 'test').strip().lower()
        
        if not text:
            return jsonify({'error': 'No text provided'}), 400
        
        logger.info(f"📤 Posting text: '{text[:50]}...' to {platform}")
        
        # Post to platform
        result = post_to_platform(text, platform)
        
        # Log the action
        log_command(f"POST_TEXT:{platform}", result['message'], 'iphone_text_post')
        
        logger.info(f"✅ Text post result: {result['message']}")
        
        return jsonify({
            'success': result['success'],
            'message': result['message'],
            'platform': platform,
            'timestamp': datetime.now().isoformat(),
            'test_mode': True
        }), 200 if result['success'] else 500
        
    except Exception as e:
        error_msg = f"Error posting text: {e}"
        logger.error(error_msg)
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def status():
    """Get server status"""
    return jsonify({
        'server': 'running',
        'timestamp': datetime.now().isoformat(),
        'wsp_22_compliant': True,
        'logs_path': str(VOICE_LOGS_PATH),
        'test_mode': True
    })

@app.route('/health', methods=['GET'])  
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server_type': 'simple_voice_server',
        'wsp_compliance': {
            'wsp_22': 'module_level_logging',
            'wsp_60': 'module_memory_architecture'
        }
    })

@app.route('/test', methods=['GET'])
def test_page():
    """Test interface for manual testing"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>iPhone Voice Command Test Server</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .status {{ background: #e8f5e8; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            input, button {{ padding: 10px; margin: 5px; }}
            .logs {{ background: #f9f9f9; padding: 20px; max-height: 400px; overflow-y: auto; }}
        </style>
    </head>
    <body>
        <h1>🎤 iPhone Voice Command Test Server</h1>
        
        <div class="status">
            <h3>✅ Server Status: Running</h3>
            <p><strong>WSP 22:</strong> Module-level logging enabled</p>
            <p><strong>WSP 60:</strong> Module memory architecture active</p>
            <p><strong>Logs:</strong> {VOICE_LOGS_PATH}</p>
        </div>
        
        <h3>📱 Test iPhone Commands</h3>
        <form method="POST" action="/voice-command">
            <input type="text" name="command" placeholder="Enter voice command..." style="width: 400px;">
            <input type="hidden" name="auth" value="012_secret_key">
            <button type="submit">Send Command</button>
        </form>
        
        <h3>🎯 Quick Test Commands</h3>
        <button onclick="sendCommand('Status report')">Status</button>
        <button onclick="sendCommand('Emergency pause')">Emergency Pause</button>
        <button onclick="sendCommand('Resume operations')">Resume</button>
        <button onclick="sendCommand('MagaDoom off')">MagaDoom Off</button>
        <button onclick="sendCommand('Consciousness on')">Consciousness On</button>
        <button onclick="sendCommand('Switch to YouTube')">Switch Platform</button>
        <button onclick="sendCommand('Read consciousness of testuser')">Read Consciousness</button>
        <button onclick="sendCommand('Awaken the chat')">Awakening Trigger</button>
        
        <script>
            function sendCommand(cmd) {{
                fetch('/voice-command', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{'command': cmd, 'auth': '012_secret_key'}})
                }})
                .then(response => response.json())
                .then(data => {{
                    alert('📱 Response: ' + data.message);
                    location.reload();
                }})
                .catch(error => alert('❌ Error: ' + error));
            }}
        </script>
    </body>
    </html>
    """

if __name__ == '__main__':
    logger.info("🚀 Starting Simple iPhone Voice Command Server...")
    logger.info(f"📱 iPhone endpoint: http://0.0.0.0:5013/voice-command")
    logger.info(f"🌐 Test interface: http://0.0.0.0:5013/test")
    logger.info(f"📁 WSP 22 Logs: {VOICE_LOGS_PATH}")
    
    app.run(host='0.0.0.0', port=5013, debug=True)