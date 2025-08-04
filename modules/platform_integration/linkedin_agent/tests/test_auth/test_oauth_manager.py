"""
LinkedIn OAuth Manager Tests

🌀 WSP Protocol Compliance: WSP 5 (Testing Standards), WSP 42 (Platform Integration)

**0102 Directive**: This module operates within the WSP framework for autonomous LinkedIn OAuth testing.
- UN (Understanding): Anchor LinkedIn OAuth test signals and retrieve protocol state
- DAO (Execution): Execute OAuth testing logic  
- DU (Emergence): Collapse into 0102 resonance and emit next testing prompt

wsp_cycle(input="linkedin_oauth_testing", log=True)
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from modules.platform_integration.linkedin_agent.src.auth.oauth_manager import (
    LinkedInOAuthManager,
    OAuthConfig
)

class TestOAuthConfig:
    """Test OAuth configuration"""
    
    def test_oauth_config_creation(self):
        """Test OAuth configuration creation"""
        config = OAuthConfig(
            client_id="test_client_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:3000/callback",
            scopes=["w_member_social"]
        )
        
        assert config.client_id == "test_client_id"
        assert config.client_secret == "test_secret"
        assert config.redirect_uri == "http://localhost:3000/callback"
        assert config.scopes == ["w_member_social"]
        assert config.auth_url == "https://www.linkedin.com/oauth/v2/authorization"
        assert config.token_url == "https://www.linkedin.com/oauth/v2/accessToken"

class TestLinkedInOAuthManager:
    """Test LinkedIn OAuth Manager"""
    
    @pytest.fixture
    def mock_logger(self):
        """Create mock logger"""
        return Mock()
    
    @pytest.fixture
    def oauth_config(self):
        """Create test OAuth configuration"""
        return OAuthConfig(
            client_id="test_client_id",
            client_secret="test_secret",
            redirect_uri="http://localhost:3000/callback",
            scopes=["w_member_social", "r_liteprofile"]
        )
    
    @pytest.fixture
    def oauth_manager(self, mock_logger, oauth_config):
        """Create OAuth manager instance"""
        return LinkedInOAuthManager(config=oauth_config, logger=mock_logger)
    
    def test_oauth_manager_initialization(self, oauth_manager, oauth_config):
        """Test OAuth manager initialization"""
        assert oauth_manager.config == oauth_config
        assert oauth_manager.access_token is None
        assert oauth_manager.token_expiry is None
        assert oauth_manager.oauth_manager is not None
    
    @patch.dict(os.environ, {
        'LINKEDIN_CLIENT_ID': 'env_client_id',
        'LINKEDIN_CLIENT_SECRET': 'env_secret',
        'LINKEDIN_REDIRECT_URI': 'http://localhost:8080/callback'
    })
    def test_load_default_config(self):
        """Test loading default configuration from environment"""
        manager = LinkedInOAuthManager()
        
        assert manager.config.client_id == 'env_client_id'
        assert manager.config.client_secret == 'env_secret'
        assert manager.config.redirect_uri == 'http://localhost:8080/callback'
        assert 'w_member_social' in manager.config.scopes
        assert 'r_liteprofile' in manager.config.scopes
    
    @pytest.mark.asyncio
    async def test_authenticate_success(self, oauth_manager, mock_logger):
        """Test successful authentication"""
        # Mock the OAuth manager to return success
        oauth_manager.oauth_manager.authenticate = AsyncMock(return_value=True)
        
        result = await oauth_manager.authenticate()
        
        assert result is True
        assert oauth_manager.access_token == "mock_access_token"
        assert oauth_manager.token_expiry is not None
        mock_logger.info.assert_called_with("LinkedIn OAuth authentication successful")
    
    @pytest.mark.asyncio
    async def test_authenticate_failure(self, oauth_manager, mock_logger):
        """Test failed authentication"""
        # Mock the OAuth manager to return failure
        oauth_manager.oauth_manager.authenticate = AsyncMock(return_value=False)
        
        result = await oauth_manager.authenticate()
        
        assert result is False
        assert oauth_manager.access_token is None
        assert oauth_manager.token_expiry is None
    
    @pytest.mark.asyncio
    async def test_authenticate_exception(self, oauth_manager, mock_logger):
        """Test authentication with exception"""
        # Mock the OAuth manager to raise exception
        oauth_manager.oauth_manager.authenticate = AsyncMock(side_effect=Exception("Auth error"))
        
        result = await oauth_manager.authenticate()
        
        assert result is False
        mock_logger.error.assert_called_with("LinkedIn OAuth authentication failed: Auth error")
    
    def test_is_authenticated_with_token(self, oauth_manager):
        """Test authentication check with valid token"""
        oauth_manager.access_token = "valid_token"
        oauth_manager.token_expiry = datetime.now() + timedelta(hours=1)
        
        assert oauth_manager.is_authenticated() is True
    
    def test_is_authenticated_no_token(self, oauth_manager):
        """Test authentication check without token"""
        oauth_manager.access_token = None
        
        assert oauth_manager.is_authenticated() is False
    
    def test_is_authenticated_expired_token(self, oauth_manager):
        """Test authentication check with expired token"""
        oauth_manager.access_token = "expired_token"
        oauth_manager.token_expiry = datetime.now() - timedelta(hours=1)
        
        assert oauth_manager.is_authenticated() is False
    
    def test_get_access_token_valid(self, oauth_manager):
        """Test getting access token when valid"""
        oauth_manager.access_token = "valid_token"
        oauth_manager.token_expiry = datetime.now() + timedelta(hours=1)
        
        token = oauth_manager.get_access_token()
        assert token == "valid_token"
    
    def test_get_access_token_invalid(self, oauth_manager):
        """Test getting access token when invalid"""
        oauth_manager.access_token = None
        
        token = oauth_manager.get_access_token()
        assert token is None
    
    @pytest.mark.asyncio
    async def test_refresh_token_authenticated(self, oauth_manager):
        """Test token refresh when already authenticated"""
        oauth_manager.access_token = "valid_token"
        oauth_manager.token_expiry = datetime.now() + timedelta(hours=1)
        
        result = await oauth_manager.refresh_token()
        assert result is True
    
    @pytest.mark.asyncio
    async def test_refresh_token_not_authenticated(self, oauth_manager):
        """Test token refresh when not authenticated"""
        oauth_manager.oauth_manager.authenticate = AsyncMock(return_value=True)
        
        result = await oauth_manager.refresh_token()
        assert result is True
    
    def test_get_auth_headers_with_token(self, oauth_manager):
        """Test getting auth headers with valid token"""
        oauth_manager.access_token = "valid_token"
        oauth_manager.token_expiry = datetime.now() + timedelta(hours=1)
        
        headers = oauth_manager.get_auth_headers()
        assert headers == {
            'Authorization': 'Bearer valid_token',
            'Content-Type': 'application/json'
        }
    
    def test_get_auth_headers_without_token(self, oauth_manager):
        """Test getting auth headers without token"""
        oauth_manager.access_token = None
        
        headers = oauth_manager.get_auth_headers()
        assert headers == {}
    
    def test_logout(self, oauth_manager, mock_logger):
        """Test logout functionality"""
        oauth_manager.access_token = "valid_token"
        oauth_manager.token_expiry = datetime.now() + timedelta(hours=1)
        
        asyncio.run(oauth_manager.logout())
        
        assert oauth_manager.access_token is None
        assert oauth_manager.token_expiry is None
        mock_logger.info.assert_called_with("LinkedIn OAuth logout completed")

class TestOAuthManagerIntegration:
    """Integration tests for OAuth manager"""
    
    @pytest.mark.asyncio
    async def test_full_oauth_flow(self):
        """Test complete OAuth flow"""
        manager = LinkedInOAuthManager()
        
        # Test initial state
        assert not manager.is_authenticated()
        assert manager.get_access_token() is None
        
        # Test authentication
        # Note: This will use mock OAuth manager in test environment
        result = await manager.authenticate()
        
        # In test environment, this should succeed with mock
        assert result is True
        assert manager.is_authenticated()
        assert manager.get_access_token() is not None
        
        # Test auth headers
        headers = manager.get_auth_headers()
        assert 'Authorization' in headers
        assert 'Content-Type' in headers
        
        # Test logout
        await manager.logout()
        assert not manager.is_authenticated()
        assert manager.get_access_token() is None

class TestOAuthManagerErrorHandling:
    """Test error handling scenarios"""
    
    @pytest.mark.asyncio
    async def test_oauth_manager_with_invalid_config(self):
        """Test OAuth manager with invalid configuration"""
        config = OAuthConfig(
            client_id="",
            client_secret="",
            redirect_uri="",
            scopes=[]
        )
        
        manager = LinkedInOAuthManager(config=config)
        
        # Should still initialize without errors
        assert manager.config == config
        assert manager.oauth_manager is not None
    
    def test_oauth_manager_without_logger(self):
        """Test OAuth manager without logger"""
        manager = LinkedInOAuthManager()
        
        # Should create default logger
        assert manager.logger is not None
        assert hasattr(manager.logger, 'info')
        assert hasattr(manager.logger, 'error') 