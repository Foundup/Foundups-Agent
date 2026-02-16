#!/usr/bin/env python3
"""Tests for 012 corpus source resolution."""

from __future__ import annotations

from pathlib import Path

from holo_index.adaptive_learning.ingest_012_corpus import resolve_source_path


def test_resolve_source_path_prefers_root_012(tmp_path: Path) -> None:
    repo = tmp_path
    root_src = repo / "012.txt"
    root_src.write_text("root", encoding="utf-8")
    data_path = repo / "holo_index" / "data"
    data_path.mkdir(parents=True, exist_ok=True)
    data_src = data_path / "012.txt"
    data_src.write_text("data", encoding="utf-8")

    resolved = resolve_source_path(repo, "auto")
    assert resolved == root_src


def test_resolve_source_path_explicit_relative(tmp_path: Path) -> None:
    repo = tmp_path
    docs_path = repo / "docs" / "012_moshpit"
    docs_path.mkdir(parents=True, exist_ok=True)
    src = docs_path / "012.txt"
    src.write_text("hello", encoding="utf-8")

    resolved = resolve_source_path(repo, "docs/012_moshpit/012.txt")
    assert resolved == src
