#!/usr/bin/env python3
"""
Unit tests for web asset indexing in HoloIndex code collection.
"""

import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

try:
    from holo_index.core.holo_index import HoloIndex
except ImportError:
    pytest.skip("HoloIndex dependencies unavailable", allow_module_level=True)


class DummyCollection:
    def __init__(self):
        self.add_calls = []

    def add(self, ids, embeddings, documents, metadatas):
        self.add_calls.append({
            "ids": ids,
            "embeddings": embeddings,
            "documents": documents,
            "metadatas": metadatas,
        })

    def count(self):
        if not self.add_calls:
            return 0
        return len(self.add_calls[-1]["ids"])


def _make_holo_stub(tmp_path: Path):
    holo = HoloIndex.__new__(HoloIndex)
    collection = DummyCollection()
    holo.project_root = tmp_path
    holo.need_to = {}
    holo.code_collection = collection
    holo._reset_collection = lambda name: collection
    holo._log_agent_action = lambda *args, **kwargs: None
    holo._infer_cube_tag = lambda *args, **kwargs: None
    holo._get_embedding = lambda text: [0.0, 0.0]
    return holo, collection


def test_collect_web_asset_entries_reads_public_assets(tmp_path, monkeypatch):
    public_dir = tmp_path / "public" / "js"
    public_dir.mkdir(parents=True)
    asset_path = public_dir / "foundup-cube.js"
    asset_path.write_text("const phase = 'planning...';", encoding="utf-8")

    holo, _ = _make_holo_stub(tmp_path)
    monkeypatch.setenv("HOLO_INDEX_WEB", "1")
    monkeypatch.setenv("HOLO_WEB_INDEX_ROOTS", "public")
    monkeypatch.setenv("HOLO_WEB_INDEX_MAX_FILES", "10")
    monkeypatch.setenv("HOLO_WEB_INDEX_MAX_CHARS", "200")
    monkeypatch.setenv("HOLO_WEB_INDEX_EXTENSIONS", ".js;.html")

    entries = holo._collect_web_asset_entries()

    assert entries
    locations = [entry["location"] for entry in entries]
    assert "public/js/foundup-cube.js" in locations
    assert any("planning" in entry["payload"] for entry in entries)


def test_collect_web_asset_entries_respects_disable_toggle(tmp_path, monkeypatch):
    public_dir = tmp_path / "public"
    public_dir.mkdir(parents=True)
    (public_dir / "index.html").write_text("<canvas id='buildCanvas'></canvas>", encoding="utf-8")

    holo, _ = _make_holo_stub(tmp_path)
    monkeypatch.setenv("HOLO_INDEX_WEB", "0")

    entries = holo._collect_web_asset_entries()

    assert entries == []


def test_index_code_entries_merges_navigation_and_web_assets(tmp_path, monkeypatch):
    public_dir = tmp_path / "public" / "js"
    public_dir.mkdir(parents=True)
    (public_dir / "foundup-cube.js").write_text("const status = 'promoting...';", encoding="utf-8")

    holo, collection = _make_holo_stub(tmp_path)
    holo.need_to = {"launch orchestrator": "modules/foundups/agent_market/src/orchestrator.py:launch_foundup"}

    monkeypatch.setenv("HOLO_INDEX_WEB", "1")
    monkeypatch.setenv("HOLO_WEB_INDEX_ROOTS", "public")
    monkeypatch.setenv("HOLO_INDEX_SYMBOLS", "0")

    holo.index_code_entries()

    assert collection.add_calls, "Expected index_code_entries to write to collection"
    payload = collection.add_calls[-1]
    metadatas = payload["metadatas"]
    documents = payload["documents"]

    assert any(meta.get("type") == "code" for meta in metadatas)
    assert any(meta.get("type") == "web_asset" for meta in metadatas)
    assert any(meta.get("keywords") for meta in metadatas if meta.get("type") == "web_asset")
    assert "public/js/foundup-cube.js" in documents
