# -*- coding: utf-8 -*-
"""
Tests for VisionTelemetryReporter utility used by FoundUps Vision DAE.

Validates snapshot persistence and UI-TARS dispatch behaviour.
"""

import json
from pathlib import Path

from modules.infrastructure.dae_infrastructure.foundups_vision_dae.src.vision_dae import (
    VisionTelemetryReporter,
)


def test_reporter_persists_latest_and_archive(tmp_path):
    """Reporter should create both latest and timestamped summary snapshots."""
    summary_dir = tmp_path / "summaries"
    reporter = VisionTelemetryReporter(summary_dir)

    summary = {"mission": "selenium_run_history", "summary_ready": True}
    archive_path = reporter.persist_summary(summary)

    latest_path = summary_dir / "latest_run_history.json"
    assert latest_path.exists()
    assert archive_path.exists()

    latest_data = json.loads(latest_path.read_text(encoding="utf-8"))
    archive_data = json.loads(archive_path.read_text(encoding="utf-8"))
    assert latest_data == summary
    assert archive_data == summary


def test_reporter_dispatches_to_ui_tars(tmp_path):
    """Reporter should drop summaries into UI-TARS inbox when available."""
    summary_dir = tmp_path / "summaries"
    ui_inbox = tmp_path / "ui_inbox"
    reporter = VisionTelemetryReporter(summary_dir, ui_inbox)

    summary = {"mission": "selenium_run_history", "summary_ready": True}
    reporter.persist_summary(summary)  # ensure files exist

    dispatched = reporter.dispatch_to_ui_tars(summary)
    assert dispatched is not None
    assert dispatched.exists()

    dispatched_data = json.loads(Path(dispatched).read_text(encoding="utf-8"))
    assert dispatched_data == summary
