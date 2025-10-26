# -*- coding: utf-8 -*-
"""
Test suite for Vision DAE MCP Server

Tests all MCP endpoints, worker checkpoint management, and retention cleanup.

WSP Compliance: WSP 5 (Test Coverage), WSP 72 (Module Independence)
Sprint 3 - MCP Interface Stub Testing
"""

import pytest
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone, timedelta

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent))

from modules.infrastructure.dae_infrastructure.foundups_vision_dae.mcp.vision_mcp_server import VisionMCPServer


@pytest.fixture
def temp_module_root(tmp_path):
    """Fixture providing isolated module root with memory structure"""
    module_root = tmp_path / "foundups_vision_dae"
    module_root.mkdir()

    # Create memory subdirectories
    memory_root = module_root / "memory"
    (memory_root / "session_summaries").mkdir(parents=True)
    (memory_root / "ui_tars_dispatches").mkdir(parents=True)
    (memory_root / "worker_state").mkdir(parents=True)

    return module_root


@pytest.fixture
def server(temp_module_root, tmp_path):
    """Fixture providing VisionMCPServer instance with temp directories"""
    server_instance = VisionMCPServer(module_root=temp_module_root)

    # Override docs backup location to temp directory (isolate from real files)
    docs_backup = tmp_path / "docs" / "session_backups" / "foundups_vision_dae" / "run_history"
    docs_backup.mkdir(parents=True, exist_ok=True)
    server_instance.docs_backup_dir = docs_backup

    return server_instance


@pytest.fixture
def sample_summary():
    """Fixture providing sample run history summary data"""
    return {
        "mission": "selenium_run_history",
        "summary_ready": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "raw_session_count": 42,
        "timespan_days": 7,
        "aggregates": {
            "total_urls": 15,
            "unique_domains": 8
        },
        "patterns": [
            "frequent_navigation",
            "form_interaction"
        ]
    }


# =============================================================================
# get_latest_summary() Tests
# =============================================================================

class TestGetLatestSummary:
    """Test get_latest_summary endpoint"""

    def test_no_summary_exists(self, server):
        """Should return error when no summary files exist"""
        result = server.get_latest_summary()

        assert result["success"] is False
        assert "No run history summary found" in result["error"]
        assert "checked_paths" in result

    def test_module_memory_summary_exists(self, server, sample_summary):
        """Should return summary from module memory location"""
        # Write summary to module memory
        summary_file = server.session_summaries_dir / "latest_run_history.json"
        with summary_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        result = server.get_latest_summary()

        assert result["success"] is True
        assert result["source"] == "module_memory"
        assert result["summary"]["raw_session_count"] == 42
        assert result["summary"]["timespan_days"] == 7
        assert "timestamp" in result
        assert "file_path" in result

    def test_docs_backup_summary_exists(self, server, sample_summary):
        """Should return summary from docs backup location"""
        # Write summary to docs backup (legacy support)
        server.docs_backup_dir.mkdir(parents=True, exist_ok=True)
        summary_file = server.docs_backup_dir / "latest_run_history.json"
        with summary_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        result = server.get_latest_summary()

        assert result["success"] is True
        assert result["source"] == "docs_backup"
        assert result["summary"]["raw_session_count"] == 42

    def test_prefers_most_recent_file(self, server, sample_summary):
        """Should return most recently modified file when both exist"""
        import time

        # Write older file to docs backup
        server.docs_backup_dir.mkdir(parents=True, exist_ok=True)
        old_file = server.docs_backup_dir / "latest_run_history.json"
        with old_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        time.sleep(0.1)

        # Write newer file to module memory
        newer_summary = sample_summary.copy()
        newer_summary["raw_session_count"] = 99
        newer_file = server.session_summaries_dir / "latest_run_history.json"
        with newer_file.open("w", encoding="utf-8") as f:
            json.dump(newer_summary, f)

        result = server.get_latest_summary()

        assert result["success"] is True
        assert result["summary"]["raw_session_count"] == 99  # Newer file

    def test_invalid_json_handling(self, server):
        """Should return error for malformed JSON"""
        # Write invalid JSON
        summary_file = server.session_summaries_dir / "latest_run_history.json"
        with summary_file.open("w", encoding="utf-8") as f:
            f.write("{invalid json content")

        result = server.get_latest_summary()

        assert result["success"] is False
        assert "Invalid JSON" in result["error"]


# =============================================================================
# list_recent_summaries() Tests
# =============================================================================

class TestListRecentSummaries:
    """Test list_recent_summaries endpoint"""

    def test_no_summaries_exist(self, server):
        """Should return empty list when no summaries exist"""
        result = server.list_recent_summaries()

        assert result["success"] is True
        assert result["summaries"] == []
        assert result["total_found"] == 0
        assert result["limit_applied"] == 10

    def test_lists_multiple_summaries(self, server, sample_summary):
        """Should list multiple summary files with metadata"""
        # Create 3 timestamped summaries
        for i in range(3):
            summary = sample_summary.copy()
            summary["raw_session_count"] = 10 + i
            filename = f"run_history_2025101{i}_120000.json"
            summary_file = server.session_summaries_dir / filename

            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f)

        result = server.list_recent_summaries()

        assert result["success"] is True
        assert len(result["summaries"]) == 3
        assert result["total_found"] == 3

        # Check metadata present
        for summary in result["summaries"]:
            assert "filename" in summary
            assert "timestamp" in summary
            assert "size_bytes" in summary
            assert "source" in summary
            assert "session_count" in summary
            assert "timespan_days" in summary

    def test_limit_parameter_works(self, server, sample_summary):
        """Should respect limit parameter"""
        # Create 15 summaries
        for i in range(15):
            filename = f"run_history_2025101{i:02d}_120000.json"
            summary_file = server.session_summaries_dir / filename

            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(sample_summary, f)

        result = server.list_recent_summaries(limit=5)

        assert result["success"] is True
        assert len(result["summaries"]) == 5
        assert result["total_found"] == 15
        assert result["limit_applied"] == 5

    def test_sorts_by_timestamp_descending(self, server, sample_summary):
        """Should return most recent summaries first"""
        import time

        # Create summaries with different timestamps
        summaries_data = []
        for i in range(3):
            summary = sample_summary.copy()
            summary["raw_session_count"] = i
            filename = f"run_history_{i}.json"
            summary_file = server.session_summaries_dir / filename

            with summary_file.open("w", encoding="utf-8") as f:
                json.dump(summary, f)

            summaries_data.append(summary["timestamp"])
            time.sleep(0.05)

        result = server.list_recent_summaries()

        assert result["success"] is True
        # Timestamps should be descending
        timestamps = [s["timestamp"] for s in result["summaries"]]
        assert timestamps == sorted(timestamps, reverse=True)

    def test_skips_malformed_files(self, server, sample_summary):
        """Should skip files with invalid JSON"""
        # Create 1 valid summary
        valid_file = server.session_summaries_dir / "run_history_001.json"
        with valid_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        # Create 1 invalid summary
        invalid_file = server.session_summaries_dir / "run_history_002.json"
        with invalid_file.open("w", encoding="utf-8") as f:
            f.write("{invalid json")

        result = server.list_recent_summaries()

        assert result["success"] is True
        assert len(result["summaries"]) == 1  # Only valid file


# =============================================================================
# Worker State Tests
# =============================================================================

class TestWorkerState:
    """Test worker checkpoint get/update operations"""

    def test_get_worker_state_empty(self, server):
        """Should return zeros when no checkpoint files exist"""
        result = server.get_worker_state()

        assert result["success"] is True
        assert result["worker_state"]["browser_offset"] == 0
        assert result["worker_state"]["batch_index"] == 0
        assert result["worker_state"]["last_session_id"] == 0
        assert result["checkpoint_timestamp"] is None

    def test_update_worker_checkpoint(self, server):
        """Should create/update checkpoint files"""
        result = server.update_worker_checkpoint(
            browser_offset=1024,
            batch_index=5,
            last_session_id=42
        )

        assert result["success"] is True
        assert set(result["updated_fields"]) == {"browser_offset", "batch_index", "last_session_id"}
        assert "timestamp" in result

        # Verify files created
        assert (server.worker_state_dir / "browser_telemetry_offset.txt").exists()
        assert (server.worker_state_dir / "session_batch_index.txt").exists()
        assert (server.worker_state_dir / "last_session_id.txt").exists()

    def test_update_partial_checkpoint(self, server):
        """Should update only specified fields"""
        result = server.update_worker_checkpoint(browser_offset=2048)

        assert result["success"] is True
        assert result["updated_fields"] == ["browser_offset"]

    def test_get_worker_state_after_update(self, server):
        """Should read checkpoint values correctly"""
        # Update checkpoint
        server.update_worker_checkpoint(
            browser_offset=1024,
            batch_index=5,
            last_session_id=42
        )

        # Read checkpoint
        result = server.get_worker_state()

        assert result["success"] is True
        assert result["worker_state"]["browser_offset"] == 1024
        assert result["worker_state"]["batch_index"] == 5
        assert result["worker_state"]["last_session_id"] == 42
        assert result["checkpoint_timestamp"] is not None

    def test_checkpoint_persistence(self, server):
        """Should persist checkpoint across server restarts"""
        # Update checkpoint
        server.update_worker_checkpoint(browser_offset=9999)

        # Create new server instance (simulates restart)
        new_server = VisionMCPServer(module_root=server.module_root)
        result = new_server.get_worker_state()

        assert result["success"] is True
        assert result["worker_state"]["browser_offset"] == 9999


# =============================================================================
# Retention Cleanup Tests
# =============================================================================

class TestRetentionCleanup:
    """Test automated retention cleanup for summaries and dispatches"""

    def test_cleanup_old_summaries(self, server, sample_summary):
        """Should delete summaries older than retention period"""
        import time

        # Create old summary (modify mtime to simulate age)
        old_file = server.session_summaries_dir / "run_history_old.json"
        with old_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        # Modify mtime to 35 days ago
        old_mtime = (datetime.now(timezone.utc) - timedelta(days=35)).timestamp()
        old_file.touch()
        os.utime(old_file, (old_mtime, old_mtime))

        # Create recent summary
        recent_file = server.session_summaries_dir / "run_history_recent.json"
        with recent_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        result = server.cleanup_old_summaries(days_to_keep=30)

        assert result["success"] is True
        assert result["deleted_count"] == 1
        assert result["kept_count"] == 1
        assert not old_file.exists()
        assert recent_file.exists()

    def test_never_deletes_latest_summary(self, server, sample_summary):
        """Should never delete latest_run_history.json regardless of age"""
        # Create latest_run_history.json with old mtime
        latest_file = server.session_summaries_dir / "latest_run_history.json"
        with latest_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        # Modify mtime to 100 days ago
        old_mtime = (datetime.now(timezone.utc) - timedelta(days=100)).timestamp()
        os.utime(latest_file, (old_mtime, old_mtime))

        result = server.cleanup_old_summaries(days_to_keep=30)

        assert result["success"] is True
        assert result["deleted_count"] == 0
        assert result["kept_count"] == 1
        assert latest_file.exists()  # Never deleted

    def test_cleanup_old_dispatches(self, server, sample_summary):
        """Should delete UI-TARS dispatch files older than retention period"""
        # Create old dispatch
        old_dispatch = server.ui_tars_dispatches_dir / "vision_summary_old.json"
        with old_dispatch.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        # Modify mtime to 20 days ago
        old_mtime = (datetime.now(timezone.utc) - timedelta(days=20)).timestamp()
        os.utime(old_dispatch, (old_mtime, old_mtime))

        # Create recent dispatch
        recent_dispatch = server.ui_tars_dispatches_dir / "vision_summary_recent.json"
        with recent_dispatch.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        result = server.cleanup_old_dispatches(days_to_keep=14)

        assert result["success"] is True
        assert result["deleted_count"] == 1
        assert result["kept_count"] == 1
        assert not old_dispatch.exists()
        assert recent_dispatch.exists()

    def test_cleanup_with_custom_retention(self, server, sample_summary):
        """Should respect custom retention period"""
        # Create file 10 days old
        test_file = server.session_summaries_dir / "run_history_test.json"
        with test_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        old_mtime = (datetime.now(timezone.utc) - timedelta(days=10)).timestamp()
        os.utime(test_file, (old_mtime, old_mtime))

        # Should delete with 7-day retention
        result = server.cleanup_old_summaries(days_to_keep=7)
        assert result["deleted_count"] == 1

        # Recreate file
        with test_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)
        os.utime(test_file, (old_mtime, old_mtime))

        # Should keep with 14-day retention
        result = server.cleanup_old_summaries(days_to_keep=14)
        assert result["deleted_count"] == 0


# =============================================================================
# Integration Tests
# =============================================================================

class TestMCPServerIntegration:
    """End-to-end integration tests"""

    def test_full_workflow(self, server, sample_summary):
        """Test complete workflow: summary → list → checkpoint → cleanup"""
        # 1. Write summary
        summary_file = server.session_summaries_dir / "latest_run_history.json"
        with summary_file.open("w", encoding="utf-8") as f:
            json.dump(sample_summary, f)

        # 2. Get latest summary
        latest = server.get_latest_summary()
        assert latest["success"] is True
        assert latest["summary"]["raw_session_count"] == 42

        # 3. List summaries
        summaries = server.list_recent_summaries(limit=10)
        assert summaries["success"] is True
        assert summaries["total_found"] >= 1

        # 4. Update worker checkpoint
        checkpoint = server.update_worker_checkpoint(
            browser_offset=1024,
            batch_index=5,
            last_session_id=42
        )
        assert checkpoint["success"] is True

        # 5. Get worker state
        state = server.get_worker_state()
        assert state["success"] is True
        assert state["worker_state"]["browser_offset"] == 1024

        # 6. Cleanup (should not delete recent files)
        cleanup = server.cleanup_old_summaries(days_to_keep=30)
        assert cleanup["success"] is True
        assert cleanup["deleted_count"] == 0

    def test_concurrent_checkpoint_updates(self, server):
        """Test worker checkpoint under concurrent updates"""
        # Simulate multiple checkpoint updates
        for i in range(10):
            result = server.update_worker_checkpoint(
                browser_offset=i * 100,
                batch_index=i
            )
            assert result["success"] is True

        # Final state should reflect last update
        state = server.get_worker_state()
        assert state["worker_state"]["browser_offset"] == 900
        assert state["worker_state"]["batch_index"] == 9


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
