#!/usr/bin/env python3
"""
Multi-Agent Management System for FoundUps Agent
Supports multiple agents from different accounts with dynamic identity management.
Handles same-account scenarios to prevent identity conflicts.
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../../..')))

from utils.oauth_manager import get_authenticated_service, get_authenticated_service_with_fallback

logger = logging.getLogger(__name__)

@dataclass
class AgentIdentity:
    """Represents an agent's identity and capabilities."""
    agent_id: str
    channel_id: str
    channel_name: str
    credential_set: str
    account_email: Optional[str] = None
    last_active: Optional[str] = None
    status: str = "available"  # available, active, cooldown, error, same_account_conflict
    capabilities: List[str] = None
    conflict_reason: Optional[str] = None
    admin_users: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["chat_monitoring", "emoji_response", "banter_generation"]

@dataclass
class AgentSession:
    """Represents an active agent session."""
    agent_id: str
    stream_id: str
    stream_title: str
    start_time: str
    user_channel_id: Optional[str] = None
    message_count: int = 0
    response_count: int = 0
    last_activity: Optional[str] = None
    
    def __post_init__(self):
        if self.last_activity is None:
            self.last_activity = self.start_time

class SameAccountDetector:
    """Detects and manages same-account conflicts between user and agent."""
    
    def __init__(self):
        self.conflict_log_file = "memory/same_account_conflicts.json"
        self.conflicts: List[Dict[str, Any]] = []
        self._load_conflicts()
    
    def _load_conflicts(self):
        """Load conflict history from file."""
        if os.path.exists(self.conflict_log_file):
            try:
                with open(self.conflict_log_file, 'r') as f:
                    self.conflicts = json.load(f)
            except Exception as e:
                logger.error(f"Error loading conflict log: {e}")
                self.conflicts = []
    
    def _save_conflicts(self):
        """Save conflict history to file."""
        try:
            os.makedirs(os.path.dirname(self.conflict_log_file), exist_ok=True)
            with open(self.conflict_log_file, 'w') as f:
                json.dump(self.conflicts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving conflict log: {e}")
    
    def detect_user_identity(self, user_channel_id: str) -> Dict[str, Any]:
        """
        Detect user identity information.
        
        Args:
            user_channel_id: The user's channel ID
            
        Returns:
            Dictionary with user identity information
        """
        user_info = {
            "channel_id": user_channel_id,
            "detection_method": "stream_ownership",
            "confidence": "high",
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"👤 User identity detected: {user_channel_id[:8]}...{user_channel_id[-4:]}")
        return user_info
    
    def check_same_account_conflict(self, agent: AgentIdentity, user_channel_id: str) -> bool:
        """
        Check if agent and user are on the same account.
        
        Args:
            agent: Agent identity to check
            user_channel_id: User's channel ID
            
        Returns:
            True if conflict detected, False otherwise
        """
        is_conflict = agent.channel_id == user_channel_id
        
        if is_conflict:
            conflict_info = {
                "agent_id": agent.agent_id,
                "agent_channel_id": agent.channel_id,
                "user_channel_id": user_channel_id,
                "agent_name": agent.channel_name,
                "credential_set": agent.credential_set,
                "detected_at": datetime.now().isoformat(),
                "conflict_type": "same_channel_id"
            }
            
            self.conflicts.append(conflict_info)
            self._save_conflicts()
            
            logger.warning(f"🚨 Same-account conflict detected!")
            logger.warning(f"   Agent: {agent.channel_name} ({agent.channel_id[:8]}...{agent.channel_id[-4:]})")
            logger.warning(f"   User:  {user_channel_id[:8]}...{user_channel_id[-4:]}")
            
        return is_conflict

class AgentRegistry:
    """Manages registration and discovery of available agents."""
    
    def __init__(self):
        self.registry_file = "memory/agent_registry.json"
        self.agents: Dict[str, AgentIdentity] = {}
        self.active_sessions: Dict[str, AgentSession] = {}
        self.conflict_detector = SameAccountDetector()
        self._load_registry()
        
    def _load_registry(self):
        """Load agent registry from file."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    
                # Load agents
                for agent_data in data.get('agents', []):
                    agent = AgentIdentity(**agent_data)
                    self.agents[agent.agent_id] = agent
                    
                # Load active sessions
                for session_data in data.get('active_sessions', []):
                    session = AgentSession(**session_data)
                    self.active_sessions[session.agent_id] = session
                    
                logger.info(f"📋 Loaded {len(self.agents)} agents and {len(self.active_sessions)} active sessions")
            except Exception as e:
                logger.error(f"Error loading agent registry: {e}")
                self._create_empty_registry()
        else:
            self._create_empty_registry()
    
    def _create_empty_registry(self):
        """Create empty registry structure."""
        self.agents = {}
        self.active_sessions = {}
        self._save_registry()
    
    def _save_registry(self):
        """Save agent registry to file."""
        try:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            
            data = {
                'agents': [asdict(agent) for agent in self.agents.values()],
                'active_sessions': [asdict(session) for session in self.active_sessions.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving agent registry: {e}")
    
    def discover_agents(self, user_channel_id: Optional[str] = None) -> List[AgentIdentity]:
        """
        Discover all available agents by testing credential sets.
        
        Args:
            user_channel_id: User's channel ID to check for conflicts
            
        Returns:
            List of discovered agents
        """
        logger.info("🔍 Discovering available agents...")
        discovered_agents = []
        
        # Test each credential set
        credential_sets = ["set_1", "set_2", "set_3", "set_4"]
        
        for i, cred_set in enumerate(credential_sets):
            try:
                logger.info(f"🔑 Testing credential {cred_set}...")
                
                # Try to authenticate with this credential set
                auth_result = get_authenticated_service(i)
                if not auth_result:
                    logger.warning(f"❌ Failed to authenticate with {cred_set}")
                    continue
                
                service, credentials = auth_result
                
                # Get channel information
                request = service.channels().list(part='snippet', mine=True)
                response = request.execute()
                
                if response.get('items'):
                    channel_info = response['items'][0]
                    channel_id = channel_info['id']
                    channel_name = channel_info['snippet']['title']
                    
                    # Create agent identity
                    agent_id = f"agent_{cred_set}_{channel_name.lower().replace(' ', '_')}"
                    agent = AgentIdentity(
                        agent_id=agent_id,
                        channel_id=channel_id,
                        channel_name=channel_name,
                        credential_set=cred_set,
                        last_active=datetime.now().isoformat()
                    )
                    
                    # Check for same-account conflicts
                    if user_channel_id and self.conflict_detector.check_same_account_conflict(agent, user_channel_id):
                        agent.status = "same_account_conflict"
                        agent.conflict_reason = f"Same channel ID as user: {user_channel_id[:8]}...{user_channel_id[-4:]}"
                        logger.warning(f"⚠️ {channel_name} marked as conflicted (same account as user)")
                    else:
                        agent.status = "available"
                        logger.info(f"✅ {channel_name} available for use")
                    
                    discovered_agents.append(agent)
                    self.agents[agent_id] = agent
                    
                else:
                    logger.warning(f"❌ No channel information found for {cred_set}")
                    
            except Exception as e:
                logger.error(f"❌ Error testing {cred_set}: {e}")
                continue
        
        self._save_registry()
        logger.info(f"🎯 Discovery complete: {len(discovered_agents)} agents found")
        
        return discovered_agents
    
    def get_available_agents(self, exclude_conflicts: bool = True) -> List[AgentIdentity]:
        """
        Get list of available agents.
        
        Args:
            exclude_conflicts: Whether to exclude same-account conflicts
            
        Returns:
            List of available agents
        """
        available = []
        for agent in self.agents.values():
            # If excluding conflicts, skip conflicted agents
            if exclude_conflicts and agent.status == "same_account_conflict":
                continue
            
            # If not excluding conflicts, include all agents regardless of status
            if not exclude_conflicts:
                available.append(agent)
            else:
                # When excluding conflicts, only include genuinely available agents
                if agent.status in ["available", "cooldown"]:
                    available.append(agent)
        return available
    
    def get_conflicted_agents(self) -> List[AgentIdentity]:
        """Get list of agents with same-account conflicts."""
        return [agent for agent in self.agents.values() if agent.status == "same_account_conflict"]
    
    def get_agent_by_channel_name(self, channel_name: str) -> Optional[AgentIdentity]:
        """Find agent by channel name."""
        for agent in self.agents.values():
            if agent.channel_name.lower() == channel_name.lower():
                return agent
        return None
    
    def start_session(self, agent_id: str, stream_id: str, stream_title: str, user_channel_id: Optional[str] = None) -> bool:
        """
        Start a session for an agent.
        
        Args:
            agent_id: Agent identifier
            stream_id: Stream identifier
            stream_title: Stream title
            user_channel_id: User's channel ID for conflict checking
            
        Returns:
            True if session started successfully
        """
        if agent_id not in self.agents:
            logger.error(f"❌ Agent {agent_id} not found")
            return False
        
        agent = self.agents[agent_id]
        
        # Check for same-account conflicts
        if user_channel_id and agent.channel_id == user_channel_id:
            logger.error(f"🚨 Cannot start session: Same-account conflict detected!")
            logger.error(f"   Agent {agent.channel_name} shares channel ID with user")
            agent.status = "same_account_conflict"
            agent.conflict_reason = f"Same channel ID as user: {user_channel_id[:8]}...{user_channel_id[-4:]}"
            self._save_registry()
            return False
        
        # Create session
        session = AgentSession(
            agent_id=agent_id,
            stream_id=stream_id,
            stream_title=stream_title,
            start_time=datetime.now().isoformat(),
            user_channel_id=user_channel_id
        )
        
        self.active_sessions[agent_id] = session
        agent.status = "active"
        agent.last_active = datetime.now().isoformat()
        
        self._save_registry()
        logger.info(f"🚀 Session started for {agent.channel_name}")
        
        return True
    
    def end_session(self, agent_id: str):
        """End a session for an agent."""
        if agent_id in self.active_sessions:
            del self.active_sessions[agent_id]
            
        if agent_id in self.agents:
            self.agents[agent_id].status = "available"
            
        self._save_registry()
        logger.info(f"🛑 Session ended for agent {agent_id}")

class MultiAgentManager:
    """Manages multiple agents and their coordination with same-account conflict prevention."""
    
    def __init__(self):
        self.registry = AgentRegistry()
        self.current_agent: Optional[AgentIdentity] = None
        self.user_channel_id: Optional[str] = None
        self.coordination_rules = {
            "max_concurrent_agents": 3,
            "min_response_interval": 30,  # seconds between different agents
            "agent_rotation_enabled": True,
            "prefer_channel_affinity": True,
            "block_same_account": True
        }
    
    def initialize(self, user_channel_id: Optional[str] = None) -> bool:
        """
        Initialize the multi-agent system.
        
        Args:
            user_channel_id: User's channel ID for conflict detection
            
        Returns:
            True if initialization successful
        """
        logger.info("🤖 Initializing Multi-Agent Management System...")
        
        self.user_channel_id = user_channel_id
        if user_channel_id:
            logger.info(f"👤 User channel ID: {user_channel_id[:8]}...{user_channel_id[-4:]}")
        
        # Discover available agents
        agents = self.registry.discover_agents(user_channel_id)
        
        if not agents:
            logger.error("❌ No agents discovered! Check credential configuration.")
            return False
        
        available_agents = self.registry.get_available_agents()
        conflicted_agents = self.registry.get_conflicted_agents()
        
        logger.info(f"✅ Multi-agent system initialized with {len(agents)} agents")
        logger.info(f"   Available for use: {len(available_agents)}")
        if conflicted_agents:
            logger.warning(f"   Same-account conflicts: {len(conflicted_agents)}")
        
        self._print_agent_summary()
        return True
    
    def _print_agent_summary(self):
        """Print a summary of all discovered agents."""
        logger.info("📊 AGENT SUMMARY:")
        for agent in self.registry.agents.values():
            status_emoji = {
                "available": "✅",
                "active": "🔄",
                "same_account_conflict": "⚠️",
                "cooldown": "⏳",
                "error": "❌"
            }.get(agent.status, "❓")
            
            logger.info(f"   {status_emoji} {agent.channel_name} ({agent.credential_set}) - {agent.status}")
            if agent.conflict_reason:
                logger.info(f"      └─ {agent.conflict_reason}")
    
    def select_agent(self, preferred_name: Optional[str] = None, allow_conflicts: bool = False) -> Optional[AgentIdentity]:
        """
        Select an agent for use.
        
        Args:
            preferred_name: Preferred agent channel name
            allow_conflicts: Whether to allow same-account conflicts
            
        Returns:
            Selected agent or None if none available
        """
        available_agents = self.registry.get_available_agents(exclude_conflicts=not allow_conflicts)
        
        if not available_agents:
            logger.warning("❌ No available agents found")
            return None
        
        # Try to find preferred agent with working credentials
        if preferred_name:
            preferred_agents = [agent for agent in available_agents 
                             if agent.channel_name.lower() == preferred_name.lower()]
            
            if preferred_agents:
                # Test each preferred agent to find one with working credentials
                for agent in preferred_agents:
                    if agent.status == "same_account_conflict" and not allow_conflicts:
                        logger.warning(f"⚠️ {preferred_name} ({agent.credential_set}) has same-account conflict, skipping")
                        continue
                    
                    # Test if this agent's credentials are working
                    credential_index = int(agent.credential_set.split('_')[1]) - 1
                    try:
                        from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_authenticated_service
                        auth_result = get_authenticated_service(credential_index)
                        if auth_result:
                            logger.info(f"🎯 Selected preferred agent: {agent.channel_name} ({agent.credential_set})")
                            return agent
                        else:
                            logger.warning(f"⚠️ {preferred_name} ({agent.credential_set}) credentials not working, trying next")
                    except Exception as e:
                        logger.warning(f"⚠️ {preferred_name} ({agent.credential_set}) failed credential test: {e}")
                        continue
                
                logger.warning(f"⚠️ No working credentials found for {preferred_name}, selecting alternative")
        
        # Select first available agent with working credentials
        for agent in available_agents:
            credential_index = int(agent.credential_set.split('_')[1]) - 1
            try:
                from modules.infrastructure.oauth_management.oauth_management.src.oauth_manager import get_authenticated_service
                auth_result = get_authenticated_service(credential_index)
                if auth_result:
                    logger.info(f"🤖 Auto-selected agent: {agent.channel_name} ({agent.credential_set})")
                    return agent
                else:
                    logger.warning(f"⚠️ {agent.channel_name} ({agent.credential_set}) credentials not working, trying next")
            except Exception as e:
                logger.warning(f"⚠️ {agent.channel_name} ({agent.credential_set}) failed credential test: {e}")
                continue
        
        logger.error("❌ No agents with working credentials found")
        return None
    
    def start_agent_session(self, agent: AgentIdentity, stream_id: str, stream_title: str) -> bool:
        """Start a session with the selected agent."""
        success = self.registry.start_session(agent.agent_id, stream_id, stream_title, self.user_channel_id)
        if success:
            self.current_agent = agent
            logger.info(f"🚀 Agent session started: {agent.channel_name}")
        return success
    
    def end_current_session(self):
        """End the current agent session."""
        if self.current_agent:
            self.registry.end_session(self.current_agent.agent_id)
            logger.info(f"🛑 Ended session for {self.current_agent.channel_name}")
            self.current_agent = None
    
    def update_activity(self, message_count: int = 0, response_count: int = 0):
        """Update activity metrics for current session."""
        if self.current_agent and self.current_agent.agent_id in self.registry.active_sessions:
            session = self.registry.active_sessions[self.current_agent.agent_id]
            session.message_count += message_count
            session.response_count += response_count
            session.last_activity = datetime.now().isoformat()
            self.registry._save_registry()
    
    def get_bot_identity_list(self) -> List[str]:
        """Generate comprehensive bot identity list for self-detection."""
        bot_names = set()
        
        # Add all discovered agent channel names
        for agent in self.registry.agents.values():
            bot_names.add(agent.channel_name)
            # Add variations
            bot_names.add(f"{agent.channel_name} Agent")
            bot_names.add(f"{agent.channel_name}Agent")
        
        # Add common variations
        bot_names.update([
            "FoundUps Agent",
            "FoundUpsAgent",
            "UnDaoDu",
            "Move2Japan"
        ])
        
        return list(bot_names)
    
    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report."""
        available_agents = self.registry.get_available_agents()
        conflicted_agents = self.registry.get_conflicted_agents()
        
        return {
            "total_agents": len(self.registry.agents),
            "available_agents": len(available_agents),
            "conflicted_agents": len(conflicted_agents),
            "active_sessions": [asdict(session) for session in self.registry.active_sessions.values()],
            "current_agent": self.current_agent.channel_name if self.current_agent else None,
            "user_channel_id": self.user_channel_id,
            "agents": [asdict(agent) for agent in self.registry.agents.values()]
        }

# Global instance
_agent_manager: Optional[MultiAgentManager] = None

def get_agent_manager() -> MultiAgentManager:
    """Get the global agent manager instance."""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = MultiAgentManager()
    return _agent_manager

def show_agent_status():
    """Show current agent status."""
    manager = get_agent_manager()
    report = manager.get_status_report()
    
    print("\n🤖 MULTI-AGENT STATUS REPORT")
    print("=" * 50)
    print(f"Total Agents: {report['total_agents']}")
    print(f"Available: {report['available_agents']}")
    print(f"Conflicted: {report['conflicted_agents']}")
    print(f"Active Sessions: {len(report['active_sessions'])}")
    print(f"Current Agent: {report['current_agent'] or 'None'}")
    
    if report['agents']:
        print("\nAgent Details:")
        for agent_data in report['agents']:
            status_emoji = {
                "available": "✅",
                "active": "🔄", 
                "same_account_conflict": "⚠️",
                "cooldown": "⏳",
                "error": "❌"
            }.get(agent_data['status'], "❓")
            
            print(f"  {status_emoji} {agent_data['channel_name']} ({agent_data['credential_set']}) - {agent_data['status']}")
            if agent_data.get('conflict_reason'):
                print(f"      └─ {agent_data['conflict_reason']}")

if __name__ == "__main__":
    # Quick test/demo
    manager = MultiAgentManager()
    success = manager.initialize()
    if success:
        show_agent_status()
    else:
        print("❌ Failed to initialize multi-agent system") 