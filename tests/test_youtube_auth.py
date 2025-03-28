import unittest
from unittest.mock import patch, MagicMock
import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from modules.youtube_auth import get_authenticated_service

class TestYoutubeAuth(unittest.TestCase):
    """Test suite for YouTube authentication module."""

    def setUp(self):
        """Set up test environment variables."""
        self.test_token_path = "credentials/oauth_token.json"
        self.test_client_secrets = "credentials/client_secrets.json"
        os.environ['GOOGLE_CLIENT_SECRETS_FILE'] = self.test_client_secrets

    @patch('modules.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.Credentials.from_authorized_user_file')
    @patch('modules.youtube_auth.build')
    def test_get_authenticated_service_with_valid_token(self, mock_build, mock_from_file, mock_exists):
        """Test successful authentication with valid token."""
        # Arrange
        mock_exists.return_value = True
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = True
        mock_creds.expired = False
        mock_from_file.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Act
        service = get_authenticated_service()

        # Assert
        self.assertEqual(service, mock_service)
        mock_exists.assert_called_once_with(self.test_token_path)
        mock_from_file.assert_called_once_with(self.test_token_path, ['https://www.googleapis.com/auth/youtube.force-ssl'])
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_creds)

    @patch('modules.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.Credentials.from_authorized_user_file')
    @patch('modules.youtube_auth.build')
    def test_get_authenticated_service_with_expired_token(self, mock_build, mock_from_file, mock_exists):
        """Test token refresh when expired."""
        # Arrange
        mock_exists.return_value = True
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = True
        mock_creds.expired = True
        mock_creds.refresh_token = "test_refresh_token"
        mock_from_file.return_value = mock_creds
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Act
        service = get_authenticated_service()

        # Assert
        self.assertEqual(service, mock_service)
        mock_creds.refresh.assert_called_once()
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_creds)

    @patch('modules.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.InstalledAppFlow.from_client_secrets_file')
    @patch('modules.youtube_auth.build')
    def test_get_authenticated_service_new_oauth_flow(self, mock_build, mock_flow, mock_exists):
        """Test new OAuth flow when no token exists."""
        # Arrange
        mock_exists.return_value = False
        mock_creds = MagicMock(spec=Credentials)
        mock_flow_instance = MagicMock(spec=InstalledAppFlow)
        mock_flow_instance.run_local_server.return_value = mock_creds
        mock_flow.return_value = mock_flow_instance
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Act
        service = get_authenticated_service()

        # Assert
        self.assertEqual(service, mock_service)
        mock_flow.assert_called_once_with(
            self.test_client_secrets,
            scopes=['https://www.googleapis.com/auth/youtube.force-ssl']
        )
        mock_flow_instance.run_local_server.assert_called_once_with(port=0)

    @patch('modules.youtube_auth.os.path.exists')
    def test_get_authenticated_service_missing_client_secrets(self, mock_exists):
        """Test error handling when client secrets file is missing."""
        # Arrange
        mock_exists.return_value = False
        os.environ['GOOGLE_CLIENT_SECRETS_FILE'] = "nonexistent.json"

        # Act & Assert
        with self.assertRaises(FileNotFoundError) as context:
            get_authenticated_service()
        
        self.assertIn("Client secrets file not found", str(context.exception))

    @patch('modules.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.Credentials.from_authorized_user_file')
    def test_get_authenticated_service_invalid_token(self, mock_from_file, mock_exists):
        """Test error handling for invalid token file."""
        # Arrange
        mock_exists.return_value = True
        mock_from_file.side_effect = ValueError("Invalid token file")

        # Act & Assert
        with self.assertRaises(ValueError) as context:
            get_authenticated_service()
        
        self.assertIn("Invalid token file", str(context.exception))

    def tearDown(self):
        """Clean up test environment."""
        if 'GOOGLE_CLIENT_SECRETS_FILE' in os.environ:
            del os.environ['GOOGLE_CLIENT_SECRETS_FILE']

if __name__ == '__main__':
    unittest.main()

