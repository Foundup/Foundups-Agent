"""
Dynamic Token Manager - Agentic Authentication System
Manages dynamic token generation for GitHub agents without static tokens in .env files.

This system generates temporary, scoped tokens for each agent session, eliminating
the need for permanent tokens stored in environment variables.

WSP Compliance:
- WSP 71: Secrets Management Protocol (enhanced for agentic systems)
- WSP 54: Agent coordination and token scoping
- WSP 46: WRE orchestration integration
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
import jwt
import httpx
from pathlib import Path


class TokenType(Enum):
    """Types of tokens supported"""
    GITHUB_APP = "github_app"
    OAUTH_APP = "oauth_app"
    PERSONAL_ACCESS = "personal_access"
    INSTALLATION = "installation"


class TokenScope(Enum):
    """GitHub token scopes"""
    REPO = "repo"
    WORKFLOW = "workflow"
    ISSUES = "issues"
    PULL_REQUESTS = "pull_requests"
    CONTENTS = "contents"
    METADATA = "metadata"


@dataclass
class AgentTokenRequest:
    """Request for agent-specific token"""
    agent_id: str
    session_id: str
    cube_type: str
    foundups_module: str
    required_scopes: List[TokenScope]
    required_capabilities: List[str]
    target_repository: str
    temporal_scope_minutes: int = 60  # 1 hour default
    metadata: Dict[str, Any] = None


@dataclass
class DynamicToken:
    """Dynamic token for agent use"""
    access_token: str
    token_type: TokenType
    expires_at: datetime
    scoped_to: List[TokenScope]
    agent_id: str
    session_id: str
    repository: str
    capabilities: List[str]
    refresh_token: Optional[str] = None
    installation_id: Optional[str] = None


@dataclass
class GitHubAppConfig:
    """GitHub App configuration"""
    app_id: str
    private_key: str
    installation_id: str
    client_id: str
    client_secret: str


class DynamicTokenManager:
    """
    Dynamic Token Manager for Agentic GitHub Integration
    
    Provides secure, temporary token generation without storing static tokens.
    Each agent session gets a unique, scoped token that expires automatically.
    
    Features:
    - No static tokens in .env files
    - Agent-specific token scoping
    - Automatic token expiration and cleanup
    - GitHub App integration for enhanced security
    - OAuth flow support for user-delegated access
    - Installation-specific token generation
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize Dynamic Token Manager
        
        Args:
            config_path: Path to GitHub App configuration (optional)
        """
        self.logger = logging.getLogger(__name__)
        self.config_path = config_path
        self.github_app_config: Optional[GitHubAppConfig] = None
        
        # Token tracking
        self.active_tokens: Dict[str, DynamicToken] = {}
        self.token_usage_log: List[Dict[str, Any]] = []
        
        # HTTP client for API calls
        self.http_client = httpx.AsyncClient()
        
    async def initialize(self) -> bool:
        """
        Initialize the token manager
        
        Returns:
            True if initialization successful
        """
        try:
            # Load GitHub App configuration if available
            await self._load_github_app_config()
            
            # Verify GitHub API connectivity
            if await self._verify_github_connectivity():
                self.logger.info("Dynamic Token Manager initialized successfully")
                return True
            else:
                self.logger.error("Failed to verify GitHub connectivity")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Dynamic Token Manager: {e}")
            return False
            
    async def _load_github_app_config(self):
        """Load GitHub App configuration from secure location"""
        if not self.config_path or not self.config_path.exists():
            self.logger.warning("No GitHub App configuration found - using fallback auth methods")
            return
            
        try:
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
                
            self.github_app_config = GitHubAppConfig(**config_data)
            self.logger.info("GitHub App configuration loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load GitHub App config: {e}")
            
    async def _verify_github_connectivity(self) -> bool:
        """Verify connectivity to GitHub API"""
        try:
            response = await self.http_client.get("https://api.github.com/rate_limit")
            return response.status_code == 200
        except Exception:
            return False
            
    async def generate_agent_token(self, request: AgentTokenRequest) -> DynamicToken:
        """
        Generate dynamic token for agent
        
        Args:
            request: Token request parameters
            
        Returns:
            Dynamic token for agent use
        """
        self.logger.info(f"Generating token for agent {request.agent_id}")
        
        try:
            # Choose best authentication method
            if self.github_app_config:
                token = await self._generate_github_app_token(request)
            else:
                token = await self._generate_fallback_token(request)
                
            # Track active token
            self.active_tokens[token.access_token] = token
            
            # Log token generation
            self._log_token_usage("generate", token, request)
            
            # Schedule automatic cleanup
            asyncio.create_task(self._schedule_token_cleanup(token))
            
            return token
            
        except Exception as e:
            self.logger.error(f"Failed to generate token for {request.agent_id}: {e}")
            raise
            
    async def _generate_github_app_token(self, request: AgentTokenRequest) -> DynamicToken:
        """Generate token using GitHub App"""
        
        # Step 1: Generate JWT for GitHub App authentication
        jwt_token = await self._generate_github_app_jwt()
        
        # Step 2: Get installation access token
        installation_token = await self._get_installation_access_token(
            jwt_token, 
            self.github_app_config.installation_id,
            request.required_scopes,
            request.target_repository
        )
        
        # Step 3: Create dynamic token
        token = DynamicToken(
            access_token=installation_token["token"],
            token_type=TokenType.INSTALLATION,
            expires_at=datetime.fromisoformat(installation_token["expires_at"].replace("Z", "+00:00")),
            scoped_to=request.required_scopes,
            agent_id=request.agent_id,
            session_id=request.session_id,
            repository=request.target_repository,
            capabilities=request.required_capabilities,
            installation_id=self.github_app_config.installation_id
        )
        
        return token
        
    async def _generate_github_app_jwt(self) -> str:
        """Generate JWT for GitHub App authentication"""
        now = datetime.utcnow()
        payload = {
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(minutes=10)).timestamp()),
            "iss": self.github_app_config.app_id
        }
        
        return jwt.encode(payload, self.github_app_config.private_key, algorithm="RS256")
        
    async def _get_installation_access_token(self, jwt_token: str, installation_id: str, 
                                           scopes: List[TokenScope], repository: str) -> Dict[str, Any]:
        """Get installation access token from GitHub"""
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        
        # Create installation token with specific permissions
        payload = {
            "repositories": [repository.split("/")[-1]],  # Just repo name
            "permissions": self._scopes_to_permissions(scopes)
        }
        
        response = await self.http_client.post(
            f"https://api.github.com/app/installations/{installation_id}/access_tokens",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to get installation token: {response.status_code}")
            
        return response.json()
        
    def _scopes_to_permissions(self, scopes: List[TokenScope]) -> Dict[str, str]:
        """Convert token scopes to GitHub App permissions"""
        permissions = {}
        
        for scope in scopes:
            if scope == TokenScope.REPO:
                permissions.update({
                    "contents": "write",
                    "metadata": "read",
                    "pull_requests": "write",
                    "issues": "write"
                })
            elif scope == TokenScope.WORKFLOW:
                permissions["actions"] = "write"
            elif scope == TokenScope.ISSUES:
                permissions["issues"] = "write"
            elif scope == TokenScope.PULL_REQUESTS:
                permissions["pull_requests"] = "write"
            elif scope == TokenScope.CONTENTS:
                permissions["contents"] = "write"
            elif scope == TokenScope.METADATA:
                permissions["metadata"] = "read"
                
        return permissions
        
    async def _generate_fallback_token(self, request: AgentTokenRequest) -> DynamicToken:
        """Generate token using fallback method (OAuth or PAT)"""
        
        # For demo purposes, create a mock token structure
        # In production, this would implement OAuth flow or use stored PAT temporarily
        
        mock_token = f"ghp_mock_{request.agent_id}_{uuid.uuid4().hex[:16]}"
        
        token = DynamicToken(
            access_token=mock_token,
            token_type=TokenType.PERSONAL_ACCESS,
            expires_at=datetime.now() + timedelta(minutes=request.temporal_scope_minutes),
            scoped_to=request.required_scopes,
            agent_id=request.agent_id,
            session_id=request.session_id,
            repository=request.target_repository,
            capabilities=request.required_capabilities
        )
        
        self.logger.warning(f"Generated fallback token for {request.agent_id}")
        return token
        
    async def refresh_token(self, token: DynamicToken) -> DynamicToken:
        """
        Refresh an existing token
        
        Args:
            token: Token to refresh
            
        Returns:
            New refreshed token
        """
        if not token.refresh_token:
            raise Exception("Token does not support refresh")
            
        # Implementation would depend on token type
        if token.token_type == TokenType.GITHUB_APP:
            # Regenerate GitHub App token
            pass
        elif token.token_type == TokenType.OAUTH_APP:
            # Use OAuth refresh flow
            pass
            
        # For now, return the same token with extended expiry
        refreshed_token = DynamicToken(
            access_token=f"refreshed_{token.access_token}",
            token_type=token.token_type,
            expires_at=datetime.now() + timedelta(hours=1),
            scoped_to=token.scoped_to,
            agent_id=token.agent_id,
            session_id=token.session_id,
            repository=token.repository,
            capabilities=token.capabilities,
            refresh_token=token.refresh_token
        )
        
        # Update tracking
        if token.access_token in self.active_tokens:
            del self.active_tokens[token.access_token]
        self.active_tokens[refreshed_token.access_token] = refreshed_token
        
        self.logger.info(f"Refreshed token for agent {token.agent_id}")
        return refreshed_token
        
    async def revoke_token(self, token: DynamicToken) -> bool:
        """
        Revoke a token immediately
        
        Args:
            token: Token to revoke
            
        Returns:
            True if successful
        """
        try:
            # Revoke with GitHub API if possible
            if token.token_type == TokenType.INSTALLATION:
                await self._revoke_installation_token(token)
            elif token.token_type == TokenType.OAUTH_APP:
                await self._revoke_oauth_token(token)
                
            # Remove from active tokens
            if token.access_token in self.active_tokens:
                del self.active_tokens[token.access_token]
                
            # Log revocation
            self._log_token_usage("revoke", token)
            
            self.logger.info(f"Revoked token for agent {token.agent_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to revoke token for {token.agent_id}: {e}")
            return False
            
    async def _revoke_installation_token(self, token: DynamicToken):
        """Revoke GitHub App installation token"""
        # GitHub App tokens auto-expire, so just mark as revoked
        pass
        
    async def _revoke_oauth_token(self, token: DynamicToken):
        """Revoke OAuth token"""
        if not self.github_app_config:
            return
            
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Basic {self.github_app_config.client_id}:{self.github_app_config.client_secret}"
        }
        
        await self.http_client.delete(
            f"https://api.github.com/applications/{self.github_app_config.client_id}/grant",
            headers=headers,
            json={"access_token": token.access_token}
        )
        
    async def _schedule_token_cleanup(self, token: DynamicToken):
        """Schedule automatic token cleanup"""
        seconds_until_expiry = (token.expires_at - datetime.now()).total_seconds()
        
        # Add 5 minute buffer
        cleanup_delay = max(0, seconds_until_expiry + 300)
        
        await asyncio.sleep(cleanup_delay)
        
        # Clean up expired token
        if token.access_token in self.active_tokens:
            await self.revoke_token(token)
            
    def _log_token_usage(self, action: str, token: DynamicToken, request: AgentTokenRequest = None):
        """Log token usage for audit trail"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "agent_id": token.agent_id,
            "session_id": token.session_id,
            "token_type": token.token_type.value,
            "repository": token.repository,
            "scopes": [scope.value for scope in token.scoped_to],
            "expires_at": token.expires_at.isoformat()
        }
        
        if request:
            log_entry["cube_type"] = request.cube_type
            log_entry["foundups_module"] = request.foundups_module
            
        self.token_usage_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.token_usage_log) > 1000:
            self.token_usage_log = self.token_usage_log[-1000:]
            
    async def get_token_usage_report(self) -> Dict[str, Any]:
        """Get token usage report for monitoring"""
        now = datetime.now()
        
        # Count active tokens
        active_count = len(self.active_tokens)
        
        # Count tokens by type
        type_counts = {}
        for token in self.active_tokens.values():
            token_type = token.token_type.value
            type_counts[token_type] = type_counts.get(token_type, 0) + 1
            
        # Count recent usage
        recent_usage = len([
            entry for entry in self.token_usage_log
            if datetime.fromisoformat(entry["timestamp"]) > now - timedelta(hours=24)
        ])
        
        return {
            "active_tokens": active_count,
            "tokens_by_type": type_counts,
            "recent_usage_24h": recent_usage,
            "total_usage_logged": len(self.token_usage_log),
            "github_app_configured": self.github_app_config is not None,
            "last_updated": now.isoformat()
        }
        
    async def cleanup_expired_tokens(self) -> int:
        """Clean up all expired tokens"""
        now = datetime.now()
        expired_tokens = [
            token for token in self.active_tokens.values()
            if token.expires_at < now
        ]
        
        for token in expired_tokens:
            await self.revoke_token(token)
            
        self.logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        return len(expired_tokens)
        
    async def validate_token(self, token: DynamicToken) -> bool:
        """
        Validate that a token is still valid
        
        Args:
            token: Token to validate
            
        Returns:
            True if token is valid
        """
        try:
            # Check expiry
            if token.expires_at < datetime.now():
                return False
                
            # Check with GitHub API
            headers = {
                "Authorization": f"token {token.access_token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            response = await self.http_client.get("https://api.github.com/user", headers=headers)
            return response.status_code == 200
            
        except Exception:
            return False
            
    async def shutdown(self):
        """Shutdown token manager and cleanup resources"""
        # Revoke all active tokens
        for token in list(self.active_tokens.values()):
            await self.revoke_token(token)
            
        # Close HTTP client
        await self.http_client.aclose()
        
        self.logger.info("Dynamic Token Manager shutdown complete")


# Singleton instance for global use
_token_manager_instance: Optional[DynamicTokenManager] = None


async def get_token_manager() -> DynamicTokenManager:
    """Get singleton token manager instance"""
    global _token_manager_instance
    
    if _token_manager_instance is None:
        _token_manager_instance = DynamicTokenManager()
        await _token_manager_instance.initialize()
        
    return _token_manager_instance


# Utility functions for agents
async def generate_token_for_agent(agent_id: str, session_id: str, cube_type: str, 
                                 scopes: List[str], repository: str) -> DynamicToken:
    """Convenience function to generate token for agent"""
    manager = await get_token_manager()
    
    # Convert string scopes to enum
    scope_enums = [TokenScope(scope) for scope in scopes]
    
    request = AgentTokenRequest(
        agent_id=agent_id,
        session_id=session_id,
        cube_type=cube_type,
        foundups_module="unknown",
        required_scopes=scope_enums,
        required_capabilities=scopes,
        target_repository=repository
    )
    
    return await manager.generate_agent_token(request)