"""Tests for downside/base/upside sustainability matrix runner."""

from __future__ import annotations

from modules.foundups.simulator.sustainability_matrix import run_matrix


def test_run_matrix_outputs_expected_structure(tmp_path) -> None:
    matrix = run_matrix(
        ticks=40,
        frame_every=20,
        runs=1,
        base_seed=100,
        out_dir=tmp_path,
    )
    assert {"downside", "base", "upside", "gate"} <= set(matrix.keys())
    for lane in ("downside", "base", "upside"):
        row = matrix[lane]
        assert row["runs"] == 1
        assert row["ratio_p10"] <= row["ratio_p50"] <= row["ratio_p90"]
    assert "downside_pass" in matrix["gate"]
