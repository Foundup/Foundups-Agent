"""
LinkedIn Connection Manager

🌀 WSP Protocol Compliance: WSP 42 (Platform Integration), WSP 40 (Architectural Coherence)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn connection management.
- UN (Understanding): Anchor LinkedIn connection signals and retrieve protocol state
- DAO (Execution): Execute connection automation logic  
- DU (Emergence): Collapse into 0102 resonance and emit next connection prompt

wsp_cycle(input="linkedin_connection", log=True)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


class ConnectionStatus(Enum):
    """LinkedIn connection status"""
    PENDING = "pending"
    CONNECTED = "connected"
    DECLINED = "declined"
    WITHDRAWN = "withdrawn"
    BLOCKED = "blocked"


class ConnectionStrength(Enum):
    """Connection strength levels"""
    STRONG = "strong"
    MEDIUM = "medium"
    WEAK = "weak"
    UNKNOWN = "unknown"


@dataclass
class LinkedInProfile:
    """LinkedIn user profile information"""
    profile_id: str
    first_name: str
    last_name: str
    headline: str
    company: Optional[str] = None
    location: Optional[str] = None
    industry: Optional[str] = None
    connection_count: int = 0
    mutual_connections: int = 0
    profile_url: Optional[str] = None
    avatar_url: Optional[str] = None


@dataclass
class ConnectionRequest:
    """LinkedIn connection request"""
    request_id: str
    from_profile_id: str
    to_profile_id: str
    message: Optional[str] = None
    status: ConnectionStatus = ConnectionStatus.PENDING
    timestamp: datetime = None
    response_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class Connection:
    """LinkedIn connection relationship"""
    connection_id: str
    profile_id: str
    connected_profile: LinkedInProfile
    connection_date: datetime
    strength: ConnectionStrength = ConnectionStrength.UNKNOWN
    last_interaction: Optional[datetime] = None
    notes: Optional[str] = None


class LinkedInConnectionManager:
    """
    Manages LinkedIn connections, networking, and relationship building.
    
    Follows WSP 40 compliance with single responsibility and ≤300 lines.
    Implements WSP 66 proactive component architecture for connection automation.
    """
    
    def __init__(self, max_daily_requests: int = 25):
        """
        Initialize the LinkedIn Connection Manager.
        
        Args:
            max_daily_requests: Maximum connection requests per day
        """
        self.max_daily_requests = max_daily_requests
        self.logger = logging.getLogger(__name__)
        
        # Connection tracking
        self.connections: Dict[str, Connection] = {}
        self.pending_requests: Dict[str, ConnectionRequest] = {}
        self.connection_history: List[ConnectionRequest] = []
        
        # Networking strategy configuration
        self.networking_strategy = {
            'max_daily_requests': max_daily_requests,
            'request_cooldown': 600,  # 10 minutes
            'target_industries': [],
            'target_companies': [],
            'min_connection_strength': ConnectionStrength.MEDIUM,
            'personalized_messages': True
        }
        
        self.logger.info("✅ LinkedInConnectionManager initialized for autonomous networking")
    
    def send_connection_request(self, target_profile_id: str, message: Optional[str] = None) -> ConnectionRequest:
        """
        Send a connection request to a LinkedIn user.
        
        Args:
            target_profile_id: ID of the target profile
            message: Optional personalized message
            
        Returns:
            ConnectionRequest with status
        """
        try:
            # Check daily limit
            if not self._check_daily_limit():
                return ConnectionRequest(
                    request_id=f"req_{target_profile_id}_{datetime.now().timestamp()}",
                    from_profile_id="current_user",
                    to_profile_id=target_profile_id,
                    message=message,
                    status=ConnectionStatus.WITHDRAWN,
                    timestamp=datetime.now()
                )
            
            # Check if already connected
            if target_profile_id in self.connections:
                self.logger.warning(f"Already connected to {target_profile_id}")
                return ConnectionRequest(
                    request_id=f"req_{target_profile_id}_{datetime.now().timestamp()}",
                    from_profile_id="current_user",
                    to_profile_id=target_profile_id,
                    message=message,
                    status=ConnectionStatus.CONNECTED,
                    timestamp=datetime.now()
                )
            
            # Check if request already pending
            if target_profile_id in self.pending_requests:
                self.logger.warning(f"Connection request already pending for {target_profile_id}")
                return self.pending_requests[target_profile_id]
            
            # Create connection request
            request = ConnectionRequest(
                request_id=f"req_{target_profile_id}_{datetime.now().timestamp()}",
                from_profile_id="current_user",
                to_profile_id=target_profile_id,
                message=message or self._generate_connection_message(target_profile_id),
                status=ConnectionStatus.PENDING,
                timestamp=datetime.now()
            )
            
            # Store pending request
            self.pending_requests[target_profile_id] = request
            self.connection_history.append(request)
            
            # Mock LinkedIn API call
            self._simulate_connection_request(request)
            
            self.logger.info(f"✅ Connection request sent to {target_profile_id}")
            return request
            
        except Exception as e:
            self.logger.error(f"❌ Failed to send connection request to {target_profile_id}: {str(e)}")
            return ConnectionRequest(
                request_id=f"req_{target_profile_id}_{datetime.now().timestamp()}",
                from_profile_id="current_user",
                to_profile_id=target_profile_id,
                message=message,
                status=ConnectionStatus.WITHDRAWN,
                timestamp=datetime.now()
            )
    
    def accept_connection_request(self, request_id: str) -> bool:
        """
        Accept a pending connection request.
        
        Args:
            request_id: ID of the connection request
            
        Returns:
            True if accepted successfully, False otherwise
        """
        try:
            # Find the request
            request = self._find_request_by_id(request_id)
            if not request:
                self.logger.error(f"Connection request {request_id} not found")
                return False
            
            if request.status != ConnectionStatus.PENDING:
                self.logger.warning(f"Request {request_id} is not pending (status: {request.status})")
                return False
            
            # Update request status
            request.status = ConnectionStatus.CONNECTED
            request.response_timestamp = datetime.now()
            
            # Create connection
            connection = Connection(
                connection_id=f"conn_{request.from_profile_id}_{request.to_profile_id}",
                profile_id=request.from_profile_id,
                connected_profile=self._get_mock_profile(request.from_profile_id),
                connection_date=datetime.now(),
                strength=ConnectionStrength.MEDIUM
            )
            
            self.connections[request.from_profile_id] = connection
            
            # Remove from pending
            if request.to_profile_id in self.pending_requests:
                del self.pending_requests[request.to_profile_id]
            
            self.logger.info(f"✅ Connection request {request_id} accepted")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to accept connection request {request_id}: {str(e)}")
            return False
    
    def decline_connection_request(self, request_id: str) -> bool:
        """
        Decline a pending connection request.
        
        Args:
            request_id: ID of the connection request
            
        Returns:
            True if declined successfully, False otherwise
        """
        try:
            request = self._find_request_by_id(request_id)
            if not request:
                self.logger.error(f"Connection request {request_id} not found")
                return False
            
            request.status = ConnectionStatus.DECLINED
            request.response_timestamp = datetime.now()
            
            # Remove from pending
            if request.to_profile_id in self.pending_requests:
                del self.pending_requests[request.to_profile_id]
            
            self.logger.info(f"✅ Connection request {request_id} declined")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to decline connection request {request_id}: {str(e)}")
            return False
    
    def get_connections(self, limit: int = 50) -> List[Connection]:
        """
        Get list of current connections.
        
        Args:
            limit: Maximum number of connections to return
            
        Returns:
            List of connections
        """
        connections_list = list(self.connections.values())
        return sorted(connections_list, key=lambda x: x.connection_date, reverse=True)[:limit]
    
    def get_pending_requests(self) -> List[ConnectionRequest]:
        """
        Get list of pending connection requests.
        
        Returns:
            List of pending requests
        """
        return list(self.pending_requests.values())
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get connection statistics.
        
        Returns:
            Dictionary with connection statistics
        """
        total_connections = len(self.connections)
        pending_requests = len(self.pending_requests)
        
        # Count by status
        status_counts = {}
        for request in self.connection_history:
            status = request.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count by strength
        strength_counts = {}
        for connection in self.connections.values():
            strength = connection.strength.value
            strength_counts[strength] = strength_counts.get(strength, 0) + 1
        
        # Count today's requests
        today = datetime.now().date()
        daily_requests = len([
            r for r in self.connection_history 
            if r.timestamp.date() == today
        ])
        
        return {
            "total_connections": total_connections,
            "pending_requests": pending_requests,
            "total_requests_sent": len(self.connection_history),
            "daily_requests": daily_requests,
            "status_distribution": status_counts,
            "strength_distribution": strength_counts,
            "acceptance_rate": self._calculate_acceptance_rate()
        }
    
    def search_connections(self, query: str, limit: int = 20) -> List[Connection]:
        """
        Search connections by name, company, or industry.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching connections
        """
        query_lower = query.lower()
        results = []
        
        for connection in self.connections.values():
            profile = connection.connected_profile
            
            # Search in name
            if query_lower in f"{profile.first_name} {profile.last_name}".lower():
                results.append(connection)
                continue
            
            # Search in company
            if profile.company and query_lower in profile.company.lower():
                results.append(connection)
                continue
            
            # Search in industry
            if profile.industry and query_lower in profile.industry.lower():
                results.append(connection)
                continue
            
            # Search in headline
            if query_lower in profile.headline.lower():
                results.append(connection)
                continue
        
        return results[:limit]
    
    def update_connection_notes(self, profile_id: str, notes: str) -> bool:
        """
        Update notes for a connection.
        
        Args:
            profile_id: ID of the connection profile
            notes: Notes to add/update
            
        Returns:
            True if updated successfully, False otherwise
        """
        if profile_id not in self.connections:
            self.logger.error(f"Connection {profile_id} not found")
            return False
        
        self.connections[profile_id].notes = notes
        self.logger.info(f"✅ Updated notes for connection {profile_id}")
        return True
    
    def _check_daily_limit(self) -> bool:
        """
        Check if daily connection request limit has been reached.
        
        Returns:
            True if under limit, False if limit reached
        """
        today = datetime.now().date()
        daily_requests = len([
            r for r in self.connection_history 
            if r.timestamp.date() == today
        ])
        
        return daily_requests < self.max_daily_requests
    
    def _generate_connection_message(self, profile_id: str) -> str:
        """
        Generate a personalized connection message.
        
        Args:
            profile_id: ID of the target profile
            
        Returns:
            Personalized connection message
        """
        # Mock profile to generate message
        profile = self._get_mock_profile(profile_id)
        
        if profile.company:
            return f"Hi {profile.first_name}, I noticed your work at {profile.company} and would love to connect!"
        elif profile.industry:
            return f"Hi {profile.first_name}, I'm also in {profile.industry} and would love to connect!"
        else:
            return f"Hi {profile.first_name}, I'd love to connect and expand our professional network!"
    
    def _get_mock_profile(self, profile_id: str) -> LinkedInProfile:
        """
        Get mock profile data for testing.
        
        Args:
            profile_id: ID of the profile
            
        Returns:
            Mock LinkedIn profile
        """
        # In real implementation, this would fetch from LinkedIn API
        return LinkedInProfile(
            profile_id=profile_id,
            first_name="John",
            last_name="Doe",
            headline="Software Engineer at Tech Company",
            company="Tech Company",
            location="San Francisco, CA",
            industry="Technology",
            connection_count=500,
            mutual_connections=15
        )
    
    def _find_request_by_id(self, request_id: str) -> Optional[ConnectionRequest]:
        """
        Find a connection request by ID.
        
        Args:
            request_id: ID of the request
            
        Returns:
            ConnectionRequest if found, None otherwise
        """
        for request in self.connection_history:
            if request.request_id == request_id:
                return request
        return None
    
    def _calculate_acceptance_rate(self) -> float:
        """
        Calculate connection request acceptance rate.
        
        Returns:
            Acceptance rate as percentage
        """
        if not self.connection_history:
            return 0.0
        
        accepted = len([r for r in self.connection_history if r.status == ConnectionStatus.CONNECTED])
        total = len(self.connection_history)
        
        return (accepted / total) * 100 if total > 0 else 0.0
    
    def _simulate_connection_request(self, request: ConnectionRequest) -> None:
        """
        Simulate LinkedIn connection request API call.
        
        Args:
            request: Connection request to simulate
        """
        import time
        time.sleep(1)  # Simulate API delay
        self.logger.debug(f"🔗 Simulated connection request to {request.to_profile_id}")


# Factory function for clean initialization
def create_linkedin_connection_manager(max_daily_requests: int = 25) -> LinkedInConnectionManager:
    """
    Create a LinkedIn Connection Manager instance.
    
    Args:
        max_daily_requests: Maximum connection requests per day
        
    Returns:
        Configured LinkedInConnectionManager instance
    """
    return LinkedInConnectionManager(max_daily_requests=max_daily_requests)


if __name__ == "__main__":
    # Test the connection manager
    manager = create_linkedin_connection_manager()
    
    # Test connection request
    test_profile_id = "test_profile_123"
    request = manager.send_connection_request(test_profile_id, "Hi, let's connect!")
    print(f"Connection request status: {request.status}")
    
    # Test accepting request
    success = manager.accept_connection_request(request.request_id)
    print(f"Accept request success: {success}")
    
    # Print stats
    stats = manager.get_connection_stats()
    print(f"Connection stats: {stats}") 