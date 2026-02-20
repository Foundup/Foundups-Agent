"""Unit tests for CABR treasury flow routing semantics."""

from __future__ import annotations

from modules.foundups.simulator.economics.cabr_flow_router import (
    CABRFlowInputs,
    route_cabr_ups_flow,
)


def test_valve_closed_routes_zero_flow() -> None:
    result = route_cabr_ups_flow(
        CABRFlowInputs(
            treasury_ups_available=1000.0,
            cabr_pipe_size=0.9,
            pob_validated=False,
            requested_ups=100.0,
            release_rate=0.1,
        )
    )
    assert result.valve_open is False
    assert result.routed_ups == 0.0
    assert result.treasury_ups_after == 1000.0


def test_pipe_size_controls_flow_rate() -> None:
    low = route_cabr_ups_flow(
        CABRFlowInputs(
            treasury_ups_available=1000.0,
            cabr_pipe_size=0.25,
            pob_validated=True,
            requested_ups=100.0,
            release_rate=0.1,
        )
    )
    high = route_cabr_ups_flow(
        CABRFlowInputs(
            treasury_ups_available=1000.0,
            cabr_pipe_size=0.75,
            pob_validated=True,
            requested_ups=100.0,
            release_rate=0.1,
        )
    )
    assert high.routed_ups == low.routed_ups * 3


def test_release_budget_caps_flow() -> None:
    result = route_cabr_ups_flow(
        CABRFlowInputs(
            treasury_ups_available=50.0,
            cabr_pipe_size=1.0,
            pob_validated=True,
            requested_ups=1000.0,
            release_rate=0.1,  # 10% of treasury per event
        )
    )
    assert result.epoch_release_budget_ups == 5.0
    assert result.routed_ups == 5.0
    assert result.treasury_ups_after == 45.0
