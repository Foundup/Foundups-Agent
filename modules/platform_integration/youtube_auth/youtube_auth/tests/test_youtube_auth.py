import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys

# Adjust sys.path to include the modules directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import the module under test and dependencies
from modules.platform_integration.youtube_auth.youtube_auth.src.youtube_auth import get_authenticated_service
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request # Import Request
from googleapiclient.errors import HttpError # Import HttpError

class TestYoutubeAuth(unittest.TestCase):
    """Test suite for YouTube authentication functions."""

    # Clear environment variables that might interfere
    def setUp(self):
        self.env_vars_to_clear = [f'GOOGLE_CLIENT_SECRETS_FILE_{i}' for i in range(1, 5)] + \
                                 [f'OAUTH_TOKEN_FILE_{i}' for i in range(1, 5)] + \
                                 ['YOUTUBE_SCOPES']
        self.original_values = {k: os.environ.get(k) for k in self.env_vars_to_clear}
        for var in self.env_vars_to_clear:
            if var in os.environ:
                del os.environ[var]
        # Set minimal required env vars for tests
        os.environ['YOUTUBE_SCOPES'] = 'https://www.googleapis.com/auth/youtube.readonly'
        os.environ['GOOGLE_CLIENT_SECRETS_FILE_1'] = 'credentials/client_secret.json' # Needed for get_credentials_for_index mock setup
        os.environ['OAUTH_TOKEN_FILE_1'] = 'credentials/oauth_token.json' # Needed for get_credentials_for_index mock setup


    def tearDown(self):
        for var, value in self.original_values.items():
            if value is None:
                if var in os.environ:
                    del os.environ[var]
            else:
                os.environ[var] = value

    @patch('modules.youtube_auth.src.youtube_auth.build')
    @patch('modules.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    def test_get_authenticated_service_with_valid_token(self, mock_get_creds, mock_exists, mock_from_file, mock_build):
        """Test successful authentication with valid token."""
        # Arrange
        mock_get_creds.return_value = ('credentials/client_secret.json', 'credentials/oauth_token.json')
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
        mock_get_creds.assert_called_once_with(1) # Check first credential set
        mock_exists.assert_called_once_with('credentials/oauth_token.json')
        mock_from_file.assert_called_once_with('credentials/oauth_token.json', ['https://www.googleapis.com/auth/youtube.readonly'])
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_creds)


    @patch('modules.youtube_auth.src.youtube_auth.build')
    @patch('modules.youtube_auth.src.youtube_auth.Request')
    @patch('modules.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.youtube_auth.src.youtube_auth.os.makedirs')
    def test_get_authenticated_service_with_expired_token(self, mock_makedirs, mock_open_file, mock_get_creds, mock_exists, mock_from_file, mock_request, mock_build):
        """Test token refresh when expired."""
        # Arrange
        mock_get_creds.return_value = ('credentials/client_secret.json', 'credentials/oauth_token.json')
        mock_exists.return_value = True
        mock_creds = MagicMock(spec=Credentials)
        mock_creds.valid = False # Simulate invalid initially
        mock_creds.expired = True
        mock_creds.refresh_token = "test_refresh_token"
        mock_from_file.return_value = mock_creds
        # Mock the refresh method
        mock_creds.refresh.return_value = None
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        # Mock the request object needed for refresh
        mock_req_instance = MagicMock()
        mock_request.return_value = mock_req_instance
        # Mock creds.to_json()
        mock_creds.to_json.return_value = '{"token": "refreshed"}'


        # Act
        service = get_authenticated_service()

        # Assert
        self.assertEqual(service, mock_service)
        mock_get_creds.assert_called_once_with(1)
        mock_exists.assert_called_once_with('credentials/oauth_token.json')
        mock_from_file.assert_called_once_with('credentials/oauth_token.json', ['https://www.googleapis.com/auth/youtube.readonly'])
        mock_creds.refresh.assert_called_once_with(mock_req_instance)
        mock_makedirs.assert_called_once_with(os.path.dirname('credentials/oauth_token.json'), exist_ok=True)
        mock_open_file.assert_called_once_with('credentials/oauth_token.json', 'w')
        mock_open_file().write.assert_called_once_with('{"token": "refreshed"}')
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_creds)


    @patch('modules.youtube_auth.src.youtube_auth.build')
    @patch('modules.youtube_auth.src.youtube_auth.google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file')
    @patch('modules.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    @patch('builtins.open', new_callable=mock_open)
    @patch('modules.youtube_auth.src.youtube_auth.os.makedirs')
    def test_get_authenticated_service_new_oauth_flow(self, mock_makedirs, mock_open_file, mock_get_creds, mock_exists, mock_flow, mock_build):
        """Test new OAuth flow when no token exists."""
        # Arrange
        mock_get_creds.return_value = ('credentials/client_secret.json', 'credentials/oauth_token.json')
        mock_exists.return_value = False # Simulate token file not existing
        mock_flow_instance = MagicMock(spec=InstalledAppFlow)
        mock_new_creds = MagicMock(spec=Credentials)
        mock_flow_instance.run_local_server.return_value = mock_new_creds
        mock_flow.return_value = mock_flow_instance
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        # Mock creds.to_json() for saving
        mock_new_creds.to_json.return_value = '{"token": "new"}'


        # Act
        service = get_authenticated_service()

        # Assert
        self.assertEqual(service, mock_service)
        mock_get_creds.assert_called_once_with(1)
        mock_exists.assert_called_once_with('credentials/oauth_token.json')
        mock_flow.assert_called_once_with('credentials/client_secret.json', ['https://www.googleapis.com/auth/youtube.readonly'])
        mock_flow_instance.run_local_server.assert_called_once_with(port=0)
        mock_makedirs.assert_called_once_with(os.path.dirname('credentials/oauth_token.json'), exist_ok=True)
        mock_open_file.assert_called_once_with('credentials/oauth_token.json', 'w')
        mock_open_file().write.assert_called_once_with('{"token": "new"}')
        mock_build.assert_called_once_with('youtube', 'v3', credentials=mock_new_creds)


    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    def test_get_authenticated_service_missing_client_secrets(self, mock_get_creds):
        """Test error handling when client secrets file cannot be resolved by get_credentials_for_index."""
        # Arrange
        # Simulate get_credentials_for_index returning None for all indices
        mock_get_creds.return_value = None

        # Act & Assert
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
            get_authenticated_service()
        # Ensure it tried all 4 indices
        self.assertEqual(mock_get_creds.call_count, 4)
        mock_get_creds.assert_any_call(1)
        mock_get_creds.assert_any_call(2)
        mock_get_creds.assert_any_call(3)
        mock_get_creds.assert_any_call(4)


    @patch('modules.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file')
    @patch('modules.youtube_auth.src.youtube_auth.os.path.exists')
    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    # Note: We are not mocking the OAuth flow here, as the ValueError should prevent it
    def test_get_authenticated_service_invalid_token(self, mock_get_creds, mock_exists, mock_from_file):
        """Test error handling for invalid token file that raises non-refresh error."""
        # Arrange
        mock_get_creds.return_value = ('credentials/client_secret.json', 'credentials/oauth_token.json')
        mock_exists.return_value = True
        # Simulate an error during credential loading that IS NOT refresh-related
        mock_from_file.side_effect = ValueError("Invalid token file structure")

        # Act & Assert
        # Expect the function to log the error and move to the next credential set,
        # eventually failing if all sets have this issue.
        with self.assertRaisesRegex(Exception, "Could not authenticate with any Google credential set."):
             get_authenticated_service()

        # Assertions to ensure it tried to load, failed, and didn't try to build/refresh
        mock_get_creds.assert_any_call(1) # Should have at least tried index 1
        mock_exists.assert_called_with('credentials/oauth_token.json')
        mock_from_file.assert_called_with('credentials/oauth_token.json', ['https://www.googleapis.com/auth/youtube.readonly'])
        # Check call counts - should try all 4 if the error persists
        self.assertEqual(mock_get_creds.call_count, 4)


    @patch('modules.youtube_auth.src.youtube_auth.build')
    @patch('modules.youtube_auth.src.youtube_auth.get_credentials_for_index')
    def test_get_authenticated_service_quota_exceeded(self, mock_get_creds, mock_build):
        """Test fallback mechanism when HttpError (quotaExceeded) occurs."""
        # Arrange
        # Creds setup for index 1
        mock_creds1 = MagicMock(spec=Credentials, valid=True, expired=False)
        # Creds setup for index 2 (successful one)
        mock_creds2 = MagicMock(spec=Credentials, valid=True, expired=False)

        # Mock get_credentials_for_index to return different creds based on index
        def side_effect_get_creds(index):
            if index == 1:
                return ('path/to/secrets1.json', 'path/to/token1.json')
            elif index == 2:
                return ('path/to/secrets2.json', 'path/to/token2.json')
            else:
                return None # Fail others
        mock_get_creds.side_effect = side_effect_get_creds

        # Mock os.path.exists to always return true for token files
        with patch('modules.youtube_auth.src.youtube_auth.os.path.exists', return_value=True) as mock_exists_inner:
            # Mock from_authorized_user_file to return appropriate creds
            with patch('modules.youtube_auth.src.youtube_auth.google.oauth2.credentials.Credentials.from_authorized_user_file') as mock_from_file_inner:
                def side_effect_from_file(token_file, scopes):
                    if token_file == 'path/to/token1.json':
                        return mock_creds1
                    elif token_file == 'path/to/token2.json':
                        return mock_creds2
                    return None
                mock_from_file_inner.side_effect = side_effect_from_file

                # Mock build to raise quota error for creds1, succeed for creds2
                mock_service = MagicMock()
                def side_effect_build(service, version, credentials):
                    if credentials == mock_creds1:
                        # Simulate quota exceeded error
                        http_error = HttpError(resp=MagicMock(status=403), content=b'{"error": {"errors": [{"reason": "quotaExceeded"}]}}')
                        raise http_error
                    elif credentials == mock_creds2:
                        return mock_service # Success
                    else:
                        raise Exception("Unexpected credentials")
                mock_build.side_effect = side_effect_build

                # Act
                service = get_authenticated_service()

                # Assert
                self.assertEqual(service, mock_service) # Should return service from index 2
                self.assertEqual(mock_get_creds.call_count, 2) # Called for 1 and 2
                self.assertEqual(mock_build.call_count, 2) # Build called for 1 and 2
                mock_build.assert_any_call('youtube', 'v3', credentials=mock_creds1)
                mock_build.assert_any_call('youtube', 'v3', credentials=mock_creds2)


if __name__ == '__main__':
    unittest.main()

