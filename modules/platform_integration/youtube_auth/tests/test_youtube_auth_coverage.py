#!/usr/bin/env python3
"""
Comprehensive test coverage for YouTube Auth module.
Focuses on covering missing lines and edge cases.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Adjust sys.path to include the modules directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the functions under test
from modules.platform_integration.youtube_auth.src.youtube_auth import (
    get_credentials_for_index, 
    get_authenticated_service
)
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError


class TestYoutubeAuthCoverage(unittest.TestCase):
    """Test suite for comprehensive YouTube authentication coverage."""

    def setUp(self):
        """Set up test environment."""
        self.env_vars_to_clear = [f'GOOGLE_CLIENT_SECRETS_FILE_{i}' for i in range(1, 5)] + \
                                 [f'OAUTH_TOKEN_FILE_{i}' for i in range(1, 5)] + \
                                 ['YOUTUBE_SCOPES']
        self.original_values = {k: os.environ.get(k) for k in self.env_vars_to_clear}
        for var in self.env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]

    def tearDown(self):
        """Clean up test environment."""
        for var, value in self.original_values.items():
            if value is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = value

    # ===== Tests for get_credentials_for_index function (lines 20-30) =====
    
    def test_get_credentials_for_index_success(self):
        """Test get_credentials_for_index with valid environment variables."""
        # Arrange
        os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'test_secrets.json'
        os.environ['OAUTH_TOKEN_FILE_1'] = 'test_token.json'
        
        with patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists', return_value=True):
            # Act
            result = get_credentials_for_index(1)
            
            # Assert
            self.assertEqual(result, ('test_secrets.json', 'test_token.json'))

    def test_get_credentials_for_index_missing_client_secrets_env(self):
        """Test get_credentials_for_index when client secrets env var is missing."""
        # Arrange - only set token file, not client secrets
        os.environ['OAUTH_TOKEN_FILE_1'] = 'test_token.json'
        
        # Act
        result = get_credentials_for_index(1)
        
        # Assert
        self.assertIsNone(result)

    def test_get_credentials_for_index_missing_token_file_env(self):
        """Test get_credentials_for_index when token file env var is missing."""
        # Arrange - only set client secrets, not token file
        os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'test_secrets.json'
        
        # Act
        result = get_credentials_for_index(1)
        
        # Assert
        self.assertIsNone(result)

    def test_get_credentials_for_index_client_secrets_file_not_exists(self):
        """Test get_credentials_for_index when client secrets file doesn't exist."""
        # Arrange
        os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'nonexistent_secrets.json'
        os.environ['OAUTH_TOKEN_FILE_1'] = 'test_token.json'
        
        with patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists', return_value=False):
            # Act
            result = get_credentials_for_index(1)
            
            # Assert
            self.assertIsNone(result)

    # ===== Tests for error handling paths in get_authenticated_service =====
    
    def test_get_authenticated_service_missing_scopes(self):
        """Test get_authenticated_service when YOUTUBE_SCOPES is not set."""
        # Arrange - no YOUTUBE_SCOPES environment variable
        
        # Act & Assert
        with self.assertRaisesRegex(ValueError, "YOUTUBE_SCOPES must be defined in .env"):
            get_authenticated_service()

    def test_get_authenticated_service_empty_scopes(self):
        """Test get_authenticated_service when YOUTUBE_SCOPES is empty."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = ''
        
        # Act & Assert
        with self.assertRaisesRegex(ValueError, "YOUTUBE_SCOPES must be defined in .env"):
            get_authenticated_service()

    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.get_credentials_for_index')
    def test_get_authenticated_service_all_credential_sets_none(self, mock_get_creds):
        """Test get_authenticated_service when all credential sets return None."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        mock_get_creds.return_value = None
        
        # Act & Assert
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
            get_authenticated_service()
        
        # Verify it tried all 4 credential sets
        self.assertEqual(mock_get_creds.call_count, 4)

    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.build')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.Request')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.get_credentials_for_index')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.makedirs')
    def test_get_authenticated_service_refresh_failure(self, mock_makedirs, mock_get_creds, mock_exists, mock_from_file, mock_request, mock_build):
        """Test get_authenticated_service when token refresh fails."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        mock_get_creds.return_value = ('secrets.json', 'token.json')
        mock_exists.return_value = True
        
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = "test_refresh_token"
        mock_from_file.return_value = mock_creds
        
        # Mock refresh to raise an exception
        mock_creds.refresh.side_effect = Exception("Refresh failed")
        
        # Act & Assert
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
            get_authenticated_service()

    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.build')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.get_credentials_for_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.makedirs')
    def test_get_authenticated_service_save_credentials_failure(self, mock_makedirs, mock_open_file, mock_get_creds, mock_exists, mock_flow, mock_build):
        """Test get_authenticated_service when saving credentials fails."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        mock_get_creds.return_value = ('secrets.json', 'token.json')
        mock_exists.return_value = False
        
        mock_flow_instance = MagicMock(spec=InstalledAppFlow)
        mock_new_creds = MagicMock(spec=Credentials)
        mock_flow_instance.run_local_server.return_value = mock_new_creds
        mock_flow.return_value = mock_flow_instance
        mock_new_creds.to_json.return_value = '{"token": "new"}'
        
        # Mock file writing to raise an exception
        mock_open_file.side_effect = IOError("Cannot write file")
        
        # Act & Assert
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
            get_authenticated_service()

    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.build')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.get_credentials_for_index')
    def test_get_authenticated_service_build_service_failure(self, mock_get_creds, mock_exists, mock_from_file, mock_build):
        """Test get_authenticated_service when building YouTube service fails."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        mock_get_creds.return_value = ('secrets.json', 'token.json')
        mock_exists.return_value = True
        
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = True
        mock_from_file.return_value = mock_creds
        
        # Mock build to raise a non-quota exception
        mock_build.side_effect = Exception("Service build failed")
        
        # Act & Assert
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
            get_authenticated_service()

    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.build')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.Request')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.get_credentials_for_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.platform_integration.youtube_auth.src.youtube_auth.os.makedirs')
    def test_get_authenticated_service_no_refresh_token(self, mock_makedirs, mock_open_file, mock_get_creds, mock_exists, mock_from_file, mock_request, mock_build):
        """Test get_authenticated_service when credentials are invalid but have no refresh token."""
        # Arrange
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        mock_get_creds.return_value = ('secrets.json', 'token.json')
        mock_exists.return_value = True
        
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = None  # No refresh token
        mock_from_file.return_value = mock_creds
        
        # Mock OAuth flow
        with patch('modules.platform_integration.youtube_auth.src.youtube_auth.google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file') as mock_flow:
            mock_flow_instance = MagicMock(spec=InstalledAppFlow)
            mock_new_creds = MagicMock(spec=Credentials)
            mock_flow_instance.run_local_server.return_value = mock_new_creds
            mock_flow.return_value = mock_flow_instance
            mock_new_creds.to_json.return_value = '{"token": "new"}'
            
            mock_service = MagicMock()
            mock_build.return_value = mock_service
            
            # Act
            result = get_authenticated_service()
            
            # Assert
            self.assertEqual(result, mock_service)
            mock_flow.assert_called_once_with('secrets.json', ['https://www.googleapis.com/auth/youtube.readonly'])
            mock_flow_instance.run_local_server.assert_called_once_with(port=0)


if __name__ == '__main__':
    unittest.main() 