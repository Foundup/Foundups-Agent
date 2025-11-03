#!/usr/bin/env python3
"""
Acoustic Lab - Test Suite for Web Application

Tests the Flask web application endpoints and functionality.
"""



import unittest
import json
from unittest.mock import patch, MagicMock
from src.web_app import create_app


class TestWebApp(unittest.TestCase):
    """Test cases for web application functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.app = create_app()
        self.client = self.app.test_client()

    def test_index_page(self):
        """Test that index page loads correctly."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Acoustic Lab', response.data)
        self.assertIn(b'Educational Platform', response.data)

    def test_health_check(self):
        """Test health check endpoint."""
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)

        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertEqual(data['service'], 'Acoustic Lab')
        self.assertIn('stats', data)

    @patch('src.web_app.check_ip_geofencing')
    def test_upload_missing_file(self, mock_geofence):
        """Test upload endpoint with missing file."""
        response = self.client.post('/upload')
        self.assertEqual(response.status_code, 400)

        data = json.loads(response.data)
        self.assertIn('Missing audio file', data['error'])

    @patch('src.web_app.check_ip_geofencing')
    def test_upload_invalid_file_type(self, mock_geofence):
        """Test upload endpoint with invalid file type."""
        data = {'audio': (b'test', 'test.mp3')}
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.data)
        self.assertIn('Only WAV files are accepted', response_data['error'])

    @patch('src.web_app.check_ip_geofencing')
    def test_upload_invalid_metadata(self, mock_geofence):
        """Test upload endpoint with invalid metadata JSON."""
        data = {
            'audio': (b'test', 'test.wav'),
            'metadata': 'invalid json'
        }
        response = self.client.post('/upload', data=data, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)

        response_data = json.loads(response.data)
        self.assertIn('Invalid metadata JSON', response_data['error'])


class TestIPGeofencing(unittest.TestCase):
    """Test cases for IP geofencing functionality."""

    @patch('requests.get')
    def test_valid_utah_ip(self, mock_get):
        """Test IP geofencing with valid Utah IP."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'region': 'UT',
            'regionName': 'Utah'
        }
        mock_get.return_value = mock_response

        from src.web_app import check_ip_geofencing
        # Should not raise exception
        check_ip_geofencing('192.168.1.1')

    @patch('requests.get')
    def test_invalid_non_utah_ip(self, mock_get):
        """Test IP geofencing with non-Utah IP."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'status': 'success',
            'region': 'CA',
            'regionName': 'California'
        }
        mock_get.return_value = mock_response

        from src.web_app import check_ip_geofencing, IPGeofencingError
        with self.assertRaises(IPGeofencingError):
            check_ip_geofencing('192.168.1.1')

    @patch('requests.get')
    def test_geolocation_service_failure(self, mock_get):
        """Test graceful handling when geolocation service fails."""
        mock_get.side_effect = Exception("Service unavailable")

        from src.web_app import check_ip_geofencing
        # Should not raise exception (graceful degradation)
        check_ip_geofencing('192.168.1.1')


if __name__ == '__main__':
    unittest.main()
