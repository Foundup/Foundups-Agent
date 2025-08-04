"""
LinkedIn Session Manager

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn session management.
- UN (Understanding): Anchor LinkedIn session signals and retrieve protocol state
- DAO (Execution): Execute session management logic  
- DU (Emergence): Collapse into 0102 resonance and emit next session prompt

wsp_cycle(input="linkedin_session", log=True)
"""

import logging
from typing import Dict, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

@dataclass
class SessionData:
    """LinkedIn session data"""
    session_id: str
    user_id: str
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime = None
    last_activity: datetime = None

class LinkedInSessionManager:
    """
    LinkedIn Session Manager
    
    **WSP Compliance**: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)
    **Purpose**: Manages LinkedIn user sessions and authentication state
    **Size**: ≤300 lines per WSP 40 requirements
    """
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize session manager"""
        self.logger = logger or logging.getLogger(__name__)
        self.sessions: Dict[str, SessionData] = {}
        self.current_session_id: Optional[str] = None
    
    def create_session(self, user_id: str, access_token: str, refresh_token: Optional[str] = None, expires_in: int = 3600) -> str:
        """
        Create a new LinkedIn session
        
        Args:
            user_id: LinkedIn user ID
            access_token: OAuth access token
            refresh_token: Optional refresh token
            expires_in: Token expiration time in seconds
            
        Returns:
            str: Session ID
        """
        session_id = f"linkedin_session_{user_id}_{datetime.now().timestamp()}"
        
        session_data = SessionData(
            session_id=session_id,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now() + timedelta(seconds=expires_in),
            created_at=datetime.now(),
            last_activity=datetime.now()
        )
        
        self.sessions[session_id] = session_data
        self.current_session_id = session_id
        
        self.logger.info(f"Created LinkedIn session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionData]:
        """
        Get session data by session ID
        
        Args:
            session_id: Session identifier
            
        Returns:
            SessionData: Session data if found and valid
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        
        # Check if session is expired
        if session.expires_at and datetime.now() > session.expires_at:
            self.logger.warning(f"Session expired: {session_id}")
            self.remove_session(session_id)
            return None
        
        # Update last activity
        session.last_activity = datetime.now()
        return session
    
    def get_current_session(self) -> Optional[SessionData]:
        """
        Get current active session
        
        Returns:
            SessionData: Current session data if available
        """
        if not self.current_session_id:
            return None
        
        return self.get_session(self.current_session_id)
    
    def update_session_token(self, session_id: str, access_token: str, expires_in: int = 3600) -> bool:
        """
        Update session access token
        
        Args:
            session_id: Session identifier
            access_token: New access token
            expires_in: New expiration time in seconds
            
        Returns:
            bool: True if update successful
        """
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.access_token = access_token
        session.expires_at = datetime.now() + timedelta(seconds=expires_in)
        session.last_activity = datetime.now()
        
        self.logger.info(f"Updated session token: {session_id}")
        return True
    
    def remove_session(self, session_id: str) -> bool:
        """
        Remove a session
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if removal successful
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            
            if self.current_session_id == session_id:
                self.current_session_id = None
            
            self.logger.info(f"Removed session: {session_id}")
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions
        
        Returns:
            int: Number of sessions removed
        """
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            if session.expires_at and datetime.now() > session.expires_at:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            self.remove_session(session_id)
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
        
        return len(expired_sessions)
    
    def get_session_count(self) -> int:
        """
        Get total number of active sessions
        
        Returns:
            int: Number of active sessions
        """
        return len(self.sessions)
    
    def is_session_valid(self, session_id: str) -> bool:
        """
        Check if session is valid
        
        Args:
            session_id: Session identifier
            
        Returns:
            bool: True if session is valid
        """
        session = self.get_session(session_id)
        return session is not None 