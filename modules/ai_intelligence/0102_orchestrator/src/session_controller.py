"""
Session Controller - Meeting Session Management for 0102 Orchestrator

Handles all aspects of meeting session lifecycle:
- Auto-launch meetings when conditions are met
- Session state management and monitoring
- Platform-specific session creation
- Meeting coordination across AMO ecosystem
- Session completion and cleanup

Part of the 0102 unified AI companion layer.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SessionStatus(Enum):
    """Status states for meeting sessions"""
    PENDING = "pending"           # Session scheduled but not started
    LAUNCHING = "launching"       # Currently being launched
    ACTIVE = "active"            # Session in progress
    COMPLETED = "completed"      # Session finished
    FAILED = "failed"           # Launch or session failed
    CANCELLED = "cancelled"     # Cancelled before start


class LaunchResult(Enum):
    """Results of session launch attempts"""
    SUCCESS = "success"
    FAILED_PLATFORM = "failed_platform"
    FAILED_PARTICIPANTS = "failed_participants"
    FAILED_PERMISSIONS = "failed_permissions"
    FAILED_TIMEOUT = "failed_timeout"


@dataclass
class SessionInfo:
    """Information about a meeting session"""
    session_id: str
    intent_id: str
    participants: List[str]
    platform: str
    launch_time: datetime
    expected_duration: int  # minutes
    status: SessionStatus
    meeting_link: Optional[str] = None
    platform_session_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class LaunchRequest:
    """Request to launch a meeting session"""
    intent_id: str
    participants: List[str]
    platform: str
    context: Dict[str, Any]
    priority: str = "MEDIUM"
    auto_invite: bool = True
    timeout_seconds: int = 30


class SessionController:
    """
    Manages meeting session lifecycle for 0102 orchestrator.
    
    Handles auto-launch, state management, and coordination
    with platform-specific session launchers.
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_history: List[SessionInfo] = []
        self.launch_callbacks: Dict[str, Callable] = {}
        self.platform_launchers: Dict[str, Callable] = {}
        
        # Register default platform launchers
        self._register_default_launchers()
        
        logger.info("SessionController initialized - Ready to manage meeting sessions")
    
    async def launch_session(self, request: LaunchRequest) -> SessionInfo:
        """
        Launch a new meeting session based on launch request.
        
        This is the main entry point for creating and starting meetings.
        """
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.active_sessions)}"
        
        session_info = SessionInfo(
            session_id=session_id,
            intent_id=request.intent_id,
            participants=request.participants,
            platform=request.platform,
            launch_time=datetime.now(),
            expected_duration=request.context.get('duration_minutes', 30),
            status=SessionStatus.LAUNCHING,
            metadata={
                'priority': request.priority,
                'auto_invite': request.auto_invite,
                'launch_context': request.context
            }
        )
        
        self.active_sessions[session_id] = session_info
        
        logger.info(f"Launching session {session_id} on {request.platform} with {len(request.participants)} participants")
        
        try:
            # Launch the platform-specific session
            launch_result = await self._launch_platform_session(session_info, request)
            
            if launch_result == LaunchResult.SUCCESS:
                session_info.status = SessionStatus.ACTIVE
                logger.info(f"Session {session_id} launched successfully")
                
                # Start session monitoring
                asyncio.create_task(self._monitor_session(session_info))
                
                # Send invitations if requested
                if request.auto_invite:
                    await self._send_session_invitations(session_info)
                    
            else:
                session_info.status = SessionStatus.FAILED
                session_info.metadata['failure_reason'] = launch_result.value
                logger.error(f"Session {session_id} launch failed: {launch_result.value}")
                
        except Exception as e:
            session_info.status = SessionStatus.FAILED
            session_info.metadata['error'] = str(e)
            logger.error(f"Session {session_id} launch error: {e}")
        
        return session_info
    
    async def get_session_status(self, session_id: str) -> Optional[SessionInfo]:
        """Get current status of a session"""
        return self.active_sessions.get(session_id)
    
    async def list_active_sessions(self, user_id: Optional[str] = None) -> List[SessionInfo]:
        """List all active sessions, optionally filtered by user"""
        sessions = list(self.active_sessions.values())
        
        if user_id:
            sessions = [s for s in sessions if user_id in s.participants]
            
        return [s for s in sessions if s.status == SessionStatus.ACTIVE]
    
    async def end_session(self, session_id: str, reason: str = "completed") -> bool:
        """End an active session"""
        if session_id not in self.active_sessions:
            return False
            
        session_info = self.active_sessions[session_id]
        session_info.status = SessionStatus.COMPLETED
        session_info.metadata['end_reason'] = reason
        session_info.metadata['end_time'] = datetime.now()
        
        # Move to history
        self.session_history.append(session_info)
        del self.active_sessions[session_id]
        
        logger.info(f"Session {session_id} ended: {reason}")
        return True
    
    async def cancel_session(self, session_id: str, reason: str = "cancelled") -> bool:
        """Cancel a pending or active session"""
        if session_id not in self.active_sessions:
            return False
            
        session_info = self.active_sessions[session_id]
        session_info.status = SessionStatus.CANCELLED
        session_info.metadata['cancel_reason'] = reason
        session_info.metadata['cancel_time'] = datetime.now()
        
        # Cleanup platform-specific session if needed
        await self._cleanup_platform_session(session_info)
        
        # Move to history
        self.session_history.append(session_info)
        del self.active_sessions[session_id]
        
        logger.info(f"Session {session_id} cancelled: {reason}")
        return True
    
    def register_platform_launcher(self, platform: str, launcher: Callable):
        """Register a platform-specific session launcher"""
        self.platform_launchers[platform] = launcher
        logger.info(f"Registered platform launcher for {platform}")
    
    def register_launch_callback(self, event: str, callback: Callable):
        """Register callback for launch events"""
        self.launch_callbacks[event] = callback
        logger.info(f"Registered launch callback for {event}")
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get statistics about session usage"""
        total_sessions = len(self.session_history) + len(self.active_sessions)
        active_count = len(self.active_sessions)
        
        # Platform usage
        platform_usage = {}
        for session in self.session_history + list(self.active_sessions.values()):
            platform = session.platform
            platform_usage[platform] = platform_usage.get(platform, 0) + 1
        
        # Success rate
        completed_sessions = [s for s in self.session_history if s.status == SessionStatus.COMPLETED]
        success_rate = len(completed_sessions) / max(1, len(self.session_history)) * 100
        
        return {
            'total_sessions': total_sessions,
            'active_sessions': active_count,
            'completed_sessions': len(completed_sessions),
            'success_rate': round(success_rate, 2),
            'platform_usage': platform_usage,
            'average_duration': self._calculate_average_duration()
        }
    
    # Internal implementation methods
    
    async def _launch_platform_session(self, session_info: SessionInfo, request: LaunchRequest) -> LaunchResult:
        """Launch session on specific platform"""
        platform = session_info.platform
        
        if platform not in self.platform_launchers:
            logger.warning(f"No launcher registered for platform: {platform}")
            return await self._default_platform_launcher(session_info, request)
        
        try:
            launcher = self.platform_launchers[platform]
            result = await launcher(session_info, request)
            return result
        except Exception as e:
            logger.error(f"Platform launcher error for {platform}: {e}")
            return LaunchResult.FAILED_PLATFORM
    
    async def _default_platform_launcher(self, session_info: SessionInfo, request: LaunchRequest) -> LaunchResult:
        """Default implementation for platform session launch (PoC)"""
        # Simulate platform session creation
        await asyncio.sleep(1)  # Simulate API call delay
        
        # Generate mock meeting link
        session_info.meeting_link = f"https://{session_info.platform}.example.com/meeting/{session_info.session_id}"
        session_info.platform_session_id = f"{session_info.platform}_{session_info.session_id}"
        
        logger.info(f"Created {session_info.platform} session: {session_info.meeting_link}")
        return LaunchResult.SUCCESS
    
    async def _send_session_invitations(self, session_info: SessionInfo):
        """Send meeting invitations to participants"""
        for participant in session_info.participants:
            invitation_message = self._generate_invitation_message(session_info, participant)
            logger.info(f"Sent invitation to {participant}: {invitation_message}")
            
        # In real implementation, this would integrate with notification system
    
    def _generate_invitation_message(self, session_info: SessionInfo, participant: str) -> str:
        """Generate invitation message for participant"""
        return f"""
[HANDSHAKE] Meeting Starting Now!

Platform: {session_info.platform.title()}
Meeting Link: {session_info.meeting_link or 'Generating...'}
Duration: {session_info.expected_duration} minutes
Session ID: {session_info.session_id}

Click the link to join!
        """.strip()
    
    async def _monitor_session(self, session_info: SessionInfo):
        """Monitor active session for completion or issues"""
        start_time = datetime.now()
        expected_end = start_time + timedelta(minutes=session_info.expected_duration)
        
        # Monitor until expected end time
        while datetime.now() < expected_end and session_info.status == SessionStatus.ACTIVE:
            await asyncio.sleep(30)  # Check every 30 seconds
            
            # In real implementation: Check platform-specific session status
            
        # Auto-end session if still active past expected duration
        if session_info.status == SessionStatus.ACTIVE:
            await self.end_session(session_info.session_id, "auto_timeout")
    
    async def _cleanup_platform_session(self, session_info: SessionInfo):
        """Cleanup platform-specific session resources"""
        platform = session_info.platform
        
        if session_info.platform_session_id:
            logger.info(f"Cleaning up {platform} session: {session_info.platform_session_id}")
            # In real implementation: Call platform-specific cleanup APIs
    
    def _register_default_launchers(self):
        """Register default platform launchers for common platforms"""
        # Default launchers that will be replaced by real implementations
        self.platform_launchers.update({
            'discord': self._default_platform_launcher,
            'zoom': self._default_platform_launcher,
            'whatsapp': self._default_platform_launcher,
            'teams': self._default_platform_launcher,
            'slack': self._default_platform_launcher
        })
    
    def _calculate_average_duration(self) -> float:
        """Calculate average session duration from history"""
        completed_sessions = [s for s in self.session_history if s.status == SessionStatus.COMPLETED]
        
        if not completed_sessions:
            return 0.0
            
        total_duration = sum(s.expected_duration for s in completed_sessions)
        return round(total_duration / len(completed_sessions), 2)


# Demo and testing functions
async def demo_session_controller():
    """Demonstrate session controller functionality"""
    controller = SessionController()
    
    print("=== 0102 Session Controller Demo ===")
    
    # Create launch request
    launch_request = LaunchRequest(
        intent_id="intent_123",
        participants=["alice", "bob"],
        platform="discord",
        context={
            'purpose': 'Demo meeting',
            'duration_minutes': 30,
            'priority': 'HIGH'
        }
    )
    
    # Launch session
    session = await controller.launch_session(launch_request)
    print(f"[OK] Session launched: {session.session_id}")
    print(f"[PIN] Platform: {session.platform}")
    print(f"[LINK] Link: {session.meeting_link}")
    print(f"[U+1F465] Participants: {', '.join(session.participants)}")
    
    # Check session status
    await asyncio.sleep(2)
    status = await controller.get_session_status(session.session_id)
    print(f"[DATA] Status: {status.status.value}")
    
    # Get statistics
    stats = await controller.get_session_statistics()
    print(f"[UP] Statistics: {stats}")
    
    # End session
    await controller.end_session(session.session_id, "demo_completed")
    print(f"[U+1F3C1] Session ended")
    
    return controller


if __name__ == "__main__":
    # Run demo
    asyncio.run(demo_session_controller()) 