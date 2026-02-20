"""Tests for CABR pipe-flow compute graph payloads."""

from __future__ import annotations

from modules.foundups.simulator.economics.compute_graph import (
    build_compute_graph_payload,
    calculate_compute_equivalent,
    calculate_compute_weight,
)
from modules.foundups.simulator.economics.pool_distribution import COMPUTE_TIER_WEIGHTS


def test_compute_weight_matches_pool_distribution_formula() -> None:
    weight = calculate_compute_weight(tokens_used=2000, model_tier="sonnet")
    assert weight == (2000 / 1000) * COMPUTE_TIER_WEIGHTS["sonnet"]


def test_cabr_pipe_size_scales_routed_ups_linearly() -> None:
    low = calculate_compute_equivalent(
        tokens_used=1000,
        model_tier="haiku",
        cabr_pipe_size=0.25,
        epoch_ups_available=10.0,
    )
    high = calculate_compute_equivalent(
        tokens_used=1000,
        model_tier="haiku",
        cabr_pipe_size=0.75,
        epoch_ups_available=10.0,
    )
    assert high.ups_routed > low.ups_routed
    assert high.ups_routed == low.ups_routed * 3


def test_legacy_aliases_still_work() -> None:
    legacy = calculate_compute_equivalent(
        tokens_used=1000,
        model_tier="haiku",
        cabr_v3_score=0.5,
        base_fi_rate=20.0,
    )
    modern = calculate_compute_equivalent(
        tokens_used=1000,
        model_tier="haiku",
        cabr_pipe_size=0.5,
        epoch_ups_available=20.0,
    )
    assert legacy.ups_routed == modern.ups_routed


def test_payload_tiers_sorted_by_weight_desc() -> None:
    payload = build_compute_graph_payload()
    tiers = payload["tiers"]
    weights = [row["tier_weight"] for row in tiers]
    assert weights == sorted(weights, reverse=True)


def test_angel_seeding_total_ups_respects_pipe_budget() -> None:
    payload = build_compute_graph_payload(
        agents_assigned=10,
        model_tier="opus",
        cabr_pipe_size=0.65,
        epoch_ups_available=1000.0,
    )
    total_ups = payload["angel_seeding_example"]["total"]["ups_received"]
    assert total_ups == 650.0
