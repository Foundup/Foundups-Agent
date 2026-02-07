import os
import sqlite3
import tempfile

from holo_index.core.video_search import VideoContentIndex


def _make_index(db_path: str) -> VideoContentIndex:
    index = VideoContentIndex.__new__(VideoContentIndex)
    index.metadata_db = db_path
    return index


def test_metadata_db_insert():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "video_metadata.db")
        index = _make_index(db_path)
        index._init_metadata_db()

        index._record_metadata(
            "vid_0_00",
            {
                "video_id": "vid",
                "title": "Test Video",
                "channel": "undaodu",
                "start_time": "0:00",
                "end_time": "0:10",
                "speaker": "012",
                "topics": "memory,testing",
                "segment_type": "content",
                "indexed_at": "2026-02-06T00:00:00",
            },
            "test content",
        )

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT segment_id, content_hash FROM segments WHERE segment_id = ?", ("vid_0_00",))
        row = cur.fetchone()
        conn.close()

        assert row is not None
        assert row[0] == "vid_0_00"
        assert row[1]


def test_metadata_db_disable():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "video_metadata.db")
        index = _make_index(db_path)
        index._init_metadata_db()

        os.environ["VIDEO_INDEX_SQLITE_DISABLE"] = "1"
        try:
            index._record_metadata(
                "vid_skip",
                {"video_id": "vid", "title": "Skip"},
                "test content",
            )
        finally:
            os.environ.pop("VIDEO_INDEX_SQLITE_DISABLE", None)

        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT segment_id FROM segments WHERE segment_id = ?", ("vid_skip",))
        row = cur.fetchone()
        conn.close()

        assert row is None
#!/usr/bin/env python3
"""
Tests for VideoContentIndex SQLite metadata indexing.
WSP: 5 (Testing), 34 (Test Documentation)
"""

import sqlite3
from pathlib import Path

import pytest

import holo_index.core.video_search as video_search


class _DummyCollection:
    def count(self):
        return 0

    def get(self, ids=None, include=None, limit=None):
        return {}

    def add(self, ids=None, embeddings=None, documents=None, metadatas=None):
        return None


class _DummyClient:
    def __init__(self, path):
        self.path = path

    def get_collection(self, name):
        return _DummyCollection()

    def create_collection(self, name):
        return _DummyCollection()


class _DummyChromadb:
    PersistentClient = _DummyClient


def _reset_health_state():
    video_search.VideoContentIndex._health_checked = False
    video_search.VideoContentIndex._health_ok = True


def test_sqlite_metadata_written(tmp_path, monkeypatch):
    _reset_health_state()
    monkeypatch.setattr(video_search, "chromadb", _DummyChromadb)
    monkeypatch.setenv("CHROMADB_VIDEO_INDEX_HEALTHCHECK", "0")
    monkeypatch.delenv("VIDEO_INDEX_SQLITE_DISABLE", raising=False)

    index = video_search.VideoContentIndex(ssd_path=str(tmp_path))

    metadata = {
        "video_id": "vid123",
        "title": "Test Video",
        "channel": "test",
        "start_time": "0:00",
        "end_time": "0:10",
        "speaker": "Speaker",
        "topics": "topic1,topic2",
        "segment_type": "content",
        "indexed_at": "2026-02-06T00:00:00",
    }

    index._record_metadata("vid123_0_00", metadata, "hello world")

    db_path = Path(tmp_path) / "video_index" / "video_metadata.db"
    assert db_path.exists()

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT segment_id, video_id FROM segments WHERE segment_id = ?", ("vid123_0_00",))
    row = cur.fetchone()
    conn.close()

    assert row == ("vid123_0_00", "vid123")
