# -*- coding: utf-8 -*-
import sys
import io


# === UTF-8 ENFORCEMENT (WSP 90) ===
# Prevent UnicodeEncodeError on Windows systems
# Only apply when running as main script, not during import
if __name__ == '__main__' and sys.platform.startswith('win'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except (OSError, ValueError):
        # Ignore if stdout/stderr already wrapped or closed
        pass
# === END UTF-8 ENFORCEMENT ===

﻿"""Validation for NAVIGATION.py schema and coverage."""

from pathlib import Path

import importlib

NAV = importlib.import_module("NAVIGATION")


def test_need_to_entries_are_semantic():
    assert NAV.NEED_TO, "NEED_TO map cannot be empty"
    for need, location in NAV.NEED_TO.items():
        assert isinstance(need, str) and need.strip(), "Need keys must be non-empty strings"
        assert isinstance(location, str) and location.strip(), f"Location missing for {need}"


def test_module_graph_contains_wre_flow():
    core_flows = NAV.MODULE_GRAPH.get("core_flows", {})
    assert "wre_plugin_flow" in core_flows, "wre_plugin_flow linkage is required for WRE introspection"
    assert len(core_flows["wre_plugin_flow"]) >= 3, "wre_plugin_flow should illustrate full recall sequence"


def test_coverage_table_tracks_need_to_entries():
    coverage_path = Path("WSP_framework/reports/NAVIGATION/NAVIGATION_COVERAGE.md")
    assert coverage_path.exists(), "Coverage table missing"
    lines = [line for line in coverage_path.read_text(encoding="utf-8").splitlines() if line.startswith("|")]
    # Skip header divider lines
    coverage_needs = {
        line.split("|")[1].strip()
        for line in lines[2:]
        if line.count("|") >= 3
    }
    missing = sorted(set(NAV.NEED_TO.keys()) - coverage_needs)
    assert not missing, f"Coverage table missing NEED_TO entries: {missing}"


def test_navigation_operations_present():
    assert "run navigation audit" in NAV.NEED_TO, "Audit shortcut missing"
    assert "validate navigation schema" in NAV.NEED_TO, "Validation shortcut missing"
    assert "NAVIGATION.py" in NAV.__file__, "Module import path unexpected"
