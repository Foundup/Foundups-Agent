#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for dashboard snapshot export utility.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

from modules.infrastructure.wre_core.src.dashboard_snapshot_export import (
    export_dashboard_snapshot,
    prune_old_snapshots,
)


def test_export_dashboard_snapshot_writes_files(tmp_path):
    payload = {
        "healthy": True,
        "alerts": [],
        "dashboard": {"tot_confidence_rate": 0.72},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    result = export_dashboard_snapshot(
        output_dir=tmp_path,
        retention_days=30,
        pretty=True,
        health_data=payload,
    )

    snapshot = Path(result["snapshot_path"])
    latest = Path(result["latest_path"])

    assert snapshot.exists()
    assert latest.exists()
    assert result["healthy"] is True
    text = latest.read_text(encoding="utf-8")
    assert "\"source_of_truth\": \"sqlite\"" in text


def test_prune_old_snapshots_removes_aged_files(tmp_path):
    old_file = tmp_path / "dashboard_snapshot_old.json"
    new_file = tmp_path / "dashboard_snapshot_new.json"
    latest = tmp_path / "latest.json"

    old_file.write_text("{}", encoding="utf-8")
    new_file.write_text("{}", encoding="utf-8")
    latest.write_text("{}", encoding="utf-8")

    old_time = datetime.now(timezone.utc) - timedelta(days=45)
    new_time = datetime.now(timezone.utc)
    old_ts = old_time.timestamp()
    new_ts = new_time.timestamp()

    import os

    os.utime(old_file, (old_ts, old_ts))
    os.utime(new_file, (new_ts, new_ts))
    os.utime(latest, (old_ts, old_ts))

    removed = prune_old_snapshots(tmp_path, retention_days=30)
    assert removed == 1
    assert not old_file.exists()
    assert new_file.exists()
    # latest.json should never be touched by pruning
    assert latest.exists()
