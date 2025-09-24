#!/usr/bin/env python3
"""
Test suite for HoloIndex CLI functionality
"""

import os
import sys
import unittest
import tempfile
from unittest.mock import patch, MagicMock

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from holo_index.cli import HoloIndex, QwenAdvisor
except ImportError:
    # Skip tests if dependencies not available
    import pytest
    pytest.skip("HoloIndex CLI dependencies not available", allow_module_level=True)


class TestHoloIndexCLI(unittest.TestCase):
    """Test HoloIndex CLI functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.test_data_dir, ignore_errors=True)

    @patch("holo_index.cli.SentenceTransformer")
    @patch("holo_index.cli.chromadb.PersistentClient")
    def test_holoindex_initialization(self, mock_client, mock_model):
        """Test HoloIndex can be initialized."""
        mock_client.return_value = MagicMock()
        mock_model.return_value = MagicMock()

        holo = HoloIndex(ssd_path=self.test_data_dir)
        self.assertIsNotNone(holo)

    def test_qwen_advisor_stub(self):
        """Test QwenAdvisor basic functionality."""
        # This is a stub test - will be expanded based on actual implementation
        advisor = QwenAdvisor()
        self.assertIsNotNone(advisor)

    @patch('sys.argv', ['holo_index.py', '--help'])
    def test_cli_help(self):
        """Test CLI help display."""
        with self.assertRaises(SystemExit):
            from holo_index.cli import main
            main()

    def test_search_functionality(self):
        """Test basic search functionality."""
        # This will be expanded once we understand the search API
        pass

    def test_wsp_compliance_checking(self):
        """Test WSP compliance features."""
        # This will be expanded for WSP violation detection
        pass


class TestIntegrationWithWSP87(unittest.TestCase):
    """Test integration with WSP 87 Navigation Protocol."""

    def test_navigation_integration(self):
        """Test that HoloIndex integrates with NAVIGATION.py."""
        try:
            from NAVIGATION import NEED_TO
            # Test that HoloIndex can access navigation data
            self.assertIsInstance(NEED_TO, dict)
        except ImportError:
            self.skipTest("NAVIGATION.py not available")

    def test_semantic_search_prevention(self):
        """Test that semantic search prevents vibecoding."""
        # Mock a search that finds existing code
        # Verify it recommends using existing code instead of creating new
        pass


if __name__ == '__main__':
    unittest.main()
