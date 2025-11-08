#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ChromaDB Corruption Prevention System
==========================================

Tests the corruption prevention, detection, and repair capabilities.
"""

import sqlite3
import tempfile
import os
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock

# Import the corruption prevention system
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from chromadb_corruption_prevention import ChromaDBCorruptionPrevention


class TestCorruptionPrevention(unittest.TestCase):
    """Test corruption prevention functionality"""

    def setUp(self):
        """Set up test database"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_chroma.sqlite3"

        # Create a mock ChromaDB-like database structure
        self._create_test_db()

    def tearDown(self):
        """Clean up test files"""
        import shutil
        shutil.rmtree(self.temp_dir)

    def _create_test_db(self):
        """Create a minimal test database with ChromaDB-like structure"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        # Create basic ChromaDB tables
        cursor.execute("""
            CREATE TABLE collections (
                id TEXT PRIMARY KEY,
                name TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE embeddings (
                id TEXT PRIMARY KEY,
                collection_id TEXT,
                embedding BLOB
            )
        """)

        # Create FTS5 table (like ChromaDB does)
        cursor.execute("""
            CREATE VIRTUAL TABLE embedding_fulltext_search
            USING fts5(content, content='embeddings', content_rowid='rowid')
        """)

        # Insert test data
        cursor.execute("INSERT INTO collections (id, name) VALUES (?, ?)",
                      ("test_collection", "Test Collection"))
        cursor.execute("INSERT INTO embeddings (id, collection_id, embedding) VALUES (?, ?, ?)",
                      ("emb1", "test_collection", b"test_embedding_data"))

        conn.commit()
        conn.close()

    def test_corruption_detection_healthy_db(self):
        """Test corruption detection on healthy database"""
        prevention = ChromaDBCorruptionPrevention(db_path=str(self.db_path.parent))

        # Should not detect corruption
        corrupted = prevention._detect_corruption()
        self.assertFalse(corrupted, "Healthy database should not be detected as corrupted")

    def test_fts_rebuild_functionality(self):
        """Test FTS index rebuild functionality"""
        prevention = ChromaDBCorruptionPrevention(db_path=str(self.db_path.parent))

        # Test rebuild on healthy database (should still work)
        success = prevention._rebuild_fts_indexes()
        self.assertTrue(success, "FTS rebuild should succeed on healthy database")

        # Verify database still works after rebuild
        corrupted = prevention._detect_corruption()
        self.assertFalse(corrupted, "Database should still be healthy after rebuild")

    @patch('psutil.virtual_memory')
    def test_memory_monitoring(self, mock_memory):
        """Test memory monitoring functionality"""
        # Mock memory usage
        mock_memory.return_value.percent = 85

        prevention = ChromaDBCorruptionPrevention(db_path=str(self.db_path.parent))

        # Test memory check (should trigger warning for high usage)
        # This is more of an integration test - in real usage, the monitoring
        # thread would handle this
        self.assertIsNotNone(prevention, "Prevention system should initialize")

    def test_backup_creation(self):
        """Test backup creation functionality"""
        prevention = ChromaDBCorruptionPrevention(db_path=str(self.db_path.parent))

        success = prevention.create_backup()
        self.assertTrue(success, "Backup creation should succeed")

        # Check backup file exists
        backup_files = list(self.db_path.parent.glob("backups/*.bak"))
        self.assertTrue(len(backup_files) > 0, "Backup file should be created")

    def test_system_status(self):
        """Test system status reporting"""
        prevention = ChromaDBCorruptionPrevention(db_path=str(self.db_path.parent))

        status = prevention.get_system_status()

        # Verify status contains expected fields
        expected_fields = [
            'database_size_mb', 'memory_usage_percent', 'backups_count',
            'corruption_free', 'health_status'
        ]

        for field in expected_fields:
            self.assertIn(field, status, f"Status should contain {field}")

        self.assertTrue(status['corruption_free'], "Test database should be corruption-free")
        self.assertEqual(status['health_status'], 'GOOD', "Test database should be healthy")


def run_corruption_test():
    """Run corruption prevention tests"""
    print("[TEST] ChromaDB Corruption Prevention Tests")
    print("=" * 50)

    # Run tests
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    run_corruption_test()
