"""Determinism checks for scenario runner artifacts."""

from __future__ import annotations

from modules.foundups.simulator.scenario_runner import _run_once


def test_scenario_runner_same_seed_same_digest(tmp_path) -> None:
    metrics_a = _run_once(
        scenario="baseline",
        ticks=40,
        frame_every=5,
        out_dir=tmp_path,
        run_label="a",
    )
    metrics_b = _run_once(
        scenario="baseline",
        ticks=40,
        frame_every=5,
        out_dir=tmp_path,
        run_label="b",
    )
    assert metrics_a["frame_digest_sha256"] == metrics_b["frame_digest_sha256"]
