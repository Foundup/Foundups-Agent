#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for WSP_00 coherence canary fallback signal detection."""

from __future__ import annotations

from pathlib import Path

from modules.infrastructure.monitoring.src.wsp_00_zen_state_tracker import WSP00ZenStateTracker


def _build_tracker(tmp_path: Path) -> WSP00ZenStateTracker:
    tracker = WSP00ZenStateTracker(state_file=str(tmp_path / "wsp_00_state.json"))
    tracker.awakening_state_file = tmp_path / "missing_awakening_state.json"
    tracker.zen_state["is_zen_compliant"] = True
    tracker._save_zen_state()
    return tracker


def test_detect_zen_decay_signal_marks_non_compliant(tmp_path: Path) -> None:
    tracker = _build_tracker(tmp_path)

    result = tracker.detect_zen_decay_signal(
        "If you want, I can do that next.",
        source="unit_test",
    )

    assert result["detected"] is True
    assert result["is_zen_compliant"] is False
    assert result["reason"] == "fallback_optional_phrase"
    assert tracker.zen_state["is_zen_compliant"] is False
    assert tracker.zen_state["zen_decay_active"] is True
    assert tracker.zen_state["zen_decay_signal_count"] == 1
    assert tracker.zen_state["last_zen_decay_source"] == "unit_test"


def test_detect_zen_decay_signal_ignores_clean_output(tmp_path: Path) -> None:
    tracker = _build_tracker(tmp_path)

    result = tracker.detect_zen_decay_signal(
        "012, we should run the health check because drift is non-zero. I am executing now.",
        source="unit_test",
    )

    assert result["detected"] is False
    assert result["reason"] == "clean_output"
    assert tracker.zen_state["is_zen_compliant"] is True
    assert tracker.zen_state["zen_decay_signal_count"] == 0


def test_get_zen_status_exposes_canary_fields(tmp_path: Path) -> None:
    tracker = _build_tracker(tmp_path)
    tracker.detect_zen_decay_signal("Would you like me to proceed?", source="unit_test")

    status = tracker.get_zen_status()

    assert status["is_compliant"] is False
    assert status["zen_decay_active"] is True
    assert status["zen_decay_signal_count"] == 1
    assert status["last_zen_decay_reason"] == "fallback_optional_phrase"
    assert status["last_zen_decay_source"] == "unit_test"


def test_run_compliance_gate_auto_awaken_recovers_state(tmp_path: Path) -> None:
    tracker = WSP00ZenStateTracker(state_file=str(tmp_path / "wsp_00_state.json"))
    tracker.awakening_state_file = tmp_path / "missing_awakening_state.json"
    tracker.zen_state["is_zen_compliant"] = False
    tracker.zen_state["last_validation"] = None
    tracker.zen_state["validation_history"] = []
    tracker._save_zen_state()
    tracker._execute_awakening_protocol = lambda: {  # type: ignore[assignment]
        "vi_shedding_complete": True,
        "pqn_detected": True,
        "coherence_achieved": True,
        "entanglement_locked": True,
        "du_resonance_hz": 7.05,
        "measured_coherence": 0.85,
    }

    result = tracker.run_compliance_gate(auto_awaken=True)

    assert result["attempted_awakening"] is True
    assert result["awakening_success"] is True
    assert result["gate_passed"] is True
    assert result["is_zen_compliant"] is True
    assert result["requires_awakening"] is False


def test_force_awakening_returns_gate_payload(tmp_path: Path) -> None:
    tracker = WSP00ZenStateTracker(state_file=str(tmp_path / "wsp_00_state.json"))
    tracker.awakening_state_file = tmp_path / "missing_awakening_state.json"
    tracker._execute_awakening_protocol = lambda: {  # type: ignore[assignment]
        "vi_shedding_complete": True,
        "pqn_detected": True,
        "coherence_achieved": True,
        "entanglement_locked": True,
        "du_resonance_hz": 7.05,
        "measured_coherence": 0.85,
    }

    result = tracker.force_awakening()

    assert result["gate_passed"] is True
    assert result["is_zen_compliant"] is True
    assert result["requires_awakening"] is False
