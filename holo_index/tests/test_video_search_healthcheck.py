#!/usr/bin/env python3
"""
Unit tests for VideoContentIndex health probe and env toggles.

WSP: 5 (Testing), 34 (Test Documentation), 84 (Reuse)
"""

import types

import pytest

import holo_index.core.video_search as video_search


class _DummyCollection:
    def count(self):
        return 0


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


def test_disable_env_blocks_index(monkeypatch):
    _reset_health_state()
    monkeypatch.setenv("CHROMADB_VIDEO_INDEX_DISABLE", "1")
    monkeypatch.setattr(video_search, "chromadb", _DummyChromadb)

    with pytest.raises(RuntimeError):
        video_search.VideoContentIndex()


def test_healthcheck_disabled_skips_probe(monkeypatch):
    _reset_health_state()
    monkeypatch.setenv("CHROMADB_VIDEO_INDEX_HEALTHCHECK", "0")
    monkeypatch.setattr(video_search, "chromadb", _DummyChromadb)

    # If subprocess is called, fail the test
    def _boom(*args, **kwargs):
        raise AssertionError("subprocess.run should not be called when healthcheck is disabled")

    monkeypatch.setattr(video_search.subprocess, "run", _boom)

    index = video_search.VideoContentIndex()
    assert index is not None


def test_healthcheck_failure_blocks_index(monkeypatch):
    _reset_health_state()
    monkeypatch.setattr(video_search, "chromadb", _DummyChromadb)

    class _Result:
        returncode = 1
        stdout = ""
        stderr = "boom"

    monkeypatch.setattr(video_search.subprocess, "run", lambda *a, **k: _Result())

    with pytest.raises(RuntimeError):
        video_search.VideoContentIndex()

