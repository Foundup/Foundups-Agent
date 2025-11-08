#!/usr/bin/env python3
"""
ChromaDB Corruption Prevention System
Implements comprehensive safeguards against database corruption
"""

import chromadb
import sqlite3
import os
import psutil
import time
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from contextlib import contextmanager
import threading

class ChromaDBCorruptionPrevention:
    """Comprehensive system to prevent ChromaDB corruption"""

    def __init__(self, db_path: str = "E:/HoloIndex/vectors"):
        self.db_path = Path(db_path)
        self.db_file = self.db_path / "chroma.sqlite3"
        self.backup_dir = self.db_path / "backups"
        self.backup_dir.mkdir(exist_ok=True)

        # Configuration
        self.max_batch_size = 5  # Conservative batch size
        self.max_memory_percent = 80  # Memory usage threshold
        self.backup_interval_hours = 24
        self.health_check_interval = 300  # 5 minutes

        # Setup logging
        self.setup_logging()

        # Start health monitoring
        self.health_monitor_thread = threading.Thread(
            target=self._health_monitor_loop,
            daemon=True
        )
        self.health_monitor_thread.start()

    def setup_logging(self):
        """Setup comprehensive logging"""
        self.logger = logging.getLogger('ChromaDB_Prevention')
        self.logger.setLevel(logging.INFO)

        # File handler
        log_file = self.db_path / "chromadb_prevention.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    @contextmanager
    def transaction_guard(self):
        """Context manager for safe database transactions"""
        memory_before = psutil.virtual_memory().percent
        start_time = time.time()

        try:
            self.logger.info(f"Starting transaction - Memory: {memory_before:.1f}%")
            yield

            memory_after = psutil.virtual_memory().percent
            duration = time.time() - start_time

            self.logger.info(
                f"Transaction completed - Duration: {duration:.2f}s, "
                f"Memory: {memory_before:.1f}% -> {memory_after:.1f}%"
            )

        except Exception as e:
            memory_after = psutil.virtual_memory().percent
            duration = time.time() - start_time

            self.logger.error(
                f"Transaction failed - Duration: {duration:.2f}s, "
                f"Memory: {memory_after:.1f}%, Error: {str(e)}"
            )

            # Check if corruption occurred
            if self._detect_corruption():
                self.logger.critical("Database corruption detected - initiating recovery")
                self._emergency_recovery()

            raise

    def _rebuild_fts_indexes(self) -> bool:
        """
        Attempt to repair known FTS index corruption in place by issuing a REBUILD command.
        Returns True when the rebuild succeeds, False otherwise.
        """
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()
            cursor.execute("INSERT INTO embedding_fulltext_search(embedding_fulltext_search) VALUES('rebuild')")
            conn.commit()
            conn.close()
            self.logger.info("FTS index rebuild completed successfully")
            return True
        except Exception as rebuild_error:
            self.logger.error(f"FTS index rebuild failed: {rebuild_error}")
            return False

    def _detect_corruption(self) -> bool:
        """Detect database corruption"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Test basic queries
            cursor.execute("SELECT COUNT(*) FROM collections")
            cursor.execute("SELECT COUNT(*) FROM embeddings LIMIT 1")

            # Test integrity
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()

            # Attempt targeted repair for known FTS corruption before flagging failure
            if result and isinstance(result[0], str) and "malformed inverted index" in result[0]:
                self.logger.warning(f"Integrity check warning: {result[0]} - attempting FTS rebuild")
                conn.close()
                if self._rebuild_fts_indexes():
                    # Re-run integrity check after repair
                    conn = sqlite3.connect(str(self.db_file))
                    cursor = conn.cursor()
                    cursor.execute("PRAGMA integrity_check")
                    result = cursor.fetchone()
                else:
                    return True

            conn.close()

            if result and result[0] != "ok":
                self.logger.error(f"Integrity check failed: {result[0]}")
                return True

            return False

        except Exception as e:
            self.logger.error(f"Corruption detection failed: {str(e)}")
            return True

    def _emergency_recovery(self):
        """Emergency recovery from corruption"""
        self.logger.critical("Initiating emergency recovery protocol")

        # Find latest backup
        backups = list(self.backup_dir.glob("chroma.sqlite3.backup_*"))
        if not backups:
            self.logger.error("No backups available for recovery")
            return

        latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
        self.logger.info(f"Using backup: {latest_backup}")

        # Replace corrupted database
        corrupted_backup = self.db_file.with_suffix('.corrupted')
        shutil.move(str(self.db_file), str(corrupted_backup))
        shutil.copy2(str(latest_backup), str(self.db_file))

        self.logger.critical("Emergency recovery completed")

    def create_backup(self, force: bool = False) -> bool:
        """Create database backup"""
        try:
            # Check if backup needed
            if not force:
                backups = list(self.backup_dir.glob("chroma.sqlite3.backup_*"))
                if backups:
                    latest_backup = max(backups, key=lambda x: x.stat().st_mtime)
                    age_hours = (time.time() - latest_backup.stat().st_mtime) / 3600
                    if age_hours < self.backup_interval_hours:
                        return True  # Recent backup exists

            # Create backup
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = self.backup_dir / f"chroma.sqlite3.backup_{timestamp}"

            # SQLite backup (safe way)
            conn = sqlite3.connect(str(self.db_file))
            backup_conn = sqlite3.connect(str(backup_file))

            with backup_conn:
                conn.backup(backup_conn)

            conn.close()
            backup_conn.close()

            # Cleanup old backups (keep last 7)
            backups = sorted(self.backup_dir.glob("chroma.sqlite3.backup_*"),
                           key=lambda x: x.stat().st_mtime)
            if len(backups) > 7:
                for old_backup in backups[:-7]:
                    old_backup.unlink()

            self.logger.info(f"Backup created: {backup_file}")
            return True

        except Exception as e:
            self.logger.error(f"Backup failed: {str(e)}")
            return False

    def optimize_database(self):
        """Optimize database performance"""
        try:
            conn = sqlite3.connect(str(self.db_file))
            cursor = conn.cursor()

            # Set optimal pragmas
            optimizations = [
                "PRAGMA journal_mode = WAL",
                "PRAGMA synchronous = NORMAL",
                "PRAGMA cache_size = -1024",  # 1MB cache
                "PRAGMA temp_store = MEMORY",
                "PRAGMA mmap_size = 268435456",  # 256MB mmap
                "VACUUM",
                "PRAGMA optimize"
            ]

            for opt in optimizations:
                cursor.execute(opt)

            conn.commit()
            conn.close()

            self.logger.info("Database optimization completed")

        except Exception as e:
            self.logger.error(f"Database optimization failed: {str(e)}")

    def safe_batch_index(self, collection_name: str, ids: List[str],
                        embeddings: List[List[float]], documents: List[str],
                        metadatas: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """Safely index documents in batches with corruption prevention"""

        if len(ids) == 0:
            return True, "No documents to index"

        # Check memory before starting
        memory = psutil.virtual_memory()
        if memory.percent > self.max_memory_percent:
            return False, f"Memory usage too high: {memory.percent:.1f}% > {self.max_memory_percent}%"

        # Create backup before large operations
        if len(ids) > 50:
            self.create_backup(force=True)

        try:
            client = chromadb.PersistentClient(path=str(self.db_path))

            # Get or create collection
            try:
                collection = client.get_collection(collection_name)
            except:
                collection = client.create_collection(collection_name)

            # Process in safe batches
            batch_size = min(self.max_batch_size, len(ids))

            with self.transaction_guard():
                for i in range(0, len(ids), batch_size):
                    end_idx = min(i + batch_size, len(ids))

                    batch_ids = ids[i:end_idx]
                    batch_embeddings = embeddings[i:end_idx]
                    batch_documents = documents[i:end_idx]
                    batch_metadatas = metadatas[i:end_idx]

                    # Timeout protection
                    start_time = time.time()
                    collection.add(
                        ids=batch_ids,
                        embeddings=batch_embeddings,
                        documents=batch_documents,
                        metadatas=batch_metadatas
                    )

                    # Check for timeout
                    if time.time() - start_time > 30:  # 30 second timeout
                        raise TimeoutError("Batch indexing timed out")

                    self.logger.debug(f"Indexed batch {i//batch_size + 1} ({end_idx - i} documents)")

            return True, f"Successfully indexed {len(ids)} documents"

        except Exception as e:
            error_msg = f"Indexing failed: {str(e)}"
            self.logger.error(error_msg)

            # Check for corruption
            if self._detect_corruption():
                self._emergency_recovery()
                return False, f"{error_msg} (recovery attempted)"

            return False, error_msg

    def _health_monitor_loop(self):
        """Continuous health monitoring loop"""
        while True:
            try:
                # Health checks
                if self._detect_corruption():
                    self.logger.warning("Health check: Corruption detected")
                    self._emergency_recovery()

                # Memory monitoring
                memory = psutil.virtual_memory()
                if memory.percent > self.max_memory_percent:
                    self.logger.warning(f"High memory usage: {memory.percent:.1f}%")

                # Automatic backup
                self.create_backup(force=False)

                # Database optimization (weekly)
                if datetime.now().weekday() == 0 and datetime.now().hour == 2:
                    self.optimize_database()

            except Exception as e:
                self.logger.error(f"Health monitor error: {str(e)}")

            time.sleep(self.health_check_interval)

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage(str(self.db_path))

            backups = list(self.backup_dir.glob("chroma.sqlite3.backup_*"))
            latest_backup = max(backups, key=lambda x: x.stat().st_mtime) if backups else None

            client = chromadb.PersistentClient(path=str(self.db_path))
            collections = client.list_collections()

            return {
                "database_size_mb": os.path.getsize(self.db_file) / (1024*1024),
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent,
                "collections_count": len(collections),
                "backups_count": len(backups),
                "latest_backup_age_hours": (time.time() - latest_backup.stat().st_mtime) / 3600 if latest_backup else None,
                "corruption_free": not self._detect_corruption(),
                "health_status": "GOOD" if not self._detect_corruption() and memory.percent < self.max_memory_percent else "WARNING"
            }

        except Exception as e:
            return {
                "error": str(e),
                "health_status": "ERROR"
            }

def main():
    """Demonstrate the prevention system"""
    print("ChromaDB Corruption Prevention System")
    print("=" * 50)

    prevention = ChromaDBCorruptionPrevention()

    # Create initial backup
    print("Creating initial backup...")
    prevention.create_backup(force=True)

    # Optimize database
    print("Optimizing database...")
    prevention.optimize_database()

    # Get status
    status = prevention.get_system_status()
    print("\nSystem Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")

    print("\nPrevention system active - monitoring in background")

if __name__ == "__main__":
    main()
