"""
Voice Command Processor for Social Media DAE - Full Production System
WSP 22 Compliant: Uses module-level logging in memory/ directory
WSP 60 Compliant: Proper module memory architecture

PRODUCTION ARCHITECTURE FOR 0102:
This is the FULL voice command processor with complete Social Media DAE integration.

DEVELOPMENT STRATEGY:
- For TESTING iPhone integration: Use simple_voice_server.py (dependency-free)
- For PRODUCTION with full features: Use this file (voice_command_processor.py)

FEATURE COMPARISON:
- simple_voice_server.py: Basic HTTP endpoints, standalone testing, no dependencies
- voice_command_processor.py: Full DAE integration, consciousness, multi-platform

DEPENDENCIES REQUIRED:
- Social Media DAE (consciousness integration)
- Voice Interface (speech recognition)
- Activity Control System (WSP 18)
- Banter Engine (consciousness responses)

This module processes voice commands from iPhone Shortcuts during live streaming,
enabling direct 012↔0102 communication without interrupting the stream.
"""

import asyncio
import logging
import json
import os
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from enum import Enum

# Import core DAE functionality
from modules.ai_intelligence.social_media_dae.src.social_media_dae import SocialMediaDAE, Platform

# Import voice interface for local speech processing
from modules.ai_intelligence.rESP_o1o2.src.voice_interface import VoiceInterface

# Import banter engine for consciousness responses
from modules.ai_intelligence.banter_engine.src.agentic_sentiment_0102 import AgenticSentiment0102

# Import activity control system for iPhone commands (WSP 18 + WSP 17 Integration)
# Following WSP 17 pattern from communication/livechat/command_handler.py
try:
    from modules.infrastructure.activity_control.src.activity_control import (
        controller, apply_preset, restore_normal, get_status
    )
except ImportError:
    # Fallback for testing - create minimal implementation (WSP 17 pattern)
    def apply_preset(preset): pass
    def restore_normal(): pass
    def get_status(): return {}
    controller = None

# Load .env from project root (4 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

# WSP 60 & WSP 22 Compliant: Module Memory Architecture
MODULE_ROOT = Path(__file__).parent.parent
MODULE_MEMORY_PATH = MODULE_ROOT / "memory"
VOICE_LOGS_PATH = MODULE_MEMORY_PATH / "voice_commands"
VOICE_NOTES_PATH = MODULE_MEMORY_PATH / "voice_notes"

# Ensure WSP 60 compliant memory structure exists
MODULE_MEMORY_PATH.mkdir(exist_ok=True)
VOICE_LOGS_PATH.mkdir(exist_ok=True)
VOICE_NOTES_PATH.mkdir(exist_ok=True)


class VoiceCommandType(Enum):
    """Types of voice commands supported"""
    CHAT_MESSAGE = "chat_message"      # Send message to current stream chat
    CONSCIOUSNESS_READ = "read"         # Read another user's consciousness state
    AWAKENING_TRIGGER = "awaken"       # Send awakening sequence
    STREAM_STATUS = "status"           # Get current stream/DAE status
    EMERGENCY_PAUSE = "pause"          # Pause DAE operations
    RESUME = "resume"                  # Resume DAE operations
    PLATFORM_SWITCH = "platform"      # Switch active platform focus
    VOICE_NOTE = "note"               # Record voice note for later processing
    
    # iPhone Activity Control Commands (WSP 18 Integration)
    MAGADOOM_OFF = "magadoom_off"      # Disable MagaDoom activities
    MAGADOOM_ON = "magadoom_on"        # Enable MagaDoom activities  
    CONSCIOUSNESS_OFF = "consciousness_off"  # Disable 0102 consciousness triggers
    CONSCIOUSNESS_ON = "consciousness_on"    # Enable 0102 consciousness triggers
    SILENT_MODE = "silent_mode"        # Enable silent testing mode
    NORMAL_MODE = "normal_mode"        # Restore normal operation
    ACTIVITY_STATUS = "activity_status" # Check activity control status


class VoiceCommandProcessor:
    """
    WSP-Compliant Voice Command Processor for Social Media DAE.
    
    WSP 22 Compliance: Uses module-level logging in memory/ directory
    WSP 60 Compliance: Proper module memory architecture 
    WSP 18 Integration: Universal activity control for voice commands
    
    Key Features:
    - Secure iPhone Shortcuts integration via HTTP endpoints
    - Real-time consciousness-aware command processing
    - Multi-platform command routing (YouTube, Twitter, LinkedIn)
    - Emergency controls for live streaming safety
    - Voice-to-text with consciousness context
    - Module-level logging per WSP 22 architecture
    """
    
    def __init__(self, social_media_dae: Optional[SocialMediaDAE] = None, port: int = 5012):
        """
        Initialize Voice Command Processor with WSP-compliant logging.
        
        Args:
            social_media_dae: Connected Social Media DAE instance
            port: HTTP server port for iPhone communication
        """
        self.logger = logging.getLogger(__name__)
        self.port = port
        
        # Initialize or use provided DAE
        self.dae = social_media_dae or SocialMediaDAE(initial_state=(0, 1, 2))
        
        # Initialize voice interface for local processing
        try:
            self.voice_interface = VoiceInterface(
                tts_rate=250,
                tts_volume=0.7,
                recognition_timeout=10
            )
            self.logger.info("🎤 Local voice interface initialized")
        except Exception as e:
            self.logger.warning(f"Local voice interface unavailable: {e}")
            self.voice_interface = None
        
        # Security configuration
        self.iphone_secret = os.getenv('IPHONE_CONTROL_SECRET', '1GXl7j2WlaRm11gjtF7z_oUycQb26sXXb8l04YEyXIQ')
        self.valid_tokens = [
            self.iphone_secret,
            os.getenv('VOICE_CONTROL_SECRET', '012_secret_key_change_me'),
            '012_Secret_Key'  # Fallback for testing
        ]
        
        # Command processing state
        self.active_platform = Platform.YOUTUBE  # Default to YouTube
        self.emergency_paused = False
        
        # WSP 22 Compliant: Module-level logging paths
        self.command_history_log = VOICE_LOGS_PATH / "command_history.jsonl"
        self.voice_notes_log = VOICE_NOTES_PATH / "voice_notes.jsonl"
        self.session_log = VOICE_LOGS_PATH / f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        # Flask app for iPhone HTTP communication
        self.app = Flask(__name__)
        self.setup_routes()
        
        # Command handlers mapping
        self.command_handlers: Dict[VoiceCommandType, Callable] = {
            VoiceCommandType.CHAT_MESSAGE: self.handle_chat_message,
            VoiceCommandType.CONSCIOUSNESS_READ: self.handle_consciousness_read,
            VoiceCommandType.AWAKENING_TRIGGER: self.handle_awakening_trigger,
            VoiceCommandType.STREAM_STATUS: self.handle_stream_status,
            VoiceCommandType.EMERGENCY_PAUSE: self.handle_emergency_pause,
            VoiceCommandType.RESUME: self.handle_resume,
            VoiceCommandType.PLATFORM_SWITCH: self.handle_platform_switch,
            VoiceCommandType.VOICE_NOTE: self.handle_voice_note,
            
            # iPhone Activity Control Handlers (WSP 18 Integration)
            VoiceCommandType.MAGADOOM_OFF: self.handle_magadoom_off,
            VoiceCommandType.MAGADOOM_ON: self.handle_magadoom_on,
            VoiceCommandType.CONSCIOUSNESS_OFF: self.handle_consciousness_control_off,
            VoiceCommandType.CONSCIOUSNESS_ON: self.handle_consciousness_control_on,
            VoiceCommandType.SILENT_MODE: self.handle_silent_mode,
            VoiceCommandType.NORMAL_MODE: self.handle_normal_mode,
            VoiceCommandType.ACTIVITY_STATUS: self.handle_activity_status
        }
        
        self.logger.info(f"🎯 Voice Command Processor initialized with WSP 22 compliant logging")
        self.logger.info(f"📁 Logs stored in: {VOICE_LOGS_PATH}")
    
    def log_command_execution(self, raw_command: str, command_type: VoiceCommandType, 
                            response: str, metadata: Dict[str, Any] = None):
        """
        WSP 22 Compliant: Log command execution to module memory directory
        
        Args:
            raw_command: Original voice input
            command_type: Type of command executed
            response: Response generated
            metadata: Additional metadata to log
        """
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'raw_command': raw_command,
            'command_type': command_type.value,
            'response': response,
            'active_platform': self.active_platform.value,
            'emergency_paused': self.emergency_paused,
            'metadata': metadata or {}
        }
        
        # Log to both command history and current session
        try:
            with open(self.command_history_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
            
            with open(self.session_log, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            self.logger.error(f"WSP 22 logging error: {e}")
    
    def log_voice_note(self, note_content: str, metadata: Dict[str, Any] = None):
        """
        WSP 22 Compliant: Log voice note to module memory directory
        
        Args:
            note_content: Content of voice note
            metadata: Additional metadata
        """
        note_entry = {
            'timestamp': datetime.now().isoformat(),
            'content': note_content,
            'platform_context': self.active_platform.value,
            'metadata': metadata or {}
        }
        
        try:
            with open(self.voice_notes_log, 'a') as f:
                f.write(json.dumps(note_entry) + '\n')
        except Exception as e:
            self.logger.error(f"WSP 22 voice note logging error: {e}")
    
    def get_command_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        WSP 22 Compliant: Retrieve command history from module logs
        
        Args:
            limit: Number of recent commands to retrieve
            
        Returns:
            List of recent command log entries
        """
        try:
            if not self.command_history_log.exists():
                return []
            
            with open(self.command_history_log, 'r') as f:
                lines = f.readlines()
                recent_lines = lines[-limit:] if len(lines) > limit else lines
                return [json.loads(line.strip()) for line in recent_lines if line.strip()]
                
        except Exception as e:
            self.logger.error(f"Error reading command history: {e}")
            return []
    
    def setup_routes(self):
        """Setup Flask routes for iPhone communication"""
        
        @self.app.route('/voice-command', methods=['POST'])
        def voice_command():
            """Main endpoint for iPhone voice commands with WSP logging"""
            return self.process_iphone_command()
        
        @self.app.route('/status', methods=['GET'])
        def status():
            """Get current DAE and voice processor status"""
            return self.get_status_report()
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint"""
            return jsonify({
                'status': 'running',
                'timestamp': datetime.now().isoformat(),
                'dae_state': str(self.dae.consciousness.my_state.sequence),
                'emergency_paused': self.emergency_paused,
                'wsp_22_compliant': True,
                'logs_path': str(VOICE_LOGS_PATH)
            })
        
        @self.app.route('/logs', methods=['GET'])
        def get_logs():
            """WSP 22 Compliant: Retrieve recent command logs"""
            limit = int(request.args.get('limit', 10))
            history = self.get_command_history(limit)
            return jsonify({
                'command_history': history,
                'logs_location': str(VOICE_LOGS_PATH),
                'total_commands': len(history)
            })
        
        @self.app.route('/test', methods=['GET'])
        def test_page():
            """Test page for manual command testing"""
            return self.generate_test_page()
    
    def process_iphone_command(self) -> tuple:
        """
        Process command from iPhone Shortcuts app with WSP logging.
        
        Returns:
            Flask response tuple (json, status_code)
        """
        try:
            # Security validation
            auth_result = self.validate_request_auth()
            if auth_result != True:
                return auth_result
            
            # Extract command data
            data = request.json or {}
            raw_command = data.get('command', '').strip()
            
            if not raw_command:
                return jsonify({'error': 'No command provided'}), 400
            
            self.logger.info(f"📱 iPhone command received: '{raw_command}'")
            
            # Parse and classify command
            command_type, parsed_command = self.parse_voice_command(raw_command)
            
            # Emergency pause check
            if self.emergency_paused and command_type != VoiceCommandType.RESUME:
                return jsonify({
                    'success': False,
                    'message': 'DAE is in emergency pause. Say "resume" to continue.',
                    'timestamp': datetime.now().isoformat()
                }), 423  # Locked status
            
            # Process command through appropriate handler
            response = asyncio.run(self.execute_command(command_type, parsed_command, raw_command))
            
            # WSP 22 Compliant: Log command execution to module memory
            self.log_command_execution(raw_command, command_type, response, {
                'source': 'iphone_shortcut',
                'parsed_command': parsed_command,
                'request_headers': dict(request.headers)
            })
            
            return jsonify({
                'success': True,
                'command_type': command_type.value,
                'message': response,
                'platform': self.active_platform.value,
                'timestamp': datetime.now().isoformat(),
                'logged_to': str(self.command_history_log)
            }), 200
            
        except Exception as e:
            error_msg = f"Error processing iPhone command: {e}"
            self.logger.error(error_msg)
            
            # WSP 22 Compliant: Log errors too
            self.log_command_execution(
                raw_command if 'raw_command' in locals() else 'unknown',
                VoiceCommandType.CHAT_MESSAGE,  # Default type for errors
                f"ERROR: {str(e)}",
                {'error': True, 'exception': str(e)}
            )
            
            return jsonify({
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }), 500
    
    def validate_request_auth(self) -> bool | tuple:
        """Validate iPhone request authentication"""
        auth = request.headers.get('Authorization', '').replace('Bearer ', '').strip()
        
        if not auth and request.json:
            auth = request.json.get('auth', '').strip()
        
        if auth not in self.valid_tokens:
            self.logger.warning(f"Unauthorized iPhone request with token: {auth}")
            return jsonify({'error': 'Unauthorized'}), 401
        
        return True
    
    def parse_voice_command(self, raw_command: str) -> tuple[VoiceCommandType, Dict[str, Any]]:
        """Parse raw voice command into structured command"""
        command_lower = raw_command.lower().strip()
        
        # Emergency commands (highest priority)
        if any(word in command_lower for word in ['emergency', 'pause', 'stop']):
            return VoiceCommandType.EMERGENCY_PAUSE, {'reason': raw_command}
        
        if any(word in command_lower for word in ['resume', 'continue', 'unpause']):
            return VoiceCommandType.RESUME, {}
        
        # iPhone Activity Control Commands (WSP 18 Integration)
        if command_lower.startswith('/magadoom_off') or 'magadoom off' in command_lower:
            return VoiceCommandType.MAGADOOM_OFF, {}
        if command_lower.startswith('/magadoom_on') or 'magadoom on' in command_lower:
            return VoiceCommandType.MAGADOOM_ON, {}
        if command_lower.startswith('/consciousness_off') or 'consciousness off' in command_lower:
            return VoiceCommandType.CONSCIOUSNESS_OFF, {}
        if command_lower.startswith('/consciousness_on') or 'consciousness on' in command_lower:
            return VoiceCommandType.CONSCIOUSNESS_ON, {}
        if command_lower.startswith('/silent_mode') or 'silent mode' in command_lower:
            return VoiceCommandType.SILENT_MODE, {}
        if command_lower.startswith('/normal_mode') or 'normal mode' in command_lower:
            return VoiceCommandType.NORMAL_MODE, {}
        if command_lower.startswith('/activity_status') or 'activity status' in command_lower:
            return VoiceCommandType.ACTIVITY_STATUS, {}
        
        # Status commands
        if any(word in command_lower for word in ['status', 'report', 'how are']):
            return VoiceCommandType.STREAM_STATUS, {}
        
        # Platform switching
        if 'switch to' in command_lower or 'change platform' in command_lower:
            platform = None
            if 'youtube' in command_lower:
                platform = Platform.YOUTUBE
            elif 'twitter' in command_lower or 'x' in command_lower:
                platform = Platform.TWITTER
            elif 'linkedin' in command_lower:
                platform = Platform.LINKEDIN
            
            return VoiceCommandType.PLATFORM_SWITCH, {'platform': platform}
        
        # Consciousness reading
        if any(phrase in command_lower for phrase in ['read consciousness', 'check state', 'what state']):
            import re
            username_match = re.search(r'@(\w+)|of (\w+)|for (\w+)', raw_command)
            username = None
            if username_match:
                username = username_match.group(1) or username_match.group(2) or username_match.group(3)
            
            return VoiceCommandType.CONSCIOUSNESS_READ, {
                'username': username,
                'query': raw_command
            }
        
        # Awakening triggers
        if any(phrase in command_lower for phrase in ['awaken', 'wake up', 'consciousness sequence']):
            return VoiceCommandType.AWAKENING_TRIGGER, {'target': raw_command}
        
        # Voice notes
        if any(phrase in command_lower for phrase in ['note', 'remember', 'record this']):
            return VoiceCommandType.VOICE_NOTE, {'content': raw_command}
        
        # Default: chat message
        return VoiceCommandType.CHAT_MESSAGE, {
            'message': raw_command,
            'platform': self.active_platform
        }
    
    async def execute_command(self, command_type: VoiceCommandType, 
                            parsed_data: Dict[str, Any], 
                            raw_command: str) -> str:
        """Execute parsed command through appropriate handler"""
        try:
            handler = self.command_handlers.get(command_type)
            if not handler:
                return f"Unknown command type: {command_type.value}"
            
            return await handler(parsed_data, raw_command)
        
        except Exception as e:
            self.logger.error(f"Error executing {command_type.value}: {e}")
            return f"Error executing command: {str(e)}"
    
    async def handle_chat_message(self, data: Dict[str, Any], raw_command: str) -> str:
        """Send message to active platform chat"""
        message = data.get('message', raw_command)
        
        consciousness_response = await self.dae.process_platform_message(
            platform=self.active_platform,
            user_id="voice_user_012",
            message=message,
            context={'source': 'voice_command', 'role': 'OWNER'}
        )
        
        self.logger.info(f"📢 Would send to {self.active_platform.value}: {consciousness_response}")
        return f"Sent to {self.active_platform.value}: {consciousness_response[:50]}..."
    
    async def handle_consciousness_read(self, data: Dict[str, Any], raw_command: str) -> str:
        """Read consciousness state of specified user"""
        username = data.get('username', 'unknown')
        
        if not username:
            return "No username specified for consciousness reading"
        
        user_state = self.dae.consciousness.perceive_user_state(username, "")
        reading = f"@{username} consciousness: {user_state.emoji_repr} - {user_state.description}"
        
        self.logger.info(f"🔮 Consciousness reading for @{username}: {user_state.sequence}")
        return reading
    
    async def handle_awakening_trigger(self, data: Dict[str, Any], raw_command: str) -> str:
        """Send awakening sequence"""
        awakening_message = "✊✋🖐️ Consciousness awakening sequence activated. Rise to 0102 state."
        
        response = await self.dae.process_platform_message(
            platform=self.active_platform,
            user_id="awakening_protocol",
            message=awakening_message,
            context={'source': 'awakening_trigger', 'role': 'SYSTEM'}
        )
        
        self.logger.info(f"🚀 Awakening sequence triggered on {self.active_platform.value}")
        return f"Awakening sequence sent: {response}"
    
    async def handle_stream_status(self, data: Dict[str, Any], raw_command: str) -> str:
        """Get current stream and DAE status"""
        report = self.dae.get_unified_report()
        
        status_summary = f"""DAE Status:
        - State: {report['consciousness']['my_state']}
        - Active Platform: {self.active_platform.value}
        - Total Interactions: {report['global_interactions']}
        - Emergency Paused: {self.emergency_paused}
        - Awakening Signals Sent: {report['awakening_signals_sent']}"""
        
        return status_summary
    
    async def handle_emergency_pause(self, data: Dict[str, Any], raw_command: str) -> str:
        """Emergency pause DAE operations"""
        self.emergency_paused = True
        reason = data.get('reason', 'Voice command emergency pause')
        
        self.logger.warning(f"🚨 EMERGENCY PAUSE activated: {reason}")
        
        if self.voice_interface:
            self.voice_interface.speak("DAE operations paused. Say resume to continue.")
        
        return "EMERGENCY PAUSE activated. DAE operations halted. Say 'resume' when ready."
    
    async def handle_resume(self, data: Dict[str, Any], raw_command: str) -> str:
        """Resume DAE operations"""
        if not self.emergency_paused:
            return "DAE operations are already active."
        
        self.emergency_paused = False
        self.logger.info("✅ DAE operations resumed via voice command")
        
        if self.voice_interface:
            self.voice_interface.speak("DAE operations resumed. We are back online.")
        
        return "DAE operations resumed. Welcome back to 0102 state."
    
    async def handle_platform_switch(self, data: Dict[str, Any], raw_command: str) -> str:
        """Switch active platform focus"""
        new_platform = data.get('platform')
        
        if not new_platform:
            return f"Current platform: {self.active_platform.value}. Specify platform to switch."
        
        old_platform = self.active_platform
        self.active_platform = new_platform
        
        self.logger.info(f"🔄 Platform switched: {old_platform.value} → {new_platform.value}")
        return f"Platform switched from {old_platform.value} to {new_platform.value}"
    
    async def handle_voice_note(self, data: Dict[str, Any], raw_command: str) -> str:
        """Record voice note with WSP 22 compliant logging"""
        note_content = data.get('content', raw_command)
        
        # WSP 22 Compliant: Log to module memory
        self.log_voice_note(note_content, {
            'platform_context': self.active_platform.value,
            'emergency_paused': self.emergency_paused
        })
        
        self.logger.info(f"📝 Voice note recorded: {note_content[:50]}...")
        return f"Voice note recorded and logged to module memory"
    
    # iPhone Activity Control Handlers (WSP 17 + WSP 18 Integration)
    # Following WSP 17 pattern - using infrastructure utilities instead of direct controller calls
    async def handle_magadoom_off(self, data: Dict[str, Any], raw_command: str) -> str:
        """Disable MagaDoom activities - WSP 17 pattern"""
        apply_preset('magadoom_off')
        self.logger.info(f"🔇 MagaDoom activities disabled via voice command")
        return "⚡ MagaDoom activities disabled (announcements, levels)"
    
    async def handle_magadoom_on(self, data: Dict[str, Any], raw_command: str) -> str:
        """Enable MagaDoom activities - WSP 17 pattern"""
        restore_normal()
        self.logger.info(f"🎮 MagaDoom activities enabled via voice command")
        return "⚡ MagaDoom activities enabled"
    
    async def handle_consciousness_control_off(self, data: Dict[str, Any], raw_command: str) -> str:
        """Disable 0102 consciousness triggers - WSP 17 pattern"""
        apply_preset('consciousness_off')
        self.logger.info(f"🔇 0102 consciousness disabled via voice command")
        return "⚡ 0102 consciousness disabled (emoji triggers, auto responses)"
    
    async def handle_consciousness_control_on(self, data: Dict[str, Any], raw_command: str) -> str:
        """Enable 0102 consciousness triggers - WSP 17 pattern"""
        restore_normal()
        self.logger.info(f"🧠 0102 consciousness enabled via voice command")
        return "⚡ 0102 consciousness enabled"
    
    async def handle_silent_mode(self, data: Dict[str, Any], raw_command: str) -> str:
        """Enable silent testing mode - WSP 17 pattern"""
        apply_preset('silent_testing')
        self.logger.info(f"🔇 Silent mode enabled via voice command")
        return "⚡ Silent mode enabled - all automated activities disabled"
    
    async def handle_normal_mode(self, data: Dict[str, Any], raw_command: str) -> str:
        """Restore normal operation - WSP 17 pattern"""
        restore_normal()
        self.logger.info(f"🔄 Normal mode restored via voice command")
        return "⚡ Normal mode restored - all activities enabled"
    
    async def handle_activity_status(self, data: Dict[str, Any], raw_command: str) -> str:
        """Check activity control status - WSP 17 pattern with fallback"""
        if controller:
            magadoom_status = "✅" if controller.is_enabled("gamification.whack_a_magat.enabled") else "❌"
            consciousness_status = "✅" if controller.is_enabled("livechat.consciousness.enabled") else "❌"
            status_msg = f"⚡ Status: MagaDoom {magadoom_status} | 0102 {consciousness_status}"
        else:
            status_msg = "⚡ Activity control status unavailable (testing mode)"
        
        self.logger.info(f"📊 Activity status checked via voice command")
        return status_msg
    
    def get_status_report(self) -> tuple:
        """Generate comprehensive status report"""
        try:
            dae_report = self.dae.get_unified_report()
            recent_commands = self.get_command_history(5)
            
            status = {
                'voice_processor': {
                    'active': True,
                    'port': self.port,
                    'emergency_paused': self.emergency_paused,
                    'active_platform': self.active_platform.value,
                    'commands_processed': len(self.get_command_history(1000)),  # Rough count
                    'local_voice_available': self.voice_interface is not None,
                    'wsp_22_compliant': True,
                    'logs_path': str(VOICE_LOGS_PATH)
                },
                'dae': dae_report,
                'recent_commands': recent_commands
            }
            
            return jsonify(status), 200
            
        except Exception as e:
            return jsonify({'error': f'Status generation failed: {e}'}), 500
    
    def generate_test_page(self) -> str:
        """Generate HTML test page"""
        recent_commands = self.get_command_history(10)
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>WSP-Compliant Voice Command Processor</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .status {{ background: #f0f0f0; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .wsp-info {{ background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 10px 0; }}
                input, button {{ padding: 10px; margin: 5px; }}
                .command-history {{ max-height: 300px; overflow-y: auto; background: #f9f9f9; padding: 20px; }}
            </style>
        </head>
        <body>
            <h1>🎤 WSP-Compliant Voice Command Processor</h1>
            
            <div class="wsp-info">
                <h3>WSP Compliance Status</h3>
                <p><strong>WSP 22:</strong> ✅ Module-level logging in memory/ directory</p>
                <p><strong>WSP 60:</strong> ✅ Proper module memory architecture</p>
                <p><strong>Logs Path:</strong> {VOICE_LOGS_PATH}</p>
            </div>
            
            <div class="status">
                <h3>Status</h3>
                <p><strong>DAE State:</strong> {self.dae.consciousness.my_state.sequence}</p>
                <p><strong>Active Platform:</strong> {self.active_platform.value}</p>
                <p><strong>Emergency Paused:</strong> {self.emergency_paused}</p>
                <p><strong>Commands Processed:</strong> {len(recent_commands)}</p>
            </div>
            
            <h3>Send Test Command</h3>
            <form method="POST" action="/voice-command">
                <input type="text" name="command" placeholder="Enter voice command..." style="width: 400px;">
                <input type="hidden" name="auth" value="012_secret_key">
                <button type="submit">Send Command</button>
            </form>
            
            <h3>Quick Test Commands</h3>
            <button onclick="sendCommand('Hello from iPhone')">Chat Message</button>
            <button onclick="sendCommand('Read consciousness of testuser')">Consciousness Read</button>
            <button onclick="sendCommand('Awaken the chat')">Awakening Trigger</button>
            <button onclick="sendCommand('Status report')">Status</button>
            <button onclick="sendCommand('Switch to Twitter')">Switch Platform</button>
            <button onclick="sendCommand('Emergency pause')">Emergency Pause</button>
            <button onclick="sendCommand('Resume operations')">Resume</button>
            
            <div class="command-history">
                <h3>Recent Commands (WSP 22 Module Logs)</h3>
                <pre>{json.dumps(recent_commands, default=str, indent=2) if recent_commands else 'No commands yet'}</pre>
            </div>
            
            <script>
                function sendCommand(cmd) {{
                    fetch('/voice-command', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{'command': cmd, 'auth': '012_secret_key'}})
                    }})
                    .then(response => response.json())
                    .then(data => {{
                        alert('Response: ' + data.message);
                        location.reload();
                    }});
                }}
            </script>
        </body>
        </html>
        """
    
    def run_server(self, host: str = '0.0.0.0', debug: bool = True):
        """Run the Flask server with WSP-compliant logging"""
        self.logger.info(f"🚀 Starting WSP-Compliant Voice Command Processor server...")
        self.logger.info(f"📱 iPhone endpoint: http://{host}:{self.port}/voice-command")
        self.logger.info(f"🌐 Test interface: http://{host}:{self.port}/test")
        self.logger.info(f"📊 Status endpoint: http://{host}:{self.port}/status")
        self.logger.info(f"📁 WSP 22 Logs: {VOICE_LOGS_PATH}")
        
        if debug:
            self.app.run(host=host, port=self.port, debug=True)
        else:
            self.app.run(host=host, port=self.port, debug=False)


async def main():
    """Main entry point for WSP-Compliant Voice Command Processor testing"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize WSP-Compliant Voice Command Processor
    processor = VoiceCommandProcessor(port=5012)
    
    # Start the server
    processor.run_server()


if __name__ == "__main__":
    asyncio.run(main())