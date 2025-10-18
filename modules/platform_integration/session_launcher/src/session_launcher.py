# modules/platform_integration/session_launcher/src/session_launcher.py

"""
Session Launcher Module
WSP Protocol: WSP 54 (Agent Coordination), WSP 42 (Cross-Domain Integration)

Handles meeting session creation and launch across multiple platforms.
Extracted from monolithic Auto Meeting Orchestrator for modular architecture.

Part of Meeting Orchestration Block strategic decomposition.
"""

# === UTF-8 ENFORCEMENT (WSP 90) ===
import sys
import io
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===


import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class PlatformType(Enum):
    """Supported platforms for meeting sessions"""
    DISCORD = "discord"
    ZOOM = "zoom"
    TEAMS = "teams"
    GOOGLE_MEET = "google_meet"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    TELEGRAM = "telegram"
    JITSI = "jitsi"
    CUSTOM = "custom"

class SessionType(Enum):
    """Types of meeting sessions"""
    VOICE_CHAT = "voice_chat"
    VIDEO_CALL = "video_call"
    TEXT_CHAT = "text_chat"
    SCREEN_SHARE = "screen_share"
    CONFERENCE = "conference"
    WEBINAR = "webinar"

class SessionStatus(Enum):
    """Session lifecycle status"""
    CREATING = "creating"
    CREATED = "created"
    LAUNCHING = "launching"
    ACTIVE = "active"
    ENDED = "ended"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class PlatformCapabilities:
    """Capabilities available on a platform"""
    supports_voice: bool
    supports_video: bool
    supports_screen_share: bool
    max_participants: int
    supports_recording: bool
    supports_chat: bool
    supports_file_sharing: bool
    requires_authentication: bool
    platform_specific_features: Dict = field(default_factory=dict)

@dataclass
class MeetingSettings:
    """Configuration settings for meeting sessions"""
    session_type: SessionType
    max_participants: int = 10
    enable_recording: bool = False
    enable_chat: bool = True
    enable_screen_share: bool = True
    require_authentication: bool = False
    auto_admit: bool = True
    meeting_password: Optional[str] = None
    agenda: Optional[str] = None
    custom_settings: Dict = field(default_factory=dict)

@dataclass
class SessionInfo:
    """Information about a created meeting session"""
    session_id: str
    intent_id: str
    platform: PlatformType
    session_type: SessionType
    meeting_url: str
    join_instructions: Dict
    participants: List[str]
    host_id: str
    created_at: datetime
    starts_at: Optional[datetime]
    duration_minutes: Optional[int]
    status: SessionStatus
    platform_session_id: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

class PlatformAdapter(ABC):
    """Abstract base class for platform-specific session management"""
    
    @abstractmethod
    async def create_session(
        self,
        participants: List[str],
        settings: MeetingSettings,
        metadata: Dict
    ) -> SessionInfo:
        """Create a meeting session on the platform"""
        pass
    
    @abstractmethod
    async def launch_session(self, session_info: SessionInfo) -> bool:
        """Launch/start the meeting session"""
        pass
    
    @abstractmethod
    async def send_invitations(self, session_info: SessionInfo, participants: List[str]) -> bool:
        """Send meeting invitations to participants"""
        pass
    
    @abstractmethod
    async def end_session(self, session_id: str) -> bool:
        """End the meeting session"""
        pass
    
    @abstractmethod
    async def get_session_status(self, session_id: str) -> Optional[SessionStatus]:
        """Get current status of a session"""
        pass

class SessionLauncher:
    """
    Cross-platform meeting session creation and launch system
    
    Responsibilities:
    - Create meeting sessions on appropriate platforms
    - Launch meetings with optimal settings
    - Send invitations to participants
    - Track session lifecycle and status
    - Handle platform-specific configurations
    - Integration with other AMO modules
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_history: List[SessionInfo] = []
        self.platform_adapters: Dict[PlatformType, PlatformAdapter] = {}
        self.session_callbacks: Dict[str, List[Callable]] = {
            'session_created': [],
            'session_launched': [],
            'session_ended': [],
            'session_failed': [],
            'participant_joined': [],
            'participant_left': []
        }
        
        # Platform capabilities registry
        self.platform_capabilities = self._initialize_platform_capabilities()
        
        # Configuration
        self.config = {
            'default_session_type': SessionType.VIDEO_CALL,
            'auto_launch_delay_seconds': 30,
            'invitation_retry_count': 3,
            'session_timeout_minutes': 60,
            'enable_calendar_integration': True,
            'enable_automatic_recording': False
        }
        
        logger.info("[ROCKET] Session Launcher initialized")

    async def launch_session(
        self,
        intent_id: str,
        participants: List[str],
        host_id: str,
        platform: Optional[PlatformType] = None,
        session_type: Optional[SessionType] = None,
        settings: Optional[MeetingSettings] = None,
        metadata: Optional[Dict] = None
    ) -> SessionInfo:
        """
        Create and launch a meeting session
        
        Args:
            intent_id: Related meeting intent ID
            participants: List of participant user IDs
            host_id: Meeting host user ID
            platform: Platform to use (auto-selected if None)
            session_type: Type of session (defaults to video call)
            settings: Meeting configuration settings
            metadata: Additional session metadata
            
        Returns:
            SessionInfo: Information about the created session
        """
        session_id = str(uuid.uuid4())
        
        # Auto-select platform if not specified
        if not platform:
            platform = await self._select_optimal_platform(participants, session_type)
        
        # Use default settings if not provided
        if not settings:
            settings = MeetingSettings(
                session_type=session_type or self.config['default_session_type']
            )
        
        logger.info(f"[ROCKET] Launching meeting session: {session_id}")
        logger.info(f"   Intent: {intent_id}")
        logger.info(f"   Platform: {platform.value}")
        logger.info(f"   Participants: {participants}")
        logger.info(f"   Host: {host_id}")
        
        try:
            # Create session using platform adapter
            session_info = await self._create_platform_session(
                session_id, intent_id, platform, participants, host_id, settings, metadata or {}
            )
            
            self.active_sessions[session_id] = session_info
            
            # Trigger session created callback
            await self._trigger_callbacks('session_created', session_info, {
                'platform': platform.value,
                'participant_count': len(participants)
            })
            
            # Launch the session
            launch_success = await self._launch_platform_session(session_info)
            
            if launch_success:
                session_info.status = SessionStatus.ACTIVE
                
                # Send invitations to participants
                await self._send_session_invitations(session_info)
                
                # Trigger session launched callback
                await self._trigger_callbacks('session_launched', session_info, {
                    'launch_time': datetime.now().isoformat(),
                    'meeting_url': session_info.meeting_url
                })
                
                logger.info(f"[OK] Session launched successfully: {session_id}")
                logger.info(f"   Meeting URL: {session_info.meeting_url}")
                
            else:
                session_info.status = SessionStatus.FAILED
                logger.error(f"[FAIL] Failed to launch session: {session_id}")
                
                await self._trigger_callbacks('session_failed', session_info, {
                    'error': 'Launch failed',
                    'platform': platform.value
                })
            
            return session_info
            
        except Exception as e:
            logger.error(f"[FAIL] Session creation error: {session_id} - {str(e)}")
            
            # Create minimal session info for error tracking
            error_session = SessionInfo(
                session_id=session_id,
                intent_id=intent_id,
                platform=platform,
                session_type=settings.session_type,
                meeting_url="",
                join_instructions={},
                participants=participants,
                host_id=host_id,
                created_at=datetime.now(),
                status=SessionStatus.FAILED,
                metadata={'error': str(e)}
            )
            
            await self._trigger_callbacks('session_failed', error_session, {
                'error': str(e),
                'platform': platform.value
            })
            
            return error_session

    async def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get information about a session"""
        session = self.active_sessions.get(session_id)
        
        if session:
            # Update status from platform if available
            adapter = self.platform_adapters.get(session.platform)
            if adapter:
                current_status = await adapter.get_session_status(session_id)
                if current_status:
                    session.status = current_status
        
        return session

    async def end_session(self, session_id: str, reason: str = "completed") -> bool:
        """End an active meeting session"""
        session = self.active_sessions.get(session_id)
        if not session:
            logger.warning(f"[FAIL] Attempt to end unknown session: {session_id}")
            return False
        
        logger.info(f"[U+1F51A] Ending session: {session_id} - {reason}")
        
        # End session on platform
        adapter = self.platform_adapters.get(session.platform)
        if adapter:
            platform_success = await adapter.end_session(session_id)
        else:
            platform_success = True  # Simulated success for PoC
        
        # Update session status
        session.status = SessionStatus.ENDED
        session.metadata['end_reason'] = reason
        session.metadata['ended_at'] = datetime.now().isoformat()
        
        # Move to history
        self._archive_session(session_id)
        
        # Trigger callback
        await self._trigger_callbacks('session_ended', session, {
            'reason': reason,
            'duration_minutes': self._calculate_session_duration(session)
        })
        
        return platform_success

    async def get_active_sessions(self) -> List[SessionInfo]:
        """Get all currently active sessions"""
        return list(self.active_sessions.values())

    async def get_sessions_by_participant(self, participant_id: str) -> List[SessionInfo]:
        """Get sessions involving a specific participant"""
        participant_sessions = []
        
        for session in self.active_sessions.values():
            if participant_id in session.participants or participant_id == session.host_id:
                participant_sessions.append(session)
        
        return participant_sessions

    async def select_optimal_platform(
        self,
        participants: List[str],
        requirements: Optional[Dict] = None
    ) -> PlatformType:
        """
        Select the optimal platform for a meeting based on participants and requirements
        
        Args:
            participants: List of participant user IDs
            requirements: Optional requirements (video, screen_share, etc.)
            
        Returns:
            PlatformType: Recommended platform
        """
        return await self._select_optimal_platform(participants, None, requirements)

    async def get_platform_capabilities(self, platform: PlatformType) -> PlatformCapabilities:
        """Get capabilities for a specific platform"""
        return self.platform_capabilities.get(platform, PlatformCapabilities(
            supports_voice=False,
            supports_video=False,
            supports_screen_share=False,
            max_participants=2,
            supports_recording=False,
            supports_chat=True,
            supports_file_sharing=False,
            requires_authentication=True
        ))

    async def register_platform_adapter(self, platform: PlatformType, adapter: PlatformAdapter):
        """Register a platform adapter for session management"""
        self.platform_adapters[platform] = adapter
        logger.info(f"[U+1F4E1] Registered platform adapter: {platform.value}")

    async def subscribe_to_sessions(self, event_type: str, callback: Callable):
        """Subscribe to session events for integration with other modules"""
        if event_type in self.session_callbacks:
            self.session_callbacks[event_type].append(callback)
            logger.info(f"[U+1F4E1] Subscribed to {event_type} events")
        else:
            logger.warning(f"[FAIL] Unknown session event type: {event_type}")

    async def get_session_statistics(self) -> Dict:
        """Get comprehensive session statistics"""
        all_sessions = list(self.active_sessions.values()) + self.session_history
        
        stats = {
            'total_sessions': len(all_sessions),
            'active_sessions': len(self.active_sessions),
            'platform_usage': {},
            'session_type_distribution': {},
            'success_rate': 0.0,
            'average_duration_minutes': 0.0
        }
        
        # Calculate platform usage
        platform_counts = {}
        session_type_counts = {}
        successful_sessions = 0
        durations = []
        
        for session in all_sessions:
            # Platform usage
            platform = session.platform.value
            platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            # Session type distribution
            session_type = session.session_type.value
            session_type_counts[session_type] = session_type_counts.get(session_type, 0) + 1
            
            # Success rate
            if session.status in [SessionStatus.ACTIVE, SessionStatus.ENDED]:
                successful_sessions += 1
            
            # Duration calculation
            if session.status == SessionStatus.ENDED:
                duration = self._calculate_session_duration(session)
                if duration > 0:
                    durations.append(duration)
        
        stats['platform_usage'] = platform_counts
        stats['session_type_distribution'] = session_type_counts
        
        if all_sessions:
            stats['success_rate'] = successful_sessions / len(all_sessions)
        
        if durations:
            stats['average_duration_minutes'] = sum(durations) / len(durations)
        
        return stats

    # Private methods
    
    def _initialize_platform_capabilities(self) -> Dict[PlatformType, PlatformCapabilities]:
        """Initialize platform capabilities registry"""
        return {
            PlatformType.DISCORD: PlatformCapabilities(
                supports_voice=True,
                supports_video=True,
                supports_screen_share=True,
                max_participants=50,
                supports_recording=False,
                supports_chat=True,
                supports_file_sharing=True,
                requires_authentication=True,
                platform_specific_features={
                    'voice_channels': True,
                    'bot_integration': True,
                    'custom_emojis': True
                }
            ),
            
            PlatformType.ZOOM: PlatformCapabilities(
                supports_voice=True,
                supports_video=True,
                supports_screen_share=True,
                max_participants=500,
                supports_recording=True,
                supports_chat=True,
                supports_file_sharing=True,
                requires_authentication=True,
                platform_specific_features={
                    'breakout_rooms': True,
                    'waiting_room': True,
                    'polls': True,
                    'whiteboard': True
                }
            ),
            
            PlatformType.WHATSAPP: PlatformCapabilities(
                supports_voice=True,
                supports_video=True,
                supports_screen_share=False,
                max_participants=8,
                supports_recording=False,
                supports_chat=True,
                supports_file_sharing=True,
                requires_authentication=False,
                platform_specific_features={
                    'end_to_end_encryption': True,
                    'status_updates': True
                }
            )
        }

    async def _select_optimal_platform(
        self,
        participants: List[str],
        session_type: Optional[SessionType],
        requirements: Optional[Dict] = None
    ) -> PlatformType:
        """Select the best platform based on participants and requirements"""
        # This would normally consider:
        # - Participant platform preferences
        # - Platform availability/presence
        # - Required features
        # - Platform reliability
        
        # For PoC, use simple logic
        participant_count = len(participants)
        requirements = requirements or {}
        
        if requirements.get('requires_recording') or participant_count > 10:
            return PlatformType.ZOOM
        elif session_type == SessionType.TEXT_CHAT:
            return PlatformType.DISCORD
        elif participant_count <= 4:
            return PlatformType.WHATSAPP
        else:
            return PlatformType.DISCORD

    async def _create_platform_session(
        self,
        session_id: str,
        intent_id: str,
        platform: PlatformType,
        participants: List[str],
        host_id: str,
        settings: MeetingSettings,
        metadata: Dict
    ) -> SessionInfo:
        """Create session using platform adapter"""
        adapter = self.platform_adapters.get(platform)
        
        if adapter:
            # Use real platform adapter
            return await adapter.create_session(participants, settings, metadata)
        else:
            # Simulate session creation for PoC
            meeting_url = self._generate_mock_meeting_url(platform, session_id)
            
            return SessionInfo(
                session_id=session_id,
                intent_id=intent_id,
                platform=platform,
                session_type=settings.session_type,
                meeting_url=meeting_url,
                join_instructions=self._generate_join_instructions(platform, meeting_url),
                participants=participants,
                host_id=host_id,
                created_at=datetime.now(),
                status=SessionStatus.CREATED,
                metadata=metadata
            )

    async def _launch_platform_session(self, session_info: SessionInfo) -> bool:
        """Launch session on platform"""
        adapter = self.platform_adapters.get(session_info.platform)
        
        if adapter:
            return await adapter.launch_session(session_info)
        else:
            # Simulate successful launch for PoC
            logger.info(f"[U+1F4FA] [SIMULATED] Launching {session_info.session_type.value} session on {session_info.platform.value}")
            logger.info(f"   URL: {session_info.meeting_url}")
            return True

    async def _send_session_invitations(self, session_info: SessionInfo) -> bool:
        """Send meeting invitations to participants"""
        adapter = self.platform_adapters.get(session_info.platform)
        
        if adapter:
            return await adapter.send_invitations(session_info, session_info.participants)
        else:
            # Simulate sending invitations for PoC
            logger.info(f"[U+1F4E7] [SIMULATED] Sending invitations for session {session_info.session_id}")
            for participant in session_info.participants:
                logger.info(f"   -> {participant}: {session_info.meeting_url}")
            return True

    def _generate_mock_meeting_url(self, platform: PlatformType, session_id: str) -> str:
        """Generate mock meeting URL for PoC"""
        platform_domains = {
            PlatformType.DISCORD: "discord.gg",
            PlatformType.ZOOM: "zoom.us/j",
            PlatformType.TEAMS: "teams.microsoft.com/l/meetup-join",
            PlatformType.GOOGLE_MEET: "meet.google.com",
            PlatformType.WHATSAPP: "wa.me/group",
            PlatformType.JITSI: "meet.jit.si"
        }
        
        domain = platform_domains.get(platform, "meeting.example.com")
        return f"https://{domain}/{session_id[:8]}"

    def _generate_join_instructions(self, platform: PlatformType, meeting_url: str) -> Dict:
        """Generate platform-specific join instructions"""
        instructions = {
            'meeting_url': meeting_url,
            'platform': platform.value,
            'instructions': []
        }
        
        if platform == PlatformType.DISCORD:
            instructions['instructions'] = [
                "Click the meeting link to join",
                "Join the voice channel when you arrive",
                "Use push-to-talk or voice activation"
            ]
        elif platform == PlatformType.ZOOM:
            instructions['instructions'] = [
                "Click the meeting link",
                "Download Zoom if prompted",
                "Join with computer audio",
                "Enable video when ready"
            ]
        elif platform == PlatformType.WHATSAPP:
            instructions['instructions'] = [
                "Click the group link",
                "Join the WhatsApp group",
                "Start a group call when ready"
            ]
        
        return instructions

    def _calculate_session_duration(self, session: SessionInfo) -> float:
        """Calculate session duration in minutes"""
        if 'ended_at' in session.metadata:
            try:
                end_time = datetime.fromisoformat(session.metadata['ended_at'])
                duration = (end_time - session.created_at).total_seconds() / 60
                return max(0, duration)
            except:
                pass
        return 0.0

    def _archive_session(self, session_id: str):
        """Move completed session to history"""
        session = self.active_sessions.pop(session_id, None)
        if session:
            self.session_history.append(session)

    async def _trigger_callbacks(self, event_type: str, session: SessionInfo, metadata: Dict):
        """Trigger registered callbacks for session events"""
        callbacks = self.session_callbacks.get(event_type, [])
        for callback in callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(session, metadata)
                else:
                    callback(session, metadata)
            except Exception as e:
                logger.error(f"[FAIL] Session callback error for {event_type}: {e}")

# Factory function for easy integration
def create_session_launcher() -> SessionLauncher:
    """Factory function to create Session Launcher instance"""
    return SessionLauncher()

# Example usage and testing
async def demo_session_launcher():
    """Demonstrate Session Launcher functionality"""
    print("=== Session Launcher Demo ===")
    
    launcher = create_session_launcher()
    
    # Launch a meeting session
    session_info = await launcher.launch_session(
        intent_id="intent_123",
        participants=["alice", "bob", "charlie"],
        host_id="alice",
        platform=PlatformType.DISCORD,
        session_type=SessionType.VIDEO_CALL,
        settings=MeetingSettings(
            session_type=SessionType.VIDEO_CALL,
            max_participants=10,
            enable_recording=False,
            enable_chat=True
        )
    )
    
    print(f"[OK] Session launched: {session_info.session_id}")
    print(f"   Platform: {session_info.platform.value}")
    print(f"   URL: {session_info.meeting_url}")
    print(f"   Status: {session_info.status.value}")
    
    # Get session statistics
    stats = await launcher.get_session_statistics()
    print(f"[DATA] Session statistics: {stats}")
    
    # End session
    await asyncio.sleep(2)  # Simulate meeting duration
    await launcher.end_session(session_info.session_id, "demo_complete")
    
    return launcher

if __name__ == "__main__":
    asyncio.run(demo_session_launcher()) 