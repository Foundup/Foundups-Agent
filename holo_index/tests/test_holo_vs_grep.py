#!/usr/bin/env python3
"""
Integration tests comparing HoloIndex output vs traditional grep/glob workflows.

Purpose: demonstrate 0102 value (semantic previews, module context) versus raw ripgrep.
"""

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYTHON_EXE = REPO_ROOT / ".venv" / "Scripts" / "python.exe"
RG_PATH = shutil.which("rg")


def _run_holo_search(query: str, limit: int = 3, verbose: bool = False) -> str:
    cmd = [
        str(PYTHON_EXE),
        "holo_index.py",
        "--search",
        query,
        "--limit",
        str(limit)
    ]
    if verbose:
        cmd.append("--verbose")

    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=os.environ
    )
    assert result.returncode == 0, f"HoloIndex CLI failed: {result.stderr}"
    return result.stdout


def _run_rg(query: str) -> subprocess.CompletedProcess:
    if not RG_PATH:
        pytest.skip("ripgrep (rg) not installed in PATH")

    return subprocess.run(
        [RG_PATH, "-n", query, "modules"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )


@pytest.mark.integration
def test_semantic_query_finds_results_where_grep_cannot():
    """HoloIndex should solve semantic PQN queries that literal grep cannot."""
    query = "PQN module in youtube dae"
    holo_output = _run_holo_search(query, limit=4, verbose=True)

    assert "[RESULTS]" in holo_output
    assert "pqn_alignment" in holo_output.lower()
    assert "YOUTUBE_DAE_INTEGRATION.md" in holo_output

    rg_result = _run_rg(query)
    # ripgrep returns exit code 1 when no matches
    assert rg_result.returncode != 0
    assert rg_result.stdout.strip() == ""


@pytest.mark.integration
def test_literal_symbol_found_by_both_holo_and_grep():
    """Literal symbol queries should be found by both systems."""
    query = "pendingClassificationItem"
    holo_output = _run_holo_search(query, verbose=True)
    assert "pendingClassificationItem" in holo_output
    normalized = holo_output.replace("\\", "/").lower()
    assert "modules/foundups/gotjunk/frontend" in normalized

    rg_result = _run_rg(query)
    assert rg_result.returncode == 0
    assert "pendingClassificationItem" in rg_result.stdout


@pytest.mark.integration
def test_tsx_preview_provides_context_beyond_glob():
    """HoloIndex should return semantic results when literal rg fails."""
    query = "handle item classification"
    holo_output = _run_holo_search(query, limit=2, verbose=True)

    assert "[RESULTS]" in holo_output

    rg_result = _run_rg("handle item classification")
    # ripgrep should fail because phrase doesn't exist verbatim
    assert rg_result.stdout.strip() == ""
